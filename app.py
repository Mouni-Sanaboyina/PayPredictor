from flask import Flask, render_template, request, session
import requests
import re

app = Flask(__name__)
app.secret_key = '250af7cf7520d84edb0cc57634feda7e'

def format_bot_message(message):
    message = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', message)
    message = re.sub(r'\*(.*?)\*', r'<em>\1</em>', message)
    message = ''.join(f'<p>{para.strip()}</p>' for para in message.split('\n') if para.strip())
    return message

def generate_ai_response(user_question):
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "gemma:2b",
                "messages": [{"role": "user", "content": user_question}],
                "stream": False
            }
        )
        data = response.json()
        if 'message' in data and 'content' in data['message']:
            return data['message']['content']
        elif 'error' in data:
            return f"Error from model: {data['error']}"
        else:
            return "Unexpected response format from model."
    except Exception as e:
        return f"Error generating response: {str(e)}"

questions_by_branch = {
    "CSE": [
        "How comfortable are you with Data Structures and Algorithms? (1-10)",
        "How strong are your problem-solving skills? (1-10)",
        "How good are you in Programming Languages like C++, Java, or Python? (1-10)",
        "How familiar are you with Database Management Systems (DBMS)? (1-10)",
        "How confident are you in Operating Systems and Computer Networks? (1-10)",
        "How often do you participate in coding contests or practice on platforms like LeetCode/Codeforces? (1-10)",
        "How comfortable are you with system design concepts or basic software architecture? (1-10)"
    ],
    "CSE(AI & DS)": [
        "How familiar are you with core Machine Learning algorithms (e.g., linear regression, SVM, decision trees)? (1-10)",
        "How comfortable are you with Python and libraries like NumPy, Pandas, Scikit-learn? (1-10)",
        "How strong is your knowledge of statistics and probability? (1-10)",
        "How confident are you in building and understanding data pipelines and preprocessing steps? (1-10)",
        "Have you worked with any real-world datasets or done mini-projects in AI/DS? (1-10)",
        "How good are you with Deep Learning frameworks like TensorFlow or PyTorch? (1-10)",
        "How comfortable are you with model evaluation and tuning (e.g., cross-validation, hyperparameter tuning)? (1-10)"
    ],
    "CSE(AI&ML)": [
        "How well do you understand supervised and unsupervised learning concepts? (1-10)",
        "How confident are you in writing Python code for AI/ML applications? (1-10)",
        "Have you implemented any ML models from scratch or using libraries like Scikit-learn? (1-10)",
        "How familiar are you with neural networks and their architectures (e.g., CNNs, RNNs)? (1-10)",
        "How comfortable are you with data preprocessing and feature engineering? (1-10)",
        "How experienced are you with model evaluation techniques like accuracy, precision, recall, F1-score? (1-10)",
        "How strong is your understanding of overfitting, underfitting, and regularization techniques? (1-10)"
    ],
    "IT": [
        "Rate your proficiency in programming languages like Python, Java, or C (1-10).",
        "How confident are you in solving Data Structures and Algorithms problems (1-10)?",
        "Rate your understanding of databases and SQL (1-10).",
        "How well do you understand networking and cybersecurity fundamentals (1-10)?",
        "Rate your experience with real-world projects, internships, or hackathons (1-10).",
        "How familiar are you with version control systems like Git and GitHub (1-10)?",
        "Rate your understanding of operating systems and system-level concepts (1-10)."
    ],
    "CYBER": [
        "How familiar are you with basic cybersecurity concepts like CIA triad (Confidentiality, Integrity, Availability)? (1-10)",
        "How comfortable are you with using tools like Wireshark, Nmap, or Burp Suite? (1-10)",
        "Have you practiced ethical hacking or taken part in CTFs (Capture The Flag challenges)? (1-10)",
        "How well do you understand network protocols like TCP/IP, HTTP, and DNS? (1-10)",
        "How strong is your knowledge of vulnerabilities like XSS, SQL injection, and buffer overflow? (1-10)",
        "Have you worked with or studied cryptographic techniques (e.g., hashing, encryption)? (1-10)",
        "How confident are you in analyzing logs and identifying security incidents? (1-10)"
    ],
    "MECH": [
        "How well do you understand core mechanical subjects like Thermodynamics, SOM, and Fluid Mechanics? (1-10)",
        "How comfortable are you with using CAD tools like AutoCAD, SolidWorks, or CATIA? (1-10)",
        "How familiar are you with manufacturing processes and material science? (1-10)",
        "Have you done any projects related to automotive, robotics, or design analysis? (1-10)",
        "How well do you understand kinematics and dynamics of machines? (1-10)",
        "Have you worked with simulation tools like ANSYS or MATLAB? (1-10)",
        "How confident are you in interpreting engineering drawings and blueprints? (1-10)"
    ],
    "CIVIL": [
        "How strong is your understanding of Structural Analysis and Design? (1-10)",
        "How comfortable are you with AutoCAD and STAAD Pro? (1-10)",
        "How well do you understand construction materials and their properties? (1-10)",
        "Have you worked on any site management or planning projects? (1-10)",
        "How familiar are you with surveying and geotechnical engineering concepts? (1-10)",
        "How confident are you in interpreting civil engineering drawings and blueprints? (1-10)",
        "How skilled are you with project management and safety regulations? (1-10)"
    ],
    "ECE": [
        "How well do you understand analog and digital circuits? (1-10)",
        "How comfortable are you with microcontrollers and embedded systems? (1-10)",
        "How strong is your knowledge of communication systems? (1-10)",
        "How skilled are you in using EDA tools like MATLAB and Simulink? (1-10)",
        "How familiar are you with signal processing concepts? (1-10)",
        "How confident are you with VLSI design fundamentals? (1-10)",
        "How experienced are you with wireless communication technologies? (1-10)"
    ],
    "EEE": [
        "How strong is your understanding of power systems and electrical machines? (1-10)",
        "How comfortable are you with circuit analysis and control systems? (1-10)",
        "How skilled are you in using software like MATLAB and PSCAD? (1-10)",
        "How familiar are you with renewable energy technologies? (1-10)",
        "How confident are you in electrical wiring and safety practices? (1-10)",
        "How experienced are you with electrical instrumentation and measurements? (1-10)",
        "How good are you at troubleshooting electrical circuits and systems? (1-10)"
    ]
}

@app.route("/", methods=["GET", "POST"])
def home():
    branches = list(questions_by_branch.keys())

    if "step" not in session:
        session["step"] = 0
        session["branch"] = None
        session["answers"] = []

    if request.method == "POST":
        step_form = request.form.get("step", type=int)

        if step_form == -1:
            user_question = request.form.get("user_question")
            if user_question:
                bot_reply = format_bot_message(generate_ai_response(user_question))
                return render_template(
                    "index.html",
                    result="Career Advice Provided",
                    bot_message=session.get("advice", ""),
                    branch=session.get("branch"),
                    followup_answer=bot_reply,
                    step=0,
                    branches=branches
                )
            else:
                return render_template("index.html", error="Please enter a question.", step=0, branches=branches)

        if session["step"] == 0:
            branch = request.form.get("branch")
            if branch in questions_by_branch:
                session["branch"] = branch
                session["step"] = 1
                session["answers"] = []
            else:
                return render_template("index.html", error="Please select a valid branch.", step=0, branches=branches)

        else:
            answer = request.form.get("answer")
            if answer is None or not answer.isdigit():
                return render_template("index.html", error="Please enter a valid numeric answer.", step=session["step"], branch=session["branch"], branches=branches)

            session["answers"].append(int(answer))
            session["step"] += 1

        if session["step"] > len(questions_by_branch[session["branch"]]):
            prompt = f"Branch: {session['branch']}\nAnswers:\n"
            for i, ans in enumerate(session["answers"], 1):
                prompt += f"Q{i}: {questions_by_branch[session['branch']][i-1]}\nA{i}: {ans}\n"
            prompt += (
    "Based on these answers, first predict an approximate annual salary package (in INR) the student might expect (e.g., 'Predicted Salary: ₹X LPA'), "
    "then provide personalized career advice based on their current skill level."
)


            raw_advice = generate_ai_response(prompt)
            advice = format_bot_message(raw_advice)

            session["advice"] = advice
            branch = session["branch"]
            answers = session["answers"]
            session["step"] = 0

            return render_template(
                "index.html",
                result="Your predicted salary package and career advice",
                bot_message=advice,
                branch=branch,
                answers=answers,
                step=0,
                branches=branches
            )

    if session["step"] == 0:
        return render_template("index.html", step=0, branches=branches)
    else:
        question_index = session["step"] - 1
        current_question = questions_by_branch[session["branch"]][question_index]
        return render_template("index.html", step=session["step"], question=current_question, branch=session["branch"], branches=branches)

if __name__ == "__main__":
    app.run(debug=True)
