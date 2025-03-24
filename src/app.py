"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from pydantic import BaseModel
import re

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    # Novas atividades esportivas
    "Soccer Team": {
        "description": "Join the school soccer team and compete in tournaments",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": []
    },
    "Basketball Club": {
        "description": "Practice basketball and participate in friendly matches",
        "schedule": "Wednesdays, 3:00 PM - 4:30 PM",
        "max_participants": 15,
        "participants": []
    },
    # Novas atividades artísticas
    "Drama Club": {
        "description": "Explore acting and participate in school plays",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": []
    },
    "Painting Workshop": {
        "description": "Learn painting techniques and create your own artwork",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": []
    },
    # Novas atividades intelectuais
    "Math Club": {
        "description": "Solve challenging math problems and prepare for competitions",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 10,
        "participants": []
    },
    "Debate Team": {
        "description": "Develop public speaking skills and participate in debates",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.get("/activities/{activity_name}")
def get_activity(activity_name: str):
    """Retrieve details for a specific activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    return activities[activity_name]

class SignupRequest(BaseModel):
    email: str

@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, request: SignupRequest):
    """Sign up a student for an activity"""
    email = request.email

    # Validar formato do email
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    # Validar se a atividade existe
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    # Verificar se o aluno já está inscrito
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up for this activity")

    # Verificar se a atividade já atingiu o limite de participantes
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is already full")

    # Adicionar aluno
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}
