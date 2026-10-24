# RepoGuide frontend redesign notes

This update redesigns the React frontend around the supplied lavender dashboard reference while retaining the existing FastAPI endpoints for registration, login/session checks, repository bug analysis, and snippet analysis.

## Included
- Persistent seven-item sidebar and responsive workspace layout.
- Dashboard with real latest-scan values and horizontal category/severity bars (empty states are shown until a scan exists).
- Repository analysis page with severity filtering, finding details, copyable proposed fixes, and Markdown report download.
- Interactive Python snippet sandbox on the Analyze Repository page.
- Q&A page that answers a limited set of questions from the latest scan results; it does not execute code or modify files.
- Separate cosmic-style interactive Code Map page. The current nodes are an illustrative RepoGuide module map, not yet generated from a live dependency-graph API.
- Light/dark mode and three accent palettes (Cosmic Violet, Ocean Blue, Mint Green), saved in browser local storage.
- Added `POST /auth/logout` to clear the server-side session cookie when signing out.

## Run locally
1. Keep your existing local `backend/.env` file in place; it is intentionally not included in this archive because it may contain credentials.
2. Start the backend from the `backend` directory using your existing virtual environment and `python -m uvicorn main:app --reload`.
3. In a second terminal, open `frontend`, run `npm install`, then `npm run dev`.
4. Open the local Vite URL printed in the terminal.

The frontend still expects the FastAPI server at `http://localhost:8000`, matching the existing project setup.
