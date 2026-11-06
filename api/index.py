import os
import sys

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

# Create Flask application instance
app = create_app()

# WSGI handler for Vercel
if __name__ == "__main__":
    app.run()
