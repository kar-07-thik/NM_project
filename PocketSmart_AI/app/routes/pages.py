from flask import Blueprint, render_template
from flask_login import current_user
from app.dependencies import require_login
from app.models import RecommendationHistory

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', title="Home")
    return render_template('index.html', title="Welcome")

@pages_bp.route('/dashboard')
@require_login
def dashboard():
    # Fetch user's recent recommendation history
    history = RecommendationHistory.query.filter_by(user_id=current_user.id).order_by(RecommendationHistory.created_at.desc()).limit(5).all()
    return render_template('dashboard.html', title="Dashboard", history=history)

@pages_bp.route('/history')
@require_login
def history():
    history = RecommendationHistory.query.filter_by(user_id=current_user.id).order_by(RecommendationHistory.created_at.desc()).all()
    return render_template('history.html', title="My History", history=history)
