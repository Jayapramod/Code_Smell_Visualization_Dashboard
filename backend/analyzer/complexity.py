from pathlib import Path
import ast
import re


# ---------------------------------------------------------
# File reading
# ---------------------------------------------------------

def read_file(file_path: Path) -> str:
    """
    Safely read source code from a file.
    """

    try:
        return file_path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return ""


# ---------------------------------------------------------
# Python cyclomatic complexity
# ---------------------------------------------------------

def calculate_python_cyclomatic_complexity(
    node: ast.AST,
) -> int:
    """
    Calculate cyclomatic complexity for a Python function.

    Base complexity = 1.

    Additional paths are added for:
    - if
    - for
    - while
    - except
    - with
    - boolean conditions
    - ternary expressions
    """

    complexity = 1

    for child in ast.walk(node):

        if isinstance(
            child,
            (
                ast.If,
                ast.For,
                ast.AsyncFor,
                ast.While,
                ast.ExceptHandler,
                ast.With,
                ast.AsyncWith,
                ast.IfExp,
            ),
        ):
            complexity += 1

        elif isinstance(child, ast.BoolOp):

            complexity += (
                len(child.values) - 1
            )

    return complexity


# ---------------------------------------------------------
# Python loop analysis
# ---------------------------------------------------------

def calculate_python_loop_depth(
    node: ast.AST,
) -> int:
    """
    Calculate the maximum nested loop depth.
    """

    loop_nodes = (
        ast.For,
        ast.AsyncFor,
        ast.While,
    )

    maximum_depth = 0

    def visit(current_node, depth):

        nonlocal maximum_depth

        if isinstance(
            current_node,
            loop_nodes,
        ):
            depth += 1

            maximum_depth = max(
                maximum_depth,
                depth,
            )

        for child in ast.iter_child_nodes(
            current_node
        ):
            visit(child, depth)

    visit(node, 0)

    return maximum_depth


# ---------------------------------------------------------
# Time complexity estimation
# ---------------------------------------------------------

def estimate_time_complexity_from_loop_depth(
    loop_depth: int,
) -> str:
    """
    Estimate Big-O time complexity based on
    maximum loop nesting.

    This is an approximation, not a formal proof.
    """

    if loop_depth <= 0:
        return "O(1)"

    if loop_depth == 1:
        return "O(n)"

    if loop_depth == 2:
        return "O(n²)"

    if loop_depth == 3:
        return "O(n³)"

    return f"O(n^{loop_depth})"


def estimate_python_time_complexity(
    node: ast.AST,
) -> str:
    """
    Estimate the time complexity of a Python function.
    """

    loop_depth = calculate_python_loop_depth(node)

    return estimate_time_complexity_from_loop_depth(
        loop_depth
    )


# ---------------------------------------------------------
# Python function analysis
# ---------------------------------------------------------

def analyze_python_functions(
    source_code: str,
) -> dict:

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return {
            "complexity": [],
            "functionsAnalyzed": 0,
            "classesAnalyzed": 0,
        }

    complexity_results = []

    functions_analyzed = 0
    classes_analyzed = 0

    # ---------------------------------------------
    # Count classes
    # ---------------------------------------------

    for node in ast.walk(tree):

        if isinstance(node, ast.ClassDef):
            classes_analyzed += 1

    # ---------------------------------------------
    # Analyze functions
    # ---------------------------------------------

    for node in ast.walk(tree):

        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        functions_analyzed += 1

        complexity = (
            calculate_python_cyclomatic_complexity(
                node
            )
        )

        time_complexity = (
            estimate_python_time_complexity(
                node
            )
        )

        complexity_results.append(
            {
                "function": node.name,
                "line": getattr(
                    node,
                    "lineno",
                    1,
                ),
                "cyclomaticComplexity": complexity,
                "timeComplexity": time_complexity,
            }
        )

    return {
        "complexity": complexity_results,
        "functionsAnalyzed": functions_analyzed,
        "classesAnalyzed": classes_analyzed,
    }


# ---------------------------------------------------------
# JavaScript / TypeScript analysis
# ---------------------------------------------------------

def calculate_javascript_complexity(
    function_source: str,
) -> int:
    """
    Approximate cyclomatic complexity for
    JavaScript / TypeScript.
    """

    complexity = 1

    # if statements
    complexity += len(
        re.findall(
            r"\bif\s*\(",
            function_source,
        )
    )

    # loops
    complexity += len(
        re.findall(
            r"\b(?:for|while|do)\b",
            function_source,
        )
    )

    # switch cases
    complexity += len(
        re.findall(
            r"\bcase\b",
            function_source,
        )
    )

    # catch blocks
    complexity += len(
        re.findall(
            r"\bcatch\s*\(",
            function_source,
        )
    )

    # Logical conditions
    complexity += len(
        re.findall(
            r"&&|\|\|",
            function_source,
        )
    )

    # Ternary operators
    complexity += len(
        re.findall(
            r"\?",
            function_source,
        )
    )

    return complexity


def calculate_javascript_loop_depth(
    function_source: str,
) -> int:
    """
    Estimate maximum loop nesting in JavaScript/TypeScript.
    """

    loop_pattern = re.compile(
        r"\b(?:for|while|do)\b"
    )

    # Lightweight approximation.
    loop_count = len(
        loop_pattern.findall(
            function_source
        )
    )

    if loop_count == 0:
        return 0

    # Since we are not using a JavaScript AST yet,
    # use the number of loops as a conservative estimate.
    return min(loop_count, 5)


def analyze_javascript_functions(
    source_code: str,
) -> dict:

    complexity_results = []

    function_pattern = re.compile(
        r"""
        (?:
            function\s+(\w+)\s*\([^)]*\)
            |
            (?:const|let|var)\s+(\w+)
            \s*=\s*
            (?:async\s*)?
            (?:\([^)]*\)|\w+)
            \s*=>
        )
        """,
        re.VERBOSE,
    )

    functions_analyzed = 0

    for match in function_pattern.finditer(
        source_code
    ):

        function_name = (
            match.group(1)
            or match.group(2)
            or "anonymous"
        )

        line_number = (
            source_code[:match.start()].count("\n")
            + 1
        )

        remaining = source_code[match.end():]

        opening = remaining.find("{")

        if opening == -1:
            continue

        brace_count = 0
        end_position = None

        for index, character in enumerate(
            remaining[opening:]
        ):

            if character == "{":
                brace_count += 1

            elif character == "}":
                brace_count -= 1

                if brace_count == 0:
                    end_position = (
                        opening + index
                    )
                    break

        if end_position is None:
            continue

        function_source = remaining[
            opening:end_position + 1
        ]

        complexity = (
            calculate_javascript_complexity(
                function_source
            )
        )

        loop_depth = (
            calculate_javascript_loop_depth(
                function_source
            )
        )

        time_complexity = (
            estimate_time_complexity_from_loop_depth(
                loop_depth
            )
        )

        complexity_results.append(
            {
                "function": function_name,
                "line": line_number,
                "cyclomaticComplexity": complexity,
                "timeComplexity": time_complexity,
            }
        )

        functions_analyzed += 1

    # Count classes
    classes_analyzed = len(
        re.findall(
            r"\bclass\s+\w+",
            source_code,
        )
    )

    return {
        "complexity": complexity_results,
        "functionsAnalyzed": functions_analyzed,
        "classesAnalyzed": classes_analyzed,
    }


# ---------------------------------------------------------
# Main complexity analyzer
# ---------------------------------------------------------

def analyze_complexity(
    file_path: Path,
) -> dict:
    """
    Analyze complexity for a single source file.

    Returns:

    {
        "complexity": [
            {
                "function": "calculate_total",
                "line": 10,
                "cyclomaticComplexity": 4,
                "timeComplexity": "O(n)"
            }
        ],
        "functionsAnalyzed": 1,
        "classesAnalyzed": 0
    }
    """

    source_code = read_file(file_path)

    if not source_code:
        return {
            "complexity": [],
            "functionsAnalyzed": 0,
            "classesAnalyzed": 0,
        }

    extension = file_path.suffix.lower()

    # ---------------------------------------------
    # Python
    # ---------------------------------------------

    if extension == ".py":
        return analyze_python_functions(
            source_code
        )

    # ---------------------------------------------
    # JavaScript / TypeScript
    # ---------------------------------------------

    if extension in {
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
    }:
        return analyze_javascript_functions(
            source_code
        )

    # ---------------------------------------------
    # Unsupported file
    # ---------------------------------------------

    return {
        "complexity": [],
        "functionsAnalyzed": 0,
        "classesAnalyzed": 0,
    }
