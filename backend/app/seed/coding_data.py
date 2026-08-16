"""
Coding and SQL problems seed data.
Strictly mapped to topics across CAP392 (Java), CAP206 (DBMS), CAP135 (Front-End), CAB213 (AI), CAB114 (Model Opt).
"""

CODING_PROBLEMS = [
    # -------------------------------------------------------------
    # CAP392 - Java Programming
    # -------------------------------------------------------------
    {
        "course_code": "CAP392",
        "unit_number": 1,
        "topic_name": "for loop",
        "title": "Reverse an Integer Array in Java",
        "language": "JAVA",
        "difficulty": "EASY",
        "description": "Write a Java program that reverses an array of integers in-place or into a new array and prints the space-separated elements.",
        "starter_code": """public class Solution {
    public static void main(String[] args) {
        int[] arr = {10, 20, 30, 40, 50};
        // TODO: Reverse the array and print elements space-separated
        for (int i = arr.length - 1; i >= 0; i--) {
            System.out.print(arr[i] + (i > 0 ? " " : ""));
        }
    }
}""",
        "expected_output": "50 40 30 20 10",
        "hints": "Loop backwards from arr.length - 1 down to 0.",
        "examples": "Input: [10, 20, 30, 40, 50] -> Output: 50 40 30 20 10",
    },
    {
        "course_code": "CAP392",
        "unit_number": 2,
        "topic_name": "method overloading",
        "title": "Method Overloading: Area Calculator",
        "language": "JAVA",
        "difficulty": "EASY",
        "description": "Create an AreaCalculator class with overloaded area() methods for a square (int side) and a rectangle (int length, int breadth). Print the calculated areas.",
        "starter_code": """class AreaCalculator {
    public int area(int side) {
        return side * side;
    }
    public int area(int l, int b) {
        return l * b;
    }
}

public class Solution {
    public static void main(String[] args) {
        AreaCalculator calc = new AreaCalculator();
        System.out.println("Square: " + calc.area(5));
        System.out.println("Rectangle: " + calc.area(4, 6));
    }
}""",
        "expected_output": "Square: 25\nRectangle: 24",
        "hints": "Define two methods with the same name 'area' but different parameter signatures.",
        "examples": "area(5) -> 25\narea(4, 6) -> 24",
    },
    {
        "course_code": "CAP392",
        "unit_number": 4,
        "topic_name": "user-defined exceptions",
        "title": "Custom Exception: InvalidAgeException",
        "language": "JAVA",
        "difficulty": "MEDIUM",
        "description": "Define a custom checked exception 'InvalidAgeException'. Throw it when age < 18 in checkEligibility(int age). Handle it with try-catch and print the exception message.",
        "starter_code": """class InvalidAgeException extends Exception {
    public InvalidAgeException(String msg) {
        super(msg);
    }
}

public class Solution {
    static void checkEligibility(int age) throws InvalidAgeException {
        if (age < 18) {
            throw new InvalidAgeException("Not eligible for voting");
        }
        System.out.println("Eligible for voting");
    }

    public static void main(String[] args) {
        try {
            checkEligibility(16);
        } catch (InvalidAgeException e) {
            System.out.println("Caught: " + e.getMessage());
        }
    }
}""",
        "expected_output": "Caught: Not eligible for voting",
        "hints": "Extend Exception class and call super(message) in constructor.",
        "examples": "checkEligibility(16) -> Caught: Not eligible for voting",
    },

    # -------------------------------------------------------------
    # CAP206 - Database Management Systems (SQL)
    # -------------------------------------------------------------
    {
        "course_code": "CAP206",
        "unit_number": 2,
        "topic_name": "joins",
        "title": "SQL INNER JOIN: Students and Departments",
        "language": "SQL",
        "difficulty": "EASY",
        "description": "Write an SQL query to retrieve student name, course, and department name by joining Students and Departments on department_id.",
        "starter_code": """-- Schema provided:
-- Students(id, name, course, dept_id)
-- Departments(id, dept_name)

SELECT s.name, s.course, d.dept_name
FROM Students s
INNER JOIN Departments d ON s.dept_id = d.id
ORDER BY s.id;""",
        "expected_output": "Alice|CS|Computer Science\nBob|AI|Computer Science\nCharlie|ECE|Electronics",
        "hints": "Use INNER JOIN on s.dept_id = d.id and order by student id.",
        "examples": "Joins students table with departments table.",
    },
    {
        "course_code": "CAP206",
        "unit_number": 2,
        "topic_name": "basic SQL query structure",
        "title": "SQL Aggregation with GROUP BY and HAVING",
        "language": "SQL",
        "difficulty": "MEDIUM",
        "description": "Find departments that have more than 1 student enrolled, displaying dept_id and the total student count.",
        "starter_code": """-- Table: Students(id, name, dept_id, score)

SELECT dept_id, COUNT(*) AS student_count
FROM Students
GROUP BY dept_id
HAVING COUNT(*) > 1
ORDER BY dept_id;""",
        "expected_output": "101|2",
        "hints": "Filter aggregated groups using the HAVING clause, not WHERE.",
        "examples": "Groups records by dept_id and keeps only groups with count > 1.",
    },

    # -------------------------------------------------------------
    # CAP135 - Front End Web Development (JS & HTML)
    # -------------------------------------------------------------
    {
        "course_code": "CAP135",
        "unit_number": 6,
        "topic_name": "form validation",
        "title": "JavaScript Email & Password Validator",
        "language": "JAVASCRIPT",
        "difficulty": "EASY",
        "description": "Write a JavaScript function validateForm(email, password) that returns true if email contains '@' and '.' and password length >= 8, otherwise false.",
        "starter_code": """function validateForm(email, password) {
    const hasAt = email.includes('@');
    const hasDot = email.includes('.');
    const isPassValid = password && password.length >= 8;
    return hasAt && hasDot && isPassValid;
}

// Test cases
console.log(validateForm("student@university.edu", "pass1234"));
console.log(validateForm("invalid-email", "short"));""",
        "expected_output": "true\nfalse",
        "hints": "Use string includes() method or RegExp with length checks.",
        "examples": "validateForm('test@example.com', '12345678') -> true",
    },

    # -------------------------------------------------------------
    # CAB213 - Applied AI: CV and NLP (Python)
    # -------------------------------------------------------------
    {
        "course_code": "CAB213",
        "unit_number": 4,
        "topic_name": "tokenization",
        "title": "Python NLP: Simple Tokenizer & Stopword Remover",
        "language": "PYTHON",
        "difficulty": "EASY",
        "description": "Write a Python function remove_stopwords(text, stopwords) that tokenizes text into lowercase words and returns the filtered word list.",
        "starter_code": """def remove_stopwords(text: str, stopwords: set) -> list:
    tokens = text.lower().split()
    return [t for t in tokens if t not in stopwords]

text = "Natural Language Processing with Deep Learning and AI"
stops = {"with", "and"}
filtered = remove_stopwords(text, stops)
print(" ".join(filtered))""",
        "expected_output": "natural language processing deep learning ai",
        "hints": "Lowercase string, split by spaces, and use list comprehension filtering against the stopwords set.",
        "examples": "removes stopwords 'with', 'and' from the sentence.",
    },
    {
        "course_code": "CAB213",
        "unit_number": 6,
        "topic_name": "evaluation metrics",
        "title": "Compute Precision, Recall, and F1-Score in Python",
        "language": "PYTHON",
        "difficulty": "MEDIUM",
        "description": "Given TP, FP, FN counts, calculate Precision, Recall, and F1-Score rounded to 2 decimal places.",
        "starter_code": """def compute_metrics(tp: int, fp: int, fn: int):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    return round(precision, 2), round(recall, 2), round(f1, 2)

p, r, f = compute_metrics(80, 20, 10)
print(f"P={p}, R={r}, F1={f}")""",
        "expected_output": "P=0.8, R=0.89, F1=0.84",
        "hints": "Precision = TP/(TP+FP), Recall = TP/(TP+FN), F1 = 2*(P*R)/(P+R).",
        "examples": "TP=80, FP=20, FN=10 -> P=0.8, R=0.89, F1=0.84",
    },

    # -------------------------------------------------------------
    # CAB114 - Model Optimization (Python)
    # -------------------------------------------------------------
    {
        "course_code": "CAB114",
        "unit_number": 3,
        "topic_name": "step decay",
        "title": "Learning Rate Step Decay Scheduler",
        "language": "PYTHON",
        "difficulty": "MEDIUM",
        "description": "Implement a step decay learning rate function lr_schedule(initial_lr, epoch, drop_rate, epochs_per_drop). Compute LR for epoch 0, 10, 20 with initial_lr=0.1, drop_rate=0.5, epochs_per_drop=10.",
        "starter_code": """import math

def step_decay(initial_lr: float, epoch: int, drop: float, epochs_drop: int) -> float:
    return initial_lr * math.pow(drop, math.floor(epoch / epochs_drop))

for ep in [0, 10, 20]:
    lr = step_decay(0.1, ep, 0.5, 10)
    print(f"Epoch {ep}: {lr:.4f}")""",
        "expected_output": "Epoch 0: 0.1000\nEpoch 10: 0.0500\nEpoch 20: 0.0250",
        "hints": "Formula: lr = initial_lr * (drop ^ floor(epoch / epochs_drop)).",
        "examples": "Epoch 0: 0.1, Epoch 10: 0.05, Epoch 20: 0.025",
    }
]
