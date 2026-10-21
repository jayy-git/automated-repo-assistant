import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo import MongoClient
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware


import re

from pydantic import BaseModel, EmailStr
from pwdlib import PasswordHash
from pymongo.errors import DuplicateKeyError

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


# Define the data required for registration
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


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
    # Get the MongoDB database
    database = app.state.database

    # Get the users collection
    users = database["users"]

    # Normalize the email
    email = str(user.email).lower().strip()

    # Check whether the email is already registered
    existing_user = users.find_one({"email": email})

    if existing_user:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    # Hash the password before storing it
    hashed_password = password_hasher.hash(user.password)

    # Save the new user in MongoDB
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
    # Get the users collection
    users = app.state.database["users"]

    # Normalize the email
    email = str(user.email).lower().strip()

    # Find the account
    existing_user = users.find_one({"email": email})

    # Reject unknown email addresses
    if not existing_user:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    # Verify the submitted password against the stored hash
    password_is_valid = password_hasher.verify(
        user.password,
        existing_user["password_hash"]
    )

    # Reject an incorrect password
    if not password_is_valid:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    # Create a session for the authenticated user
    request.session["user_id"] = str(existing_user["_id"])
    request.session["role"] = existing_user["role"]
    print("DEBUG: Session type:", type(request.session))
    print("DEBUG: Session contents:", dict(request.session))
    # Return basic account information
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