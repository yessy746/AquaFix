from flask import Flask, render_template, request, redirect
import sqlite3
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_db():
    conn = sqlite3.connect("aquafix.db")
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# DISTANCE FUNCTION
# -----------------------------
def distance(lat1, lon1, lat2, lon2):
    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# -----------------------------
# FIND NEAREST TEAM
# -----------------------------
def find_nearest_team(lat, lng):
    conn = get_db()

    teams = conn.execute(
        "SELECT * FROM teams"
    ).fetchall()

    conn.close()

    if not teams:
        return "No Team Available"

    min_dist = float("inf")
    nearest_team = "Unassigned"

    for team in teams:

        d = distance(
            lat,
            lng,
            team["lat"],
            team["lng"]
        )

        if d < min_dist:
            min_dist = d
            nearest_team = team["name"]

    return nearest_team


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------
# ABOUT PAGE
# -----------------------------
@app.route("/about")
def about():
    return render_template("about.html")


# -----------------------------
# REPORT COMPLAINT
# -----------------------------
@app.route("/report", methods=["GET", "POST"])
def report():

    if request.method == "POST":

        try:

            name = request.form["name"]
            email = request.form["email"]
            phone = request.form["phone"]
            issue = request.form["issue_type"]
            description = request.form["description"]

            lat = float(request.form.get("lat", 0))
            lng = float(request.form.get("lng", 0))

            assigned_team = find_nearest_team(lat, lng)

            conn = get_db()

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO complaints
                (
                    name,
                    email,
                    phone,
                    issue,
                    description,
                    lat,
                    lng,
                    assigned_team,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    phone,
                    issue,
                    description,
                    lat,
                    lng,
                    assigned_team,
                    "Pending"
                )
            )

            complaint_id = cursor.lastrowid

            conn.commit()
            conn.close()

            return render_template(
                "success.html",
                complaint_id=complaint_id,
                assigned_team=assigned_team
            )

        except Exception as e:
            print("ERROR:", e)
            return f"Error: {e}"

    return render_template("report.html")


# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():

    conn = get_db()

    complaints = conn.execute(
        "SELECT * FROM complaints"
    ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        complaints=complaints
    )


# -----------------------------
# ADMIN PANEL
# -----------------------------
@app.route("/admin")
def admin():

    conn = get_db()

    complaints = conn.execute(
        "SELECT * FROM complaints"
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        complaints=complaints
    )


# -----------------------------
# MAP VIEW
# -----------------------------
@app.route("/map")
def map_view():

    conn = get_db()

    rows = conn.execute(
        "SELECT * FROM complaints"
    ).fetchall()

    conn.close()

    complaints = [dict(row) for row in rows]

    return render_template(
        "map.html",
        complaints=complaints
    )


# -----------------------------
# UPDATE STATUS
# -----------------------------
@app.route("/update/<int:id>/<status>")
def update_status(id, status):

    conn = get_db()

    conn.execute(
        "UPDATE complaints SET status=? WHERE id=?",
        (status, id)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# -----------------------------
# FEEDBACK SYSTEM
# -----------------------------
@app.route("/feedback/<int:id>", methods=["GET", "POST"])
def feedback(id):

    if request.method == "POST":

        rating = request.form["rating"]
        comment = request.form["comment"]

        conn = get_db()

        conn.execute(
            """
            INSERT INTO feedback
            (
                complaint_id,
                rating,
                comment
            )
            VALUES (?, ?, ?)
            """,
            (
                id,
                rating,
                comment
            )
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template(
        "feedback.html",
        complaint_id=id
    )


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)