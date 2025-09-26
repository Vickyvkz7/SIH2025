import os
import json
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, jsonify
)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime
import openai

# ---------- Load environment ----------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# ---------- Flask setup ----------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "supersecretkey")  # change in production

# ---------- File upload config ----------
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- Dummy user storage (in-memory) ----------
users = {
    "student@example.com": {
        "email": "student@example.com",
        "password": "12345",
        "name": "Student User",
        "qualification": "12th",
        "school_background": "Science Stream",
        "marks": "85%",
        "subjects": "Maths, Physics, Computer Science",
        "interests": "AI, Web Development, Data Science",
        "skills": "Python, HTML, CSS",
        "career_goal": "Software Engineer",
        "college": "Government College of Engineering",
        "joined": "2025",
        "guidelines": "Focus on AI & Data Science for future scope.",
        "profile_pic": None,
        "recommended_field": None,
        "chat_history": [
            {"role": "assistant", "content": "👋 Hello! I’m your AI career counselor. How can I help today?"}
        ],
        "applied_colleges": [],
    }
}

# ---------- Load colleges (persisted file) ----------
colleges_file = "colleges.json"
if os.path.exists(colleges_file):
    with open(colleges_file, "r", encoding="utf-8") as f:
        colleges_data = json.load(f)
else:
    colleges_data = [
        {
            "id": 1,
            "name": "Government College of Engineering",
            "district": "Srinagar",
            "type": "Engineering",
            "fields": "Engineering/Tech",
        },
        {
            "id": 2,
            "name": "Government Medical College Srinagar",
            "district": "Srinagar",
            "type": "Medical",
            "fields": "Medicine/Biology",
        },
        {
            "id": 3,
            "name": "Arts & Humanities College Jammu",
            "district": "Jammu",
            "type": "Arts",
            "fields": "Arts/Design",
        },
    ]
    with open(colleges_file, "w", encoding="utf-8") as f:
        json.dump(colleges_data, f, indent=4, ensure_ascii=False)

# ---------- Load timeline ----------
timeline_file = "timeline.json"
if os.path.exists(timeline_file):
    with open(timeline_file, "r", encoding="utf-8") as f:
        timeline_data = json.load(f)
else:
    timeline_data = [
        {"year": "2025", "event": "Take Career Quiz & Identify Field"},
        {"year": "2026", "event": "Prepare for Entrance Exams"},
        {"year": "2027", "event": "Apply to Top Colleges"},
        {"year": "2028", "event": "Start Undergraduate Program"},
    ]
    with open(timeline_file, "w", encoding="utf-8") as f:
        json.dump(timeline_data, f, indent=4, ensure_ascii=False)


# ---------- Routes ----------

@app.route("/")
def index():
    return redirect(url_for("dashboard") if "user" in session else url_for("login"))


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = users.get(email)
        if user and user.get("password") == password:
            session["user"] = email
            flash("Login successful! 🎉", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid email or password ❌", "danger")
    return render_template("login.html")


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # user fields
        name = request.form.get("name", "")
        qualification = request.form.get("qualification", "")
        school_background = request.form.get("school_background", "")
        marks = request.form.get("marks", "")
        subjects = request.form.get("subjects", "")
        interests = request.form.get("interests", "")
        skills = request.form.get("skills", "")
        career_goal = request.form.get("career_goal", "")

        # profile pic
        profile_pic = None
        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                profile_pic = f"uploads/{filename}"

        if not email or not password:
            flash("Please provide email and password", "warning")
            return render_template("register.html")

        if email in users:
            flash("Email already registered ⚠️", "warning")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match ❌", "danger")
            return render_template("register.html")

        users[email] = {
            "email": email,
            "password": password,
            "name": name or email.split("@")[0].title(),
            "qualification": qualification,
            "school_background": school_background,
            "marks": marks,
            "subjects": subjects,
            "interests": interests,
            "skills": skills,
            "career_goal": career_goal,
            "college": "",
            "joined": "",
            "guidelines": "",
            "profile_pic": profile_pic,
            "recommended_field": None,
            "chat_history": [
                {"role": "assistant", "content": "👋 Hello! I’m your AI career counselor. How can I help today?"}
            ],
            "applied_colleges": [],
        }
        session["user"] = email
        flash("Registration successful ✅ Welcome!", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


# Dashboard
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Please log in first ⚠️", "warning")
        return redirect(url_for("login"))

    user_email = session["user"]
    user_data = users.get(user_email)
    if not user_data:
        session.pop("user", None)
        flash("User not found. Please register or log in again.", "danger")
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=user_data)


# Profile view
@app.route("/profile")
def profile():
    if "user" not in session:
        flash("Please log in to view your profile ⚠️", "warning")
        return redirect(url_for("login"))
    return render_template("profile.html", user=users[session["user"]])


# Edit profile
@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    if "user" not in session:
        flash("Please log in first ⚠️", "warning")
        return redirect(url_for("login"))

    user_data = users[session["user"]]
    if request.method == "POST":
        for field in [
            "name",
            "qualification",
            "school_background",
            "marks",
            "subjects",
            "college",
            "joined",
            "interests",
            "skills",
            "career_goal",
            "guidelines",
        ]:
            user_data[field] = request.form.get(field, user_data.get(field, ""))
        # profile picture
        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                user_data["profile_pic"] = f"uploads/{filename}"

        flash("Profile updated successfully ✅", "success")
        return redirect(url_for("profile"))

    return render_template("edit_profile.html", user=user_data)


# Chat page (shows history)
@app.route("/chat")
def chat():
    if "user" not in session:
        flash("Please log in first ⚠️", "warning")
        return redirect(url_for("login"))
    user_data = users[session["user"]]
    # Ensure chat_history exists
    if "chat_history" not in user_data:
        user_data["chat_history"] = [
            {"role": "assistant", "content": "👋 Hello! I’m your AI career counselor. How can I help today?"}
        ]
    return render_template("chat.html", chat_history=user_data["chat_history"])


# Reset chat
@app.route("/chat/reset")
def chat_reset():
    if "user" not in session:
        return redirect(url_for("login"))
    user_data = users[session["user"]]
    user_data["chat_history"] = [
        {"role": "assistant", "content": "🔄 Chat reset. 👋 How can I help with your career journey now?"}
    ]
    return redirect(url_for("chat"))


# Chat API with live AI + domain-specific fallback
@app.route("/chat/api", methods=["POST"])
def chat_api():
    if "user" not in session:
        return jsonify({"reply": "⚠️ Please log in first."})

    user_data = users[session["user"]]
    data = request.get_json() or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"reply": "⚠️ Please type a message."})

    # Save user message
    user_data.setdefault("chat_history", []).append({"role": "user", "content": user_message})

    bot_reply = None

    # Try real OpenAI if API key present
    if OPENAI_API_KEY:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a helpful AI career counselor for students in Jammu & Kashmir."}]
                         + user_data["chat_history"],
                max_tokens=600,
                temperature=0.7,
            )
            bot_reply = response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            # we will fall back to domain messages below, but keep a short reason for debugging (not shown to user)
            error_text = str(e)
            # choose friendly message later
            bot_reply = None
    # If bot_reply still None, use fallback messages (domain-specific)
    if not bot_reply:
        fallback_replies = [
            "🎓 NEET / Medical: Focus on NCERT Biology & Chemistry. Practice previous years' papers and timed mocks.",
            "📐 JEE / Engineering: Strengthen Physics fundamentals, practice problem solving and take regular mock tests.",
            "📚 UPSC / Civil Services: Start early with NCERTs, read daily editorials, and practice answer-writing.",
            "⚖️ Law (CLAT): Work on legal reasoning, logical ability, and comprehension. Take mock tests and read case summaries.",
            "💼 Commerce / CA / CS: Build basics in Accountancy, Business Studies and practice numerical problems.",
            "🎨 Arts / Design: Build a strong portfolio, practice creative projects, and consider design entrance prep.",
            "💻 IT / CS: Start learning Python, data structures, and small projects (web apps, scripts) to build a portfolio.",
            "🏛️ Government exams (JKPSC etc.): Track official notifications, focus on basics and current affairs, and practice mock papers.",
            "💡 Career tip: Improve soft skills (communication, teamwork) — employers value these highly.",
            "🎯 Scholarships: Look for schemes like PMSSS (for J&K students) and state scholarships; they can reduce costs significantly."
        ]
        # Pick reply based on keywords in user_message for slightly smarter fallback
        user_low = user_message.lower()
        selected = None
        keyword_map = {
            ("neet", "medical", "biology", "mbbs"): 0,
            ("jee", "engineering", "physics", "math"): 1,
            ("upsc", "civil services", "ias", "ias/ips"): 2,
            ("clat", "law", "llb"): 3,
            ("ca", "commerce", "cs", "account"): 4,
            ("arts", "design", "painting", "fine"): 5,
            ("python", "coding", "data science", "machine", "ai", "web"): 6,
            ("jkpsc", "state", "psc", "government exam"): 7,
            ("scholarship", "pmsss", "financial", "grant"): 9,
        }
        for keys, idx in keyword_map.items():
            for k in keys:
                if k in user_low:
                    selected = fallback_replies[idx]
                    break
            if selected:
                break

        if not selected:
            # rotate through general helpful lines so it's not repetitive
            selected = fallback_replies[len(user_data["chat_history"]) % len(fallback_replies)]

        bot_reply = f"{selected}\n\n⚠️ (AI currently unavailable for live replies.)"

    # Save assistant reply into history
    user_data.setdefault("chat_history", []).append({"role": "assistant", "content": bot_reply})

    return jsonify({"reply": bot_reply})


# Quiz
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "user" not in session:
        flash("Please log in first ⚠️", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        answers = [request.form.get(f"q{i}", "") for i in range(1, 11)]

        scores = {
            "Engineering/Tech": 0,
            "Medicine/Biology": 0,
            "Arts/Design": 0,
            "Business/Management": 0,
            "Education/Research": 0,
        }

        for ans in answers:
            a = (ans or "").lower()
            if any(x in a for x in ["math", "coding", "problem"]):
                scores["Engineering/Tech"] += 2
            if any(x in a for x in ["biology", "helping", "health"]):
                scores["Medicine/Biology"] += 2
            if any(x in a for x in ["drawing", "creative", "design"]):
                scores["Arts/Design"] += 2
            if any(x in a for x in ["leadership", "business", "money"]):
                scores["Business/Management"] += 2
            if any(x in a for x in ["reading", "teaching", "research"]):
                scores["Education/Research"] += 2

        best_field = max(scores, key=scores.get)
        users[session["user"]]["recommended_field"] = best_field

        return render_template("quiz_result.html", field=best_field, scores=scores)

    return render_template("quiz.html")

# Colleges listing (filter + pagination)
@app.route("/colleges")
def colleges():
    search = request.args.get("search", "").lower()
    district = request.args.get("district", "").lower()
    ctype = request.args.get("type", "").lower()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 6))

    filtered = []
    for c in colleges_data:
        if search and search not in c["name"].lower():
            continue
        if district and c["district"].lower() != district:
            continue
        if ctype and c["type"].lower() != ctype:
            continue
        filtered.append(c)

    total = len(filtered)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered[start:end]

    total_pages = (total // per_page + (1 if total % per_page else 0))

    # ✅ Unique districts for dropdown
    all_districts = sorted({c["district"] for c in colleges_data})

    return render_template(
        "colleges.html",
        colleges=paginated,
        page=page,
        total_pages=total_pages,
        search=search,
        district=district,
        ctype=ctype,
        all_districts=all_districts  # 👈 important fix
    )


# College detail + Nearby Colleges + Map
@app.route("/college/<int:college_id>")
def college_detail(college_id):
    college = next((c for c in colleges_data if c.get("id") == college_id), None)
    if not college:
        flash("College not found ⚠️", "danger")
        return redirect(url_for("colleges"))

    # Nearby colleges = same district, excluding itself
    nearby = [
        c for c in colleges_data
        if c.get("district") == college.get("district") and c.get("id") != college_id
    ][:3]  # limit to 3 nearby colleges

    # Google Maps embed
    maps_url = f"https://www.google.com/maps?q={college['name']} {college['district']}&output=embed"

    user = users.get(session.get("user")) if "user" in session else None
    return render_template(
        "college_detail.html",
        college=college,
        user=user,
        maps_url=maps_url,
        nearby=nearby
    )


@app.route("/college/<int:college_id>/apply")
def apply_college(college_id):
    if "user" not in session:
        flash("Please log in to apply ⚠️", "warning")
        return redirect(url_for("login"))

    email = session["user"]
    user_data = users[email]
    user_data.setdefault("applied_colleges", [])

    if college_id in user_data["applied_colleges"]:
        flash("✅ You have already applied to this college.", "info")
        return redirect(url_for("college_detail", college_id=college_id))

    user_data["applied_colleges"].append(college_id)
    flash("🎉 Application submitted successfully!", "success")
    return redirect(url_for("college_detail", college_id=college_id))


# Recommended colleges based on quiz
@app.route("/recommended_colleges")
def recommended_colleges():
    if "user" not in session:
        flash("Please log in first ⚠️", "warning")
        return redirect(url_for("login"))

    user = users[session["user"]]
    field = user.get("recommended_field")
    if not field:
        flash("Please take the quiz first to get recommendations 🎯", "info")
        return redirect(url_for("quiz"))

    filtered = [
        c for c in colleges_data if field.lower() in c.get("fields", "").lower()
    ]
    return render_template("recommended_colleges.html", colleges=filtered, field=field)

# Timeline
@app.route("/timeline")
def timeline():
    if "user" not in session:
        flash("Please log in first ⚠️", "warning")
        return redirect(url_for("login"))
    steps = [
        {"name": "Career Quiz", "description": "Discover your strengths and suggested fields of study.", "link": url_for("quiz")},
        {"name": "Entrance Exam Preparation", "description": "Start preparing for entrance exams with focus.", "link": url_for("exam_prep")},
        {"name": "College Applications", "description": "Apply to recommended colleges matching your interests.", "link": url_for("colleges")},
        {"name": "Profile & Interests", "description": "Update your profile with interests, skills and goals.", "link": url_for("profile")},
        {"name": "Start College 🎓", "description": "Kickstart your academic journey in your chosen field.", "link": url_for("dashboard")},
    ]
    current_step = 2
    return render_template("timeline.html", steps=steps, current_step=current_step)


# ===== Entrance Exam Preparation =====
@app.route("/exam_prep")
def exam_prep():
    if "user" not in session:
        flash("Please log in first ⚠️", "warning")
        return redirect(url_for("login"))

    user = users[session["user"]]
    field = user.get("recommended_field", "General")

    # Exam data with date
    exams = {
        "Engineering/Tech": [
            {"name": "JEE Main", "description": "National level exam for engineering colleges like NITs, IIITs.",
             "plan": "Focus on NCERT + Previous Year Papers. Daily 6 hrs of study with mock tests.",
             "date": "2025-04-06",
             "resources": [
                 {"title": "NTA JEE Official", "link": "https://jeemain.nta.nic.in/"},
                 {"title": "Physics Wallah JEE", "link": "https://www.pw.live/"},
                 {"title": "JEE Mains PYQs", "link": "https://jeemains.in/pyqs"}
             ],
             "progress": 20},
            {"name": "JKCET", "description": "State-level entrance exam in Jammu & Kashmir.",
             "plan": "Revise NCERT of PCM thoroughly. Solve past 5-year JKCET papers.",
             "date": "2025-05-15",
             "resources": [
                 {"title": "JKBOPEE Official", "link": "https://jkbopee.gov.in/"},
                 {"title": "JKCET Study Guide", "link": "https://www.examguide.com/jkcet"}
             ],
             "progress": 10}
        ],
        "Medicine/Biology": [
            {"name": "NEET UG", "description": "National exam for MBBS/BDS admissions.",
             "plan": "Daily 8 hrs study. Strong NCERT focus. Practice diagrams & mock tests.",
             "date": "2025-05-05",
             "resources": [
                 {"title": "NEET Official", "link": "https://neet.nta.nic.in/"},
                 {"title": "Allen NEET Prep", "link": "https://www.allen.ac.in/"},
                 {"title": "Biology Notes", "link": "https://www.neetprep.com/"}
             ],
             "progress": 15}
        ],
        "Arts/Design": [
            {"name": "NIFT Entrance", "description": "Fashion & Design admission test.",
             "plan": "Practice sketching daily. Focus on creativity & design aptitude.",
             "date": "2025-02-21",
             "resources": [
                 {"title": "NIFT Official", "link": "https://nift.ac.in/"},
                 {"title": "Design Entrance Prep", "link": "https://www.dsource.in/"}
             ],
             "progress": 5}
        ],
        "General": [
            {"name": "CUET", "description": "Common University Entrance Test for multiple fields.",
             "plan": "Focus on NCERT + GK. Daily 3 hrs practice on aptitude and reasoning.",
             "date": "2025-06-15",
             "resources": [
                 {"title": "CUET Official", "link": "https://cuet.samarth.ac.in/"},
                 {"title": "CUET Guide", "link": "https://cuetguide.com/"}
             ],
             "progress": 0}
        ]
    }

    exam_list = exams.get(field, exams["General"])

    # Add countdown for each exam
    today = datetime.today()
    for exam in exam_list:
        exam_date = datetime.strptime(exam["date"], "%Y-%m-%d")
        days_left = (exam_date - today).days
        exam["days_left"] = days_left if days_left >= 0 else 0

    return render_template("exam_prep.html", exams=exam_list, field=field)

# ===== Parents Dashboard =====
@app.route("/parents_dashboard")
def parents_dashboard():
    # Dummy data for now, later can connect to DB or JSON
    courses_10_12 = [
        {"stream": "Science", "subjects": "Physics, Chemistry, Math/Biology, English"},
        {"stream": "Commerce", "subjects": "Accountancy, Business Studies, Economics, Math/CS"},
        {"stream": "Arts", "subjects": "History, Political Science, Sociology, Literature"},
    ]

    scholarships = [
        {"name": "National Scholarship", "eligibility": "Above 80% in 12th", "amount": "₹50,000/year"},
        {"name": "State Merit Scholarship", "eligibility": "J&K Domicile + Above 75%", "amount": "₹25,000/year"},
    ]

    quotas = [
        "SC/ST Reservation",
        "OBC Reservation",
        "EWS (Economically Weaker Section)",
        "Defence Personnel Quota",
        "PWD Quota"
    ]

    occupations = [
        "Engineering & Technology",
        "Medical & Healthcare",
        "Civil Services",
        "Law",
        "Teaching & Research",
        "Entrepreneurship"
    ]

    gov_exams = [
        {"exam": "NEET", "qualification": "12th Science with PCB"},
        {"exam": "JEE", "qualification": "12th Science with PCM"},
        {"exam": "UPSC CSE", "qualification": "Graduate"},
        {"exam": "SSC CGL", "qualification": "Graduate"},
        {"exam": "Bank PO", "qualification": "Graduate"},
    ]

    admission_alerts = [
        {"college": "NIT Srinagar", "last_date": "30 June 2025"},
        {"college": "AIIMS Jammu", "last_date": "15 July 2025"},
        {"college": "University of Jammu", "last_date": "10 August 2025"},
    ]

    financial_planning = [
        "Start SIP/FD for child’s higher education",
        "Look for education loans with low interest rates",
        "Apply for multiple scholarships",
        "Balance between private & government colleges"
    ]

    course_mapping = [
        {"course": "B.Tech (CSE)", "outcome": "Software Engineer, Data Scientist, AI Specialist"},
        {"course": "MBBS", "outcome": "Doctor, Surgeon, Specialist"},
        {"course": "B.Com", "outcome": "CA, Accountant, Banking Professional"},
        {"course": "BA", "outcome": "Civil Services, Journalism, Teaching"},
    ]

    return render_template(
        "parents_dashboard.html",
        courses=courses_10_12,
        scholarships=scholarships,
        quotas=quotas,
        occupations=occupations,
        gov_exams=gov_exams,
        admission_alerts=admission_alerts,
        financial_planning=financial_planning,
        course_mapping=course_mapping
    )

@app.route("/parents/courses")
def parents_courses():
    courses_after_10th = [
        {
            "stream": "Science",
            "subjects": "Physics, Chemistry, Math/Biology, English",
            "opportunities": "Engineering, Medicine, Research, IT, Pure Sciences"
        },
        {
            "stream": "Commerce",
            "subjects": "Accountancy, Business Studies, Economics, Math/CS",
            "opportunities": "CA, CS, CMA, Banking, Management, Finance"
        },
        {
            "stream": "Arts/Humanities",
            "subjects": "History, Political Science, Sociology, Literature, Psychology",
            "opportunities": "Civil Services, Law, Journalism, Design, Teaching"
        },
        {
            "stream": "Diploma/Polytechnic",
            "subjects": "Applied Science & Technical Subjects",
            "opportunities": "Direct entry into engineering fields, technician jobs"
        },
        {
            "stream": "Vocational Courses",
            "subjects": "Tailoring, Photography, Computer Basics, Tourism, Agriculture",
            "opportunities": "Skilled jobs, entrepreneurship, early employment"
        },
        {
            "stream": "ITI (Industrial Training)",
            "subjects": "Electrician, Fitter, Mechanic, Welder, Computer Operator",
            "opportunities": "Skilled industry jobs, government technical posts"
        },
    ]

    courses_after_12th = [
        {"stream": "Engineering/Technology", "subjects": "PCM", "opportunities": "B.Tech, B.E, AI, Robotics"},
        {"stream": "Medical", "subjects": "PCB", "opportunities": "MBBS, BDS, BAMS, Nursing, Pharmacy"},
        {"stream": "Commerce & Management", "subjects": "Accountancy, Business Studies", "opportunities": "B.Com, BBA, MBA"},
        {"stream": "Arts & Humanities", "subjects": "Humanities", "opportunities": "BA, Law, Journalism, Civil Services"},
        {"stream": "Law", "subjects": "Any stream", "opportunities": "BA LLB, BBA LLB"},
        {"stream": "Design & Creative", "subjects": "Any stream", "opportunities": "Fashion, Animation, Fine Arts"},
        {"stream": "Defense & Civil Services", "subjects": "Any stream", "opportunities": "NDA, UPSC (later)"},
        {"stream": "Hotel Management & Tourism", "subjects": "Any stream", "opportunities": "BHM, Tourism Industry"},
        {"stream": "Education & Research", "subjects": "Any stream", "opportunities": "B.Ed, Teaching, Research"},
    ]

    course_outcomes = [
        {"course": "B.Tech (CSE)", "outcomes": "Software Engineer, Data Scientist, AI Specialist"},
        {"course": "MBBS", "outcomes": "Doctor, Surgeon, Specialist"},
        {"course": "B.Com", "outcomes": "CA, Accountant, Finance Professional"},
        {"course": "BA (Humanities)", "outcomes": "Civil Services, Journalism, Teaching"},
        {"course": "LLB", "outcomes": "Lawyer, Judge, Legal Advisor"},
        {"course": "B.Des", "outcomes": "Fashion Designer, Animator, UI/UX Designer"},
        {"course": "BHM", "outcomes": "Hotel Manager, Travel Consultant"},
        {"course": "B.Ed", "outcomes": "Teacher, Lecturer, Researcher"},
    ]

    return render_template(
        "parents_courses.html",
        courses_after_10th=courses_after_10th,
        courses_after_12th=courses_after_12th,
        course_outcomes=course_outcomes
    )
# parents scholorships

@app.route("/parents/scholarships")
def parents_scholarships():
    scholarships = [
        {
            "name": "National Merit Scholarship",
            "eligibility": "Class 10/12 toppers, merit-based",
            "benefits": "₹10,000 per annum for 2 years",
            "apply_link": "https://scholarships.gov.in/",
            "category": "Merit-based Central"
        },
        {
            "name": "Post-Matric Scholarship (SC/ST/OBC)",
            "eligibility": "Students from reserved categories studying post-matric courses",
            "benefits": "Tuition fee waiver, hostel allowance, monthly stipend",
            "apply_link": "https://scholarships.gov.in/",
            "category": "Need-based Central"
        },
        {
            "name": "AICTE Pragati Scholarship (Girls)",
            "eligibility": "Girl students in technical/engineering colleges",
            "benefits": "₹50,000 annually + tuition reimbursement",
            "apply_link": "https://aicte-pragati-saksham.gov.in/",
            "category": "Girls Central"
        },
        {
            "name": "INSPIRE Scholarship (Science Stream)",
            "eligibility": "Top 1% in Class 12, pursuing BSc/Integrated MSc",
            "benefits": "₹80,000 per year",
            "apply_link": "https://online-inspire.gov.in/",
            "category": "Merit-based Central"
        },
        {
            "name": "State Government Scholarships",
            "eligibility": "Varies by state (check local portal)",
            "benefits": "Fee reimbursement, stipend, book grants",
            "apply_link": "https://scholarships.gov.in/",
            "category": "Need-based State"
        }
    ]
    return render_template("parents_scholarships.html", scholarships=scholarships)

# ------------------------------
# Quota / Reservation Data
# ------------------------------
quotas = [
    {"name": "Scheduled Caste (SC)", "category": "SC", "reservation": "15%",
     "eligibility": "Students with valid SC certificate",
     "notes": "Applicable in Central & State institutions"},

    {"name": "Scheduled Tribe (ST)", "category": "ST", "reservation": "7.5%",
     "eligibility": "Students with valid ST certificate",
     "notes": "Relaxation in cut-offs and fees"},

    {"name": "Other Backward Classes (OBC – Non Creamy Layer)", "category": "OBC", "reservation": "27%",
     "eligibility": "OBC students (Non-Creamy Layer, income < ₹8 lakh)",
     "notes": "Requires central OBC certificate"},

    {"name": "Economically Weaker Section (EWS)", "category": "EWS", "reservation": "10%",
     "eligibility": "General category, income < ₹8 lakh",
     "notes": "Requires valid EWS certificate"},

    {"name": "Persons with Disability (PwD)", "category": "PwD", "reservation": "5%",
     "eligibility": "Minimum 40% disability with certificate",
     "notes": "Reservation across all categories"},

    {"name": "Minority Communities", "category": "Minority", "reservation": "Varies",
     "eligibility": "Muslim, Christian, Sikh, Buddhist, Jain, Parsi",
     "notes": "Special scholarships and state quotas available"},

    {"name": "State Quotas", "category": "State", "reservation": "Varies by state",
     "eligibility": "Domicile students",
     "notes": "Each state has unique reservation policies"},
]

# ------------------------------
# Route for Quotas / Reservation
# ------------------------------
@app.route("/parents/quotas")
def parents_quotas():
    return render_template("parents_quota.html", quotas=quotas)


# ===== Occupation Guidance =====
@app.route("/parents/occupation")
def parents_occupation():
    occupations = [
        {
            "name": "Engineering & Technology",
            "description": "Focuses on innovation, design, and solving technical problems.",
            "paths": ["B.Tech", "Diploma", "Polytechnic"],
            "careers": ["Software Engineer", "Mechanical Engineer", "AI Specialist"],
            "salary": "₹4–12 LPA",
            "future": "High demand in IT, AI, Robotics, and Renewable Energy",
            "colleges": ["IITs", "NITs", "IIITs", "Top State Universities"],
            "tips": "Encourage logical thinking and problem-solving practice."
        },
        {
            "name": "Medical & Healthcare",
            "description": "Career in medicine, surgery, and allied healthcare services.",
            "paths": ["MBBS", "BDS", "Nursing", "Pharmacy"],
            "careers": ["Doctor", "Surgeon", "Dentist", "Pharmacist"],
            "salary": "₹5–20 LPA",
            "future": "Evergreen demand in healthcare worldwide",
            "colleges": ["AIIMS", "JIPMER", "State Medical Colleges"],
            "tips": "Strong biology background and compassion are key."
        },
        {
            "name": "Civil Services",
            "description": "Prestigious government jobs via UPSC/State PSC exams.",
            "paths": ["Any Graduate Degree"],
            "careers": ["IAS", "IPS", "IFS", "IRS"],
            "salary": "₹7–18 LPA + perks",
            "future": "Stable and influential career",
            "colleges": ["Delhi University", "JNU", "State Universities"],
            "tips": "Focus on current affairs and communication skills."
        }
    ]
    return render_template("occupation_guidance.html", occupations=occupations)
# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully 👋", "info")
    return redirect(url_for("login"))


# Run server
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=int(os.getenv("PORT", 5000)))
