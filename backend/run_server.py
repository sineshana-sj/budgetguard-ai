import sys
import os

# Clean path
sys.path = [p for p in sys.path if not p.lower().rstrip('\\/').endswith('desktop')]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, BASE_DIR)
sys.path.insert(1, ROOT_DIR)


import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Starting BudgetGuard AI API Server on http://127.0.0.1:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
