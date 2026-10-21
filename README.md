# RepoGuide 🚀

### Build Together. Ship Smarter.

RepoGuide is a developer-focused platform designed to help developers work with code, explore projects, and collaborate more effectively.

The project is being developed with a React frontend, a Python FastAPI backend, and MongoDB for data storage.

Our goal is to create a platform that makes development workflows easier and helps developers focus on building useful things.

---

# 📌 Table of Contents

1. About the Project
2. Current Features
3. Technology Stack
4. Prerequisites
5. Downloading the Project
6. Setting Up the Backend
7. Configuring Environment Variables
8. Starting the Backend
9. Setting Up the Frontend
10. Starting the Frontend
11. Testing the Application
12. Project Structure
13. Common Errors and Solutions
14. Important Security Guidelines
15. Contributing to the Project

---

# 1. About the Project

RepoGuide is a collaborative development project created to make software development workflows easier.

The project currently includes a React-based login interface and a FastAPI backend with session-based authentication.

MongoDB is used to store application data, including user account information.

The project is being developed further, and additional functionality will be added as development progresses.

## Our Goals

- Create a clean and user-friendly interface.
- Provide secure user authentication.
- Connect the frontend to the backend.
- Store application data using MongoDB.
- Build a foundation for future developer-focused features.
- Make the project easy for other developers to set up and contribute to.

---

# 2. Current Features

The current implementation includes:

- A responsive login interface and developer workspace.
- A FastAPI backend with repository intelligence and bug analysis endpoints.
- User registration and login API endpoints with session-based authentication.
- MongoDB database connectivity and password hashing.
- **AST-Based Bug Detection & Code Improvement Engine** (`backend/bug_analyzer.py`):
  - Detects syntax errors, mutable defaults, bare except clauses, swallowed exceptions, unmanaged open() leaks, unreachable dead code, and variable shadowing.
  - Generates non-destructive, syntax-validated code fixes.
  - Calculates an overall **Code Health Score (0-100)**.
- **Developer Workspace & Code Sandbox**:
  - Full repository scanner with severity filter pills (`Critical`, `High`, `Medium`, `Low`).
  - Interactive Python Code Sandbox for testing snippets live.
  - "How it's scored" expandable scoring reference guide.
  - **Download REPORT** button for exporting comprehensive Markdown bug reports.
- Comprehensive automated test suite (31 unit tests).

---

# 3. Technology Stack

The project uses the following technologies.

| Technology | Purpose                              |
| ---------- | ------------------------------------ |
| React      | Builds the frontend user interface   |
| Vite       | Runs the frontend development server |
| JavaScript | Frontend programming language        |
| CSS        | Styles the interface                 |
| Python     | Backend programming language         |
| FastAPI    | Creates the backend API              |
| Uvicorn    | Runs the backend server              |
| MongoDB    | Stores application data              |
| PyMongo    | Connects Python to MongoDB           |
| Git        | Tracks code changes                  |
| GitHub     | Hosts the project repository         |

You do not need to learn every technology before running the project.

Follow the setup instructions below in order.

---

# 4. Prerequisites

Before running Hackloop, install the following software.

## 4.1 Install Git

Git allows you to download the project and retrieve updates from GitHub.

Download Git from:

https://git-scm.com/downloads

Choose the Windows installer if you are using Windows.

Run the installer and follow the installation instructions.

After installation, open a new terminal and run:

```powershell
git --version
```

If Git is installed correctly, you should see a version number.

For example:

```text
git version 2.x.x
```

Your exact version may be different.

## 4.2 Install Python

Python is required to run the backend.

Download Python from:

https://www.python.org/downloads/

Install a Python version compatible with the project's dependencies.

During installation on Windows, enable the option to add Python to PATH if the installer offers it.

After installation, open a new terminal and run:

```powershell
python --version
```

You should see your installed Python version.

If the command does not work, try:

```powershell
py --version
```

If neither command works, check your Python installation before continuing.

## 4.3 Install Node.js

Node.js is required to run the React frontend and install its dependencies.

Download the current compatible LTS version from:

https://nodejs.org/

Install it using the recommended installation options.

After installation, open a new terminal and run:

```powershell
node --version
```

Then run:

```powershell
npm --version
```

Both commands should display version numbers.

**Important:** npm is included with Node.js. You do not normally need to install npm separately.

## 4.4 Install Visual Studio Code

Visual Studio Code is a code editor that makes it easier to open the project, edit files, and use the terminal.

Download it from:

https://code.visualstudio.com/

You can use another code editor if you prefer, but the instructions in this README use VS Code.

## 4.5 Set Up MongoDB

RepoGuide uses MongoDB to store application data.

The current backend connects to MongoDB using a connection string stored in an environment file.

You need access to a MongoDB database.

If the project owner provides access to an existing MongoDB Atlas database, use the connection details provided securely by the owner.

Otherwise, create your own MongoDB Atlas account and database:

https://www.mongodb.com/atlas

To connect successfully, your MongoDB configuration must include:

- A valid MongoDB connection string.
- A database user with appropriate permissions.
- Network access allowing your computer to connect to the database.

Do not put database credentials directly into Python or JavaScript files.

The connection string will be configured in the backend's `.env` file.

**Note:** Installing MongoDB locally is not required if you are using an accessible MongoDB Atlas database.

---

# 5. Downloading the Project

Once the prerequisites are installed, download the project.

## Step 1: Open a terminal

On Windows, you can use:

- Windows Terminal
- PowerShell
- The integrated terminal in VS Code

## Step 2: Choose where to store the project

For example, to store the project in your C drive, run:

```powershell
cd C:\
```

This changes the terminal's current directory to the C drive.

## Step 3: Clone the repository

Run:

```powershell
git clone https://github.com/jayy-git/automated-repo-assistant-.git
```

This downloads the repository to your computer.

## Step 4: Enter the project folder

Run:

```powershell
cd automated-repo-assistant-
```

## Step 5: Open the project in VS Code

Run:

```powershell
code .
```

The command opens the current project folder in VS Code.

If the `code` command is unavailable, open VS Code manually and select:

**File → Open Folder**

Then select the downloaded `automated-repo-assistant-` folder.

You should see the `backend` and `frontend` folders in the Explorer.

Congratulations! The project is now on your computer.

---

# 6. Setting Up the Backend

The backend handles authentication, database operations, and API requests.

It is built using Python and FastAPI.

## Step 1: Open the backend folder

In VS Code, open the integrated terminal:

**Terminal → New Terminal**

Navigate to the backend directory:

```powershell
cd backend
```

Make sure the terminal is now inside the backend folder.

## Step 2: Create a Python virtual environment

Run:

```powershell
python -m venv .venv
```

A virtual environment creates an isolated Python environment for the project.

This prevents the project's Python dependencies from interfering with other Python projects on your computer.

If `python` is unavailable but `py` works, use:

```powershell
py -m venv .venv
```

## Step 3: Activate the virtual environment

On Windows PowerShell, run:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, your terminal should show `(.venv)` at the beginning of the prompt.

For example:

```text
(.venv) PS C:\path\to\automated-repo-assistant-\backend>
```

This indicates that the virtual environment is active.

### If PowerShell blocks activation

If PowerShell reports that script execution is disabled, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then try activating the environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

This execution-policy change applies only to the current PowerShell process.

## Step 4: Install Python dependencies

Make sure the terminal is inside the backend directory and the virtual environment is active.

Run:

```powershell
python -m pip install -r requirements.txt
```

This reads `requirements.txt` and installs the Python packages required by the backend.

Wait for the installation to finish before continuing.

If the installation fails, read the error message before trying again.

---

# 7. Configuring Environment Variables

The backend needs environment variables to connect to MongoDB and protect user sessions.

These settings belong in a file named `.env`.

## Step 1: Create the environment file

In VS Code, find the `backend` folder.

Right-click the folder and select:

**New File**

Name the file:

```text
.env
```

The file must be inside the backend folder.

Your structure should look like this:

```text
automated-repo-assistant-/
└── backend/
    ├── main.py
    ├── check_db.py
    ├── requirements.txt
    └── .env
```

## Step 2: Add the environment variables

Open `backend/.env` and add:

```dotenv
MONGODB_URI=YOUR_MONGODB_CONNECTION_STRING
SESSION_SECRET=YOUR_RANDOM_SECRET
```

Replace the first placeholder with your actual MongoDB connection string.

Replace the second placeholder with a securely generated random secret.

These are examples of the variable names expected by the current backend.

Do not leave the placeholder values in place when running the application.

## Step 3: Generate a session secret

A session secret helps protect the application's session cookies.

With Python installed, you can generate a random secret by running:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the generated value into your `.env` file.

For example:

```dotenv
SESSION_SECRET=PASTE_YOUR_GENERATED_SECRET_HERE
```

The example above is a placeholder. Use the actual value generated on your computer.

Keep this secret private.

## Step 4: Configure MongoDB access

Make sure your MongoDB connection string is valid.

If you use MongoDB Atlas:

1. Open your MongoDB Atlas account.
2. Select the appropriate project and database.
3. Obtain the connection string using the database connection instructions.
4. Make sure the database user has the required permissions.
5. Configure network access for your computer.
6. Put the connection string into `MONGODB_URI`.

If your connection string contains a username and password, those credentials must be valid.

If your database password contains special characters, they may need to be URL-encoded in the connection string.

## Step 5: Save the file

Press:

**Ctrl + S**

Your `.env` file is now configured.

### Security warning

Never upload your `.env` file to GitHub.

The project's `.gitignore` should exclude it.

If you share the project with teammates, give them their own credentials or arrange database access securely.

Do not send database passwords or session secrets in public messages.

---

# 8. Starting the Backend

The backend and frontend run as two separate development servers.

Start the backend first.

## Step 1: Open the backend terminal

In VS Code, open a terminal and navigate to the backend folder if necessary:

```powershell
cd backend
```

If you are already in the backend folder, do not run the command again.

## Step 2: Activate the virtual environment

If the prompt does not show `(.venv)`, run:

```powershell
.\.venv\Scripts\Activate.ps1
```

If the environment is already active, you can skip this step.

## Step 3: Start FastAPI

Run:

```powershell
python -m uvicorn main:app --reload
```

This starts the backend development server.

Here is what the command means:

- `python -m` runs a Python module.
- `uvicorn` starts the ASGI server.
- `main:app` tells Uvicorn to load the `app` application object from `main.py`.
- `--reload` automatically restarts the server when backend code changes.

Wait until you see a message similar to:

```text
Application startup complete.
```

The backend should now be available at:

http://127.0.0.1:8000

## Step 4: Test the backend

Open this address in your browser:

http://127.0.0.1:8000

You should receive a JSON response similar to:

```json
{
  "message": "Hackloop API is running!"
}
```

You can also open the interactive API documentation:

http://127.0.0.1:8000/docs

The documentation allows you to inspect and test available API endpoints.

**Important:** Keep the backend terminal open while using the application.

Closing the terminal stops the backend server.

---

# 9. Setting Up the Frontend

The frontend is built using React and Vite.

It provides the interface that users interact with in their browsers.

## Step 1: Open another terminal

In VS Code, click:

**Terminal → New Terminal**

You should now have a separate terminal for the frontend.

Do not stop the backend terminal.

## Step 2: Navigate to the frontend folder

From the project root, run:

```powershell
cd frontend
```

If the new terminal starts inside the backend folder instead, use:

```powershell
cd ..\frontend
```

Make sure the terminal is now inside the frontend folder.

## Step 3: Install frontend dependencies

Run:

```powershell
npm install
```

This reads the frontend's `package.json` and installs the JavaScript packages required by the application.

It may take a little time on the first run.

Wait until the command finishes.

You do not need to install React or Vite globally.

## Step 4: Start the frontend

Run:

```powershell
npm run dev
```

Vite will start the frontend development server.

You should see output similar to:

```text
VITE ready

Local: http://localhost:5173/
```

The exact startup time and version may differ.

## Step 5: Open the application

Open this address:

http://localhost:5173/

You should see the Hackloop login interface.

**Important:** Keep both terminals running:

- Terminal 1: FastAPI backend.
- Terminal 2: React/Vite frontend.

The application needs both development servers to be running.

---

# 10. Testing the Application

After starting both servers, test the application.

## Check 1: Backend

Open:

http://127.0.0.1:8000

Confirm that the API returns its running message.

## Check 2: API documentation

Open:

http://127.0.0.1:8000/docs

Confirm that the API documentation loads.

The current backend includes these endpoints:

| Method | Endpoint                     | Purpose                                           |
| ------ | ---------------------------- | ------------------------------------------------- |
| GET    | `/`                          | Checks whether the API is running                 |
| POST   | `/auth/register`             | Registers a user                                  |
| POST   | `/auth/login`                | Authenticates a user                              |
| GET    | `/auth/me`                   | Checks the current session                        |
| POST   | `/repository/quality-check`  | Performs repository governance & documentation checks |
| POST   | `/repository/analyze-bugs`   | Runs AST static bug analysis & health score calculation |
| POST   | `/code/analyze-snippet`      | Analyzes a Python code snippet live on the fly    |
| POST   | `/repository/download-report`| Exports the complete bug analysis report (Markdown) |

## Check 3: Frontend

Open:

http://localhost:5173/

Confirm that the login interface appears.

## Check 4: Authentication

If you already have an account, use its registered email address and password.

If you do not have an account, use the registration endpoint available in the API documentation, if appropriate for your setup.

Do not assume that your Google account automatically works with Hackloop.

Google sign-in requires a separate integration. The current login form uses the application's own authentication system.

## Check 5: Session

After a successful login, the frontend should check whether the backend recognizes your session.

If authentication succeeds, the current interface should display the authenticated state.

If it fails, check the browser console and backend terminal for error messages.

---

# 11. Project Structure

The repository is organized into separate frontend and backend directories.

```text
automated-repo-assistant-/
│
├── backend/
│   ├── main.py
│   ├── check_db.py
│   ├── requirements.txt
│   ├── .env
│   └── .venv/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

Some files and folders, such as `.env` and `.venv`, are created locally and are not committed to GitHub.

The exact project structure may change as development progresses.

## What do the main files do?

### `backend/main.py`

Contains the FastAPI application, API endpoints, authentication logic, and backend configuration.

### `backend/check_db.py`

Contains the database-checking utility used during development.

### `backend/requirements.txt`

Lists the Python dependencies required by the backend.

### `backend/.env`

Stores local environment variables, such as the MongoDB connection string and session secret.

This file must remain private.

### `frontend/src/App.jsx`

Contains the main React application component.

### `frontend/src/App.css`

Contains styles used by the main React application.

### `frontend/src/index.css`

Contains global frontend styles.

### `frontend/src/main.jsx`

Provides the entry point for the React application.

### `frontend/package.json`

Defines frontend dependencies and available npm scripts.

### `.gitignore`

Tells Git which files and folders should not be committed.

---

# 12. Common Errors and Solutions

Here are some common problems you may encounter during setup.

## Error 1: `git is not recognized`

**Cause:** Git is not installed or is not available in your terminal's PATH.

**Solution:**

1. Install Git from https://git-scm.com/downloads
2. Close and reopen your terminal.
3. Run:

```powershell
git --version
```

## Error 2: `python is not recognized`

**Cause:** Python is not installed or is not available in your PATH.

**Solution:**

Install Python from https://www.python.org/downloads/

Reopen your terminal and check:

```powershell
python --version
```

If necessary, try:

```powershell
py --version
```

## Error 3: `No module named fastapi`

**Cause:** The required Python packages have not been installed in the environment being used.

**Solution:**

Navigate to the backend directory.

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the backend again.

## Error 4: `No module named pymongo`

**Cause:** PyMongo is missing from the active Python environment.

**Solution:**

Run:

```powershell
python -m pip install -r requirements.txt
```

Make sure the virtual environment is activated.

## Error 5: MongoDB connection failure

**Possible causes:**

- The connection string is incorrect.
- The database username or password is incorrect.
- Your computer is not permitted by the database's network-access rules.
- The database is unavailable.

**Solution:**

1. Check `backend/.env`.
2. Verify `MONGODB_URI`.
3. Check your MongoDB database user's permissions.
4. Verify the network-access configuration.
5. Restart the backend after correcting the configuration.

Never post your connection string in a public issue or commit it to GitHub.

## Error 6: `npm is not recognized`

**Cause:** Node.js is not installed or is not available in your terminal's PATH.

**Solution:**

Install Node.js from https://nodejs.org/

Restart your terminal and run:

```powershell
node --version
npm --version
```

## Error 7: `Missing script: dev`

**Cause:** The frontend's `package.json` does not contain the expected development script.

**Solution:**

Make sure your terminal is inside the `frontend` directory.

Run:

```powershell
npm run
```

This lists the scripts available in the project.

If `dev` is missing, inspect `frontend/package.json` before changing anything.

## Error 8: Frontend cannot connect to the backend

**Possible causes:**

- The backend is not running.
- The frontend is using the wrong API address.
- CORS is not configured correctly.
- The request URL is incorrect.

**Solution:**

1. Confirm that FastAPI is running at `http://127.0.0.1:8000`.
2. Confirm that the frontend is running at `http://localhost:5173`.
3. Inspect the browser's Developer Tools and Console.
4. Check the backend terminal for errors.
5. Verify that the backend's CORS configuration allows the frontend origin.

The frontend and backend must use compatible addresses and ports.

## Error 9: `401 Unauthorized` or `Invalid email or password`

**Cause:** The supplied credentials may not match an existing account.

**Solution:**

- Check the email address.
- Check the password.
- Confirm that the account has been registered in the database.
- Review the backend terminal for additional errors.

A Google account will not automatically work unless Google authentication has been implemented.

## Error 10: Login succeeds, but the session is not recognized

**Possible causes:**

- The browser did not store the session cookie.
- The frontend did not send the cookie with the session-check request.
- The backend's session configuration is incorrect.
- The frontend and backend are using incompatible cookie settings.

**Solution:**

1. Confirm that the login endpoint succeeds.
2. Check the browser's Developer Tools under Network.
3. Inspect the login response and its cookie-related headers.
4. Inspect the subsequent `/auth/me` request.
5. Check the backend terminal for errors.

Do not disable authentication or expose session secrets as a workaround.

## Error 11: Port 8000 or 5173 is already in use

**Cause:** Another process is already using the required port.

**Solution:**

Check whether another backend or frontend development server is running.

If you already have the relevant server open in another terminal, use that server rather than starting another instance.

If necessary, stop the old development server and restart it.

---

# 13. Important Security Guidelines

Please follow these rules when working on Hackloop.

## Never commit secrets

Do not upload:

- `.env` files containing credentials.
- MongoDB passwords.
- Session secrets.
- API keys.
- Private tokens.
- Personal credentials.

## Do not upload dependency folders

Avoid committing:

- Python virtual environments.
- `node_modules`.
- Python cache files.

These folders can be recreated by installing the declared dependencies.

## Do not share accounts unnecessarily

Each developer should use appropriately authorized credentials.

If you use a shared development database, coordinate access with the project owner.

Do not place credentials in public GitHub issues or commit messages.

## Keep dependencies documented

When you add a Python dependency, update:

```text
backend/requirements.txt
```

When you add a frontend dependency, update the frontend's `package.json` and `package-lock.json` through npm.

---

# 14. Contributing to the Project

Everyone on the team is welcome to contribute.

If you are new to Git and GitHub, follow these steps.

## Step 1: Check your current changes

From the project root, run:

```powershell
git status
```

This shows which files have changed.

## Step 2: Download the latest changes

Before starting new work, run:

```powershell
git pull
```

This retrieves changes from the configured upstream branch.

If Git reports a conflict, do not overwrite files blindly. Ask a teammate to help resolve it.

## Step 3: Make your changes

Edit the files required for your task.

Test your changes locally before committing them.

## Step 4: Stage your changes

Run:

```powershell
git add .
```

This stages your changes for the next commit.

Before committing, inspect the staged changes and verify that no secrets or local environment files are included.

## Step 5: Commit your changes

Run:

```powershell
git commit -m "Describe your changes"
```

Replace the example message with a short description of your work.

A commit saves a snapshot of the staged changes in your local Git history.

## Step 6: Push your changes

If you are working on the shared branch and have permission to push, run:

```powershell
git push
```

For team projects, using a separate branch and opening a pull request is generally preferable.

A pull request allows teammates to review changes before merging them.

**Important:** Do not push directly to the shared branch if the team has agreed to use pull requests.

---

# 15. Quick Start Reference

After the initial setup is complete, these are the commands used to run the application.

## Backend

Open a terminal in the project root:

```powershell
cd backend
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start the backend:

```powershell
python -m uvicorn main:app --reload
```

Backend:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

## Frontend

Open a second terminal in the project root:

```powershell
cd frontend
```

Start the frontend:

```powershell
npm run dev
```

Frontend:

http://localhost:5173/

Keep both terminals running while using the application.

---

# Final Note

Hackloop is an evolving project.

Some features are still under development, and the setup instructions may change as the codebase grows.

If you encounter a problem:

1. Read the error message carefully.
2. Check the relevant troubleshooting section.
3. Confirm that you are running commands from the correct directory.
4. Verify that the required server is running.
5. Ask the team for help if the problem persists.

Thank you for being part of Hackloop.

**Build Together. Ship Smarter.** 🚀
