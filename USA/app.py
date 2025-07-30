from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)
app.config['DATABASE'] = 'college.db' # Define the database file name

# --- Database Setup ---

def get_db():
    """Establishes a connection to the database."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE']
            # Remove this line: detect_types=sqlite3.PARSE_DATES
        )
        g.db.row_factory = sqlite3.Row # Allows accessing columns by name
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database schema."""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                college_id TEXT UNIQUE NOT NULL,
                id_card_number TEXT UNIQUE NOT NULL,
                stream TEXT NOT NULL,
                mobile_number TEXT NOT NULL,
                parents_mobile_number TEXT NOT NULL
            )
        ''')
        db.commit()
        print("Database initialized successfully.") # For debugging

# Call init_db once when the application starts
with app.app_context():
    init_db()

# --- Routes ---
@app.route('/')
def index():
    """Displays the student input form and the list of registered students."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students ORDER BY name")
    students = cursor.fetchall()
    return render_template('index.html', students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    """Handles the submission of the student registration form."""
    if request.method == 'POST':
        name = request.form['name'].strip()
        college_id = request.form['college_id'].strip()
        id_card_number = request.form['id_card_number'].strip()
        stream = request.form['stream'].strip()
        mobile_number = request.form['mobile_number'].strip()
        parents_mobile_number = request.form['parents_mobile_number'].strip()

        # Basic validation
        if not all([name, college_id, id_card_number, stream, mobile_number, parents_mobile_number]):
            # You could add a flash message here for better user feedback
            return "Error: All fields are required!", 400

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('''
                INSERT INTO students (name, college_id, id_card_number, stream, mobile_number, parents_mobile_number)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, college_id, id_card_number, stream, mobile_number, parents_mobile_number))
            db.commit()
            print(f"Student {name} added successfully.") # For debugging
        except sqlite3.IntegrityError as e:
            # Handle unique constraint violations (e.g., college_id or id_card_number already exists)
            print(f"Database error: {e}")
            return f"Error: A student with that College ID or ID Card Number already exists. ({e})", 409
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return f"An unexpected error occurred: {e}", 500

        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) # debug=True allows auto-reloading and better error messages