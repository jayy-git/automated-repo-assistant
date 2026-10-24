import os
from datetime import datetime, timezone
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
from repository_analyzer import scan_repository
from repository_qa import answer_repository_question
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

class RepositoryQuestionRequest(BaseModel):
    repository_path: str = "."
    question: str


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
    SessionMiddleware,
    secret_key=session_secret,
    session_cookie="hackloop_session",
    same_site="lax",
    https_only=False,
    max_age=3600,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.post("/auth/logout")
def logout_user(request: Request):
    """Clear the current authenticated session cookie."""
    request.session.clear()
    return {"message": "Logged out successfully."}


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

        # Save a compact, user-scoped record for the real health-trend chart.
        relative_repo = target_path.relative_to(project_root).as_posix() or "."
        app.state.database["scan_history"].insert_one({
            "user_id": user_id,
            "repository_path": relative_repo,
            "repository_name": results.get("repository_name") or target_path.name,
            "scanned_at": datetime.now(timezone.utc),
            "health_score": results.get("health_score"),
            "total_findings": results.get("total_findings", len(results.get("findings", []))),
            "severity_breakdown": results.get("severity_breakdown", {}),
            "total_python_files": results.get("total_python_files", 0),
        })
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

@app.post("/repository/ask")
def repository_ask(request: Request, payload: RepositoryQuestionRequest):
    """Answer questions about a repository. Protected by session authentication."""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Please log in before asking repository questions."
        )

    project_root = Path(__file__).resolve().parent.parent
    path_candidate = Path(payload.repository_path)
    target_path = (
        (project_root / path_candidate).resolve()
        if not path_candidate.is_absolute()
        else path_candidate.resolve()
    )

    if not target_path.is_relative_to(project_root):
        raise HTTPException(
            status_code=403,
            detail="You can only ask questions about repositories inside the project directory."
        )

    try:
        return answer_repository_question(
            repository_path=str(target_path),
            question=payload.question
        )
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

=@app.get("/repository/files")
def get_repository_files(
    request: Request,
    repository_path: str = ".",
):
    """Return a safe inventory of repository files for the workspace."""

    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Please log in before exploring repository files.",
        )

    project_root = Path(__file__).resolve().parent.parent
    path_candidate = Path(repository_path)

    target_path = (
        (project_root / path_candidate).resolve()
        if not path_candidate.is_absolute()
        else path_candidate.resolve()
    )

    if not target_path.is_relative_to(project_root):
        raise HTTPException(
            status_code=403,
            detail="You can only explore repositories inside the project directory.",
        )

    if not target_path.exists() or not target_path.is_dir():
        raise HTTPException(
            status_code=404,
            detail="Repository directory was not found.",
        )

    try:
        inventory = scan_repository(str(target_path))
        return inventory
    except (FileNotFoundError, NotADirectoryError) as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.get("/repository/scan-history")
def get_repository_scan_history(request: Request, repository_path: Optional[str] = None, limit: int = 20):
    """Return real scan history for the authenticated user only."""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Please log in to view scan history.")

    query = {"user_id": user_id}
    if repository_path:
        project_root = Path(__file__).resolve().parent.parent
        candidate = Path(repository_path)
        target_path = ((project_root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve())
        if not target_path.is_relative_to(project_root):
            raise HTTPException(status_code=403, detail="You can only view history for repositories inside the project directory.")
        query["repository_path"] = target_path.relative_to(project_root).as_posix() or "."

    safe_limit = max(1, min(int(limit), 50))
    records = app.state.database["scan_history"].find(query, {"_id": 0}).sort("scanned_at", -1).limit(safe_limit)
    history = []
    for record in reversed(list(records)):
        scanned_at = record.get("scanned_at")
        history.append({
            "repository_path": record.get("repository_path", "."),
            "repository_name": record.get("repository_name", "Repository"),
            "scanned_at": scanned_at.isoformat() if scanned_at else None,
            "health_score": record.get("health_score"),
            "total_findings": record.get("total_findings", 0),
            "severity_breakdown": record.get("severity_breakdown", {}),
            "total_python_files": record.get("total_python_files", 0),
        })
    return {"history": history}


@app.get("/repository/file-content")
def get_repository_file_content(request: Request, repository_path: str = ".", file_path: str = ""):
    """Return a bounded text file from an authenticated repository, preventing path traversal."""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Please log in before opening repository files.")
    if not file_path.strip():
        raise HTTPException(status_code=400, detail="A file path is required.")

    project_root = Path(__file__).resolve().parent.parent
    repo_candidate = Path(repository_path)
    target_repo = ((project_root / repo_candidate).resolve() if not repo_candidate.is_absolute() else repo_candidate.resolve())
    if not target_repo.is_relative_to(project_root):
        raise HTTPException(status_code=403, detail="You can only explore repositories inside the project directory.")
    if not target_repo.exists() or not target_repo.is_dir():
        raise HTTPException(status_code=404, detail="Repository directory was not found.")

    relative_file = Path(file_path)
    target_file = (target_repo / relative_file).resolve()
    if not target_file.is_relative_to(target_repo):
        raise HTTPException(status_code=403, detail="The requested file is outside the repository.")
    if not target_file.exists() or not target_file.is_file():
        raise HTTPException(status_code=404, detail="File was not found in this repository.")

    # Avoid returning secrets, binaries, dependency trees, or huge files to the UI.
    blocked_parts = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}
    if any(part.lower() in blocked_parts for part in target_file.relative_to(target_repo).parts):
        raise HTTPException(status_code=403, detail="Files in generated or dependency directories cannot be opened.")
    if target_file.name.lower().startswith(".env") or target_file.name.lower() in {"id_rsa", "id_ed25519"} or target_file.suffix.lower() in {".pem", ".key", ".p12", ".pfx", ".db", ".sqlite", ".sqlite3", ".exe", ".dll", ".so", ".bin", ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip"}:
        raise HTTPException(status_code=403, detail="This file type is not available in the code viewer.")
    if target_file.stat().st_size > 200_000:
        raise HTTPException(status_code=413, detail="This file is too large to display (limit: 200 KB).")
    try:
        content = target_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=415, detail="This file is not a UTF-8 text file.")
    except OSError:
        raise HTTPException(status_code=500, detail="The file could not be read.")
    return {"file_path": target_file.relative_to(target_repo).as_posix(), "content": content, "size_bytes": target_file.stat().st_size}
