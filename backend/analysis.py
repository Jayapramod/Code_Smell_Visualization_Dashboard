from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from pathlib import Path
import subprocess
import tempfile
import shutil
import re
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CodeLens API",
    description="Backend API for repository code analysis",
    version="1.0.0",
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

# ============================================================
# Request / Response Models
# ============================================================

class AnalyzeRequest(BaseModel):
    repository_url: HttpUrl
    branch: str = "main"


# ============================================================
# Repository URL Validation
# ============================================================

def validate_repository_url(repository_url: str) -> bool:
    """
    Validate that the supplied URL looks like a GitHub repository URL.
    """

    pattern = r"^https://github\.com/[^/]+/[^/]+/?$"

    return bool(re.match(pattern, repository_url))


# ============================================================
# Clone Repository
# ============================================================

def clone_repository(
    repository_url: str,
    branch: str,
    destination: Path,
) -> None:
    """
    Clone the requested repository branch into destination.
    """

    command = [
        "git",
        "clone",
        "--depth",
        "1",
        "--branch",
        branch,
        repository_url,
        str(destination),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
        )

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=408,
            detail="Repository cloning timed out.",
        )

    if result.returncode != 0:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to clone repository: {result.stderr.strip()}",
        )


# ============================================================
# Analyzer
# ============================================================

def run_analyzer(repository_path: Path) -> dict:
    """
    Run the repository analyzer.

    This is intentionally a placeholder for now.
    We will replace this with the actual analyzer later.
    """

    # TODO:
    # Connect the actual analyzer here.

    return {
        "metrics": {
            "totalFiles": 0,
            "loc": 0,
            "totalSmells": 0,
            "avgComplexity": 0,
            "maxComplexity": 0,
            "filesWithSmells": 0,
            "functionsAnalyzed": 0,
            "classesAnalyzed": 0,
        },
        "summary": {
            "health": "Not analyzed",
            "message": "Analyzer implementation is not connected yet.",
        },
        "smells": [],
        "complexity": [],
    }


# ============================================================
# POST /api/analyze
# ============================================================

@app.post("/api/analyze")
def analyze_repository(request: AnalyzeRequest):
    """
    Clone a repository and analyze it.

    Request:

    {
        "repository_url": "https://github.com/user/repository",
        "branch": "main"
    }
    """

    repository_url = str(request.repository_url)
    branch = request.branch.strip()

    # --------------------------------------------------------
    # Validate URL
    # --------------------------------------------------------

    if not validate_repository_url(repository_url):
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub repository URL.",
        )

    # --------------------------------------------------------
    # Validate branch
    # --------------------------------------------------------

    if not branch:
        raise HTTPException(
            status_code=400,
            detail="Branch cannot be empty.",
        )

    # --------------------------------------------------------
    # Create temporary directory
    # --------------------------------------------------------

    temp_directory = Path(
        tempfile.mkdtemp(prefix="codelens_")
    )

    repository_path = temp_directory / "repository"

    try:

        # ----------------------------------------------------
        # Clone repository
        # ----------------------------------------------------

        clone_repository(
            repository_url=repository_url,
            branch=branch,
            destination=repository_path,
        )

        # ----------------------------------------------------
        # Run analyzer
        # ----------------------------------------------------

        analysis_result = run_analyzer(
            repository_path
        )

        # ----------------------------------------------------
        # Add repository information
        # ----------------------------------------------------

        response = {
            "repository": {
                "url": repository_url,
                "branch": branch,
            },
            "analysis": analysis_result,
        }

        return response

    finally:

        # ----------------------------------------------------
        # Always remove cloned repository
        # ----------------------------------------------------

        shutil.rmtree(
            temp_directory,
            ignore_errors=True,
        )


# ============================================================
# Health Check
# ============================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "CodeLens API",
    }

