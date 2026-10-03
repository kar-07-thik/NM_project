import os
from flask import Blueprint, render_template, request, flash, current_app, redirect, url_for
from werkzeug.utils import secure_filename
from flask_login import current_user
from app.dependencies import require_login
from app.services.recommendation_service import process_home_recommendation, process_party_recommendation, process_jewelry_recommendation

recommendations_bp = Blueprint('recommendations', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@recommendations_bp.route('/home', methods=['GET', 'POST'])
@require_login
def home_planner():
    if request.method == 'POST':
        try:
            total_budget = float(request.form.get('total_budget'))
            rooms = request.form.getlist('rooms')
            
            fixtures = {
                'lights': request.form.get('lights', 0),
                'fans': request.form.get('fans', 0),
                'furniture': request.form.get('furniture', 0),
                'dining': request.form.get('dining', 0)
            }
            
            result = process_home_recommendation(current_user.id, total_budget, rooms, fixtures)
            if "error" in result:
                flash(result["error"], "danger")
                return redirect(url_for('recommendations.home_planner'))
                
            return render_template('recommendations.html', title="Home Recommendations", result=result, planner_type="Home")
            
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            
    return render_template('home_planner.html', title="Home Planner")

@recommendations_bp.route('/party', methods=['GET', 'POST'])
@require_login
def party_planner():
    if request.method == 'POST':
        try:
            total_budget = float(request.form.get('total_budget'))
            guest_count = int(request.form.get('guest_count'))
            event_type = request.form.get('event_type')
            
            result = process_party_recommendation(current_user.id, total_budget, guest_count, event_type)
            if "error" in result:
                flash(result["error"], "danger")
                return redirect(url_for('recommendations.party_planner'))
                
            return render_template('recommendations.html', title="Party Recommendations", result=result, planner_type="Party")
            
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            
    return render_template('party_planner.html', title="Party Planner")

@recommendations_bp.route('/jewelry', methods=['GET', 'POST'])
@require_login
def jewelry_planner():
    if request.method == 'POST':
        try:
            total_budget = float(request.form.get('total_budget'))
            
            if 'outfit_image' not in request.files:
                flash('No image uploaded', 'danger')
                return redirect(request.url)
                
            file = request.files['outfit_image']
            if file.filename == '':
                flash('No selected file', 'danger')
                return redirect(request.url)
                
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                file.save(filepath)
                
                result = process_jewelry_recommendation(current_user.id, total_budget, filepath)
                if "error" in result:
                    flash(result["error"], "danger")
                    return redirect(url_for('recommendations.jewelry_planner'))
                    
                return render_template('recommendations.html', title="Jewelry Recommendations", result=result, planner_type="Jewelry")
            else:
                flash('Allowed image types are -> png, jpg, jpeg, webp', 'danger')
                
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            
    return render_template('jewelry_planner.html', title="Jewelry Planner")
