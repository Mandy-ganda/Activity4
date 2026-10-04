import json
import math
import os
from datetime import datetime

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from geometry import circle_area, triangle_area, triangle_area_sides
from linked_list import LinkedList

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGES_FILE = os.path.join(BASE_DIR, "messages.json")

# ---------------------------------------------------------------------------
# EDIT YOUR PERSONAL DATA HERE
# ---------------------------------------------------------------------------
PROFILE = {
    "full_name": "Mandy Nicole B. Aragoncillo",
    "nickname": "Mandy",
    "tagline": "Money is power, Toni Fowler",
    "typed": ["future engineer", "PUP BSCPE student", "pretty little baby"],
    "course": "BS Computer Engineering",
    "course_short": "BSCPE",
    "year": "2nd year",
    "school": "Polytechnic University of the Philippines",
    "bio": (
        "Hi, I'm Mandy, a Computer Engineering student at PUP with a drive to "
        "succeed and a firm believer that money is power because of Toni Fowler."
        "\n At naniniwala sa kasabihang walang masamang damo sa malinis na aso"
    ),
    "about": [
        "I'm Mandy, a student who likes asking one simple question: “How does this work?”",
        "I'm still somewhere between “I know how to do this” and “wait... why isn't this working?” — and honestly, that's where most of my learning happens.",
        "And if this portfolio is anything, I hope it's a little glimpse of who I am, what I've learned, and where I'm going next. 🌸",
    ],
    "email": "mandyaragoncillo@gmail.com",
    "phone": "09300872976",
    "location": "Malakaban, Binangonan, Rizal",
    "socials": [
        {"name": "Facebook", "url": "https://www.facebook.com/mandynicole.aragoncillo.33/"},
        {"name": "GitHub", "url": "https://github.com/"},  # TODO: add your username, e.g. https://github.com/yourname
    ],
    "education": [
        {"level": "Elementary", "place": "Malakaban, Binangonan, Rizal", "honor": "Valedictorian"},
        {"level": "Junior High School", "place": "Binangonan, Rizal", "honor": "With Honors"},
        {"level": "Senior High School", "place": "Binangonan, Rizal", "honor": "With High Honors"},
        {"level": "College", "place": "Polytechnic University of the Philippines", "honor": "BSCPE, To be announced soon..."},
    ],
    "skills": [
        {"name": "Python Programming", "level": 80},
        {"name": "HTML & CSS", "level": 60},
        {"name": "Flask", "level": 50},
        {"name": "Computer Networking", "level": 40},
        {"name": "Web Development", "level": 60},
        {"name": "Computer Hardware", "level": 90},
    ],
    "interests": ["Figuring out how things work", "Building websites", "Computer hardware", "Debugging (slowly but surely)", "Learning something new"],
    "projects": [
        {"title": "Portfolio Web App", "desc": "This personal site, built with Flask for Laboratory Exercise 4.", "url": "/"},
        {"title": "Uppercase Converter", "desc": "Turn any text into UPPERCASE letters instantly.", "url": "/programs"},
        {"title": "Area Calculator", "desc": "Circle and triangle areas with a live shape preview.", "url": "/programs"},
        {"title": "Linked List Visualizer", "desc": "A singly linked list you can add to, search, and reverse.", "url": "/linked-list"},
    ],
}


@app.context_processor
def inject_globals():
    photo = os.path.join(BASE_DIR, "static", "img", "mandy.jpg")
    return {"p": PROFILE, "has_photo": os.path.exists(photo), "year": datetime.now().year}


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/programs")
def programs():
    return render_template("programs.html")


@app.route("/linked-list")
def linked_list_page():
    return render_template("linkedlist.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not (name and email and message):
            flash("Please fill in your name, email, and message.", "error")
        else:
            try:
                with open(MESSAGES_FILE, encoding="utf-8") as f:
                    saved = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                saved = []
            saved.append({"name": name, "email": email, "message": message,
                          "sent": datetime.now().isoformat(timespec="seconds")})
            with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
                json.dump(saved, f, indent=2)
            flash(f"Thanks, {name}! Your message was saved.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html")


# ---------------------------------------------------------------------------
# Area API
# ---------------------------------------------------------------------------
def _num(data, key):
    try:
        value = float(data.get(key))
    except (TypeError, ValueError):
        raise ValueError(f"Enter a number for {key}.")
    if not math.isfinite(value):
        raise ValueError(f"Enter a valid number for {key}.")
    return value


@app.post("/api/uppercase")
def api_uppercase():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if not isinstance(text, str):
        return jsonify(ok=False, error="Text must be a string."), 400
    if len(text) > 5000:
        return jsonify(ok=False, error="Keep the text under 5,000 characters."), 400
    return jsonify(ok=True, result=text.upper(), length=len(text))


@app.post("/api/area/circle")
def api_circle():
    data = request.get_json(silent=True) or {}
    try:
        r = _num(data, "radius")
        return jsonify(ok=True, area=circle_area(r),
                       steps=f"A = π × r² = π × {r:g}²")
    except ValueError as e:
        return jsonify(ok=False, error=str(e)), 400


@app.post("/api/area/triangle")
def api_triangle():
    data = request.get_json(silent=True) or {}
    try:
        if data.get("mode") == "sides":
            a, b, c = _num(data, "a"), _num(data, "b"), _num(data, "c")
            s = (a + b + c) / 2
            return jsonify(ok=True, area=triangle_area_sides(a, b, c),
                           steps=f"Heron: s = {s:g}, A = √(s(s−a)(s−b)(s−c))")
        b, h = _num(data, "base"), _num(data, "height")
        return jsonify(ok=True, area=triangle_area(b, h),
                       steps=f"A = ½ × b × h = ½ × {b:g} × {h:g}")
    except ValueError as e:
        return jsonify(ok=False, error=str(e)), 400


# ---------------------------------------------------------------------------
# Linked list API
# ---------------------------------------------------------------------------
LL = LinkedList()
for _v in ("Mandy", "PUP", "BSCPE"):
    LL.append(_v)


def _state(message, highlight=None, ok=True, status=200):
    return jsonify(ok=ok, message=message, nodes=LL.to_list(),
                   size=len(LL), highlight=highlight), status


def _value(data):
    v = str(data.get("value", "")).strip()
    if not v:
        raise ValueError("Type a value first.")
    if len(v) > 20:
        raise ValueError("Keep values to 20 characters or fewer.")
    return v


def _index(data):
    try:
        return int(data.get("index"))
    except (TypeError, ValueError):
        raise ValueError("Enter a whole number for the index.")


@app.get("/api/list")
def ll_get():
    return _state("Here is your list.")


@app.post("/api/list/<action>")
def ll_action(action):
    data = request.get_json(silent=True) or {}
    try:
        if action == "append":
            v = _value(data)
            return _state(f'Added "{v}" to the end.', LL.append(v))
        if action == "prepend":
            v = _value(data)
            return _state(f'Added "{v}" to the start.', LL.prepend(v))
        if action == "insert":
            v, i = _value(data), _index(data)
            return _state(f'Inserted "{v}" at index {i}.', LL.insert(i, v))
        if action == "remove":
            v = _value(data)
            i = LL.remove(v)
            return _state(f'Removed "{v}" (was at index {i}).')
        if action == "remove_at":
            i = _index(data)
            v = LL.remove_at(i)
            return _state(f'Removed "{v}" from index {i}.')
        if action == "search":
            v = _value(data)
            i = LL.find(v)
            if i == -1:
                return _state(f'"{v}" is not in the list.', ok=False, status=404)
            return _state(f'Found "{v}" at index {i}.', i)
        if action == "reverse":
            LL.reverse()
            return _state("List reversed.")
        if action == "clear":
            LL.clear()
            return _state("List cleared. Add a value to start again.")
    except (ValueError, IndexError) as e:
        return _state(str(e), ok=False, status=400)
    return _state("Unknown action.", ok=False, status=404)


if __name__ == "__main__":
    app.run(debug=True)
