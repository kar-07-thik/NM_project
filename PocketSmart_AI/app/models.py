from datetime import datetime
from flask_login import UserMixin
from app.database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    recommendations = db.relationship('RecommendationHistory', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'

class RecommendationHistory(db.Model):
    __tablename__ = 'recommendation_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    planner_type = db.Column(db.String(50), nullable=False) # 'home', 'party', 'jewelry'
    budget = db.Column(db.Float, nullable=False)
    input_data = db.Column(db.Text, nullable=True) # JSON string of inputs
    recommendation_data = db.Column(db.Text, nullable=False) # JSON string of Gemini response
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RecommendationHistory {self.planner_type} for User {self.user_id}>'
