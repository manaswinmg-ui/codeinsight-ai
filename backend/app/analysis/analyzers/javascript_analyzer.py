import asyncio
import json
import logging
import os
import shutil
import sys
import uuid

from app.analysis.analyzers.base import BaseAnalyzer
from app.analysis.models import StaticFinding

logger = logging.getLogger(__name__)


class JavaScriptAnalyzer(BaseAnalyzer):
    def supports(self, language: str) -> bool:
        return language.lower() in ("javascript", "typescript")

    def _get_npx_path(self) -> str:
        """Locate the npx executable in the environment."""
        npx_path = shutil.which("npx")
        if not npx_path and sys.platform == "win32":
            npx_path = shutil.which("npx.cmd")
        if not npx_path:
            npx_path = "npx"  # Fallback
        return npx_path

    async def analyze(self, code: str) -> list[StaticFinding]:
        """Run ESLint on a temporary file and parse the JSON output."""
        # Determine file extension based on code features
        extension = ".js"
        if any(
            keyword in code
            for keyword in [
                "interface ",
                "type ",
                "as ",
                ": string",
                ": number",
                ": boolean",
                ": any",
            ]
        ):
            extension = ".ts"

        npx_path = self._get_npx_path()

        # Setup directories
        backend_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        temp_dir = os.path.join(backend_dir, ".temp_analysis")

        try:
            os.makedirs(temp_dir, exist_ok=True)
        except Exception as e:
            logger.error(
                "Failed to create temp directory for JS/TS static analysis: %s", e
            )
            return []

        temp_file_path = os.path.join(temp_dir, f"temp_{uuid.uuid4().hex}{extension}")

        try:
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(code)
        except Exception as e:
            logger.error("Failed to write temp JS/TS code file: %s", e)
            return []

        findings = []
        try:
            project_root = os.path.dirname(backend_dir)
            frontend_dir = os.path.join(project_root, "frontend")
            eslintrc_path = os.path.join(frontend_dir, ".eslintrc.cjs")

            # Check if frontend eslintrc config exists
            if not os.path.exists(eslintrc_path):
                logger.warning(
                    "ESLint configuration not found at %s. Static analysis skipped.",
                    eslintrc_path,
                )
                return []

            cmd = [
                npx_path,
                "eslint",
                "--format",
                "json",
                "--no-ignore",
                "--config",
                eslintrc_path,
                temp_file_path,
            ]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=frontend_dir,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=15.0
                )
            except TimeoutError:
                logger.error("ESLint static analysis timed out.")
                try:
                    proc.kill()
                except Exception:
                    pass
                return []

            stdout_str = stdout.decode("utf-8", errors="ignore").strip()

            if not stdout_str:
                return []

            try:
                reports = json.loads(stdout_str)
            except json.JSONDecodeError:
                logger.error(
                    "Failed to parse ESLint JSON output. Output: %s", stdout_str
                )
                return []

            if not isinstance(reports, list):
                logger.error("ESLint output is not a list. Type: %s", type(reports))
                return []

            for file_report in reports:
                if not isinstance(file_report, dict):
                    continue

                messages = file_report.get("messages", [])
                for msg in messages:
                    if not isinstance(msg, dict):
                        continue

                    rule_id = msg.get("ruleId")
                    is_fatal = bool(msg.get("fatal", False))
                    message_text = str(msg.get("message", "")).strip()

                    # Determine rule code/name
                    if not rule_id:
                        rule_code = "PARSE-ERROR" if is_fatal else "UNKNOWN"
                        rule_title = "Syntax / Parsing Error"
                    else:
                        rule_code = str(rule_id)
                        rule_title = rule_code.split("/")[-1].replace("-", " ").title()

                    title = f"ESLint ({rule_code}): {rule_title}"

                    # Severity mapping
                    raw_severity = msg.get("severity", 1)
                    if is_fatal:
                        severity = "critical"
                    elif raw_severity == 2:
                        severity = "high"
                    else:
                        severity = "medium"

                    # Category mapping
                    rule_lower = rule_code.lower()
                    if is_fatal:
                        category = "BUG"
                    elif any(
                        k in rule_lower
                        for k in ["eval", "security", "xss", "csrf", "injection"]
                    ):
                        category = "SECURITY"
                    elif any(
                        k in rule_lower
                        for k in [
                            "no-undef",
                            "no-unreachable",
                            "use-isnan",
                            "rules-of-hooks",
                            "no-empty",
                            "no-constant-condition",
                        ]
                    ):
                        category = "BUG"
                    else:
                        category = "BEST_PRACTICE"

                    finding = StaticFinding(
                        title=title,
                        description=message_text,
                        severity=severity,
                        line=int(msg.get("line", 1)),
                        column=int(msg.get("column", 1)),
                        rule=rule_code,
                        tool="eslint",
                        category=category,
                        confidence=100,
                    )
                    findings.append(finding)

        except FileNotFoundError:
            logger.warning(
                "npx/eslint executable not found. JS/TS static analysis skipped."
            )
        except Exception as e:
            logger.error("Error executing ESLint static analysis: %s", e)
        finally:
            # Clean up temp file
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception as e:
                logger.warning(
                    "Failed to remove temp JS/TS file %s: %s", temp_file_path, e
                )

        return findings
