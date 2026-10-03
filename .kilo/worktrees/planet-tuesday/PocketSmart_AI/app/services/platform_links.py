import urllib.parse

def generate_platform_links(item_name: str, planner_type: str) -> list:
    """
    Generates dynamic search links for top e-commerce platforms based on the item and category.
    """
    query = urllib.parse.quote(item_name)
    
    links = []
    
    # Generic platforms
    links.append({"platform": "Amazon", "url": f"https://www.amazon.in/s?k={query}", "class": "btn-amazon"})
    links.append({"platform": "Flipkart", "url": f"https://www.flipkart.com/search?q={query}", "class": "btn-flipkart"})
    
    if planner_type == "jewelry":
        links.append({"platform": "Bluestone", "url": f"https://www.bluestone.com/search?search_query={query}", "class": "btn-bluestone"})
        links.append({"platform": "Tanishq", "url": f"https://www.tanishq.co.in/search?q={query}", "class": "btn-tanishq"})
        links.append({"platform": "CaratLane", "url": f"https://www.caratlane.us/search?q={query}", "class": "btn-caratlane"})
        links.append({"platform": "Melorra", "url": f"https://www.melorra.com/jewellery/?q={query}", "class": "btn-melorra"})
        links.append({"platform": "Myntra", "url": f"https://www.myntra.com/{query}", "class": "btn-myntra"})
        
    elif planner_type == "home":
        links.append({"platform": "Ikea", "url": f"https://www.ikea.com/in/en/search/?q={query}", "class": "btn-ikea"})
        links.append({"platform": "Meesho", "url": f"https://www.meesho.com/search?q={query}", "class": "btn-meesho"})
        
    elif planner_type == "party":
        links.append({"platform": "Meesho", "url": f"https://www.meesho.com/search?q={query}", "class": "btn-meesho"})
        links.append({"platform": "Ajio", "url": f"https://www.ajio.com/search/?text={query}", "class": "btn-ajio"})

    return links
