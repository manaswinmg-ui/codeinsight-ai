import json
import random
import re

from app.ai.prompt_builder import PromptPackage
from app.ai.providers.base import AIClient
from app.ai.providers.openai_client import OpenAIClient
from app.config import settings


class MockAIClient(AIClient):
    """Code-aware mock AI client that generates contextual findings based on patterns."""

    # ── Pattern detectors ────────────────────────────────────────────────────
    # Each returns a finding dict (or None) given the source lines.

    @staticmethod
    def _detect_eval_exec(lines: list[str]) -> dict | None:
        """Detect use of eval() or exec()."""
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if re.search(r"\b(eval|exec)\s*\(", stripped):
                return {
                    "title": "Use of eval() / exec() Detected",
                    "description": (
                        "The code uses eval() or exec() which can execute arbitrary code. "
                        "This is a critical security risk, especially when the input comes "
                        "from an untrusted source."
                    ),
                    "severity": "critical",
                    "category": "SECURITY",
                    "confidence": random.randint(88, 97),
                    "impact": (
                        "An attacker could inject arbitrary code through the eval/exec call, "
                        "leading to remote code execution, data exfiltration, or full system compromise."
                    ),
                    "why_it_matters": (
                        "eval() and exec() violate the Principle of Least Privilege by granting the "
                        "input string the same permissions as the running process. They are consistently "
                        "listed in OWASP Top 10 under Injection flaws."
                    ),
                    "suggested_fix": "Replace eval/exec with a safe alternative such as ast.literal_eval() for data parsing, or a dedicated expression parser.",
                    "improved_code": (
                        "import ast\n"
                        "# Instead of eval(user_input):\n"
                        "result = ast.literal_eval(user_input)"
                    ),
                    "estimated_fix_time": "20 minutes",
                    "test_case_hint": "Test with malicious input like '__import__(\"os\").system(\"rm -rf /\")' to confirm it is rejected.",
                    "references": [
                        "https://owasp.org/www-project-top-ten/",
                        "https://docs.python.org/3/library/ast.html#ast.literal_eval",
                    ],
                    "line_start": i + 1,
                    "line_end": i + 1,
                }
        return None

    @staticmethod
    def _detect_sql_injection(lines: list[str]) -> dict | None:
        """Detect string-concatenated SQL patterns."""
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            # Detect patterns like: query = "SELECT ... " + variable  or f"SELECT ... {var}"
            if re.search(
                r"""(?:SELECT|INSERT|UPDATE|DELETE|DROP)\s+.*(?:\+\s*\w+|f['"].*\{)""",
                stripped,
                re.IGNORECASE,
            ):
                return {
                    "title": "Potential SQL Injection Vector",
                    "description": (
                        "A SQL query appears to be constructed via string concatenation or "
                        "f-string interpolation. This opens the door to SQL injection attacks."
                    ),
                    "severity": "critical",
                    "category": "SECURITY",
                    "confidence": random.randint(82, 95),
                    "impact": (
                        "Attackers can manipulate queries to bypass authentication, extract sensitive "
                        "data, or destroy database tables."
                    ),
                    "why_it_matters": (
                        "SQL injection has been the #1 web vulnerability for over a decade. "
                        "Parameterized queries eliminate this entire class of attack by separating "
                        "code from data at the database driver level."
                    ),
                    "suggested_fix": "Use parameterized queries or an ORM instead of string interpolation.",
                    "improved_code": (
                        "# Instead of: query = f\"SELECT * FROM users WHERE id = {user_id}\"\n"
                        "cursor.execute(\"SELECT * FROM users WHERE id = %s\", (user_id,))"
                    ),
                    "estimated_fix_time": "15 minutes",
                    "test_case_hint": "Test with input containing SQL metacharacters: ' OR 1=1 --",
                    "references": [
                        "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
                    ],
                    "line_start": i + 1,
                    "line_end": i + 1,
                }
        return None

    @staticmethod
    def _detect_missing_error_handling(lines: list[str]) -> dict | None:
        """Detect functions that perform I/O-like operations without try/except."""
        has_try = any("try:" in line for line in lines)
        io_patterns = [
            r"\bopen\s*\(",
            r"\brequests\.\w+\s*\(",
            r"\bfetch\s*\(",
            r"\burlopen\s*\(",
            r"\.read\s*\(",
            r"\.write\s*\(",
            r"\.connect\s*\(",
        ]
        io_line = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for pat in io_patterns:
                if re.search(pat, stripped):
                    io_line = i + 1
                    break
            if io_line:
                break

        if io_line and not has_try:
            return {
                "title": "Missing Error Handling for I/O Operations",
                "description": (
                    "The code performs file or network I/O without any try/except block. "
                    "Unhandled exceptions from I/O operations will crash the process."
                ),
                "severity": "high",
                "category": "RELIABILITY",
                "confidence": random.randint(78, 92),
                "impact": (
                    "Network timeouts, file-not-found errors, or permission issues will "
                    "propagate as unhandled exceptions, potentially crashing the service."
                ),
                "why_it_matters": (
                    "Defensive programming requires anticipating failure at trust boundaries. "
                    "I/O operations are inherently unreliable and must be wrapped in error "
                    "handling with appropriate fallback or retry logic."
                ),
                "suggested_fix": "Wrap I/O operations in try/except blocks with specific exception types.",
                "improved_code": (
                    "try:\n"
                    "    with open(filepath, 'r') as f:\n"
                    "        data = f.read()\n"
                    "except FileNotFoundError:\n"
                    "    logger.error(f'File not found: {filepath}')\n"
                    "    data = None\n"
                    "except PermissionError:\n"
                    "    logger.error(f'Permission denied: {filepath}')\n"
                    "    data = None"
                ),
                "estimated_fix_time": "10 minutes",
                "test_case_hint": "Test with a non-existent file path and verify graceful failure.",
                "references": [
                    "https://docs.python.org/3/tutorial/errors.html",
                ],
                "line_start": io_line,
                "line_end": io_line,
            }
        return None

    @staticmethod
    def _detect_no_docstrings(lines: list[str]) -> dict | None:
        """Detect function definitions without docstrings."""
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("def ") or stripped.startswith("async def "):
                # Check if next non-empty line is a docstring
                has_docstring = False
                for j in range(i + 1, min(i + 4, len(lines))):
                    next_stripped = lines[j].strip()
                    if not next_stripped:
                        continue
                    if next_stripped.startswith('"""') or next_stripped.startswith("'''") or next_stripped.startswith('"') or next_stripped.startswith("'"):
                        has_docstring = True
                    break
                if not has_docstring:
                    return {
                        "title": "Function Missing Docstring",
                        "description": (
                            f"The function defined at line {i + 1} does not have a docstring. "
                            "Functions should document their purpose, parameters, and return values."
                        ),
                        "severity": "low",
                        "category": "DOCUMENTATION",
                        "confidence": random.randint(85, 98),
                        "impact": (
                            "Missing documentation increases onboarding time for new developers "
                            "and makes maintenance more error-prone."
                        ),
                        "why_it_matters": (
                            "PEP 257 mandates docstrings for all public modules, functions, classes, "
                            "and methods. Good documentation is the cheapest form of knowledge transfer."
                        ),
                        "suggested_fix": "Add a docstring describing the function's purpose, parameters, and return type.",
                        "improved_code": (
                            "def my_function(param: str) -> bool:\n"
                            '    """Check whether param meets the required criteria.\n\n'
                            "    Args:\n"
                            "        param: The input string to validate.\n\n"
                            "    Returns:\n"
                            "        True if valid, False otherwise.\n"
                            '    """\n'
                            "    ..."
                        ),
                        "estimated_fix_time": "5 minutes",
                        "test_case_hint": "Run a docstring linter (e.g., pydocstyle) to verify compliance.",
                        "references": [
                            "https://peps.python.org/pep-0257/",
                        ],
                        "line_start": i + 1,
                        "line_end": i + 1,
                    }
        return None

    @staticmethod
    def _detect_long_functions(lines: list[str]) -> dict | None:
        """Detect functions longer than 30 lines."""
        func_start = None
        func_indent = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("def ") or stripped.startswith("async def "):
                if func_start is not None:
                    length = i - func_start
                    if length > 30:
                        return {
                            "title": "Function Too Long — Consider Refactoring",
                            "description": (
                                f"The function starting at line {func_start + 1} spans {length} lines. "
                                "Long functions are harder to understand, test, and maintain."
                            ),
                            "severity": "medium",
                            "category": "MAINTAINABILITY",
                            "confidence": random.randint(75, 90),
                            "impact": (
                                "Long functions increase cognitive load and make it difficult to "
                                "isolate bugs or write targeted unit tests."
                            ),
                            "why_it_matters": (
                                "The Single Responsibility Principle suggests each function should do "
                                "one thing well. Functions exceeding ~30 lines often indicate multiple "
                                "responsibilities that should be extracted."
                            ),
                            "suggested_fix": "Extract logical sub-tasks into helper functions with descriptive names.",
                            "improved_code": None,
                            "estimated_fix_time": "30 minutes",
                            "test_case_hint": "After refactoring, each extracted function should be independently testable.",
                            "references": [
                                "Clean Code by Robert C. Martin — Chapter 3: Functions",
                            ],
                            "line_start": func_start + 1,
                            "line_end": i,
                        }
                func_start = i
                func_indent = len(line) - len(line.lstrip())

        # Check last function
        if func_start is not None:
            length = len(lines) - func_start
            if length > 30:
                return {
                    "title": "Function Too Long — Consider Refactoring",
                    "description": (
                        f"The function starting at line {func_start + 1} spans {length} lines."
                    ),
                    "severity": "medium",
                    "category": "MAINTAINABILITY",
                    "confidence": random.randint(75, 90),
                    "impact": "Long functions increase cognitive load and reduce testability.",
                    "why_it_matters": (
                        "The Single Responsibility Principle suggests extracting sub-tasks "
                        "into smaller, focused helper functions."
                    ),
                    "suggested_fix": "Extract logical sub-tasks into helper functions.",
                    "improved_code": None,
                    "estimated_fix_time": "30 minutes",
                    "test_case_hint": "Each extracted function should be independently testable.",
                    "references": ["Clean Code by Robert C. Martin — Chapter 3: Functions"],
                    "line_start": func_start + 1,
                    "line_end": len(lines),
                }
        return None

    @staticmethod
    def _detect_hardcoded_secrets(lines: list[str]) -> dict | None:
        """Detect hardcoded passwords, API keys, or secrets."""
        secret_patterns = [
            r"""(?:password|passwd|pwd|api_key|apikey|secret|token)\s*=\s*['"][^'"]{4,}['"]""",
        ]
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for pat in secret_patterns:
                if re.search(pat, stripped, re.IGNORECASE):
                    return {
                        "title": "Hardcoded Secret or Credential Detected",
                        "description": (
                            "A password, API key, or secret value appears to be hardcoded. "
                            "Secrets in source code are exposed in version control history."
                        ),
                        "severity": "high",
                        "category": "SECURITY",
                        "confidence": random.randint(80, 95),
                        "impact": (
                            "Leaked credentials can be used for unauthorized access, "
                            "data breaches, or privilege escalation."
                        ),
                        "why_it_matters": (
                            "The CWE-798 (Use of Hard-coded Credentials) is a well-known "
                            "vulnerability. Secrets should be loaded from environment variables "
                            "or a secrets manager."
                        ),
                        "suggested_fix": "Move secrets to environment variables or a vault and load them at runtime.",
                        "improved_code": (
                            "import os\n"
                            "API_KEY = os.environ.get('API_KEY')\n"
                            "if not API_KEY:\n"
                            "    raise RuntimeError('API_KEY environment variable is required')"
                        ),
                        "estimated_fix_time": "10 minutes",
                        "test_case_hint": "Search for hardcoded strings with tools like trufflehog or git-secrets.",
                        "references": [
                            "https://cwe.mitre.org/data/definitions/798.html",
                        ],
                        "line_start": i + 1,
                        "line_end": i + 1,
                    }
        return None

    @staticmethod
    def _detect_bare_except(lines: list[str]) -> dict | None:
        """Detect bare except clauses."""
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == "except:" or stripped.startswith("except:"):
                return {
                    "title": "Bare except Clause — Catches All Exceptions",
                    "description": (
                        "A bare 'except:' clause catches all exceptions including "
                        "SystemExit, KeyboardInterrupt, and GeneratorExit, which "
                        "can mask critical errors and make debugging very difficult."
                    ),
                    "severity": "medium",
                    "category": "BEST_PRACTICE",
                    "confidence": random.randint(90, 99),
                    "impact": (
                        "Silently swallowing unexpected exceptions hides bugs and "
                        "can lead to data corruption or inconsistent state."
                    ),
                    "why_it_matters": (
                        "PEP 8 recommends catching specific exceptions. Bare excepts "
                        "violate the Zen of Python: 'Errors should never pass silently.'"
                    ),
                    "suggested_fix": "Catch specific exception types instead of using bare except.",
                    "improved_code": (
                        "try:\n"
                        "    risky_operation()\n"
                        "except (ValueError, TypeError) as e:\n"
                        "    logger.error(f'Operation failed: {e}')\n"
                        "    raise"
                    ),
                    "estimated_fix_time": "5 minutes",
                    "test_case_hint": "Verify that KeyboardInterrupt still propagates after fixing.",
                    "references": [
                        "https://peps.python.org/pep-0008/#programming-recommendations",
                    ],
                    "line_start": i + 1,
                    "line_end": i + 1,
                }
        return None

    @staticmethod
    def _detect_missing_input_validation(lines: list[str]) -> dict | None:
        """Detect functions that accept parameters without any validation."""
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (stripped.startswith("def ") or stripped.startswith("async def ")) and "(" in stripped:
                # Check for parameters (not just self/cls)
                params_match = re.search(r"\((.*?)\)", stripped)
                if params_match:
                    params = params_match.group(1)
                    param_names = [
                        p.strip().split(":")[0].split("=")[0].strip()
                        for p in params.split(",")
                        if p.strip() and p.strip() not in ("self", "cls")
                    ]
                    if len(param_names) >= 2:
                        # Check next ~10 lines for any validation pattern
                        has_validation = False
                        for j in range(i + 1, min(i + 12, len(lines))):
                            check = lines[j].strip()
                            if any(kw in check for kw in ["if not ", "isinstance(", "raise ", "assert ", "validate", ".strip()"]):
                                has_validation = True
                                break
                        if not has_validation:
                            return {
                                "title": "Missing Input Validation",
                                "description": (
                                    f"The function at line {i + 1} accepts multiple parameters "
                                    "but performs no visible input validation. Unvalidated input "
                                    "can cause crashes or security issues downstream."
                                ),
                                "severity": "high",
                                "category": "SECURITY",
                                "confidence": random.randint(72, 88),
                                "impact": (
                                    "Unvalidated input can lead to runtime exceptions, "
                                    "data corruption, or exploitation of downstream systems."
                                ),
                                "why_it_matters": (
                                    "Defense-in-depth requires validating all inputs at trust boundaries. "
                                    "This is a fundamental principle of secure software development."
                                ),
                                "suggested_fix": "Add input validation at the function entry point using guards or a validation schema.",
                                "improved_code": (
                                    "def process(data: str, count: int) -> str:\n"
                                    "    if not data or not isinstance(data, str):\n"
                                    "        raise ValueError('data must be a non-empty string')\n"
                                    "    if count < 0:\n"
                                    "        raise ValueError('count must be non-negative')\n"
                                    "    ..."
                                ),
                                "estimated_fix_time": "15 minutes",
                                "test_case_hint": "Test with None, empty string, wrong types, and boundary values.",
                                "references": [
                                    "https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html",
                                ],
                                "line_start": i + 1,
                                "line_end": i + 1,
                            }
        return None

    async def review(self, prompt_package: PromptPackage) -> str:
        """Generate code-aware mock findings by analyzing the submitted source code."""
        # Extract source code from the user prompt
        code_block = ""
        in_code = False
        for line in prompt_package.user_prompt.split("\n"):
            if line.strip() == "-----":
                in_code = not in_code
                continue
            if in_code:
                code_block += line + "\n"

        lines = code_block.split("\n") if code_block.strip() else []
        line_count = len([l for l in lines if l.strip()])

        # Run all detectors
        detectors = [
            self._detect_eval_exec,
            self._detect_sql_injection,
            self._detect_hardcoded_secrets,
            self._detect_missing_error_handling,
            self._detect_bare_except,
            self._detect_no_docstrings,
            self._detect_missing_input_validation,
            self._detect_long_functions,
        ]

        findings = []
        for detector in detectors:
            result = detector(lines)
            if result is not None:
                findings.append(result)

        # If no patterns detected, return a positive review with one info finding
        if not findings:
            findings.append({
                "title": "Clean Code — No Major Issues Detected",
                "description": (
                    "The submitted code follows good practices. No bugs, security "
                    "vulnerabilities, or significant maintainability issues were detected."
                ),
                "severity": "info",
                "category": "BEST_PRACTICE",
                "confidence": random.randint(80, 95),
                "impact": "No negative impact — the code is well-structured.",
                "why_it_matters": (
                    "Writing clean code from the start reduces technical debt and "
                    "lowers the long-term cost of maintenance."
                ),
                "suggested_fix": None,
                "improved_code": None,
                "estimated_fix_time": None,
                "test_case_hint": "Continue writing comprehensive tests to maintain this quality.",
                "references": [],
                "line_start": None,
                "line_end": None,
            })

        # Compute quality score based on findings
        deductions = {"critical": 20, "high": 15, "medium": 10, "low": 5, "info": 2}
        score = 100
        for f in findings:
            score -= deductions.get(f["severity"], 5)
        score = max(0, min(100, score))

        # Adjust score slightly based on code size (larger code = slightly lower baseline)
        if line_count > 50:
            score = max(0, score - 3)
        if line_count > 100:
            score = max(0, score - 5)

        # Build summary
        severity_counts: dict[str, int] = {}
        for f in findings:
            sev = f["severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        summary_parts = []
        for sev in ["critical", "high", "medium", "low", "info"]:
            count = severity_counts.get(sev, 0)
            if count > 0:
                summary_parts.append(f"{count} {sev}")

        finding_summary = ", ".join(summary_parts) if summary_parts else "no issues"
        summary = (
            f"Mock analysis of {line_count} lines of code detected {len(findings)} "
            f"finding(s) ({finding_summary}). "
            f"Overall quality score: {score}/100."
        )

        review_data = {
            "summary": summary,
            "quality_score": score,
            "findings": findings,
        }
        return json.dumps(review_data)


def get_ai_client() -> AIClient:
    """Resolve and return the configured AI Client instance based on settings."""
    # Fallback to Mock in development/testing if no API key is set
    if settings.ENV != "production" and not settings.OPENAI_API_KEY:
        return MockAIClient()

    provider = settings.AI_PROVIDER.lower().strip()
    if provider == "openai":
        return OpenAIClient()
    elif provider == "mock":
        return MockAIClient()
    else:
        raise ValueError(f"Unsupported AI Provider: {settings.AI_PROVIDER}")
