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


class PythonAnalyzer(BaseAnalyzer):
    def supports(self, language: str) -> bool:
        return language.lower() == "python"

    def _get_ruff_path(self) -> str:
        """Locate the ruff executable in the environment."""
        ruff_path = shutil.which("ruff")
        if not ruff_path:
            # Check virtual environment relative path
            # Root directory of backend is 4 levels up from this file:
            # app/analysis/analyzers/python_analyzer.py -> app/analysis/analyzers -> app/analysis -> app -> backend
            backend_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
            venv_dir = os.path.join(backend_dir, ".venv")
            
            if sys.platform == "win32":
                candidate = os.path.join(venv_dir, "Scripts", "ruff.exe")
            else:
                candidate = os.path.join(venv_dir, "bin", "ruff")
                
            if os.path.exists(candidate):
                ruff_path = candidate
            else:
                ruff_path = "ruff"  # Fallback to PATH lookup
        return ruff_path

    async def analyze(self, code: str) -> list[StaticFinding]:
        """Run Ruff on a temporary file and parse the JSON output."""
        ruff_path = self._get_ruff_path()
        
        # Setup workspace temp directory
        backend_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        temp_dir = os.path.join(backend_dir, ".temp_analysis")
        
        try:
            os.makedirs(temp_dir, exist_ok=True)
        except Exception as e:
            logger.error("Failed to create temp directory for static analysis: %s", e)
            return []

        temp_file_path = os.path.join(temp_dir, f"temp_{uuid.uuid4().hex}.py")
        
        try:
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(code)
        except Exception as e:
            logger.error("Failed to write temp code file for static analysis: %s", e)
            return []

        findings = []
        try:
            cmd = [ruff_path, "check", "--output-format", "json", temp_file_path]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10.0)
            except asyncio.TimeoutError:
                logger.error("Ruff static analysis execution timed out.")
                # Terminate the process if timeout occurs
                try:
                    proc.kill()
                except Exception:
                    pass
                return []

            stdout_str = stdout.decode("utf-8", errors="ignore").strip()
            
            if not stdout_str:
                return []

            try:
                diagnostics = json.loads(stdout_str)
            except json.JSONDecodeError:
                logger.error("Failed to parse Ruff JSON output. Output: %s", stdout_str)
                return []

            if not isinstance(diagnostics, list):
                logger.error("Ruff JSON output is not a list. Type: %s", type(diagnostics))
                return []

            for diag in diagnostics:
                if not isinstance(diag, dict):
                    continue

                code_val = str(diag.get("code", "UNKNOWN")).strip()
                message = str(diag.get("message", "")).strip()
                location = diag.get("location", {})
                row = int(location.get("row", 1))
                col = int(location.get("column", 1))
                name = str(diag.get("name", "ruff-issue")).strip()

                title = f"Ruff ({code_val}): {name.replace('_', ' ').replace('-', ' ').title()}"

                # Severity mapping
                is_syntax_error = code_val in ("E999", "syntax-error", "invalid-syntax")
                raw_severity = str(diag.get("severity", "warning")).lower()
                
                if is_syntax_error:
                    severity = "critical"
                elif raw_severity == "error":
                    severity = "high"
                else:
                    severity = "medium"

                # Category mapping
                if code_val.startswith("S"):
                    category = "SECURITY"
                elif code_val.startswith("PL"):
                    category = "MAINTAINABILITY"
                elif is_syntax_error:
                    category = "BUG"
                else:
                    category = "BEST_PRACTICE"

                finding = StaticFinding(
                    title=title,
                    description=message,
                    severity=severity,
                    line=row,
                    column=col,
                    rule=code_val,
                    tool="ruff",
                    category=category,
                    confidence=100
                )
                findings.append(finding)

        except FileNotFoundError:
            logger.warning("Ruff executable not found at %s. Static analysis skipped.", ruff_path)
        except Exception as e:
            logger.error("Error executing Ruff static analysis: %s", e)
        finally:
            # Clean up temp file
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception as e:
                logger.warning("Failed to remove temp file %s: %s", temp_file_path, e)

        return findings
