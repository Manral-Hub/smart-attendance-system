%%writefile app.py
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import base64
import datetime
import tempfile
import uuid
from using_face_recognition import run_attendance, update_attendance_csv, load_students_from_csv
import pandas as pd

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    filepath = None
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Run attendance
            attendance = run_attendance(filepath)
            
            # Update CSV
            date_used = update_attendance_csv(attendance)
            
            # Encode image for display
            with open(filepath, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Clean up temp file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'attendance': attendance,
                'date': date_used,
                'image': img_data
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
    except Exception as e:
        # Clean up temp file if it exists
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history')
def api_history():
    try:
        df = load_students_from_csv()
        
        # Get date columns (all columns except StudentID, Name, PhotoFilename, ParentEmail)
        date_columns = [col for col in df.columns if col not in ["StudentID", "Name", "PhotoFilename", "ParentEmail"]]
        
        # Build HTML table
        html = '<table><tr><th>Roll No</th><th>Photo</th><th>Name</th>'
        for date_col in date_columns:
            html += f'<th>{date_col}</th>'
        html += '</tr>'
        
        for _, row in df.iterrows():
            student_id = row["StudentID"]
            name = row["Name"]
            photo_path = row["PhotoFilename"]
            
            # Load and encode photo
            try:
                with open(photo_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                photo_html = f'<img src="data:image/jpeg;base64,{img_data}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 50%;" />'
            except:
                photo_html = "<span>No photo</span>"
            
            html += f'<tr><td>{student_id}</td><td>{photo_html}</td><td><strong>{name}</strong></td>'
            
            # Add attendance status for each date column
            for date_col in date_columns:
                status = row[date_col] if pd.notna(row[date_col]) else "-"
                status_class = "present" if status == "Present" else ("absent" if status == "Absent" else "na")
                html += f'<td class="{status_class}">{status}</td>'
            
            html += '</tr>'
        
        html += '</table>'
        
        return jsonify({'success': True, 'history': html})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/simulate-emails', methods=['POST'])
def simulate_emails():
    try:
        df = load_students_from_csv()
        today_date = datetime.date.today().strftime("%d-%m-%Y")
        
        messages_absent = []
        messages_present = []
        
        if today_date not in df.columns:
            return jsonify({'error': f'No attendance data found for {today_date}'}), 400
        
        for _, row in df.iterrows():
            student_name = row["Name"]
            parent_email = row.get("ParentEmail", "itsAnshu@gmail.com")
            if pd.isna(parent_email):
                parent_email = "itsAnshu@gmail.com"
            status = row[today_date] if pd.notna(row[today_date]) else "Absent"
            
            if status == "Present":
                msg = f"To: {parent_email} — Dear Parent, your ward {student_name} was Present on {today_date}. This is only for your information purpose."
                messages_present.append(msg)
            else:
                msg = f"To: {parent_email} — Dear Parent, your ward {student_name} was absent on {today_date}. Kindly update the reason for absence in your school dashboard."
                messages_absent.append(msg)
        
        return jsonify({
            'success': True,
            'absent': messages_absent,
            'present': messages_present,
            'date': today_date
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)