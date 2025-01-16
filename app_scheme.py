from flask import Flask, render_template, request, redirect, jsonify

import sqlite3

app = Flask(__name__)


def init_db():
    with sqlite3.connect("fitness.db") as conn:
        # Templates table: Stores predefined templates for exercises
        conn.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                exercise TEXT NOT NULL,
                default_sets INTEGER,
                default_reps INTEGER
            )
        """)
        
        # Training sessions table: Stores session-level data
        conn.execute("""
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                template_id INTEGER,
                FOREIGN KEY (template_id) REFERENCES templates (id)
            )
        """)
        
        # Exercises table: Stores individual sets for each exercise in a session
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                exercise TEXT NOT NULL,
                set_number INTEGER NOT NULL,  -- Track set number
                reps INTEGER NOT NULL,
                weight FLOAT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES training_sessions (id)
            )
        """)



@app.route("/")
def homepage():
    with sqlite3.connect("fitness.db") as conn:
        cursor = conn.cursor()
        
        # Fetch the last two training sessions with their template names
        cursor.execute("""
            SELECT s.id, s.date, t.name AS template_name
            FROM training_sessions s
            LEFT JOIN templates t ON s.template_id = t.id
            ORDER BY s.id DESC
            LIMIT 10
        """)
        sessions = cursor.fetchall()

        # Fetch exercises for each session and organize the data
        session_data = []
        for session in sessions:
            session_id, date, template_name = session
            cursor.execute("""
                SELECT exercise, sets, reps, weight
                FROM exercises
                WHERE session_id = ?
            """, (session_id,))
            exercises = cursor.fetchall()
            
            session_data.append({
                "session_id": session_id,
                "date": date,
                "template_name": template_name,
                "exercises": exercises
            })

    return render_template("index.html", session_data=session_data)


@app.route("/templates", methods=["GET"])
def templates():
    with sqlite3.connect("fitness.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM templates")
        templates = cursor.fetchall()
    return render_template("templates.html", templates=templates)


@app.route("/get_last_session/<exercise>", methods=["GET"])
def get_last_session(exercise):
    try:
        with sqlite3.connect("fitness.db") as conn:
            cursor = conn.cursor()
            # Query the exercises table to get the most recent session for the exercise
            cursor.execute("""
                SELECT sets, reps, weight
                FROM exercises
                WHERE exercise = ?
                ORDER BY session_id DESC LIMIT 1
            """, (exercise,))
            last_session = cursor.fetchone()
            
            if last_session:
                return jsonify({"sets": last_session[0], "reps": last_session[1], "weight": last_session[2]})
            else:
                return jsonify({"sets": "", "reps": "", "weight": ""})  # No prior session
    except Exception as e:
        print("Error fetching last session:", e)  # Debug log
        return jsonify({"error": "Failed to fetch data"}), 500



@app.route("/add", methods=["GET", "POST"])
def add_session():
    with sqlite3.connect("fitness.db") as conn:
        cursor = conn.cursor()
        
        if request.method == "POST":
            date = request.form["date"]
            template_id = request.form.get("template_id")

            # Insert the session
            cursor.execute("""
                INSERT INTO training_sessions (date, template_id)
                VALUES (?, ?)
            """, (date, template_id))
            session_id = cursor.lastrowid

            # Insert the exercises for the session
            exercises = request.form.getlist("exercise[]")
            sets = request.form.getlist("sets[]")
            reps = request.form.getlist("reps[]")
            weights = request.form.getlist("weight[]")

            for exercise, set_count, rep_count, weight in zip(exercises, sets, reps, weights):
                # Split the sets into individual set records
                set_numbers = set_count.split(",")  # Assuming the input for sets is a comma-separated list
                reps_values = rep_count.split(",")  # Assuming the input for reps is a comma-separated list
                weights_values = weight.split(",")  # Assuming the input for weights is a comma-separated list
                
                for i, (rep, set_weight) in enumerate(zip(reps_values, weights_values)):
                    cursor.execute("""
                        INSERT INTO exercises (session_id, exercise, set_number, reps, weight)
                        VALUES (?, ?, ?, ?, ?)
                    """, (session_id, exercise, i + 1, rep, set_weight))

            conn.commit()
            return redirect("/")

        # Handle GET: Render the form with template and exercise data
        cursor.execute("SELECT id, name FROM templates")
        templates = cursor.fetchall()

        # Fetch the exercises for each template
        template_exercises = {}
        for template in templates:
            template_id = template[0]
            cursor.execute("""
                SELECT exercise, default_sets, default_reps
                FROM templates
                WHERE id = ?
            """, (template_id,))
            exercises = cursor.fetchall()
            template_exercises[template_id] = exercises

        # Fetch the last session's data for each exercise (weights and reps), independent of template
        exercise_data = {}
        for template_id in template_exercises:
            for exercise, _, _ in template_exercises[template_id]:
                cursor.execute("""
                    SELECT reps, weight
                    FROM exercises
                    WHERE exercise = ?
                    ORDER BY session_id DESC
                    LIMIT 1
                """, (exercise,))
                last_exercise_data = cursor.fetchone()
                if last_exercise_data:
                    exercise_data[exercise] = last_exercise_data
                else:
                    exercise_data[exercise] = (None, None)

        return render_template("add.html", templates=templates, 
                               template_exercises=template_exercises,
                               exercise_data=exercise_data)






if __name__ == "__main__":
    init_db()
    app.run(debug=True)
