import sys
import os

# Clean sys.path to eliminate Desktop shadowing
sys.path = [p for p in sys.path if not p.lower().rstrip('\\/').endswith('desktop')]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(1, BASE_DIR)
