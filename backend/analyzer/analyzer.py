from pathlib import Path
from typing import Any

from .metrics import analyze_file_metrics
from .smells import analyze_code_smells
from .complexity import analyze_complexity


# File extensions we currently want to analyze.
SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
}


# Directories that should never be analyzed.
IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    "coverage",
}


def is_supported_file(file_path: Path) -> bool:
    """
    Check whether a file is a source file that we want to analyze.
    """
    return (
        file_path.is_file()
        and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def should_ignore(file_path: Path) -> bool:
    """
    Check whether a file belongs to an ignored directory.
    """
    return any(
        part in IGNORED_DIRECTORIES
        for part in file_path.parts
    )


def scan_repository(repository_path: Path) -> list[Path]:
    """
    Scan the repository and return all supported source files.
    """

    source_files = []

    for path in repository_path.rglob("*"):
        if should_ignore(path):
            continue

        if is_supported_file(path):
            source_files.append(path)

    return source_files


def calculate_summary(
    total_files: int,
    total_smells: int,
    average_complexity: float,
) -> dict[str, Any]:
    """
    Generate a simple overall repository health summary.
    """

    if total_files == 0:
        return {
            "health": "No Data",
            "message": "No supported source files were found.",
        }

    if total_smells == 0 and average_complexity <= 5:
        return {
            "health": "Excellent",
            "message": (
                "The repository has low code-smell density "
                "and relatively simple code."
            ),
        }

    if total_smells <= 10 and average_complexity <= 10:
        return {
            "health": "Good",
            "message": (
                "The repository is generally healthy, "
                "but some areas could be improved."
            ),
        }

    if total_smells <= 30 and average_complexity <= 15:
        return {
            "health": "Needs Improvement",
            "message": (
                "Several code-quality issues were detected. "
                "Consider refactoring complex or problematic areas."
            ),
        }

    return {
        "health": "Poor",
        "message": (
            "The repository contains a significant number of "
            "code-quality issues and complex code."
        ),
    }


def analyze_repository(repository_path: Path) -> dict[str, Any]:
    """
    Main repository analysis orchestrator.

    This function:
    1. Scans the repository.
    2. Analyzes each supported source file.
    3. Runs code-smell detection.
    4. Runs complexity analysis.
    5. Combines all results.
    """

    if not repository_path.exists():
        raise FileNotFoundError(
            f"Repository path does not exist: {repository_path}"
        )

    if not repository_path.is_dir():
        raise ValueError(
            f"Repository path is not a directory: {repository_path}"
        )

    # ---------------------------------------------------------
    # 1. Scan repository
    # ---------------------------------------------------------

    source_files = scan_repository(repository_path)

    # ---------------------------------------------------------
    # 2. Initialize aggregated results
    # ---------------------------------------------------------

    total_loc = 0
    total_smells = 0
    files_with_smells = set()

    total_complexity = 0
    complexity_count = 0
    max_complexity = 0

    functions_analyzed = 0
    classes_analyzed = 0

    all_smells = []
    all_complexity = []

    # ---------------------------------------------------------
    # 3. Analyze every source file
    # ---------------------------------------------------------

    for file_path in source_files:

        try:
            relative_path = file_path.relative_to(repository_path)
        except ValueError:
            relative_path = file_path

        # ---------------------------------------------
        # Basic file metrics
        # ---------------------------------------------

        file_metrics = analyze_file_metrics(file_path)

        total_loc += file_metrics.get("loc", 0)

        # ---------------------------------------------
        # Code smells
        # ---------------------------------------------

        smells = analyze_code_smells(
            file_path=file_path,
            file_metrics=file_metrics,
        )

        for smell in smells:
            smell["file"] = str(relative_path)

        all_smells.extend(smells)

        if smells:
            files_with_smells.add(str(relative_path))

        total_smells += len(smells)

        # ---------------------------------------------
        # Complexity
        # ---------------------------------------------

        complexity_result = analyze_complexity(file_path)

        complexity_items = complexity_result.get(
            "complexity",
            [],
        )

        for item in complexity_items:
            item["file"] = str(relative_path)

        all_complexity.extend(complexity_items)

        # ---------------------------------------------
        # Aggregate complexity
        # ---------------------------------------------

        for item in complexity_items:

            complexity = item.get(
                "cyclomaticComplexity",
                0,
            )

            if isinstance(complexity, (int, float)):

                total_complexity += complexity
                complexity_count += 1

                max_complexity = max(
                    max_complexity,
                    complexity,
                )

        # ---------------------------------------------
        # Functions and classes
        # ---------------------------------------------

        functions_analyzed += complexity_result.get(
            "functionsAnalyzed",
            0,
        )

        classes_analyzed += complexity_result.get(
            "classesAnalyzed",
            0,
        )

    # ---------------------------------------------------------
    # 4. Calculate average complexity
    # ---------------------------------------------------------

    if complexity_count > 0:
        average_complexity = round(
            total_complexity / complexity_count,
            2,
        )
    else:
        average_complexity = 0

    # ---------------------------------------------------------
    # 5. Generate summary
    # ---------------------------------------------------------

    summary = calculate_summary(
        total_files=len(source_files),
        total_smells=total_smells,
        average_complexity=average_complexity,
    )

    # ---------------------------------------------------------
    # 6. Build final result
    # ---------------------------------------------------------

    return {
        "metrics": {
            "totalFiles": len(source_files),
            "loc": total_loc,
            "totalSmells": total_smells,
            "avgComplexity": average_complexity,
            "maxComplexity": max_complexity,
            "filesWithSmells": len(files_with_smells),
            "functionsAnalyzed": functions_analyzed,
            "classesAnalyzed": classes_analyzed,
        },

        "summary": summary,

        "smells": all_smells,

        "complexity": all_complexity,
    }
