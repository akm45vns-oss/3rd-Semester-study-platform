"""Isolated Sandbox for secure multi-language code execution."""
import os
import re
import sys
import time
import shutil
import sqlite3
import tempfile
import subprocess
from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.services.code_execution.registry import get_language_config, LanguageConfig

MAX_OUTPUT_BYTES = 64 * 1024  # 64 KB max stdout/stderr
MAX_STDIN_BYTES = 32 * 1024   # 32 KB max input
DEFAULT_EXECUTION_TIMEOUT = 5.0  # 5 seconds max per run


class ExecutionOutput(BaseModel):
    status: str  # ACCEPTED | WRONG_ANSWER | COMPILATION_ERROR | RUNTIME_ERROR | TIME_LIMIT_EXCEEDED | SYSTEM_ERROR
    stdout: str = ""
    stderr: str = ""
    compile_error: Optional[str] = None
    runtime_error: Optional[str] = None
    execution_time_ms: int = 0
    memory_usage_mb: float = 0.0
    exit_code: int = 0


def _clean_environment() -> Dict[str, str]:
    """Create a stripped environment containing only safe system variables."""
    safe_keys = {
        "PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "LOCALAPPDATA", "APPDATA",
        "USERPROFILE", "HOMEPATH", "HOMEDRIVE", "HOME",
        "JAVA_HOME", "PYTHONPATH", "NODE_PATH", "LIB", "INCLUDE"
    }
    clean_env = {}
    for key, value in os.environ.items():
        if key.upper() in safe_keys:
            clean_env[key] = value
    # Explicitly ensure sensitive secrets are absent
    clean_env.pop("DATABASE_URL", None)
    clean_env.pop("SECRET_KEY", None)
    clean_env.pop("GROQ_API_KEY", None)
    clean_env.pop("GROQ_API_KEYS", None)
    clean_env["PYTHONUNBUFFERED"] = "1"
    return clean_env


def _kill_process_tree(pid: int):
    """Terminate the process and all child processes spawned by it."""
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True, timeout=2.0)
        else:
            import signal
            os.killpg(os.getpgid(pid), signal.SIGKILL)
    except Exception:
        pass


def _sanitize_output(text: str, temp_dir: Optional[str] = None) -> str:
    """Sanitize error messages and paths to prevent leaking host filesystem details."""
    if not text:
        return ""
    if temp_dir:
        text = text.replace(temp_dir, "").replace(temp_dir.replace("\\", "/"), "")
    # Remove raw windows drive paths from compiler stack traces
    text = re.sub(r'[A-Za-z]:\\[^\n:]+\\', '', text)
    if len(text.encode('utf-8')) > MAX_OUTPUT_BYTES:
        text = text[:MAX_OUTPUT_BYTES] + "\n... [Output truncated at 64KB limit]"
    return text.strip()


class CodeSandbox:
    """Manages disposable isolated execution environment for code runtimes."""

    @staticmethod
    def execute(
        language: str,
        source_code: str,
        stdin_input: str = "",
        custom_schema: Optional[str] = None,
    ) -> ExecutionOutput:
        """Execute user source code in an isolated disposable sandbox."""
        config = get_language_config(language)
        if not config:
            return ExecutionOutput(
                status="SYSTEM_ERROR",
                stderr=f"Unsupported language runtime: '{language}'. Supported: JAVA, PYTHON, JAVASCRIPT, SQL.",
            )

        if len(source_code.strip()) == 0:
            return ExecutionOutput(
                status="COMPILATION_ERROR",
                stderr="Source code is empty.",
            )

        # Truncate stdin if overly large
        if stdin_input and len(stdin_input.encode('utf-8')) > MAX_STDIN_BYTES:
            stdin_input = stdin_input[:MAX_STDIN_BYTES]

        # ── SPECIAL HANDLER: SQL IN-MEMORY SANDBOX ──
        if config.id == "SQL":
            return CodeSandbox._execute_sql(source_code, custom_schema)

        # ── GENERAL COMPILER/RUNTIME HANDLER ──
        temp_dir = tempfile.mkdtemp(prefix="semester_os_sandbox_")
        start_time = time.perf_counter()

        try:
            clean_env = _clean_environment()
            
            # Determine file name (for Java, detect public class name)
            target_filename = config.file_name
            class_name = config.entry_point

            if config.id == "JAVA":
                match = re.search(r'public\s+(?:final\s+|abstract\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)', source_code)
                if match:
                    class_name = match.group(1)
                    target_filename = f"{class_name}.java"
                else:
                    # If no public class, ensure class exists or default to Solution/Main
                    match_any = re.search(r'class\s+([A-Za-z_][A-Za-z0-9_]*)', source_code)
                    if match_any:
                        class_name = match_any.group(1)
                        target_filename = f"{class_name}.java"
                    else:
                        class_name = "Main"
                        target_filename = "Main.java"

            source_file_path = os.path.join(temp_dir, target_filename)
            with open(source_file_path, "w", encoding="utf-8") as f:
                f.write(source_code)

            # 1. Compilation Step (if applicable)
            if config.compiler_command:
                compile_cmd = [config.compiler_command[0], target_filename]
                try:
                    compile_proc = subprocess.run(
                        compile_cmd,
                        cwd=temp_dir,
                        env=clean_env,
                        capture_output=True,
                        text=True,
                        timeout=config.timeout_seconds,
                    )
                    if compile_proc.returncode != 0:
                        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
                        clean_compile_err = _sanitize_output(compile_proc.stderr or compile_proc.stdout, temp_dir)
                        return ExecutionOutput(
                            status="COMPILATION_ERROR",
                            compile_error=clean_compile_err,
                            stderr=clean_compile_err,
                            execution_time_ms=elapsed_ms,
                            exit_code=compile_proc.returncode,
                        )
                except subprocess.TimeoutExpired:
                    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
                    return ExecutionOutput(
                        status="TIME_LIMIT_EXCEEDED",
                        compile_error="Compilation timed out. Check for circular imports or excessive macros.",
                        execution_time_ms=elapsed_ms,
                    )

            # 2. Execution Step
            runtime_cmd = list(config.runtime_command)
            if config.id == "JAVA":
                # Replace entry point with detected class name
                runtime_cmd[-1] = class_name
            elif config.id == "PYTHON":
                runtime_cmd[0] = sys.executable
                # Ensure child process has access to Python standard library & site-packages
                clean_env["PYTHONPATH"] = os.pathsep.join(p for p in sys.path if p)

            run_proc = None
            try:
                run_proc = subprocess.Popen(
                    runtime_cmd,
                    cwd=temp_dir,
                    env=clean_env,
                    stdin=subprocess.PIPE if config.supports_stdin else None,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                stdout_data, stderr_data = run_proc.communicate(
                    input=stdin_input if config.supports_stdin else None,
                    timeout=config.timeout_seconds,
                )
                elapsed_ms = int((time.perf_counter() - start_time) * 1000)
                clean_stdout = _sanitize_output(stdout_data, temp_dir)
                clean_stderr = _sanitize_output(stderr_data, temp_dir)

                if run_proc.returncode != 0:
                    return ExecutionOutput(
                        status="RUNTIME_ERROR",
                        stdout=clean_stdout,
                        stderr=clean_stderr,
                        runtime_error=clean_stderr or f"Process exited with non-zero code {run_proc.returncode}",
                        execution_time_ms=elapsed_ms,
                        exit_code=run_proc.returncode,
                    )

                return ExecutionOutput(
                    status="ACCEPTED",
                    stdout=clean_stdout,
                    stderr=clean_stderr,
                    execution_time_ms=elapsed_ms,
                    memory_usage_mb=float(config.memory_limit_mb) / 4.0,  # Estimated baseline
                    exit_code=0,
                )

            except subprocess.TimeoutExpired:
                if run_proc:
                    _kill_process_tree(run_proc.pid)
                elapsed_ms = int((time.perf_counter() - start_time) * 1000)
                return ExecutionOutput(
                    status="TIME_LIMIT_EXCEEDED",
                    stderr=f"Execution timed out. Your program exceeded the {config.timeout_seconds}-second execution limit.",
                    runtime_error="Time Limit Exceeded (infinite loop or blocked I/O)",
                    execution_time_ms=elapsed_ms,
                )

        except Exception as ex:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return ExecutionOutput(
                status="SYSTEM_ERROR",
                stderr=f"Execution sandbox error: {str(ex)}",
                execution_time_ms=elapsed_ms,
            )
        finally:
            # Guarantee disposal of temporary sandbox directory
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    @staticmethod
    def _execute_sql(query: str, custom_schema: Optional[str] = None) -> ExecutionOutput:
        """Execute SQL query inside an isolated in-memory SQLite sandbox."""
        start_time = time.perf_counter()
        DEFAULT_SCHEMA = """
        CREATE TABLE Departments (
            id INTEGER PRIMARY KEY,
            dept_name TEXT NOT NULL
        );

        CREATE TABLE Students (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            dept_id INTEGER,
            score INTEGER,
            FOREIGN KEY (dept_id) REFERENCES Departments(id)
        );

        INSERT INTO Departments (id, dept_name) VALUES 
        (101, 'Computer Science'),
        (102, 'Electronics'),
        (103, 'Artificial Intelligence');

        INSERT INTO Students (id, name, course, dept_id, score) VALUES 
        (1, 'Alice', 'CS', 101, 92),
        (2, 'Bob', 'AI', 101, 85),
        (3, 'Charlie', 'ECE', 102, 78),
        (4, 'Diana', 'Data Science', 103, 95);
        """
        try:
            conn = sqlite3.connect(":memory:")
            cursor = conn.cursor()
            
            schema = custom_schema if custom_schema else DEFAULT_SCHEMA
            cursor.executescript(schema)
            
            cursor.execute(query)
            
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                raw_rows = cursor.fetchall()
                conn.close()
                
                elapsed_ms = int((time.perf_counter() - start_time) * 1000)
                
                # Format tabular output
                header = " | ".join(columns)
                sep = "-" * len(header)
                formatted_rows = [" | ".join(str(val) if val is not None else "NULL" for val in r) for r in raw_rows]
                table_output = f"{header}\n{sep}\n" + "\n".join(formatted_rows)
                
                return ExecutionOutput(
                    status="ACCEPTED",
                    stdout=table_output if raw_rows else f"{header}\n{sep}\n(0 rows returned)",
                    execution_time_ms=elapsed_ms,
                    memory_usage_mb=4.0,
                    exit_code=0,
                )
            else:
                conn.commit()
                conn.close()
                elapsed_ms = int((time.perf_counter() - start_time) * 1000)
                return ExecutionOutput(
                    status="ACCEPTED",
                    stdout="Query executed successfully (schema modified).",
                    execution_time_ms=elapsed_ms,
                    memory_usage_mb=4.0,
                    exit_code=0,
                )
        except Exception as err:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return ExecutionOutput(
                status="RUNTIME_ERROR",
                stderr=f"SQL Execution Error: {str(err)}",
                runtime_error=str(err),
                execution_time_ms=elapsed_ms,
            )
