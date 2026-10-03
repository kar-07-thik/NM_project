import os
for k in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
    os.environ.pop(k, None)

import re
import json
import uuid
import urllib.parse
from io import BytesIO
from PIL import Image
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize the Gemini Client
api_key = os.getenv("GOOGLE_API_KEY")
client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print("Failed to initialize Gemini Client:", e)

def extract_json_from_response(text: str) -> dict:
    try:
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_str = text
        return json.loads(json_str)
    except Exception:
        # Clean any trailing comma or formatting artifacts
        try:
            cleaned = re.sub(r',\s*([}\]])', r'\1', json_str)
            return json.loads(cleaned)
        except Exception:
            return {}

def save_upload_file(upload_file) -> str:
    if not upload_file or not hasattr(upload_file, 'filename') or not upload_file.filename:
        return None
    upload_dir = os.path.join("static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(upload_file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())
    return file_path

def generate_shopping_links(category_type: str, search_terms: str) -> dict:
    encoded_terms = urllib.parse.quote_plus(search_terms)
    links = {}
    
    if category_type == "home":
        links["Amazon"] = f"https://www.amazon.in/s?k={encoded_terms}"
        links["Flipkart"] = f"https://www.flipkart.com/search?q={encoded_terms}"
        links["Ikea"] = f"https://www.ikea.com/in/en/search/?q={encoded_terms}"
        links["Myntra"] = f"https://www.myntra.com/{encoded_terms}"
        links["Ajio"] = f"https://www.ajio.com/search/?text={encoded_terms}"
    elif category_type == "party":
        terms_lower = search_terms.lower()
        if "catering" in terms_lower or "food" in terms_lower or "meal" in terms_lower:
            links["Swiggy"] = f"https://www.swiggy.com/search?query={encoded_terms}"
            links["Zomato"] = f"https://www.zomato.com/search?q={encoded_terms}"
        elif "venue" in terms_lower or "hall" in terms_lower or "resort" in terms_lower or "hotel" in terms_lower:
            links["Google"] = f"https://www.google.com/search?q={encoded_terms}+venue"
            links["Booking"] = f"https://www.booking.com/search.html?ss={encoded_terms}"
            links["MakeMyTrip"] = f"https://www.makemytrip.com/hotels/hotel-listing/?searchText={encoded_terms}"
            links["OYO"] = f"https://www.oyorooms.com/search/?location={encoded_terms}"
            links["NoBroker"] = f"https://www.nobroker.in/property/search?searchTerm={encoded_terms}"
        elif "entertainment" in terms_lower or "music" in terms_lower or "dj" in terms_lower or "game" in terms_lower:
            links["Amazon"] = f"https://www.amazon.in/s?k={encoded_terms}"
            links["Flipkart"] = f"https://www.flipkart.com/search?q={encoded_terms}"
            links["BookMyShow"] = f"https://in.bookmyshow.com/search?q={encoded_terms}"
        else:
            links["Amazon"] = f"https://www.amazon.in/s?k={encoded_terms}"
            links["Flipkart"] = f"https://www.flipkart.com/search?q={encoded_terms}"
            links["Google"] = f"https://www.google.com/search?q={encoded_terms}"
    elif category_type == "jewelry":
        links["Amazon"] = f"https://www.amazon.in/s?k={encoded_terms}"
        links["Flipkart"] = f"https://www.flipkart.com/search?q={encoded_terms}"
        links["Bluestone"] = f"https://www.bluestone.com/search.html?query={encoded_terms}"
        links["Tanishq"] = f"https://www.tanishq.co.in/search?q={encoded_terms}"
        links["Caratlane"] = f"https://www.caratlane.com/search?q={encoded_terms}"
        links["Melorra"] = f"https://www.melorra.com/search?q={encoded_terms}"
        links["Meesho"] = f"https://www.meesho.com/search?q={encoded_terms}"

    return links


# ─────────────────────────────────────────────────────────────────────────────
# 1. HOME RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────────────────────
def get_home_recommendations(budget_input: dict) -> dict:
    total_budget = float(budget_input.get('total_budget', 5000))
    num_lights = int(budget_input.get('num_lights', 0))
    num_fans = int(budget_input.get('num_fans', 0))
    num_furniture = int(budget_input.get('num_furniture', 0))
    num_dining = int(budget_input.get('num_dining_tables', 0))
    has_lr = budget_input.get('has_living_room', False)
    has_kit = budget_input.get('has_kitchen', False)
    has_bed = budget_input.get('has_bedroom', False)
    reqs = budget_input.get('additional_requirements', '')

    prompt = f"""
    Generate a detailed home interior recommendation plan strictly in JSON format.
    Budget: INR {total_budget}
    Requirements:
    - Lights: {num_lights}
    - Ceiling Fans: {num_fans}
    - Furniture Pieces: {num_furniture}
    - Dining Tables: {num_dining}
    Rooms: Living Room={has_lr}, Kitchen={has_kit}, Bedroom={has_bed}
    Special Requirements: {reqs}

    Return JSON strictly in this structure:
    {{
      "total_budget": {total_budget},
      "remaining_budget": 0,
      "budget_breakdown": [
        {{
          "category": "Lighting",
          "allocation": 0,
          "items": [
            {{
              "name": "LED Bulb (Warm White)",
              "description": "Energy-efficient LED bulbs for general lighting.",
              "estimated_price": 100,
              "quantity": 5,
              "search_terms": "LED bulbs warm white"
            }}
          ]
        }}
      ],
      "calculation_table": [
         {{
           "category": "Lighting",
           "items_count": 5,
           "total_cost": 500,
           "percentage_of_budget": 10
         }}
      ],
      "additional_suggestions": "Helpful styling advice"
    }}
    """
    
    data = None
    if client:
        for model_name in ["gemini-flash-latest", "gemini-3.8-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                data = extract_json_from_response(response.text)
                if data and "budget_breakdown" in data:
                    break
            except Exception as e:
                print(f"Gemini call with {model_name} failed: {e}")

    # Fallback / Default recommendations adhering to user input (Milestone 5, Activity 5.4)
    if not data or "budget_breakdown" not in data or not data["budget_breakdown"]:
        # Intelligently split budget
        lights_qty = max(1, num_lights) if num_lights > 0 else 4
        fans_qty = max(1, num_fans) if num_fans > 0 else 2
        furn_qty = max(1, num_furniture) if num_furniture > 0 else 2
        
        light_budget = round(total_budget * 0.25, 2)
        fan_budget = round(total_budget * 0.35, 2)
        furn_budget = round(total_budget * 0.30, 2)
        rem_budget = round(total_budget - (light_budget + fan_budget + furn_budget), 2)
        
        data = {
            "total_budget": total_budget,
            "remaining_budget": max(0.0, rem_budget),
            "budget_breakdown": [
                {
                    "category": "Lighting",
                    "allocation": light_budget,
                    "items": [
                        {
                            "name": "LED Bulb (Warm White)",
                            "description": "Energy-efficient LED bulbs for ambient & task illumination.",
                            "estimated_price": round(light_budget / lights_qty, 2),
                            "quantity": lights_qty,
                            "search_terms": "LED bulbs warm white"
                        }
                    ]
                },
                {
                    "category": "Ceiling_fans",
                    "allocation": fan_budget,
                    "items": [
                        {
                            "name": "Havells Ceiling Fan",
                            "description": "High air-delivery, power-saving decorative ceiling fan.",
                            "estimated_price": round(fan_budget / fans_qty, 2),
                            "quantity": fans_qty,
                            "search_terms": "Havells ceiling fan"
                        }
                    ]
                },
                {
                    "category": "Furniture",
                    "allocation": furn_budget,
                    "items": [
                        {
                            "name": "Modern Accent Chair / Sofa",
                            "description": "Comfortable, stylish living room seating designed for compact spaces.",
                            "estimated_price": round(furn_budget * 0.6, 2),
                            "quantity": furn_qty,
                            "search_terms": "modern living room chair"
                        },
                        {
                            "name": "Solid Wood Dining Table Set",
                            "description": "Compact dining table set matching your room aesthetic.",
                            "estimated_price": round(furn_budget * 0.4, 2),
                            "quantity": max(1, num_dining),
                            "search_terms": "wooden dining table"
                        }
                    ]
                }
            ],
            "calculation_table": [
                {"category": "Lighting", "items_count": lights_qty, "total_cost": light_budget, "percentage_of_budget": 25},
                {"category": "Ceiling Fans", "items_count": fans_qty, "total_cost": fan_budget, "percentage_of_budget": 35},
                {"category": "Furniture", "items_count": furn_qty + max(1, num_dining), "total_cost": furn_budget, "percentage_of_budget": 30}
            ],
            "additional_suggestions": "Choose warm white 2700K lighting for bedrooms and neutral 4000K for kitchen areas."
        }

    # Populate shopping links
    for category in data.get("budget_breakdown", []):
        for item in category.get("items", []):
            st = item.get("search_terms", item.get("name", ""))
            item["shopping_links"] = generate_shopping_links("home", st)

    # Ensure remaining_budget is set
    if "remaining_budget" not in data:
        allocated = sum(
            sum(float(i.get("estimated_price", 0)) * int(i.get("quantity", 1)) for i in cat.get("items", []))
            for cat in data.get("budget_breakdown", [])
        )
        data["remaining_budget"] = max(0.0, round(total_budget - allocated, 2))

    return data


# ─────────────────────────────────────────────────────────────────────────────
# 2. PARTY RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────────────────────
def get_party_recommendations(budget_input: dict) -> dict:
    total_budget = float(budget_input.get('total_budget', 5000))
    num_guests = int(budget_input.get('num_guests', 10))
    party_type = budget_input.get('party_type', 'Celebration')
    venue_type = budget_input.get('venue_type', 'Home')
    needs_cat = budget_input.get('needs_catering', True)
    needs_dec = budget_input.get('needs_decoration', True)
    needs_ent = budget_input.get('needs_entertainment', True)
    reqs = budget_input.get('additional_requirements', '')

    prompt = f"""
    Generate a detailed party planner budget allocation strictly in JSON format.
    Budget: INR {total_budget}
    Guests: {num_guests}
    Party Type: {party_type}
    Venue: {venue_type}
    Needs: Catering={needs_cat}, Decoration={needs_dec}, Entertainment={needs_ent}
    Notes: {reqs}

    Return JSON strictly in this structure:
    {{
      "total_budget": {total_budget},
      "allocated_budget": {total_budget},
      "remaining_budget": 0,
      "budget_breakdown": [
        {{
          "category": "Venue",
          "total_cost": 0,
          "items": [
             {{ "name": "Home Venue Setup", "description": "Utilizing home as the venue with ambient setup", "estimated_price": 0, "quantity": 1, "search_terms": "party venue" }}
          ]
        }},
        {{
          "category": "Catering",
          "total_cost": 2000,
          "items": [
             {{ "name": "Home cooked / Buffet meal", "description": "Buffet menu for guests", "estimated_price": 2000, "quantity": 1, "search_terms": "party catering food" }}
          ]
        }},
        {{
          "category": "Entertainment",
          "total_cost": 1500,
          "items": [
             {{ "name": "Streaming & Board Games", "description": "Music playlist and party game pack", "estimated_price": 500, "quantity": 1, "search_terms": "party board games" }}
          ]
        }},
        {{
          "category": "Contingency",
          "total_cost": 500,
          "items": [
             {{ "name": "Unexpected expenses buffer", "description": "Contingency buffer for last-minute supplies", "estimated_price": 500, "quantity": 1, "search_terms": "party supplies" }}
          ]
        }}
      ],
      "venue_suggestions": [
        {{ "name": "{venue_type or 'Home'}", "type": "Residential / Event Hall", "estimated_cost": 0, "search_terms": "{venue_type} booking" }}
      ],
      "calculation_table_inr": [
        {{ "category": "Catering", "total_cost": 2000, "percentage_of_budget": 40 }},
        {{ "category": "Entertainment", "total_cost": 1500, "percentage_of_budget": 30 }}
      ]
    }}
    """

    data = None
    if client:
        for model_name in ["gemini-flash-latest", "gemini-3.8-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                data = extract_json_from_response(response.text)
                if data and "budget_breakdown" in data:
                    break
            except Exception as e:
                print(f"Gemini call for party failed with {model_name}: {e}")

    # Fallback adhering exactly to PDF page 53
    if not data or "budget_breakdown" not in data or not data["budget_breakdown"]:
        catering_amt = round(total_budget * 0.45, 2)
        entertainment_amt = round(total_budget * 0.35, 2)
        contingency_amt = round(total_budget * 0.20, 2)
        
        data = {
            "total_budget": total_budget,
            "allocated_budget": total_budget,
            "remaining_budget": 0.0,
            "budget_breakdown": [
                {
                    "category": "Venue",
                    "total_cost": 0.0,
                    "items": [
                        {
                            "name": f"{venue_type or 'Home'}",
                            "description": "Utilizing the home/preferred location as the event venue.",
                            "estimated_price": 0.0,
                            "quantity": 1,
                            "search_terms": "party venue booking"
                        }
                    ]
                },
                {
                    "category": "Catering",
                    "total_cost": catering_amt,
                    "items": [
                        {
                            "name": f"Gourmet Catering / Meal for {num_guests} guests",
                            "description": f"Curated catering packages with snacks, main course, and beverages.",
                            "estimated_price": catering_amt,
                            "quantity": 1,
                            "search_terms": "catering food delivery"
                        }
                    ]
                },
                {
                    "category": "Entertainment",
                    "total_cost": entertainment_amt,
                    "items": [
                        {
                            "name": "Streaming service & party music",
                            "description": "High-energy sound setup and curated playlist subscription.",
                            "estimated_price": round(entertainment_amt * 0.3, 2),
                            "quantity": 1,
                            "search_terms": "music speaker party"
                        },
                        {
                            "name": "Party Games & Decor Kit",
                            "description": "Fun interactive group games, balloons, and themed banners.",
                            "estimated_price": round(entertainment_amt * 0.7, 2),
                            "quantity": 1,
                            "search_terms": "party decorations board games"
                        }
                    ]
                },
                {
                    "category": "Contingency",
                    "total_cost": contingency_amt,
                    "items": [
                        {
                            "name": "Unexpected expenses & Emergency Buffer",
                            "description": "Buffer for last-minute guest additions, ice, or snacks.",
                            "estimated_price": contingency_amt,
                            "quantity": 1,
                            "search_terms": "party disposables"
                        }
                    ]
                }
            ],
            "venue_suggestions": [
                {
                    "name": f"{venue_type or 'Home Venue'}",
                    "type": "Residential / Event Hall",
                    "estimated_cost": 0.0,
                    "search_terms": "banquet hall booking"
                }
            ],
            "calculation_table_inr": [
                {"category": "Venue", "total_cost": 0, "percentage_of_budget": 0},
                {"category": "Catering", "total_cost": catering_amt, "percentage_of_budget": 45},
                {"category": "Entertainment", "total_cost": entertainment_amt, "percentage_of_budget": 35},
                {"category": "Contingency", "total_cost": contingency_amt, "percentage_of_budget": 20}
            ]
        }

    # Shopping links
    for category in data.get("budget_breakdown", []):
        cat_name = category.get("category", "")
        for item in category.get("items", []):
            st = item.get("search_terms", item.get("name", ""))
            item["shopping_links"] = generate_shopping_links("party", f"{st} {cat_name}")

    for venue in data.get("venue_suggestions", []):
        st = venue.get("search_terms", venue.get("name", ""))
        venue["shopping_links"] = generate_shopping_links("party", f"{st} venue")

    return data


# ─────────────────────────────────────────────────────────────────────────────
# 3. JEWELRY RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────────────────────
def get_jewelry_recommendations(budget_input: dict, image_path: str = None) -> dict:
    total_budget = float(budget_input.get('total_budget', 5000))
    occasion = budget_input.get('occasion', 'Special Occasion')
    preferences = budget_input.get('preferences', '')

    prompt = f"""
    Generate detailed jewelry recommendations strictly in JSON format based on the outfit and occasion.
    Budget: INR {total_budget}
    Occasion: {occasion}
    Preferences: {preferences}

    Return JSON strictly in this structure:
    {{
      "total_budget": {total_budget},
      "remaining_budget": 500,
      "outfit_analysis": {{
          "colors": ["gold", "royal blue", "emerald green"],
          "style": "classic / ethnic elegance",
          "formality": "festive / formal"
      }},
      "jewelry_recommendations": [
        {{
          "item_type": "Bracelet",
          "description": "A refined braided link bracelet with polished metal accents.",
          "style": "contemporary",
          "estimated_price": 1200,
          "search_terms": "bracelet for {occasion}"
        }},
        {{
          "item_type": "Ring",
          "description": "A sleek statement ring with minimalist geometric design.",
          "style": "minimalist",
          "estimated_price": 1500,
          "search_terms": "ring for {occasion}"
        }},
        {{
          "item_type": "Necklace / Pendant",
          "description": "A graceful pendant chain complementing the neckline.",
          "style": "classic",
          "estimated_price": 1800,
          "search_terms": "necklace pendant for {occasion}"
        }}
      ],
      "styling_tips": [
        "Keep the jewelry cohesive by sticking to consistent metal finishes.",
        "Layer subtle pieces to highlight your outfit without overwhelming it.",
        "Ensure the necklace length harmonizes with your neckline cut."
      ]
    }}
    """

    data = None
    if client:
        contents = [prompt]
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                contents.append(img)
            except Exception as e:
                print("Failed to load uploaded image for Gemini:", e)
                
        for model_name in ["gemini-flash-latest", "gemini-3.8-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents
                )
                data = extract_json_from_response(response.text)
                if data and "jewelry_recommendations" in data:
                    break
            except Exception as e:
                print(f"Gemini jewelry call with {model_name} failed: {e}")

    # Fallback matching PDF Page 57
    if not data or "jewelry_recommendations" not in data or not data["jewelry_recommendations"]:
        p1 = round(total_budget * 0.25, 2)
        p2 = round(total_budget * 0.30, 2)
        p3 = round(total_budget * 0.35, 2)
        rem = round(total_budget - (p1 + p2 + p3), 2)
        
        data = {
            "total_budget": total_budget,
            "remaining_budget": max(0.0, rem),
            "outfit_analysis": {
                "colors": ["navy blue", "white", "metallic silver"],
                "style": "classic elegance",
                "formality": "festive / formal" if "wedding" in occasion.lower() or "festive" in occasion.lower() else "smart casual"
            },
            "jewelry_recommendations": [
                {
                    "item_type": "Bracelet",
                    "description": "A refined braided link or cuff bracelet with metal accents complementing the occasion.",
                    "style": "contemporary chic",
                    "estimated_price": p1,
                    "search_terms": f"bracelet for {occasion}"
                },
                {
                    "item_type": "Ring",
                    "description": "A sterling silver or gold-plated statement ring with an elegant gemstone centerpiece.",
                    "style": "minimalist",
                    "estimated_price": p2,
                    "search_terms": f"statement ring for {occasion}"
                },
                {
                    "item_type": "Necklace / Watch",
                    "description": "A sophisticated classic timepiece or pendant necklace designed to elevate your outfit.",
                    "style": "classic",
                    "estimated_price": p3,
                    "search_terms": f"necklace watch for {occasion}"
                }
            ],
            "styling_tips": [
                f"For a {occasion}, match warm undertones with gold jewelry and cool undertones with silver or platinum.",
                "Choose one statement piece as the focal point to prevent visual clutter.",
                "Ensure metal finishes across rings, earrings, and bracelets are harmonious."
            ]
        }

    # Add shopping links for each jewelry item
    for item in data.get("jewelry_recommendations", []):
        st = item.get("search_terms", item.get("item_type", ""))
        item["shopping_links"] = generate_shopping_links("jewelry", st)

    return data