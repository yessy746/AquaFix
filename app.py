from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "aquafix.db"


def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        issue_type TEXT NOT NULL,
        description TEXT NOT NULL,
        location TEXT NOT NULL,
        assigned_team TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def assign_team(location):
    teams = [
        "North Water Maintenance Team",
        "South Water Maintenance Team",
        "East Water Maintenance Team",
        "West Water Maintenance Team"
    ]

    return teams[hash(location) % len(teams)]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/report", methods=["GET", "POST"])
def report():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        issue_type = request.form["issue_type"]
        description = request.form["description"]
        location = request.form["location"]

        assigned_team = assign_team(location)

        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO complaints
        (
            name,
            email,
            phone,
            issue_type,
            description,
            location,
            assigned_team,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            email,
            phone,
            issue_type,
            description,
            location,
            assigned_team,
            "Pending",
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

        complaint_id = cur.lastrowid

        conn.commit()
        conn.close()

        return render_template(
            "success.html",
            complaint_id=complaint_id,
            assigned_team=assigned_team
        )

    return render_template("report.html")


@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM complaints
    ORDER BY id DESC
    """)

    complaints = cur.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        complaints=complaints
    )


@app.route("/admin")
def admin():

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM complaints
    ORDER BY id DESC
    """)

    complaints = cur.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        complaints=complaints
    )


@app.route("/update/<int:id>/<status>")
def update_status(id, status):

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute(
        "UPDATE complaints SET status=? WHERE id=?",
        (status, id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)