%%writefile using_face_recognition.py
import face_recognition
import datetime
import numpy as np
import pandas as pd

CSV_PATH = "attendance_DB.csv"

def load_students_from_csv(csv_path: str = CSV_PATH):
    """Load the students table from the CSV."""
    df = pd.read_csv(csv_path)
    return df

def load_known_faces(csv_path: str = CSV_PATH):
    """
    Read students from CSV and load their face encodings
    based on the PhotoFilename column.
    """
    df = load_students_from_csv(csv_path)

    known_encodings = []
    known_names = []

    for _, row in df.iterrows():
        name = row["Name"]
        img_path = row["PhotoFilename"]

        image = face_recognition.load_image_file(img_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:  # only add if a face is found
            known_encodings.append(encodings[0])
            known_names.append(name)

    return known_encodings, known_names, df

def run_attendance(test_image_path: str, csv_path: str = CSV_PATH):
    """
    Given a test image path, compare faces with known students
    and return an attendance dict: {Name: "Present"/"Absent"}.
    """
    known_encodings, known_names, df = load_known_faces(csv_path)

    test_image = face_recognition.load_image_file(test_image_path)
    test_encodings = face_recognition.face_encodings(test_image)

    # Default everyone to Absent
    attendance = {name: "Absent" for name in df["Name"]}

    for test_encoding in test_encodings:
        matches = face_recognition.compare_faces(known_encodings, test_encoding, tolerance=0.6)
        face_distances = face_recognition.face_distance(known_encodings, test_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            student_name = known_names[best_match_index]
            attendance[student_name] = "Present"

    return attendance

def update_attendance_csv(attendance: dict, csv_path: str = CSV_PATH, date: str | None = None):
    """
    Add or update a date column in the CSV with the latest attendance.
    - attendance: dict {Name: "Present"/"Absent"}
    - date: string like 'DD-MM-YYYY'; if None, uses today's date.
    """
    if date is None:
        date = datetime.date.today().strftime("%d-%m-%Y")

    df = pd.read_csv(csv_path)

    # If this date column doesn't exist yet, create it with default 'Absent'
    if date not in df.columns:
        df[date] = "Absent"

    # Fill the column for each student based on the attendance dict
    for idx, row in df.iterrows():
        name = row["Name"]
        if name in attendance:
            new_status = attendance[name]
            current_status_in_csv = df.at[idx, date]

            # Only update if the current status in CSV is 'Absent'.
            # This allows an 'Absent' student to become 'Present' or remain 'Absent'.
            # It prevents overwriting a 'Present' status with an 'Absent' status.
            if current_status_in_csv == "Absent":
                df.at[idx, date] = new_status

    df.to_csv(csv_path, index=False)

    return date