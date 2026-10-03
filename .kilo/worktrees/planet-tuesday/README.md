# PocketSmart AI: Your Smart Budget & Recommendation Assistant

## Simple VS Code Setup & Installation Instructions

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your system.
Open this project folder (`NM_proj`) in **VS Code**.

### 2. Environment Setup
1. Open a new terminal in VS Code (`Terminal` -> `New Terminal`).
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - **Windows:**
     ```powershell
     .\venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```bash
     source venv/bin/activate
     ```

### 3. Install Dependencies
Run the following command to install all required libraries:
```bash
pip install -r requirements.txt
```

### 4. Configuration (.env)
1. Open the `.env` file in the root directory.
2. Replace `"your_gemini_api_key_here"` with your actual Google Gemini API Key.
   - *Get a key from [Google AI Studio](https://aistudio.google.com/)*.
3. Keep the default `SECRET_KEY` for local testing, or generate a new one using `openssl rand -hex 32`.

### 5. Running the Application
Start the FastAPI server using Uvicorn:
```bash
python app.py
```
*Alternatively:*
```bash
uvicorn app.py:app --reload
```

The application will be accessible at: **http://localhost:8000**

### 6. Testing Scenarios

#### Scenario 1: User Registration & Login
1. Go to `http://localhost:8000`.
2. Click **Get Started** or **Register**.
3. Create an account.
4. Sign in with the newly created credentials to access the Dashboard.

#### Scenario 2: Home Interior Planning
1. Navigate to **Home Budget Planner**.
2. Enter a Total Budget (e.g., 50000).
3. Specify the number of Lights, Ceiling Fans, and Furniture.
4. Select the rooms to include.
5. Click **Generate Recommendations**. Wait a few seconds for the Gemini AI to process and return structured results with live shopping links.

#### Scenario 3: Party Budget Planning
1. Navigate to **Party Budget Planner**.
2. Enter a budget (e.g., 10000) and Guest count (e.g., 50).
3. Specify Party Type (e.g., Birthday).
4. Check Catering, Decoration, and Entertainment.
5. Generate the plan to see category allocations and suggested venues.

#### Scenario 4: Jewelry Planner & Multimodal AI
1. Navigate to **Jewelry Budget Planner**.
2. Enter a budget (e.g., 5000), Occasion (e.g., Wedding).
3. (Optional) Upload an image of your outfit.
4. Generate the recommendations. If an image is provided, the AI will analyze the outfit colors and style to suggest matching jewelry.

#### Scenario 5: Recommendation History
1. Navigate to **History** from the navigation bar.
2. Review all past plans and click **View Full Details** to inspect the raw structured JSON response from the AI.
