import sys
from pathlib import Path

# Allow test modules to import from the project root
sys.path.insert(0, str(Path(__file__).parent.parent))
