import json
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "colleges_jk.json")

def load_colleges():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_colleges(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route("/colleges")
def colleges_list():
    q = request.args.get("q", "").strip().lower()
    district = request.args.get("district", "")
    sports = request.args.get("sports", "")  # "yes" or "no" or ""
    colleges = load_colleges()

    # filtering
    if q:
        colleges = [c for c in colleges if q in c["name"].lower() or q in c.get("district","").lower() or q in " ".join(c.get("courses",[])).lower()]
    if district:
        colleges = [c for c in colleges if c.get("district","").lower() == district.lower()]
    if sports == "yes":
        colleges = [c for c in colleges if c.get("sports_quota")]
    if sports == "no":
        colleges = [c for c in colleges if not c.get("sports_quota")]

    # simple sort by name
    colleges.sort(key=lambda x: x["name"])
    # pagination (simple)
    page = int(request.args.get("page", 1))
    per_page = 20
    total = len(colleges)
    start = (page-1)*per_page
    end = start + per_page
    page_items = colleges[start:end]

    return render_template("colleges_list.html", colleges=page_items, page=page, total=total, per_page=per_page)

@app.route("/college/<college_id>")
def college_detail(college_id):
    colleges = load_colleges()
    college = next((c for c in colleges if c["id"] == college_id), None)
    if not college:
        flash("College not found", "danger")
        return redirect(url_for("colleges_list"))
    return render_template("college_detail.html", college=college)

# Simple admin endpoint to upload/replace JSON (for local use only; secure in production)
@app.route("/admin/upload_colleges", methods=["GET", "POST"])
def admin_upload_colleges():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            flash("No file uploaded", "danger")
            return redirect(url_for("admin_upload_colleges"))
        try:
            data = json.load(file)
            save_colleges(data)
            flash("College data updated", "success")
        except Exception as e:
            flash(f"Failed to parse JSON: {e}", "danger")
    return render_template("admin_upload.html")
