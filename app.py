import os
import uuid
import sqlite3
import json as _json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv

import gemini_utils

load_dotenv()

app = FastAPI(title="PocketSmart: AI Budget Planner")

SECRET_KEY = os.getenv("SECRET_KEY", "pocket_smart_super_secret_jwt_key_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ─── SQLite Database Setup ────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "pocketsmart.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            hashed_password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS recommendations (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL,
            input_summary TEXT NOT NULL,
            full_result TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users(username)
        );
    """)
    conn.commit()
    
    # Ensure is_admin column exists if table was previously created
    cols = [row["name"] for row in cur.execute("PRAGMA table_info(users)").fetchall()]
    if "is_admin" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        conn.commit()

    # Automatically grant admin to 'admin' and 'sai'
    cur.execute("UPDATE users SET is_admin = 1 WHERE username IN ('admin', 'sai')")
    conn.commit()
    conn.close()

init_db()

# ─── Pydantic Models ──────────────────────────────────────────────────────────
class UserInDB(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    hashed_password: str
    is_admin: bool = False

import hashlib
import hmac

def get_password_hash(password: str) -> str:
    # Truncate to safe length if needed, salt and hash with PBKDF2-HMAC-SHA256
    clean_pwd = password[:72]
    salt = uuid.uuid4().hex
    key = hashlib.pbkdf2_hmac('sha256', clean_pwd.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        clean_pwd = plain_password[:72]
        if "$" in hashed_password:
            salt, key_hex = hashed_password.split("$", 1)
            new_key = hashlib.pbkdf2_hmac('sha256', clean_pwd.encode('utf-8'), salt.encode('utf-8'), 100000)
            return hmac.compare_digest(new_key.hex(), key_hex)
        return False
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_from_db(username: str) -> Optional[UserInDB]:
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if row:
        row_keys = row.keys() if hasattr(row, 'keys') else []
        is_adm = bool(row["is_admin"]) if "is_admin" in row_keys else (row["username"].lower() in ["admin", "sai"])
        return UserInDB(
            username=row["username"],
            email=row["email"],
            full_name=row["full_name"],
            hashed_password=row["hashed_password"],
            is_admin=is_adm,
        )
    return None

async def get_current_user(request: Request) -> Optional[UserInDB]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return get_user_from_db(username)
    except JWTError:
        return None

async def get_current_active_user(request: Request) -> UserInDB:
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user

# ─── Recommendation Database Helpers ──────────────────────────────────────────
def save_recommendation(rec_id, username, rec_type, input_summary, full_result):
    conn = get_db()
    conn.execute(
        "INSERT INTO recommendations (id, username, timestamp, type, input_summary, full_result) VALUES (?, ?, ?, ?, ?, ?)",
        (rec_id, username, datetime.utcnow().isoformat(), rec_type,
         _json.dumps(input_summary), _json.dumps(full_result))
    )
    conn.commit()
    conn.close()

def get_user_recommendations(username: str, limit: int = None):
    conn = get_db()
    q = "SELECT * FROM recommendations WHERE username = ? ORDER BY timestamp DESC"
    if limit:
        q += f" LIMIT {limit}"
    rows = conn.execute(q, (username,)).fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "username": r["username"],
            "timestamp": r["timestamp"],
            "type": r["type"],
            "input_summary": _json.loads(r["input_summary"]),
            "full_result": _json.loads(r["full_result"]),
        }
        for r in rows
    ]

# ─── Authentication Endpoints ─────────────────────────────────────────────────

@app.post("/register")
@app.post("/api/register")
async def api_register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: Optional[str] = Form(None),
    full_name: Optional[str] = Form(None),
):
    if len(username.strip()) < 3:
        return RedirectResponse(url="/register?error=Username+must+be+at+least+3+characters", status_code=302)
    if len(password) < 6:
        return RedirectResponse(url="/register?error=Password+must+be+at+least+6+characters", status_code=302)
    if confirm_password and password != confirm_password:
        return RedirectResponse(url="/register?error=Passwords+do+not+match", status_code=302)

    conn = get_db()
    existing = conn.execute(
        "SELECT username FROM users WHERE username = ? OR email = ?", (username.strip(), email.strip())
    ).fetchone()

    if existing:
        conn.close()
        return RedirectResponse(url="/register?error=Username+or+email+already+registered", status_code=302)

    hashed_password = get_password_hash(password)
    conn.execute(
        "INSERT INTO users (username, email, full_name, hashed_password) VALUES (?, ?, ?, ?)",
        (username.strip(), email.strip(), full_name or "", hashed_password)
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url="/login?success=Account+created+successfully!+Please+sign+in.", status_code=302)


@app.post("/token")
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
):
    user = get_user_from_db(username.strip())
    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse(url="/login?error=Invalid+username+or+password", status_code=302)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    res = RedirectResponse(url="/dashboard", status_code=302)
    res.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )
    return res


@app.get("/logout")
@app.post("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response


# ─── Budget Planning Endpoints ────────────────────────────────────────────────

@app.post("/home-budget")
@app.post("/generate-home")
async def plan_home_budget(
    request: Request,
    total_budget: float = Form(...),
    num_lights: int = Form(0),
    num_fans: int = Form(0),
    num_furniture: int = Form(0),
    num_dining_tables: int = Form(0),
    has_living_room: Optional[str] = Form(None),
    has_kitchen: Optional[str] = Form(None),
    has_bedroom: Optional[str] = Form(None),
    additional_requirements: Optional[str] = Form(None),
    user: UserInDB = Depends(get_current_active_user),
):
    budget_input = {
        "total_budget": total_budget,
        "num_lights": num_lights,
        "num_fans": num_fans,
        "num_furniture": num_furniture,
        "num_dining_tables": num_dining_tables,
        "has_living_room": has_living_room == "true",
        "has_kitchen": has_kitchen == "true",
        "has_bedroom": has_bedroom == "true",
        "additional_requirements": additional_requirements or "",
    }
    result = gemini_utils.get_home_recommendations(budget_input)
    rec_id = uuid.uuid4().hex
    save_recommendation(rec_id, user.username, "home", budget_input, result)
    return JSONResponse(content=result)


@app.post("/party-budget")
@app.post("/generate-party")
async def plan_party_budget(
    request: Request,
    total_budget: float = Form(...),
    num_guests: int = Form(0),
    party_type: str = Form(...),
    venue_type: Optional[str] = Form(None),
    needs_catering: Optional[str] = Form(None),
    needs_decoration: Optional[str] = Form(None),
    needs_entertainment: Optional[str] = Form(None),
    additional_requirements: Optional[str] = Form(None),
    user: UserInDB = Depends(get_current_active_user),
):
    budget_input = {
        "total_budget": total_budget,
        "num_guests": num_guests,
        "party_type": party_type,
        "venue_type": venue_type or "",
        "needs_catering": needs_catering == "true",
        "needs_decoration": needs_decoration == "true",
        "needs_entertainment": needs_entertainment == "true",
        "additional_requirements": additional_requirements or "",
    }
    result = gemini_utils.get_party_recommendations(budget_input)
    rec_id = uuid.uuid4().hex
    save_recommendation(rec_id, user.username, "party", budget_input, result)
    return JSONResponse(content=result)


@app.post("/jewelry-budget")
@app.post("/generate-jewelry")
async def plan_jewelry_budget(
    request: Request,
    total_budget: float = Form(...),
    occasion: str = Form(...),
    preferences: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    user: UserInDB = Depends(get_current_active_user),
):
    image_path = gemini_utils.save_upload_file(image) if image and hasattr(image, 'filename') and image.filename else None
    budget_input = {
        "total_budget": total_budget,
        "occasion": occasion,
        "preferences": preferences or "",
        "has_image": bool(image_path),
    }
    result = gemini_utils.get_jewelry_recommendations(budget_input, image_path)
    rec_id = uuid.uuid4().hex
    save_recommendation(rec_id, user.username, "jewelry", budget_input, result)
    return JSONResponse(content=result)


@app.get("/recommendation-details/{recommendation_id}")
async def get_recommendation_details(
    recommendation_id: str,
    user: UserInDB = Depends(get_current_active_user)
):
    conn = get_db()
    row = conn.execute("SELECT * FROM recommendations WHERE id = ? AND username = ?", (recommendation_id, user.username)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {
        "id": row["id"],
        "username": row["username"],
        "timestamp": row["timestamp"],
        "type": row["type"],
        "input_summary": _json.loads(row["input_summary"]),
        "full_result": _json.loads(row["full_result"]),
    }


# ─── Page Routes ──────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse(request=request, name="index.html", context={"user": user})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard")
    error = request.query_params.get("error")
    success = request.query_params.get("success")
    return templates.TemplateResponse(request=request, name="login.html", context={"error": error, "success": success})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard")
    error = request.query_params.get("error")
    return templates.TemplateResponse(request=request, name="register.html", context={"error": error})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, user: UserInDB = Depends(get_current_active_user)):
    recent_activity = get_user_recommendations(user.username, limit=3)
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"user": user, "recent_activity": recent_activity})


@app.get("/home-planner", response_class=HTMLResponse)
async def home_planner_page(request: Request, user: UserInDB = Depends(get_current_active_user)):
    return templates.TemplateResponse(request=request, name="home_planner.html", context={"user": user})


@app.get("/party-planner", response_class=HTMLResponse)
async def party_planner_page(request: Request, user: UserInDB = Depends(get_current_active_user)):
    return templates.TemplateResponse(request=request, name="party_planner.html", context={"user": user})


@app.get("/jewelry-planner", response_class=HTMLResponse)
async def jewelry_planner_page(request: Request, user: UserInDB = Depends(get_current_active_user)):
    return templates.TemplateResponse(request=request, name="jewelry_planner.html", context={"user": user})


@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, user: UserInDB = Depends(get_current_active_user)):
    history_data = get_user_recommendations(user.username)
    return templates.TemplateResponse(request=request, name="history.html", context={"user": user, "history": history_data})


# ─── In-App Visual Database Viewer & Stats (Admin Only) ───────────────────────

@app.get("/database", response_class=HTMLResponse)
async def database_view_page(request: Request, user: UserInDB = Depends(get_current_active_user)):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access Denied: Only administrators have access to view the database."
        )
    conn = get_db()
    users = conn.execute("SELECT id, username, email, full_name, hashed_password, is_admin, created_at FROM users ORDER BY id DESC").fetchall()
    recommendations = conn.execute("SELECT id, username, timestamp, type, input_summary, full_result FROM recommendations ORDER BY timestamp DESC LIMIT 50").fetchall()
    conn.close()
    return templates.TemplateResponse(
        request=request, 
        name="database.html", 
        context={
            "user": user,
            "users": [dict(u) for u in users],
            "recommendations": [dict(r) for r in recommendations],
            "db_path": DB_PATH
        }
    )


@app.get("/api/db-stats")
async def db_stats(user: UserInDB = Depends(get_current_active_user)):
    """Endpoint to check database status and statistics (Admin Only)"""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access Denied: Only administrators can view database stats."
        )
    conn = get_db()
    user_count = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
    rec_count = conn.execute("SELECT COUNT(*) as c FROM recommendations").fetchone()["c"]
    recent_users = [r["username"] for r in conn.execute("SELECT username FROM users ORDER BY id DESC LIMIT 5").fetchall()]
    conn.close()
    return {
        "status": "online",
        "database_file": DB_PATH,
        "db_exists": os.path.exists(DB_PATH),
        "total_users": user_count,
        "total_recommendations": rec_count,
        "recent_users": recent_users,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
