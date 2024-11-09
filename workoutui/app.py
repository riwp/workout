from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from pydub import AudioSegment
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize database
def init_db():
    conn = sqlite3.connect('workouts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS audio_files
                 (id INTEGER PRIMARY KEY, file_name TEXT, description TEXT, category TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS workouts
                 (id INTEGER PRIMARY KEY, name TEXT, description TEXT, category TEXT, file_ids TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return redirect('/record')

# Record Audio Page
@app.route('/record', methods=['GET', 'POST'])
def record_audio():
    if request.method == 'POST':
        # Handle audio upload and metadata storage
        audio_file = request.files['audio']
        file_name = request.form['file_name']
        description = request.form['description']
        category = request.form['category']

        # Save audio file
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
        audio_file.save(audio_path)

        # Save metadata to database
        conn = sqlite3.connect('workouts.db')
        c = conn.cursor()
        c.execute("INSERT INTO audio_files (file_name, description, category) VALUES (?, ?, ?)",
                  (audio_file.filename, description, category))
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Audio file saved successfully!"}), 200

    return render_template('record_audio.html')

# Organize Workout Page
@app.route('/organize', methods=['GET', 'POST'])
def organize_workout():
    conn = sqlite3.connect('workouts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM audio_files")
    audio_files = c.fetchall()
    conn.close()

    if request.method == 'POST':
        # Save workout
        name = request.form['workout_name']
        description = request.form['description']
        category = request.form['category']
        selected_files = request.form.getlist('selected_files')  # List of selected file IDs

        conn = sqlite3.connect('workouts.db')
        c = conn.cursor()
        c.execute("INSERT INTO workouts (name, description, category, file_ids) VALUES (?, ?, ?, ?)",
                  (name, description, category, ",".join(selected_files)))
        conn.commit()
        conn.close()

        return jsonify({"message": "Workout created successfully!"}), 200

    return render_template('organize_workout.html', audio_files=audio_files)

# Start Workout Page
@app.route('/start', methods=['GET'])
def start_workout():
    conn = sqlite3.connect('workouts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM workouts")
    workouts = c.fetchall()
    conn.close()

    return render_template('start_workout.html', workouts=workouts)

@app.route('/play_workout/<int:workout_id>', methods=['GET'])
def play_workout(workout_id):
    conn = sqlite3.connect('workouts.db')
    c = conn.cursor()
    c.execute("SELECT file_ids FROM workouts WHERE id=?", (workout_id,))
    file_ids = c.fetchone()[0].split(',')
    c.execute("SELECT file_name FROM audio_files WHERE id IN ({})".format(",".join(file_ids)))
    audio_files = c.fetchall()
    conn.close()

    # Here you would implement code to play audio files sequentially
    return jsonify(audio_files=[f[0] for f in audio_files])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
