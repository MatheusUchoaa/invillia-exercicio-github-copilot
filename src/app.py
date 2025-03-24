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
from pydantic import BaseModel, EmailStr, constr
import re
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

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

def normalize_activity_name(name: str) -> str:
    """Normaliza o nome da atividade removendo espaços extras e convertendo para lowercase"""
    return " ".join(name.strip().split()).lower()

def get_activity_by_name(activity_name: str) -> dict:
    """Busca uma atividade pelo nome normalizado"""
    normalized_name = normalize_activity_name(activity_name)
    activity = next(
        (v for k, v in activities.items() if normalize_activity_name(k) == normalized_name),
        None
    )
    if not activity:
        raise HTTPException(
            status_code=404,
            detail=f"Activity '{activity_name}' not found"
        )
    return activity

@app.get("/activities/{activity_name}")
def get_activity(activity_name: str):
    """Retrieve details for a specific activity"""
    if not re.match(r'^[a-zA-Z0-9\s]+$', activity_name):
        raise HTTPException(
            status_code=400,
            detail="Activity name can only contain letters, numbers and spaces"
        )
    
    try:
        activity = get_activity_by_name(activity_name)
        logger.info(f"Activity details retrieved for: {activity_name}")
        return activity
    except Exception as e:
        logger.error(f"Error retrieving activity {activity_name}: {str(e)}")
        raise

class SignupRequest(BaseModel):
    email: EmailStr

    @property
    def is_valid_domain(self) -> bool:
        return self.email.endswith("@mergington.edu")

@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, request: SignupRequest):
    """Sign up a student for an activity"""
    if not request.is_valid_domain:
        raise HTTPException(
            status_code=400,
            detail="Only @mergington.edu email addresses are allowed"
        )

    try:
        activity = get_activity_by_name(activity_name)
        
        if request.email in activity["participants"]:
            raise HTTPException(
                status_code=400,
                detail=f"Student '{request.email}' is already signed up for this activity"
            )

        if len(activity["participants"]) >= activity["max_participants"]:
            raise HTTPException(
                status_code=400,
                detail=f"Activity '{activity_name}' is already full"
            )

        activity["participants"].append(request.email)
        logger.info(f"Student {request.email} signed up for {activity_name}")
        return {
            "message": f"Successfully signed up {request.email} for {activity_name}",
            "current_participants": len(activity["participants"])
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during signup for {activity_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during signup"
        )
