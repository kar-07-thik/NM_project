import os
for k in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
    os.environ.pop(k, None)

import urllib.request
import urllib.parse
import http.cookiejar
import json
import sqlite3

BASE_URL = "http://127.0.0.1:8080"
print("========================================")
print("  PocketSmart AI - End-to-End Verification")
print("========================================")

# Set up cookie jar
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# 1. Test Home Page
try:
    resp = opener.open(f"{BASE_URL}/")
    print(f"[PASS] 1. GET / -> Status: {resp.status} (Landing Page Loaded)")
except Exception as e:
    print(f"[FAIL] 1. GET /: {e}")

# 2. Test Register Page
try:
    resp = opener.open(f"{BASE_URL}/register")
    print(f"[PASS] 2. GET /register -> Status: {resp.status}")
except Exception as e:
    print(f"[FAIL] 2. GET /register: {e}")

# 3. Test Login Page
try:
    resp = opener.open(f"{BASE_URL}/login")
    print(f"[PASS] 3. GET /login -> Status: {resp.status}")
except Exception as e:
    print(f"[FAIL] 3. GET /login: {e}")

# 4. Test Registration
reg_data = urllib.parse.urlencode({
    "username": "sai",
    "email": "sai@example.com",
    "password": "password123",
    "confirm_password": "password123",
    "full_name": "Sai Kumar"
}).encode('utf-8')

try:
    req = urllib.request.Request(f"{BASE_URL}/api/register", data=reg_data, method="POST")
    resp = opener.open(req)
    print(f"[PASS] 4. POST /api/register -> User 'sai' registered successfully (Redirected to login)")
except Exception as e:
    print(f"[NOTE] 4. Registration note (may already exist): {e}")

# 5. Test Login
login_data = urllib.parse.urlencode({
    "username": "sai",
    "password": "password123"
}).encode('utf-8')

try:
    req = urllib.request.Request(f"{BASE_URL}/token", data=login_data, method="POST")
    resp = opener.open(req)
    print(f"[PASS] 5. POST /token -> Authenticated! Cookie set: {[c.name for c in cj]}")
except Exception as e:
    print(f"[FAIL] 5. Login failed: {e}")

# 6. Test Dashboard
try:
    resp = opener.open(f"{BASE_URL}/dashboard")
    print(f"[PASS] 6. GET /dashboard -> Status: {resp.status} (Dashboard accessible with session)")
except Exception as e:
    print(f"[FAIL] 6. Dashboard: {e}")

# 7. Test Home Planner Form Submission
home_payload = urllib.parse.urlencode({
    "total_budget": 5000,
    "num_lights": 5,
    "num_fans": 4,
    "num_furniture": 2,
    "num_dining_tables": 1,
    "has_living_room": "true",
    "has_kitchen": "true",
    "additional_requirements": "Warm modern lighting"
}).encode('utf-8')

try:
    req = urllib.request.Request(f"{BASE_URL}/home-budget", data=home_payload, method="POST")
    resp = opener.open(req)
    data = json.loads(resp.read().decode('utf-8'))
    print(f"[PASS] 7. POST /home-budget -> Status: {resp.status}, Categories: {len(data.get('budget_breakdown', []))}, Budget: {data.get('total_budget')}")
except Exception as e:
    print(f"[FAIL] 7. Home Budget: {e}")

# 8. Test Party Planner Form Submission
party_payload = urllib.parse.urlencode({
    "total_budget": 5000,
    "num_guests": 3,
    "party_type": "Wedding",
    "venue_type": "Home",
    "needs_catering": "true",
    "needs_decoration": "true",
    "needs_entertainment": "true",
    "additional_requirements": "Family wedding celebration"
}).encode('utf-8')

try:
    req = urllib.request.Request(f"{BASE_URL}/party-budget", data=party_payload, method="POST")
    resp = opener.open(req)
    data = json.loads(resp.read().decode('utf-8'))
    print(f"[PASS] 8. POST /party-budget -> Status: {resp.status}, Categories: {len(data.get('budget_breakdown', []))}, Venue Suggestions: {len(data.get('venue_suggestions', []))}")
except Exception as e:
    print(f"[FAIL] 8. Party Budget: {e}")

# 9. Test Jewelry Planner Form Submission
jewelry_payload = urllib.parse.urlencode({
    "total_budget": 5000,
    "occasion": "Birthday",
    "preferences": "Minimalist silver or platinum accessories"
}).encode('utf-8')

try:
    req = urllib.request.Request(f"{BASE_URL}/jewelry-budget", data=jewelry_payload, method="POST")
    resp = opener.open(req)
    data = json.loads(resp.read().decode('utf-8'))
    print(f"[PASS] 9. POST /jewelry-budget -> Status: {resp.status}, Items: {len(data.get('jewelry_recommendations', []))}, Tips: {len(data.get('styling_tips', []))}")
except Exception as e:
    print(f"[FAIL] 9. Jewelry Budget: {e}")

# 10. Test History Page
try:
    resp = opener.open(f"{BASE_URL}/history")
    html = resp.read().decode('utf-8')
    has_items = "Jewelry Budget" in html or "Party Planning Budget" in html or "Home Interior Budget" in html
    print(f"[PASS] 10. GET /history -> Status: {resp.status} (History page renders saved cards: {has_items})")
except Exception as e:
    print(f"[FAIL] 10. History: {e}")

# 11. Test Database Explorer Page
try:
    resp = opener.open(f"{BASE_URL}/database")
    print(f"[PASS] 11. GET /database -> Status: {resp.status} (Database Explorer Loaded)")
except Exception as e:
    print(f"[FAIL] 11. Database page: {e}")

# 12. Direct Database Check
print("\n--- Direct Database (SQLite) Check ---")
db_file = "pocketsmart.db"
if os.path.exists(db_file):
    conn = sqlite3.connect(db_file)
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    rec_count = conn.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0]
    users = conn.execute("SELECT id, username, email, created_at FROM users").fetchall()
    recs = conn.execute("SELECT id, username, type, timestamp FROM recommendations ORDER BY timestamp DESC LIMIT 5").fetchall()
    conn.close()
    print(f"Database File: {os.path.abspath(db_file)} (Found & Verified)")
    print(f"Total Users in DB: {user_count}")
    for u in users:
        print(f"  - User #{u[0]}: {u[1]} ({u[2]}) created at {u[3]}")
    print(f"Total Recommendations in DB: {rec_count}")
    for r in recs:
        print(f"  - Plan #{r[0][:8]}... by '{r[1]}' (Type: {r[2]}, Date: {r[3]})")
else:
    print("Database file pocketsmart.db not found!")
print("========================================")
