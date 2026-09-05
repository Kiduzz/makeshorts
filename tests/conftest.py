import os
import sys

# Make the repo root importable so tests can import the app modules directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# This edition has one mode (BYOK, no user model), so there is no billing flag
# to pin here any more. Keep the import-order guarantee in mind anyway: app.py
# freezes several settings at import time and load_dotenv never overrides an
# existing variable, so anything env-dependent belongs in this file, before any
# test module imports app.
