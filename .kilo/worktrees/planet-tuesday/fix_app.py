import re

with open('app.py', 'r') as f:
    code = f.read()

# Replace templates.TemplateResponse("file.html", {"request": request, ...})
# with templates.TemplateResponse(request=request, name="file.html", context={"request": request, ...})
new_code = re.sub(
    r'templates\.TemplateResponse\(\s*(["\'][^"\']+["\'])\s*,\s*(\{.*?\})\s*\)',
    r'templates.TemplateResponse(request=request, name=\1, context=\2)',
    code
)

with open('app.py', 'w') as f:
    f.write(new_code)
