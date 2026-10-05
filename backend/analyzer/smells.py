from pathlib import Path
import ast
import re


# ---------------------------------------------------------
# Thresholds
# ---------------------------------------------------------

LONG_FUNCTION_LINES = 50
LONG_FILE_LINES = 300
TOO_MANY_PARAMETERS = 5
HIGH_COMPLEXITY = 10
DEEP_NESTING = 4


# ---------------------------------------------------------
# File reading
# ---------------------------------------------------------

def read_file(file_path: Path) -> str:
    """
    Safely read a source file.
    """

    try:
        return file_path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return ""


# ---------------------------------------------------------
# Severity
# ---------------------------------------------------------

def get_severity(value: int, warning: int, critical: int) -> str:
    """
    Convert a numeric metric into a severity level.
    """

    if value >= critical:
        return "High"

    if value >= warning:
        return "Medium"

    return "Low"


# ---------------------------------------------------------
# Python AST helpers
# ---------------------------------------------------------

def get_python_tree(source_code: str):
    """
    Parse Python source code.

    Returns None if the source cannot be parsed.
    """

    try:
        return ast.parse(source_code)
    except SyntaxError:
        return None


def get_function_end_line(node: ast.AST) -> int:
    """
    Get the ending line of a function.
    """

    end_line = getattr(node, "end_lineno", None)

    if end_line is not None:
        return end_line

    # Fallback for older Python versions.
    lines = [
        getattr(child, "lineno", 0)
        for child in ast.walk(node)
        if hasattr(child, "lineno")
    ]

    return max(lines, default=getattr(node, "lineno", 1))


def calculate_function_lines(node: ast.AST) -> int:
    """
    Calculate the number of lines occupied by a function.
    """

    start = getattr(node, "lineno", 1)
    end = get_function_end_line(node)

    return max(1, end - start + 1)


# ---------------------------------------------------------
# Deep nesting
# ---------------------------------------------------------

def calculate_python_nesting(node: ast.AST) -> int:
    """
    Calculate the maximum nesting depth inside a Python node.

    Control structures that increase nesting:

    - if
    - for
    - while
    - try
    - with
    """

    nesting_nodes = (
        ast.If,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.Try,
        ast.With,
        ast.AsyncWith,
    )

    maximum_depth = 0

    def visit(current_node, depth):
        nonlocal maximum_depth

        if isinstance(current_node, nesting_nodes):
            depth += 1
            maximum_depth = max(
                maximum_depth,
                depth,
            )

        for child in ast.iter_child_nodes(current_node):
            visit(child, depth)

    visit(node, 0)

    return maximum_depth


# ---------------------------------------------------------
# Cyclomatic complexity
# ---------------------------------------------------------

def calculate_python_complexity(node: ast.AST) -> int:
    """
    Calculate approximate cyclomatic complexity
    for a Python function.
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
            # a and b and c creates additional paths
            complexity += len(child.values) - 1

        elif isinstance(child, ast.Assert):
            complexity += 1

    return complexity


# ---------------------------------------------------------
# Python function smells
# ---------------------------------------------------------

def detect_python_function_smells(
    file_path: Path,
    source_code: str,
) -> list[dict]:

    smells = []

    tree = get_python_tree(source_code)

    if tree is None:
        return smells

    for node in ast.walk(tree):

        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        function_name = node.name
        line_number = getattr(node, "lineno", 1)

        # ---------------------------------------------
        # Long function
        # ---------------------------------------------

        function_lines = calculate_function_lines(node)

        if function_lines > LONG_FUNCTION_LINES:

            severity = get_severity(
                function_lines,
                LONG_FUNCTION_LINES,
                LONG_FUNCTION_LINES * 2,
            )

            smells.append(
                {
                    "type": "Long Function",
                    "severity": severity,
                    "line": line_number,
                    "metric": function_lines,
                    "message": (
                        f"Function '{function_name}' "
                        f"contains {function_lines} lines."
                    ),
                }
            )

        # ---------------------------------------------
        # Too many parameters
        # ---------------------------------------------

        parameters = node.args

        parameter_count = (
            len(parameters.posonlyargs)
            + len(parameters.args)
            + len(parameters.kwonlyargs)
        )

        if parameters.vararg:
            parameter_count += 1

        if parameters.kwarg:
            parameter_count += 1

        if parameter_count > TOO_MANY_PARAMETERS:

            severity = get_severity(
                parameter_count,
                TOO_MANY_PARAMETERS,
                TOO_MANY_PARAMETERS + 3,
            )

            smells.append(
                {
                    "type": "Too Many Parameters",
                    "severity": severity,
                    "line": line_number,
                    "metric": parameter_count,
                    "message": (
                        f"Function '{function_name}' "
                        f"has {parameter_count} parameters."
                    ),
                }
            )

        # ---------------------------------------------
        # High complexity
        # ---------------------------------------------

        complexity = calculate_python_complexity(node)

        if complexity > HIGH_COMPLEXITY:

            severity = get_severity(
                complexity,
                HIGH_COMPLEXITY,
                HIGH_COMPLEXITY * 2,
            )

            smells.append(
                {
                    "type": "High Complexity",
                    "severity": severity,
                    "line": line_number,
                    "metric": complexity,
                    "message": (
                        f"Function '{function_name}' "
                        f"has cyclomatic complexity "
                        f"of {complexity}."
                    ),
                }
            )

        # ---------------------------------------------
        # Deep nesting
        # ---------------------------------------------

        nesting = calculate_python_nesting(node)

        if nesting > DEEP_NESTING:

            severity = get_severity(
                nesting,
                DEEP_NESTING,
                DEEP_NESTING + 2,
            )

            smells.append(
                {
                    "type": "Deep Nesting",
                    "severity": severity,
                    "line": line_number,
                    "metric": nesting,
                    "message": (
                        f"Function '{function_name}' "
                        f"has nesting depth of {nesting}."
                    ),
                }
            )

    return smells


# ---------------------------------------------------------
# Long file
# ---------------------------------------------------------

def detect_long_file(
    file_path: Path,
    source_code: str,
) -> list[dict]:

    loc = sum(
        1
        for line in source_code.splitlines()
        if line.strip()
    )

    if loc <= LONG_FILE_LINES:
        return []

    severity = get_severity(
        loc,
        LONG_FILE_LINES,
        LONG_FILE_LINES * 2,
    )

    return [
        {
            "type": "Long File",
            "severity": severity,
            "line": 1,
            "metric": loc,
            "message": (
                f"File contains {loc} lines of code."
            ),
        }
    ]


# ---------------------------------------------------------
# TODO / FIXME
# ---------------------------------------------------------

def detect_todos(
    file_path: Path,
    source_code: str,
) -> list[dict]:

    smells = []

    pattern = re.compile(
        r"\b(TODO|FIXME)\b",
        re.IGNORECASE,
    )

    for line_number, line in enumerate(
        source_code.splitlines(),
        start=1,
    ):

        match = pattern.search(line)

        if not match:
            continue

        keyword = match.group(1).upper()

        smells.append(
            {
                "type": "TODO/FIXME",
                "severity": "Low",
                "line": line_number,
                "metric": keyword,
                "message": (
                    f"{keyword} comment found."
                ),
            }
        )

    return smells


# ---------------------------------------------------------
# JavaScript / TypeScript smells
# ---------------------------------------------------------

def detect_javascript_smells(
    file_path: Path,
    source_code: str,
) -> list[dict]:

    smells = []

    lines = source_code.splitlines()

    # ---------------------------------------------
    # Long functions - heuristic
    # ---------------------------------------------

    function_pattern = re.compile(
        r"""
        (?:
            function\s+(\w+)
            |
            (?:const|let|var)\s+(\w+)\s*=\s*
            (?:async\s*)?(?:\([^)]*\)|\w+)\s*=>
        )
        """,
        re.VERBOSE,
    )

    for match in function_pattern.finditer(source_code):

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
            remaining[opening:],
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

        function_lines = len(
            function_source.splitlines()
        )

        if function_lines > LONG_FUNCTION_LINES:

            smells.append(
                {
                    "type": "Long Function",
                    "severity": get_severity(
                        function_lines,
                        LONG_FUNCTION_LINES,
                        LONG_FUNCTION_LINES * 2,
                    ),
                    "line": line_number,
                    "metric": function_lines,
                    "message": (
                        f"Function '{function_name}' "
                        f"contains {function_lines} lines."
                    ),
                }
            )

    # ---------------------------------------------
    # Too many parameters
    # ---------------------------------------------

    parameter_pattern = re.compile(
        r"(?:function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?)\s*\(([^)]*)\)"
    )

    for match in parameter_pattern.finditer(
        source_code
    ):

        parameters = match.group(1).strip()

        if not parameters:
            continue

        parameter_count = len(
            [
                parameter
                for parameter in parameters.split(",")
                if parameter.strip()
            ]
        )

        if parameter_count <= TOO_MANY_PARAMETERS:
            continue

        line_number = (
            source_code[:match.start()].count("\n")
            + 1
        )

        smells.append(
            {
                "type": "Too Many Parameters",
                "severity": get_severity(
                    parameter_count,
                    TOO_MANY_PARAMETERS,
                    TOO_MANY_PARAMETERS + 3,
                ),
                "line": line_number,
                "metric": parameter_count,
                "message": (
                    f"Function has {parameter_count} "
                    f"parameters."
                ),
            }
        )

    return smells


# ---------------------------------------------------------
# Main smell analyzer
# ---------------------------------------------------------

def analyze_code_smells(
    file_path: Path,
    file_metrics: dict | None = None,
) -> list[dict]:
    """
    Detect all supported code smells in a file.
    """

    source_code = read_file(file_path)

    if not source_code:
        return []

    smells = []

    # ---------------------------------------------
    # Long file
    # ---------------------------------------------

    smells.extend(
        detect_long_file(
            file_path,
            source_code,
        )
    )

    # ---------------------------------------------
    # TODO / FIXME
    # ---------------------------------------------

    smells.extend(
        detect_todos(
            file_path,
            source_code,
        )
    )

    # ---------------------------------------------
    # Language-specific analysis
    # ---------------------------------------------

    extension = file_path.suffix.lower()

    if extension == ".py":

        smells.extend(
            detect_python_function_smells(
                file_path,
                source_code,
            )
        )

    elif extension in {
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
    }:

        smells.extend(
            detect_javascript_smells(
                file_path,
                source_code,
            )
        )

    return smells
