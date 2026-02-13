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

class ANPRAPITester:
    def __init__(self, base_url="https://anpr-master.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, timeout=60)
                elif data:
                    headers['Content-Type'] = 'application/json'
                    response = requests.post(url, json=data, headers=headers, timeout=30)
                else:
                    response = requests.post(url, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            print(f"   Status: {response.status_code}")
            
success = response.status_code == expected_status
            details = ""
            
            if success:
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                details = f"Expected {expected_status}, got {response.status_code}. Response: {response.text[:200]}"
                print(f"   Error: {details}")

            self.log_test(name, success, details)
            return success, response.json() if success and response.content else {}

        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"   Exception: {error_msg}")
            self.log_test(name, False, error_msg)
            return False, {}

    def create_test_image(self, width=640, height=480, format='JPEG'):
        """Create a simple test image"""
        img = Image.new('RGB', (width, height), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root Endpoint", "GET", "api/", 200)

    def test_status_endpoints(self):
        """Test status check endpoints"""
        # Test POST status
        success1, response1 = self.run_test(
            "Create Status Check", 
            "POST", 
            "api/status", 
            200,
            data={"client_name": "test_client"}
        )
        
        # Test GET status
        success2, response2 = self.run_test("Get Status Checks", "GET", "api/status", 200)
        
        return success1 and success2

    def test_single_image_detection(self):
        """Test single image detection endpoint"""
        # Create test image
        test_image = self.create_test_image()
        files = {'file': ('test_image.jpg', test_image, 'image/jpeg')}
        
        success, response = self.run_test(
            "Single Image Detection",
            "POST",
            "api/detect/image",
            200,
            files=files
        )

 if success:
            # Check response structure
            if 'success' in response and 'message' in response:
                print(f"   Detection success: {response.get('success')}")
                print(f"   Message: {response.get('message')}")
                if response.get('detection'):
                    detection = response['detection']
                    print(f"   Plate text: {detection.get('plate_text', 'N/A')}")
                    print(f"   Confidence: {detection.get('confidence', 'N/A')}")
                return True
            else:
                self.log_test("Single Image Detection - Response Structure", False, "Missing required fields in response")
                return False
        
        return success

    def test_batch_detection(self):
        """Test batch image detection endpoint"""
        # Create multiple test images
        files = []
        for i in range(2):
            test_image = self.create_test_image()
            files.append(('files', (f'test_image_{i}.jpg', test_image, 'image/jpeg')))
        
        success, response = self.run_test(
            "Batch Image Detection",
            "POST",
            "api/detect/batch",
            200,
            files=files
        )
        
        if success:
            # Check response structure
            if 'success' in response and 'total' in response:
                print(f"   Total processed: {response.get('total')}")
                print(f"   Successful: {response.get('successful')}")
                print(f"   Failed: {response.get('failed')}")
                return True
            else:
                self.log_test("Batch Detection - Response Structure", False, "Missing required fields in response")
                return False
        
        return success

 def test_detections_endpoints(self):
        """Test detection history endpoints"""
        # Test GET detections
        success1, response1 = self.run_test("Get Detections", "GET", "api/detections", 200)
        
        if success1:
            print(f"   Found {len(response1)} detections")
            
            # If we have detections, test individual detection endpoint
            if response1 and len(response1) > 0:
                detection_id = response1[0].get('id')
                if detection_id:
                    success2, response2 = self.run_test(
                        "Get Single Detection",
                        "GET",
                        f"api/detections/{detection_id}",
                        200
                    )
                    return success1 and success2
        
        return success1

    def test_file_serving(self):
        """Test file serving endpoints"""
        # This test will likely fail since we don't have actual files, but we test the endpoint structure
        success1, _ = self.run_test(
            "File Serving - Uploads",
            "GET",
            "api/files/uploads/nonexistent.jpg",
            404  # Expecting 404 for non-existent file
        )
        
        success2, _ = self.run_test(
            "File Serving - Outputs", 
            "GET",
            "api/files/outputs/nonexistent.jpg",
            404  # Expecting 404 for non-existent file
        )
        
        return success1 and success2
