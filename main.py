#!/usr/bin/env python3
"""Entry point for the Invoice Generator CLI - wrapper for backwards compatibility."""

import sys
from pathlib import Path

# Add project root to path for direct execution
sys.path.insert(0, str(Path(__file__).parent))

from src.__main__ import main

if __name__ == "__main__":
    main()
