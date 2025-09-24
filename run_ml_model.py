#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick script to run the CareCast ML model and generate predictions
"""

import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Add data directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'data'))

try:
    from data.hospital_ml_model import main
    
    if __name__ == "__main__":
        print("CareCast ML Model")
        print("=" * 40)
        
        # Check if required packages are installed
        try:
            import pandas
            import numpy
            import sklearn
            import xgboost
            print("All required packages are installed")
        except ImportError as e:
            print(f"Missing required package: {e}")
            print("Please install requirements: pip install -r requirements_ml.txt")
            sys.exit(1)
        
        # Run the main ML pipeline
        main()
        
except ImportError as e:
    print(f"Error importing ML model: {e}")
    print("Please ensure all files are in the correct location")
    sys.exit(1)
except Exception as e:
    print(f"Error running ML model: {e}")
    sys.exit(1)
