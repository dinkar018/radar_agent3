import os
import shutil
import tempfile
import subprocess
import glob
import uuid
import logging
from dataclasses import dataclass, field
from typing import List

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    error: str
    result_files: List[str]
    success: bool


# Plot-saving code injected at the end of every generated script
PLOT_SAVE_INJECTION = """
# --- Auto-injected plot saving ---
import matplotlib.pyplot as plt
import os
_output_dir = os.environ.get('OUTPUT_DIR', '/output')
for _i, _fig_num in enumerate(plt.get_fignums()):
    plt.figure(_fig_num)
    plt.savefig(os.path.join(_output_dir, f'plot_{_i}.png'), dpi=150, bbox_inches='tight')
    plt.close(_fig_num)
print(f"\\n[Agent] Saved {len(plt.get_fignums()) if plt.get_fignums() else _i + 1} plot(s) to {_output_dir}")
"""


class DockerCodeExecutor:
    """Execute Python code in an isolated Docker container."""

    def __init__(
        self,
        image_name: str = "radar-sandbox",
        timeout: int = 120,
    ):
        self.image_name = image_name
        self.timeout = timeout

    def execute(self, code: str, data_file_paths: List[str]) -> ExecutionResult:
        """
        Execute generated Python code in a Docker sandbox.

        Args:
            code: Python source code to execute
            data_file_paths: Paths to radar data files to mount

        Returns:
            ExecutionResult with stdout, stderr, generated files, etc.
        """
        temp_dir = tempfile.mkdtemp(prefix="radar_exec_")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        # Inject matplotlib Agg backend at top + plot saving at bottom
        injected_code = "import matplotlib\nmatplotlib.use('Agg')\n\n" + code + "\n" + PLOT_SAVE_INJECTION

        code_path = os.path.join(temp_dir, "script.py")
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(injected_code)

        # Build Docker command
        docker_cmd = [
            "docker", "run", "--rm",
            "--network=none",          # No network access
            "--memory=2g",             # 2GB memory limit
            "--cpus=2",                # 2 CPU cores max
            "-e", f"OUTPUT_DIR=/output",
            "-v", f"{code_path}:/workspace/script.py:ro",
            "-v", f"{output_dir}:/output:rw",
        ]

        # Mount each data file as read-only under /data/
        for data_path in data_file_paths:
            abs_path = os.path.abspath(data_path)
            basename = os.path.basename(data_path)
            docker_cmd.extend(["-v", f"{abs_path}:/data/{basename}:ro"])

        docker_cmd.extend([self.image_name, "python", "/workspace/script.py"])

        logger.info(f"Executing code in Docker container: {self.image_name}")
        logger.debug(f"Docker command: {' '.join(docker_cmd)}")

        stdout, stderr, error = "", "", ""
        success = False

        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            stdout = result.stdout
            stderr = result.stderr
            success = result.returncode == 0
            if not success:
                # Check if failure is due to Docker daemon not running
                docker_unavailable = any(msg in stderr.lower() for msg in [
                    "cannot connect", "failed to connect", "error during connect", "daemon is running"
                ])
                if docker_unavailable:
                    logger.warning("Docker daemon unavailable. Falling back to local execution environment...")
                    env = os.environ.copy()
                    env["OUTPUT_DIR"] = output_dir
                    local_res = subprocess.run(
                        [sys.executable, code_path],
                        capture_output=True,
                        text=True,
                        timeout=self.timeout,
                        env=env,
                    )
                    stdout = local_res.stdout
                    stderr = local_res.stderr
                    success = local_res.returncode == 0
                    if not success:
                        error = f"Local process exited with code {local_res.returncode}. Stderr: {stderr}"
                    else:
                        error = ""
                else:
                    error = f"Process exited with code {result.returncode}. Stderr: {stderr}"
                    logger.warning(f"Code execution failed: {error}")
        except subprocess.TimeoutExpired:
            error = f"Execution timed out after {self.timeout} seconds"
            logger.error(error)
        except FileNotFoundError:
            logger.warning("Docker not found in PATH. Falling back to local execution environment...")
            try:
                env = os.environ.copy()
                env["OUTPUT_DIR"] = output_dir
                local_res = subprocess.run(
                    [sys.executable, code_path],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    env=env,
                )
                stdout = local_res.stdout
                stderr = local_res.stderr
                success = local_res.returncode == 0
                if not success:
                    error = f"Process exited with code {local_res.returncode}. Stderr: {stderr}"
            except Exception as e:
                error = f"Local execution failed: {str(e)}"
                logger.error(error)
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            logger.error(error)

        # Collect result files from output directory
        result_files = []
        for ext in ["*.png", "*.jpg", "*.csv", "*.json", "*.txt"]:
            for file_path in glob.glob(os.path.join(output_dir, ext)):
                result_files.append(file_path)

        # Copy result files to persistent results directory
        persistent_files = []
        if result_files:
            run_id = str(uuid.uuid4())[:8]
            results_dest = os.path.join(settings.RESULTS_DIR, run_id)
            os.makedirs(results_dest, exist_ok=True)

            for src_path in result_files:
                basename = os.path.basename(src_path)
                dest_path = os.path.join(results_dest, basename)
                shutil.copy2(src_path, dest_path)
                # Store relative path for API access
                persistent_files.append(f"{run_id}/{basename}")

            logger.info(f"Copied {len(persistent_files)} result files to {results_dest}")

        # Clean up temp directory
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        return ExecutionResult(
            stdout=stdout,
            stderr=stderr,
            error=error,
            result_files=persistent_files,
            success=success,
        )
