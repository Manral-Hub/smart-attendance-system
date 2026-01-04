# Automatic Classroom Attendance System using Face Recognition

## Colab + Flask + HTML + ngrok - Web App Implementation

### Project Overview
- **Goal**: Demonstrate an automatic classroom attendance system that recognizes students' faces and marks them as present or absent.
- **Audience**: 7th-grade AI Olympiad project, focused on clear concepts rather than complex engineering.
- **Key Features**:
  - Use stored photos of students as a small "face database"
  - Capture live photos using laptop webcam OR upload photo files
  - Compare faces in the live photo against known faces and determine present/absent
  - Display results in a modern, responsive web interface
  - Log results to a CSV file which acts as a database for attendance records
  - Simulate email notifications to parents for absent students
  - View complete attendance history in a table format

---

## Architecture

### 0. Runtime Environment
**Google Colab** - Eliminates Python installation issues on Windows and keeps the setup simple and portable.

### 1. Flask Backend (`app.py`)
- Serves HTML pages via templates
- Provides API endpoints:
  - `/upload` - Process captured/uploaded images
  - `/api/history` - Retrieve attendance history
  - `/simulate-emails` - Generate email notifications
- Handles file uploads with UUID-based temporary file naming
- Uses base64 encoding for image display in browser

### 2. HTML Frontend (`templates/`)
- **`index.html`** — Main page with:
  - Live camera capture using HTML5 `getUserMedia()`
  - File upload option
  - Automatic image processing after capture/upload
  - Detection results display with student photos
- **`history.html`** — Attendance history table with:
  - Student photos displayed as circular avatars
  - Date-wise attendance columns
  - Email simulation button

### 3. Helper Modules
- **`using_face_recognition.py`** — Core face recognition and CSV logic:
  - Load student data and face encodings from CSV
  - Compare faces with tolerance of 0.6
  - Update attendance with date columns
  - Prevent overwriting "Present" status with "Absent"

### 4. Data Files
- **`attendance_DB.csv`** — Student database with columns:
  - `StudentID`, `Name`, `PhotoFilename`, `ParentEmail`
  - Date columns (format: `DD-MM-YYYY`) added dynamically
- **Student photo files** (e.g., `student1.jpg`, `student2.jpg`, etc.)

### 5. ngrok Tunnel
- Exposes Flask server (localhost:5000) to a public URL
- Makes the app accessible from any browser
- Allows judges to access the demo from their devices

---

## Google Colab Cell Structure

The project consists of **7 cells** that must be run in sequence:

### **Cell 1: Install Dependencies and Import Libraries**
```python
!pip install face_recognition opencv-python pandas flask werkzeug pyngrok

import face_recognition
import numpy as np
import datetime
import pandas as pd
```
*Installs required packages and imports core libraries.*

---

### **Cell 2: Create Face Recognition Module**
```python
%%writefile using_face_recognition.py
# [Face recognition logic code]
```
*Creates the helper module with functions for loading faces, running attendance, and updating CSV.*

**Key Functions:**
- `load_students_from_csv()` - Loads student data
- `load_known_faces()` - Loads face encodings from student photos
- `run_attendance()` - Compares test image with known faces
- `update_attendance_csv()` - Updates CSV with attendance data

---

### **Cell 3: Create Flask Application**
```python
%%writefile app.py
# [Flask server code]
```
*Creates the main Flask web server with all routes and API endpoints.*

**Routes:**
- `/` - Main page (index.html)
- `/history` - History page (history.html)
- `/upload` - POST endpoint for image processing
- `/api/history` - GET endpoint for attendance data
- `/simulate-emails` - POST endpoint for email simulation

---

### **Cell 4: Create Required Directories**
```python
import os
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)
```
*Creates necessary folders for Flask templates and static files.*

---

### **Cell 5: Create Main Page Template**
```python
%%writefile templates/index.html
# [HTML code with embedded CSS and JavaScript]
```
*Creates the main interface with camera capture and upload functionality.*

**Features:**
- Live camera preview with proper stream management
- File upload with drag-and-drop support
- Automatic image processing on capture/upload
- Results display with detection status
- Responsive design with smooth scrolling

---

### **Cell 6: Create History Page Template**
```python
%%writefile templates/history.html
# [HTML code with embedded CSS and JavaScript]
```
*Creates the attendance history view with email simulation.*

**Features:**
- Dynamic table generation from CSV data
- Student photos displayed as circular avatars
- Color-coded attendance status (green=Present, red=Absent)
- Email simulation for today's attendance

---

### **Cell 7: Start Flask Server and ngrok Tunnel**
```python
from pyngrok import ngrok
import threading
import time
import os

# Set ngrok auth token
ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN_HERE")

# Kill existing tunnels and processes
ngrok.kill()
os.system("fuser -k 5000/tcp 2>/dev/null")

# Start Flask in background
def run_flask():
    os.system("python app.py")

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Wait for Flask to start
time.sleep(3)

# Create ngrok tunnel
public_url = ngrok.connect(5000)
print("=" * 60)
print("Flask app is running!")
print("=" * 60)
print(f"Public URL: {public_url}")
print("=" * 60)
print("\nOpen this URL in your browser to access the app.")
print("Share this URL with judges for the demo.")
print("\nNote: The URL will be active as long as this cell is running.")
print("=" * 60)
```

**⚠️ IMPORTANT:** Replace `YOUR_NGROK_AUTH_TOKEN_HERE` with your actual ngrok auth token!
- Get a free token from: https://dashboard.ngrok.com/get-started/your-authtoken

---

## Setup Instructions for Google Colab

### Prerequisites
1. Google account for Colab access
2. ngrok account and auth token (free tier is sufficient)
3. `attendance_DB.csv` file with student data
4. Student photo files

### Step-by-Step Setup

1. **Open Google Colab**
   - Go to https://colab.research.google.com
   - Create a new notebook

2. **Create and Run Cells 1-6**
   - Copy the code for each cell in sequence
   - Run each cell and wait for completion
   - Cells 2, 3, 5, 6 will create files using `%%writefile` magic command

3. **Upload Data Files**
   - Click the folder icon in the left sidebar
   - Upload `attendance_DB.csv`
   - Upload all student photo files (ensure filenames match CSV entries)

4. **Update ngrok Auth Token**
   - Get your auth token from ngrok dashboard
   - Replace the placeholder in Cell 7 with your actual token

5. **Run Cell 7**
   - This starts the Flask server and creates a public URL
   - Copy the public URL shown in the output

6. **Access the Application**
   - Open the ngrok URL in your browser
   - The app is now accessible to anyone with the URL

---

## File Structure

```
Colab Environment:
/
├── app.py                          # Main Flask server
├── using_face_recognition.py       # Face recognition logic
├── templates/
│   ├── index.html                  # Main page (camera/upload + results)
│   └── history.html                # Attendance history table
├── static/                         # (Created but not used - CSS is embedded)
├── attendance_DB.csv               # Student database
└── student1.jpg, student2.jpg...  # Student photos
```

---

## Technical Details

### Camera Capture (HTML5)
- Uses `<video>` element with `getUserMedia()` API for live preview
- JavaScript captures frame to `<canvas>` element
- Converts canvas to Blob and sends to Flask via `fetch()` POST request
- Automatic camera cleanup to prevent "camera already in use" errors

### File Upload (Flask)
- Receives file via `request.files['image']`
- Saves with UUID-based unique filename to `/tmp` directory
- Processes with `run_attendance()` function
- Automatic cleanup of temporary files after processing

### Face Recognition
- Uses `face_recognition` library (built on dlib)
- Tolerance set to 0.6 for matching (adjustable)
- Compares face encodings using Euclidean distance
- Returns "Present" for matched faces, "Absent" for others

### CSV Updates
- Uses pandas for CSV operations
- Creates new date columns dynamically (format: `DD-MM-YYYY`)
- Only updates "Absent" → "Present" (never overwrites "Present" → "Absent")
- This allows multiple attendance captures in one day without losing data

### Email Simulation
- No actual SMTP (avoids email configuration complexity)
- Generates formatted message text only
- Reads `ParentEmail` from CSV
- Different messages for Present vs Absent students
- Returns formatted HTML for browser display

### Image Handling
- All images encoded in base64 for browser display
- Eliminates need for static file serving
- Works seamlessly with ngrok tunneling

---

## Demo Flow for AI Olympiad Presentation

1. **Setup Phase** (Before Judges Arrive)
   - Open Colab notebook
   - Run all cells in sequence (1-7)
   - Get the public ngrok URL
   - Test the app once to ensure it works

2. **Demonstration Flow**
   - Share the ngrok URL with judges
   - Judges can open on their devices (phones/tablets/laptops)

3. **Main Features to Demonstrate**
   
   **a) Face Recognition**
   - Open the main page
   - Click "Take Photo" to capture live image
   - OR click "Upload" to use a pre-captured photo
   - Show the detection results with student names
   
   **b) Attendance History**
   - Navigate to "Attendance History"
   - Show the table with all students and dates
   - Explain the color coding (green=Present, red=Absent)
   
   **c) Email Simulation**
   - Click "Simulate Email to Parents"
   - Show the generated messages for present/absent students
   - Explain that this could be connected to real email in production

4. **Q&A Points to Emphasize**
   - AI concept: Face recognition using machine learning
   - Practical application: Automates manual attendance
   - Real-world impact: Saves time, reduces errors, notifies parents
   - Future enhancements: SMS notifications, analytics, mobile app

---

## Common Issues and Solutions

### Issue: "No module named 'face_recognition'"
**Solution:** Make sure Cell 1 completed successfully. Re-run if needed.

### Issue: "Camera not accessible"
**Solution:** 
- Grant camera permissions in your browser
- Close other apps using the camera
- Try the "Upload" option instead

### Issue: "ngrok tunnel not connecting"
**Solution:**
- Verify auth token is correct
- Check internet connection
- Try running Cell 7 again

### Issue: "No face detected in image"
**Solution:**
- Ensure face is clearly visible and well-lit
- Photo should be front-facing
- Try with a different photo

### Issue: "CSV file not found"
**Solution:**
- Verify CSV file is uploaded to Colab
- Check filename matches exactly: `attendance_DB.csv`
- Ensure student photo paths in CSV are correct

---

## Python Version Requirements

- **Python 3.7+** (Colab provides Python 3.10 by default)
- The code uses type hints (`str | None`) which requires Python 3.10+
- All dependencies are compatible with Colab's default environment

---

## Dependencies

```
face_recognition    # Face detection and recognition
opencv-python       # Image processing
pandas              # CSV data manipulation
flask               # Web framework
werkzeug            # Flask utilities (secure filename, etc.)
pyngrok             # ngrok tunnel management
```

All packages are automatically installed in Cell 1.

---

## CSV File Format

The `attendance_DB.csv` should have the following structure:

```csv
StudentID,Name,PhotoFilename,ParentEmail,01-01-2026,02-01-2026,...
1,Aarav Kumar,student1.jpg,parent1@email.com,Present,Absent,...
2,Diya Sharma,student2.jpg,parent2@email.com,Absent,Present,...
3,Arjun Patel,student3.jpg,parent3@email.com,Present,Present,...
```

**Required Columns:**
- `StudentID` - Unique identifier (integer)
- `Name` - Student name (string)
- `PhotoFilename` - Path to photo file (string)
- `ParentEmail` - Email for notifications (string)

**Date Columns** (auto-generated):
- Added when attendance is run
- Format: `DD-MM-YYYY`
- Values: "Present" or "Absent"

---

## Future Enhancements

1. **SMS Notifications** - Integrate with Twilio for real-time alerts
2. **Analytics Dashboard** - Show attendance trends, charts, insights
3. **Mobile App** - Native Android/iOS app for teachers
4. **Multi-class Support** - Handle multiple classrooms
5. **Student Dashboard** - Allow students to view their own attendance
6. **Export Reports** - PDF/Excel reports for administration
7. **Biometric Backup** - QR codes or fingerprint as backup authentication

---

## Credits

**Project By:** Shaurya Singh Manral
**Grade:** 7th  
**Competition:** AI Olympiad 2026  
**Technologies:** Python, Flask, Face Recognition (dlib), HTML5, JavaScript, ngrok  
**Platform:** Google Colab

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This project was created for educational purposes as part of the TalentSprint AI Olympiad 2026 submission by a 7th-grade student. Feel free to use, learn from, and build upon this project!

---

## Contact

For questions or issues during the demo, contact:  
shauryasingh.manral@gmail.com

---

**Last Updated:** January 1, 2026

