"""Add backend root to sys.path so all imports work without installation."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
