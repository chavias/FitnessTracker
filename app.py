from flask import Flask, render_template, request, redirect, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    with sqlite3.connect("fitness.db") as conn:
        # Templates table: Stores predefined templates
        conn.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)

        # Template exercises table: Stores exercises associated with each template
        conn.execute("""
            CREATE TABLE IF NOT EXISTS template_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                exercise TEXT NOT NULL,
                FOREIGN KEY (template_id) REFERENCES templates (id)
            )
        """)

        # Training sessions table (unchanged)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                template_id INTEGER,
                FOREIGN KEY (template_id) REFERENCES templates (id)
            )
        """)

        # Exercises table (unchanged)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                exercise TEXT NOT NULL,
                sets INTEGER NOT NULL,
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


@app.route("/templates", methods=["GET", "POST"])
def templates():
    with sqlite3.connect("fitness.db") as conn:
        cursor = conn.cursor()

        if request.method == "POST":
            # Create a new template
            template_name = request.form["template_name"]

            # Insert the template name
            cursor.execute("INSERT INTO templates (name) VALUES (?)", (template_name,))
            template_id = cursor.lastrowid

            # Insert exercises associated with this template
            exercises = request.form.getlist("exercise[]")
            # sets = request.form.getlist("sets[]")
            # reps = request.form.getlist("reps[]")
            # weights = request.form.getlist("weight[]")

            for exercise in exercises:
                cursor.execute("""
                    INSERT INTO template_exercises (template_id, exercise)
                    VALUES (?, ?)
                """, (template_id, exercise))

            conn.commit()
            return redirect("/templates")

        # Fetch all templates and their exercises
        cursor.execute("SELECT * FROM templates")
        templates = cursor.fetchall()

        template_data = {}
        for template in templates:
            template_id = template[0]
            cursor.execute("""
                SELECT exercise
                FROM template_exercises
                WHERE template_id = ?
            """, (template_id,))
            template_data[template_id] = cursor.fetchall()

    return render_template("templates.html", templates=templates, template_data=template_data)



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
            # Handle session creation
            date = request.form["date"]
            template_id = request.form["template_id"]

            # Insert the session
            cursor.execute("""
                INSERT INTO training_sessions (date, template_id)
                VALUES (?, ?)
            """, (date, template_id))
            session_id = cursor.lastrowid

            # Insert exercises for the session
            exercises = request.form.getlist("exercise[]")
            sets = request.form.getlist("sets[]")
            reps = request.form.getlist("reps[]")
            weights = request.form.getlist("weight[]")

            for exercise, set_count, rep_count, weight in zip(exercises, sets, reps, weights):
                cursor.execute("""
                    INSERT INTO exercises (session_id, exercise, sets, reps, weight)
                    VALUES (?, ?, ?, ?, ?)
                """, (session_id, exercise, set_count, rep_count, weight))

            conn.commit()
            return redirect("/")

        # Handle GET: Render the form with template and exercise data
        cursor.execute("SELECT id, name FROM templates")
        templates = cursor.fetchall()

        # Fetch exercises for each template
        template_exercises = {}
        for template_id, _ in templates:
            cursor.execute("""
                SELECT exercise
                FROM template_exercises
                WHERE template_id = ?
            """, (template_id,))
            template_exercises[template_id] = cursor.fetchall()

        return render_template("add.html", templates=templates, template_exercises=template_exercises)



@app.route("/get_template/<int:template_id>")
def get_template(template_id):
    with sqlite3.connect("fitness.db") as conn:
        cursor = conn.cursor()

        # Fetch template exercises
        cursor.execute("""
            SELECT exercise
            FROM template_exercises
            WHERE template_id = ?
        """, (template_id,))
        exercises = cursor.fetchall()

        # Convert to JSON-serializable format
        exercises_data = [
            {"exercise": row[0]}
            for row in exercises
        ]

    return jsonify({"exercises": exercises_data})




if __name__ == "__main__":
    init_db()
    app.run(debug=True)
