import json
from app.ai.gemini_service import optimize_home_budget, optimize_party_budget, analyze_outfit_and_recommend_jewelry
from app.services.platform_links import generate_platform_links
from app.models import RecommendationHistory
from app.database import db

def process_home_recommendation(user_id: int, total_budget: float, rooms: list, fixtures: dict):
    # Call Gemini AI
    ai_response = optimize_home_budget(total_budget, rooms, fixtures)
    
    if "error" in ai_response:
        return ai_response
    
    # Enrich AI response with platform links
    for allocation in ai_response.get("allocations", []):
        search_term = f"{allocation.get('item')} for {allocation.get('category')}"
        allocation["buy_links"] = generate_platform_links(search_term, "home")
        
    # Save to history
    save_history(user_id, "home", total_budget, {"rooms": rooms, "fixtures": fixtures}, ai_response)
    
    return ai_response

def process_party_recommendation(user_id: int, total_budget: float, guest_count: int, event_type: str):
    ai_response = optimize_party_budget(total_budget, guest_count, event_type)
    
    if "error" in ai_response:
        return ai_response
        
    for allocation in ai_response.get("allocations", []):
        search_term = f"{allocation.get('category')} for {event_type} party"
        allocation["buy_links"] = generate_platform_links(search_term, "party")
        
    save_history(user_id, "party", total_budget, {"guest_count": guest_count, "event_type": event_type}, ai_response)
    
    return ai_response

def process_jewelry_recommendation(user_id: int, total_budget: float, image_path: str):
    ai_response = analyze_outfit_and_recommend_jewelry(image_path, total_budget)
    
    if "error" in ai_response:
        return ai_response
        
    for rec in ai_response.get("recommendations", []):
        search_term = f"{rec.get('item_type')} {rec.get('description')}"
        rec["buy_links"] = generate_platform_links(search_term, "jewelry")
        
    save_history(user_id, "jewelry", total_budget, {"image_uploaded": True}, ai_response)
    
    return ai_response

def save_history(user_id, planner_type, budget, input_data, recommendation_data):
    history = RecommendationHistory(
        user_id=user_id,
        planner_type=planner_type,
        budget=budget,
        input_data=json.dumps(input_data),
        recommendation_data=json.dumps(recommendation_data)
    )
    db.session.add(history)
    db.session.commit()
