# PocketSmart AI: Your Smart Budget & Recommendation Assistant

PocketSmart AI is a Flask-based web application that provides smart budget planning and product recommendations for Home Interior, Parties, and Jewelry. It integrates with Gemini AI for intelligent optimization and outfit analysis.

## Features
- **Authentication**: Secure user registration and login.
- **Home Interior Budget Planner**: Plan your home renovation and furniture budget.
- **Party Budget Planner**: Allocate funds for events, catering, and decorations.
- **Jewelry Budget Planner**: Upload an outfit image to get complementary jewelry recommendations.
- **Smart Recommendations**: Links to top Indian and Global e-commerce platforms.
- **Gemini AI Integration**: Powered by `google-genai` SDK for multimodal analysis.

## Setup Instructions for VS Code

1. **Clone or Open the Repository**
   Open the `PocketSmart_AI` folder in VS Code.

2. **Create a Virtual Environment**
   Open the integrated terminal (`Ctrl` + `\``) and run:
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set Environment Variables**
   - Copy `.env.example` to a new file named `.env`.
   - Add your Gemini API key and adjust the `SECRET_KEY`.
   ```bash
   cp .env.example .env
   ```

6. **Initialize the Database**
   Since SQLite is used, the database will be created automatically when you start the app.

7. **Run the Application**
   ```bash
   python run.py
   ```

8. **Access the Web App**
   Open your browser and navigate to: http://127.0.0.1:5000
