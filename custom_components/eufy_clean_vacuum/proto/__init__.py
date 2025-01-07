"""Proto package for Eufy Clean Vacuum."""
import os
import sys
from pathlib import Path

# Add the custom_components directory to Python path
COMPONENT_PATH = Path(__file__).parent.parent.parent
if str(COMPONENT_PATH) not in sys.path:
    sys.path.insert(0, str(COMPONENT_PATH))
