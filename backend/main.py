import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from pwdlib import PasswordHash
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from starlette.middleware.sessions import SessionMiddleware

from repository_quality_analyzer import analyze_repository_quality
from bug_analyzer import (
    analyze_python_code,
    analyze_repository_bugs,
    generate_bug_report_markdown,
)

# Load environment variables from backend/.env
env_path = Path(__file__).with_name(".env")
load_dotenv(env_path)

# Read the MongoDB connection string
mongodb_uri = os.getenv("MONGODB_URI")
session_secret = os.getenv("SESSION_SECRET")

if not session_secret:
    raise RuntimeError("SESSION_SECRET is missing from backend/.env")

if not mongodb_uri:
    raise RuntimeError("MONGODB_URI is missing from backend/.env")

# Create a password hasher
password_hasher = PasswordHash.recommended()


# Define the data models for authentication
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Data models for bug and code analysis
class RepoBugAnalysisRequest(BaseModel):
    repository_path: str = "."
    include_ai: bool = False


class SnippetAnalysisRequest(BaseModel):
    code: str
    filename: Optional[str] = "snippet.py"
    include_ai: Optional[bool] = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create one MongoDB client for the application
    client = MongoClient(mongodb_uri)

    # Check the database connection
    client.admin.command("ping")

    # Make the client available to our API routes
    app.state.mongodb_client = client
    app.state.database = client["hackloop"]

    print("Connected to MongoDB Atlas!")

    try:
        yield
    finally:
        client.close()
        print("MongoDB connection closed.")


app = FastAPI(
    title="RepoGuide API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    session_cookie="hackloop_session",
    same_site="lax",
    https_only=False,
    max_age=3600,
)


@app.get("/")
def home():
    return {
        "message": "RepoGuide API is running!"
    }


@app.post("/auth/register")
def register_user(user: RegisterRequest):
    database = app.state.database
    users = database["users"]
    email = str(user.email).lower().strip()

    existing_user = users.find_one({"email": email})
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    hashed_password = password_hasher.hash(user.password)
    result = users.insert_one({
        "name": user.name,
        "email": email,
        "password_hash": hashed_password,
        "role": "developer"
    })

    return {
        "message": "Account created successfully!",
        "user_id": str(result.inserted_id),
        "email": email
    }


@app.post("/auth/login")
def login_user(request: Request, user: LoginRequest):
    users = app.state.database["users"]
    email = str(user.email).lower().strip()

    existing_user = users.find_one({"email": email})
    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    password_is_valid = password_hasher.verify(
        user.password,
        existing_user["password_hash"]
    )
    if not password_is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    request.session["user_id"] = str(existing_user["_id"])
    request.session["role"] = existing_user["role"]

    return {
        "message": "Login successful!",
        "user_id": str(existing_user["_id"]),
        "email": existing_user["email"],
        "role": existing_user["role"]
    }


@app.get("/auth/me")
def get_current_user(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        return {"logged_in": False, "message": "No active session"}

    return {
        "logged_in": True,
        "user_id": user_id,
        "role": request.session.get("role")
    }


@app.post("/repository/quality-check")
def repository_quality_check(request: Request, repository_path: str):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Please log in before analyzing a repository."
        )

    project_root = Path(__file__).resolve().parent.parent
    target_path = Path(repository_path).resolve()

    if not target_path.is_relative_to(project_root):
        raise HTTPException(
            status_code=403,
            detail="You can only analyze repositories inside the project directory."
        )

    try:
        return analyze_repository_quality(target_path)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="The repository directory was not found."
        )
    except NotADirectoryError:
        raise HTTPException(
            status_code=400,
            detail="The provided path must be a directory."
        )


@app.post("/repository/analyze-bugs")
def repository_analyze_bugs(request: Request, payload: RepoBugAnalysisRequest):
    """
    Scans a repository directory for code-level bugs, anti-patterns, and resource leaks.
    Protected by session authentication.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Please log in before analyzing repository bugs."
        )

    project_root = Path(__file__).resolve().parent.parent
    path_candidate = Path(payload.repository_path)
    target_path = (project_root / path_candidate).resolve() if not path_candidate.is_absolute() else path_candidate.resolve()

    if not target_path.is_relative_to(project_root):
        raise HTTPException(
            status_code=403,
            detail="You can only analyze repositories inside the project directory."
        )

    try:
        results = analyze_repository_bugs(
            repository_path=str(target_path),
            include_ai_explanations=payload.include_ai
        )
        results["report_markdown"] = generate_bug_report_markdown(results)
        return results
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="The repository directory was not found."
        )
    except NotADirectoryError:
        raise HTTPException(
            status_code=400,
            detail="The provided path must be a directory."
        )


@app.post("/code/analyze-snippet")
def code_analyze_snippet(request: Request, payload: SnippetAnalysisRequest):
    """
    Analyzes an individual Python code snippet on the fly.
    Protected by session authentication.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Please log in before analyzing code snippets."
        )

    results = analyze_python_code(
        code_string=payload.code,
        filename=payload.filename or "snippet.py",
        include_ai_explanations=payload.include_ai or False
    )
    return results


@app.post("/repository/download-report")
def download_bug_report(request: Request, payload: RepoBugAnalysisRequest):
    """
    Generates and returns the markdown report content for download.
    Protected by session authentication.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Please log in before downloading reports."
        )

    project_root = Path(__file__).resolve().parent.parent
    path_candidate = Path(payload.repository_path)
    target_path = (project_root / path_candidate).resolve() if not path_candidate.is_absolute() else path_candidate.resolve()

    if not target_path.is_relative_to(project_root):
        raise HTTPException(
            status_code=403,
            detail="You can only export reports inside the project directory."
        )

    results = analyze_repository_bugs(
        repository_path=str(target_path),
        include_ai_explanations=payload.include_ai
    )
    report_md = generate_bug_report_markdown(results)

    return {
        "filename": f"BUG_REPORT_{results['repository_name']}.md",
        "markdown": report_md
    }
