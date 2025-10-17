from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass(slots=True)
class PytestRunnerTool:
    """Execute pytest for the generated project when online."""

    offline: bool = True
    name: str = "pytest_runner"

    def execute(self, test_directory: str, *, workdir: Path) -> Dict[str, str]:
        if self.offline:
            return {
                "tests": test_directory,
                "status": "simulated",
            }

        cmd = ["pytest", test_directory, "-q"]
        env = os.environ.copy()
        pythonpath = str(workdir / "src")
        if env.get("PYTHONPATH"):
            pythonpath = pythonpath + os.pathsep + env["PYTHONPATH"]
        env["PYTHONPATH"] = pythonpath
        try:
            completed = subprocess.run(
                cmd,
                cwd=workdir,
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
        except OSError as exc:  # pragma: no cover - depends on environment
            return {
                "tests": test_directory,
                "status": "error",
                "error": str(exc),
            }

        status = "passed" if completed.returncode == 0 else "failed"
        return {
            "tests": test_directory,
            "status": status,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }


@dataclass(slots=True)
class CoverageAnalyzerTool:
    """Run coverage for the generated project when available."""

    offline: bool = True
    name: str = "coverage_analyzer"

    def execute(self, *, workdir: Path, coverage_target: float, test_directory: str) -> Dict[str, str]:
        if self.offline:
            observed = max(coverage_target - 5.0, 0.0)
            return {
                "target": f"{coverage_target:.1f}",
                "observed": f"{observed:.1f}",
                "status": "estimated",
            }

        run_cmd = ["coverage", "run", "-m", "pytest", test_directory]
        json_cmd = ["coverage", "json", "-o", "coverage.json"]
        observed_value = 0.0
        env = os.environ.copy()
        pythonpath = str(workdir / "src")
        if env.get("PYTHONPATH"):
            pythonpath = pythonpath + os.pathsep + env["PYTHONPATH"]
        env["PYTHONPATH"] = pythonpath

        try:
            run_result = subprocess.run(
                run_cmd,
                cwd=workdir,
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
            if run_result.returncode != 0:
                return {
                    "target": f"{coverage_target:.1f}",
                    "observed": "0.0",
                    "status": "failed",
                    "stdout": run_result.stdout.strip(),
                    "stderr": run_result.stderr.strip(),
                }

            json_result = subprocess.run(
                json_cmd,
                cwd=workdir,
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
            if json_result.returncode != 0:
                observed_value = 0.0
            else:
                coverage_path = workdir / "coverage.json"
                try:
                    data = json.loads(coverage_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    observed_value = 0.0
                else:
                    totals = data.get("totals", {})
                    observed_raw = totals.get("percent_covered_display", totals.get("percent_covered", 0.0))
                    try:
                        observed_value = float(str(observed_raw).rstrip("%"))
                    except ValueError:
                        observed_value = 0.0
        except OSError as exc:  # pragma: no cover - depends on environment
            return {
                "target": f"{coverage_target:.1f}",
                "observed": "0.0",
                "status": "error",
                "error": str(exc),
            }

        observed_str = f"{observed_value:.1f}"
        status = "passed" if observed_value >= coverage_target else "failed"
        return {
            "target": f"{coverage_target:.1f}",
            "observed": observed_str,
            "status": status,
            "stdout": json_result.stdout.strip(),
            "stderr": json_result.stderr.strip(),
        }


__all__ = ["PytestRunnerTool", "CoverageAnalyzerTool"]
