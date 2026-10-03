import json
from google import genai
from google.genai import types
from PIL import Image
from flask import current_app

def get_gemini_client():
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in configuration")
    return genai.Client(api_key=api_key)

def optimize_home_budget(total_budget: float, rooms: list, fixtures: dict):
    client = get_gemini_client()
    
    prompt = f"""
    You are an expert home interior budget planner.
    Total Budget: ${total_budget}
    Rooms: {', '.join(rooms)}
    Fixtures requested: Lights ({fixtures.get('lights')}), Ceiling Fans ({fixtures.get('fans')}), 
    Furniture Pieces ({fixtures.get('furniture')}), Dining Tables ({fixtures.get('dining')}).
    
    Allocate the budget across the specified rooms and fixtures. Keep it realistic.
    Respond ONLY with a JSON object in the following format, with no markdown formatting or extra text:
    {{
        "allocations": [
            {{"category": "Category Name", "item": "Item Name", "allocated_amount": 100, "reasoning": "Why this amount"}}
        ],
        "total_allocated": 0,
        "remaining_budget": 0,
        "advice": "Brief overall advice"
    }}
    """
    
    try:
        # Use the newer google-genai SDK 
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        # Strip potential markdown code block markers
        text_response = response.text.replace('```json\n', '').replace('```', '').strip()
        return json.loads(text_response)
    except Exception as e:
        print(f"Gemini error: {e}")
        return {"error": "Failed to generate recommendations"}

def optimize_party_budget(total_budget: float, guest_count: int, event_type: str):
    client = get_gemini_client()
    
    prompt = f"""
    You are an expert party budget planner.
    Total Budget: ${total_budget}
    Guest Count: {guest_count}
    Event Type: {event_type}
    
    Allocate the budget for venue, catering, decorations, and entertainment.
    Respond ONLY with a JSON object in the following format, with no markdown formatting or extra text:
    {{
        "allocations": [
            {{"category": "Venue/Catering/Decor/Entertainment", "allocated_amount": 100, "reasoning": "Why this amount"}}
        ],
        "total_allocated": 0,
        "remaining_budget": 0,
        "per_person_cost": 0,
        "advice": "Brief overall advice"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        text_response = response.text.replace('```json\n', '').replace('```', '').strip()
        return json.loads(text_response)
    except Exception as e:
        print(f"Gemini error: {e}")
        return {"error": "Failed to generate recommendations"}

def analyze_outfit_and_recommend_jewelry(image_path: str, budget: float):
    client = get_gemini_client()
    
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Image load error: {e}")
        return {"error": "Failed to load image"}
    
    prompt = f"""
    You are an expert fashion consultant. 
    Analyze the uploaded outfit image. Identify the colors, style, and formality.
    Based on this analysis, recommend complementary jewelry (e.g., bracelets, rings, watches, necklaces) 
    that fits a total budget of ${budget}.
    
    Respond ONLY with a JSON object in the following format, with no markdown formatting or extra text:
    {{
        "outfit_analysis": {{
            "primary_colors": ["color1", "color2"],
            "style": "e.g., casual, formal, traditional",
            "formality": "e.g., high, medium, low"
        }},
        "recommendations": [
            {{"item_type": "e.g., Ring, Watch", "description": "Specific style recommended", "estimated_price": 50, "reasoning": "Why it matches the outfit"}}
        ],
        "total_estimated": 0,
        "advice": "Styling advice"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt],
        )
        text_response = response.text.replace('```json\n', '').replace('```', '').strip()
        return json.loads(text_response)
    except Exception as e:
        print(f"Gemini error: {e}")
        return {"error": "Failed to generate multimodal recommendations"}
