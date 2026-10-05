from pathlib import Path
import ast


# File extensions supported by the analyzer.
SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
}


def read_file(file_path: Path) -> str:
    """
    Read a source file safely.

    UTF-8 is attempted first. If the file contains an unusual
    character encoding, invalid characters are replaced instead
    of crashing the entire analysis.
    """

    try:
        return file_path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return ""


def count_lines_of_code(source_code: str) -> int:
    """
    Count non-empty lines of source code.

    Blank lines are not counted as LOC.
    """

    return sum(
        1
        for line in source_code.splitlines()
        if line.strip()
    )


def count_python_functions_and_classes(
    source_code: str,
) -> tuple[int, int]:
    """
    Count functions and classes in Python source code
    using Python's AST.

    This includes:
    - normal functions
    - async functions
    - classes
    """

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return 0, 0

    functions = 0
    classes = 0

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            functions += 1

        elif isinstance(node, ast.ClassDef):
            classes += 1

    return functions, classes


def count_javascript_functions_and_classes(
    source_code: str,
) -> tuple[int, int]:
    """
    Estimate functions and classes in JavaScript/TypeScript.

    This is intentionally a lightweight parser for now.
    A proper JavaScript/TypeScript AST parser can be added later.
    """

    import re

    # Function declarations:
    #
    # function hello() {}
    # async function hello() {}
    #
    function_declarations = len(
        re.findall(
            r"\b(?:async\s+)?function\s+\w+\s*\(",
            source_code,
        )
    )

    # Arrow functions:
    #
    # const hello = () => {}
    # const hello = async () => {}
    #
    arrow_functions = len(
        re.findall(
            r"(?:=\s*|\()\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*=>",
            source_code,
        )
    )

    functions = function_declarations + arrow_functions

    # Classes:
    #
    # class User {}
    # class User extends Person {}
    #
    classes = len(
        re.findall(
            r"\bclass\s+\w+",
            source_code,
        )
    )

    return functions, classes


def count_functions_and_classes(
    file_path: Path,
    source_code: str,
) -> tuple[int, int]:
    """
    Count functions and classes based on file type.
    """

    extension = file_path.suffix.lower()

    if extension == ".py":
        return count_python_functions_and_classes(
            source_code
        )

    if extension in {
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
    }:
        return count_javascript_functions_and_classes(
            source_code
        )

    return 0, 0


def analyze_file_metrics(file_path: Path) -> dict:
    """
    Calculate metrics for a single source file.

    Returns:
        {
            "file": "...",
            "extension": ".py",
            "loc": 100,
            "functions": 5,
            "classes": 2
        }
    """

    if not file_path.exists():
        return {
            "file": str(file_path),
            "extension": file_path.suffix.lower(),
            "loc": 0,
            "functions": 0,
            "classes": 0,
        }

    source_code = read_file(file_path)

    loc = count_lines_of_code(source_code)

    functions, classes = count_functions_and_classes(
        file_path,
        source_code,
    )

    return {
        "file": str(file_path),
        "extension": file_path.suffix.lower(),
        "loc": loc,
        "functions": functions,
        "classes": classes,
    }


def calculate_repository_metrics(
    source_files: list[Path],
) -> dict:
    """
    Calculate aggregated metrics for the entire repository.

    Args:
        source_files:
            List of supported source files.

    Returns:
        {
            "totalFiles": 10,
            "loc": 1500,
            "functions": 50,
            "classes": 12
        }
    """

    total_files = 0
    total_loc = 0
    total_functions = 0
    total_classes = 0

    for file_path in source_files:

        metrics = analyze_file_metrics(file_path)

        total_files += 1
        total_loc += metrics["loc"]
        total_functions += metrics["functions"]
        total_classes += metrics["classes"]

    return {
        "totalFiles": total_files,
        "loc": total_loc,
        "functions": total_functions,
        "classes": total_classes,
    }
