import datetime
import uuid
from flask import Blueprint, current_app, render_template, request, redirect, url_for

pages = Blueprint("tasks", __name__, template_folder="templates", static_folder="static")


@pages.context_processor
def add_calc_date_range():
    def date_range(start:datetime.datetime):
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
        return dates

    return {"date_range": date_range}

def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)


@pages.route("/")
def index():
    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = today_at_midnight()

    tasks_on_date = current_app.db.tasks.find({"added": selected_date})

    completions = [
        task["task"]
        for task in current_app.db.completions.find({"date": selected_date})
    ]

    return render_template(
        "index.html", 
        tasks=tasks_on_date,     
        selected_date=selected_date,
        completions=completions,
        title="TaskNest - Home",
    )

@pages.route('/add', methods=["GET", "POST"])
def add_task():
    today =today_at_midnight()

    if request.method == "POST":
        current_app.db.tasks.insert_one(
            {"_id": uuid.uuid4().hex, "added": today, "name": request.form.get("task")}
        )

    return render_template(
        "add_task.html", 
        title="TaskNest - Add Task", 
        selected_date=today,
    )



@pages.route("/complete", methods=["POST"])
def complete():
    date_string = request.form.get("date")
    task = request.form.get("taskId")
    date = datetime.datetime.fromisoformat(date_string)
    current_app.db.completions.insert_one({"date": date, "task": task})

    return redirect(url_for("tasks.index", date=date_string))