"""Code execution language registry and configuration."""
from typing import Dict, List, Optional
from pydantic import BaseModel


class LanguageConfig(BaseModel):
    id: str
    display_name: str
    category: str
    file_name: str
    entry_point: str
    compiler_command: Optional[List[str]] = None
    runtime_command: List[str]
    starter_code: str
    supports_stdin: bool = True
    timeout_seconds: float = 5.0
    memory_limit_mb: int = 128
    course_code: str
    description: str


LANGUAGE_REGISTRY: Dict[str, LanguageConfig] = {
    "JAVA": LanguageConfig(
        id="JAVA",
        display_name="Java (OpenJDK)",
        category="Object-Oriented",
        file_name="Main.java",
        entry_point="Main",
        compiler_command=["javac", "Main.java"],
        runtime_command=["java", "-Xmx128m", "-Xms16m", "Main"],
        starter_code="""import java.util.*;

public class Main {
    public static void main(String[] args) {
        // Write your Java code here
        System.out.println("Hello, World!");
    }
}
""",
        supports_stdin=True,
        timeout_seconds=6.0,
        memory_limit_mb=128,
        course_code="CAP392",
        description="Java Programming environment for Unit 1-6 OOP algorithms and data structures.",
    ),
    "PYTHON": LanguageConfig(
        id="PYTHON",
        display_name="Python 3",
        category="Scripting & AI",
        file_name="solution.py",
        entry_point="solution.py",
        compiler_command=None,
        runtime_command=["python", "-u", "solution.py"],
        starter_code="""# Write your Python code here
print("Hello, World!")
""",
        supports_stdin=True,
        timeout_seconds=5.0,
        memory_limit_mb=64,
        course_code="CAB213",
        description="Python runtime for Applied AI, Computer Vision, NLP, and Optimization algorithms.",
    ),
    "JAVASCRIPT": LanguageConfig(
        id="JAVASCRIPT",
        display_name="JavaScript (Node.js)",
        category="Web Technologies",
        file_name="script.js",
        entry_point="script.js",
        compiler_command=None,
        runtime_command=["node", "script.js"],
        starter_code="""// Write your JavaScript code here
console.log("Hello, World!");
""",
        supports_stdin=True,
        timeout_seconds=5.0,
        memory_limit_mb=64,
        course_code="CAP135",
        description="Modern JavaScript runtime for DOM, Events, Async, and Full-Stack logic.",
    ),
    "SQL": LanguageConfig(
        id="SQL",
        display_name="SQL (SQLite Engine)",
        category="Relational Database",
        file_name="query.sql",
        entry_point="query.sql",
        compiler_command=None,
        runtime_command=[],
        starter_code="""-- Write your SQL query here
SELECT * FROM Students;
""",
        supports_stdin=False,
        timeout_seconds=4.0,
        memory_limit_mb=32,
        course_code="CAP206",
        description="Relational SQL execution environment with preloaded schema for DBMS units.",
    ),
}


def get_language_config(lang_id: str) -> Optional[LanguageConfig]:
    """Retrieve normalized language configuration."""
    if not lang_id:
        return None
    normalized = lang_id.strip().upper()
    if normalized in ("JS", "NODE", "NODEJS"):
        normalized = "JAVASCRIPT"
    elif normalized in ("PY", "PYTHON3"):
        normalized = "PYTHON"
    return LANGUAGE_REGISTRY.get(normalized)


def list_available_languages() -> List[LanguageConfig]:
    """List all supported syllabus languages."""
    return list(LANGUAGE_REGISTRY.values())
