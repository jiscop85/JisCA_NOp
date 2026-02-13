#!/usr/bin/env python3
"""
ANPR Backend API Testing Suite
Tests all FastAPI endpoints for the license plate detection system
"""

import requests
import sys
import json
import os
from datetime import datetime
from pathlib import Path
import tempfile
from PIL import Image
import io
