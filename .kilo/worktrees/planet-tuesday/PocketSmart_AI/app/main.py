# Main entry point for any specific initializations before running.
# In a standard Flask app factory pattern, run.py typically imports create_app from app.
# We'll use this file to expose the app factory and db explicitly if needed by other modules.

from app import create_app
from app.database import db

app = create_app()

# Expose app and db for debugging or shell contexts
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'app': app}
