"""Convenience entrypoint for Windows/VSCode users."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.main import main

if __name__ == "__main__":
    main()
