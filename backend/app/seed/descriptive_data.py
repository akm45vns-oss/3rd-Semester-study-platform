"""Seed dataset of 10-Mark University Descriptive Exam Questions across 5 curriculum subjects."""

DESCRIPTIVE_QUESTIONS_DATA = [
    # ── CAP392: Java Programming ───────────────────────────────────────
    {
        "course_code": "CAP392",
        "unit_number": 1,
        "topic_keyword": "access control",
        "question_text": "Explain the four Java access specifiers (public, private, protected, default) in detail. Provide a comprehensive table comparing package-level and subclass-level visibility along with sample Java code illustrating access restrictions across packages.",
        "marks": 10,
        "difficulty": "MEDIUM",
        "question_type": "THEORY_AND_CODE",
        "answer_outline": [
            "1. Introduction to Encapsulation and Access Control",
            "2. Detailed Explanation of the 4 Access Specifiers",
            "3. Comprehensive Visibility Comparison Matrix Table",
            "4. Java Code Implementation demonstrating Cross-Package and Subclass Access",
            "5. Best Practices & Key Architectural Guidelines"
        ],
        "model_answer": """### 1. Introduction to Access Specifiers
In Java, access specifiers (modifiers) determine the visibility and scope of classes, constructors, methods, and data members. They are fundamental to **Encapsulation** and **Data Hiding**.

### 2. The Four Access Modifiers
- **`private`**: Accessible strictly inside the declaring class only.
- **`default` (package-private)**: Accessible within classes belonging to the same package.
- **`protected`**: Accessible within the same package, and by subclasses in different packages through inheritance.
- **`public`**: Accessible from any class across any package.

### 3. Visibility Matrix
| Access Modifier | Same Class | Same Package | Subclass (Diff Pkg) | Outside Package |
|---|:---:|:---:|:---:|:---:|
| `private` | Yes | No | No | No |
| `default` | Yes | Yes | No | No |
| `protected` | Yes | Yes | Yes | No |
| `public` | Yes | Yes | Yes | Yes |

### 4. Java Implementation Example
```java
package p1;

public class Parent {
    public int pubVar = 10;
    protected int protVar = 20;
    int defVar = 30;
    private int privVar = 40;

    public void display() {
        System.out.println("All variables accessible inside Parent class.");
    }
}
```

```java
package p2;
import p1.Parent;

public class Child extends Parent {
    public void testAccess() {
        System.out.println(pubVar);   // OK - public
        System.out.println(protVar);  // OK - protected via inheritance
        // System.out.println(defVar);   // COMPILE ERROR - default not visible
        // System.out.println(privVar);  // COMPILE ERROR - private not visible
    }
}
```

### 5. Architectural Best Practices
- Always declare instance fields `private` and expose them via `public` getter and setter methods.
- Use `protected` for template methods meant for extension by subclasses.""",
        "key_points": [
            "Define all 4 specifiers accurately",
            "Present a 4x4 visibility comparison matrix",
            "Provide clean code with packaging (p1 and p2)",
            "Explain protected cross-package subclass inheritance rule"
        ],
        "exam_tips": [
            "Always draw the visibility table first to secure quick structured marks",
            "Remember: protected works in different packages ONLY through inheritance"
        ],
        "important_terms": ["Encapsulation", "Package-private", "Subclass Inheritance", "Information Hiding"]
    },
    {
        "course_code": "CAP392",
        "unit_number": 2,
        "topic_keyword": "Constructor",
        "question_text": "Explain Constructor Overloading, Constructor Chaining using this() and super(), and the role of the default constructor in Java with clear code demonstrations.",
        "marks": 10,
        "difficulty": "MEDIUM",
        "question_type": "THEORY_AND_CODE",
        "answer_outline": [
            "1. Definition and Nature of Constructors",
            "2. Default vs Parameterized Constructors",
            "3. Constructor Overloading Mechanics",
            "4. Constructor Chaining with this() and super()",
            "5. Execution Sequence and Complete Code Demo"
        ],
        "model_answer": """### 1. Definition and Properties of Constructors
A constructor is a special member block invoked when an object is instantiated with `new`.
- Has the same name as the class.
- Does not have a return type (not even `void`).
- If no constructor is written, the Java compiler automatically supplies a default no-argument constructor.

### 2. Constructor Overloading & Chaining
- **Overloading**: Creating multiple constructors with different parameter lists within the same class.
- **`this(...)`**: Invokes another constructor within the same class (must be the first statement).
- **`super(...)`**: Invokes the immediate superclass constructor (must be the first statement).

### 3. Code Demonstration
```java
class Vehicle {
    String brand;
    Vehicle(String brand) {
        this.brand = brand;
        System.out.println("Vehicle initialized with brand: " + brand);
    }
}

class Car extends Vehicle {
    String model;
    int topSpeed;

    Car() {
        this("Generic Model", 120); // Constructor chaining using this()
    }

    Car(String model, int topSpeed) {
        super("Toyota");             // Constructor chaining using super()
        this.model = model;
        this.topSpeed = topSpeed;
    }

    void printSpecs() {
        System.out.println(brand + " " + model + " - " + topSpeed + " km/h");
    }
}

public class Main {
    public static void main(String[] args) {
        Car c = new Car();
        c.printSpecs();
    }
}
```""",
        "key_points": [
            "State that constructor name matches class name and has no return type",
            "Explain that this() and super() MUST be the first statement in a constructor",
            "Demonstrate constructor hierarchy call order"
        ],
        "exam_tips": [
            "Mention compiler behavior when parameterized constructor is present vs absent",
            "Clearly show console output sequence in answer sheet"
        ],
        "important_terms": ["Constructor Chaining", "Default Constructor", "super()", "this()", "Polymorphism"]
    },
    {
        "course_code": "CAP392",
        "unit_number": 3,
        "topic_keyword": "Exception handling",
        "question_text": "Describe the Java Exception Hierarchy. Explain try, catch, finally, throw, and throws. Discuss custom checked and unchecked exceptions with full code examples.",
        "marks": 10,
        "difficulty": "HARD",
        "question_type": "THEORY_AND_CODE",
        "answer_outline": [
            "1. Java Exception Hierarchy Diagram",
            "2. Checked vs Unchecked Exceptions",
            "3. The 5 Exception Keywords (try, catch, finally, throw, throws)",
            "4. Multi-catch and finally Block Semantics",
            "5. Custom User-Defined Exception Implementation"
        ],
        "model_answer": """### 1. Java Exception Hierarchy
```text
                  Throwable
                 /         \
            Exception       Error (Fatal: OutOfMemory, StackOverflow)
           /         \
    Checked (IOException)  RuntimeException (Unchecked: NullPointer, Arithmetic)
```

### 2. Checked vs Unchecked Exceptions
- **Checked Exceptions**: Checked at compile-time (e.g., `IOException`, `SQLException`). Must be caught or declared using `throws`.
- **Unchecked Exceptions**: Subclasses of `RuntimeException` (e.g., `ArithmeticException`, `NullPointerException`). Occur due to logical flaws.

### 3. The 5 Keywords
- `try`: Encloses code that might throw an exception.
- `catch`: Handles the specific exception type.
- `finally`: Block that always executes regardless of exception occurrence.
- `throw`: Explicitly throws an exception object.
- `throws`: Declares in method signature that the method may propagate an exception.

### 4. Custom Exception Code Example
```java
class InvalidAgeException extends Exception { // Checked custom exception
    public InvalidAgeException(String message) {
        super(message);
    }
}

public class VotingSystem {
    static void checkEligibility(int age) throws InvalidAgeException {
        if (age < 18) {
            throw new InvalidAgeException("Age " + age + " is not eligible for voting.");
        }
        System.out.println("Eligibility confirmed. Proceed to vote.");
    }

    public static void main(String[] args) {
        try {
            checkEligibility(16);
        } catch (InvalidAgeException e) {
            System.err.println("Caught Custom Exception: " + e.getMessage());
        } finally {
            System.out.println("Session closed.");
        }
    }
}
```""",
        "key_points": [
            "Draw Throwable -> Exception / Error hierarchy diagram",
            "Differentiate Checked vs Unchecked with concrete examples",
            "Explain finally block execution guarantee even on return statements",
            "Provide complete custom Exception class extending Exception"
        ],
        "exam_tips": [
            "Draw the Throwable hierarchy tree neatly at the top of your answer",
            "Mention System.exit(0) as the only condition where finally does not run"
        ],
        "important_terms": ["Throwable", "Checked Exception", "RuntimeException", "Custom Exception", "finally"]
    },

    # ── CAP206: Database Management Systems ────────────────────────────
    {
        "course_code": "CAP206",
        "unit_number": 1,
        "topic_keyword": "Three schema architecture",
        "question_text": "Explain the Three-Schema Architecture (ANSI/SPARC) in DBMS. Describe Logical Data Independence and Physical Data Independence with diagrams.",
        "marks": 10,
        "difficulty": "MEDIUM",
        "question_type": "THEORY_AND_DIAGRAM",
        "answer_outline": [
            "1. Purpose of ANSI/SPARC 3-Tier Architecture",
            "2. Detailed Explanation of External, Conceptual, and Internal Levels",
            "3. Mappings: External-Conceptual and Conceptual-Internal",
            "4. Physical Data Independence with Real-World Example",
            "5. Logical Data Independence with Real-World Example"
        ],
        "model_answer": """### 1. Objective of the Three-Schema Architecture
The ANSI/SPARC architecture separates user views from the physical database to achieve **Data Independence** and reduce structural coupling.

### 2. The Three Levels of Architecture
```text
  [ External View 1 ]    [ External View 2 ]    [ External View 3 ]   (External Level)
           \                 |                 /
            \─── External / Conceptual Mapping ───/
                             |
                   [ Conceptual Schema ]                             (Conceptual Level)
                             |
                ── Conceptual / Internal Mapping ──
                             |
                    [ Internal Schema ]                              (Internal Level)
                             |
                   [ Physical Database ]
```

1. **External Level (View Level)**: Describes how different groups of end-users view the data.
2. **Conceptual Level (Logical Level)**: Describes *what* data is stored in the whole database and the relationships among data (entities, data types, constraints).
3. **Internal Level (Physical Level)**: Describes *how* data is stored on disk (file organizations, indexing B-trees, hashing, compression).

### 3. Data Independence
- **Physical Data Independence**: The capacity to modify the internal schema (e.g., adding an index, changing storage from HDD to NVMe) without altering the conceptual schema.
- **Logical Data Independence**: The capacity to alter the conceptual schema (e.g., adding a new table, adding attributes) without altering existing external views or application programs.""",
        "key_points": [
            "Draw ANSI/SPARC 3-tier architecture diagram",
            "Define External, Conceptual, and Internal schemas",
            "Clearly distinguish Physical vs Logical Data Independence with examples"
        ],
        "exam_tips": [
            "Logical Data Independence is much harder to achieve than Physical Data Independence; highlight this in your conclusion"
        ],
        "important_terms": ["External Schema", "Conceptual Schema", "Internal Schema", "Data Independence", "ANSI/SPARC"]
    },
    {
        "course_code": "CAP206",
        "unit_number": 3,
        "topic_keyword": "Normalization",
        "question_text": "Define Database Normalization. Explain 1NF, 2NF, 3NF, and BCNF with concrete relation schemas, functional dependencies, anomalies, and decomposition steps.",
        "marks": 10,
        "difficulty": "HARD",
        "question_type": "THEORY_AND_DERIVATION",
        "answer_outline": [
            "1. Purpose of Normalization and Database Anomalies (Insert, Update, Delete)",
            "2. First Normal Form (1NF) - Atomic Values",
            "3. Second Normal Form (2NF) - Eliminating Partial Functional Dependencies",
            "4. Third Normal Form (3NF) - Eliminating Transitive Dependencies",
            "5. Boyce-Codd Normal Form (BCNF) - Strict Determinant Rule",
            "6. Comparison Summary Table"
        ],
        "model_answer": """### 1. Purpose of Normalization
Normalization is a systematic technique of decomposing relation schemas to minimize data redundancy and eliminate **Insertion, Deletion, and Update Anomalies**.

### 2. Normal Forms Step-by-Step

#### A. First Normal Form (1NF)
- **Rule**: Every attribute must contain only **atomic (indivisible)** values. No multi-valued or composite attributes.
- **Example**: A student having `{phone1, phone2}` in a single cell violates 1NF. Decompose into multiple rows.

#### B. Second Normal Form (2NF)
- **Rule**: Must be in 1NF **AND** no non-prime attribute should be **partially dependent** on any candidate key (Full Functional Dependency).
- **Example**: `Enrollment(StudentID, CourseID, StudentName, CourseFee)` where `(StudentID, CourseID)` is PK.
  - `StudentID -> StudentName` (Partial dependency on part of PK).
  - **Decomposition**: `Student(StudentID, StudentName)` and `CourseEnroll(StudentID, CourseID, CourseFee)`.

#### C. Third Normal Form (3NF)
- **Rule**: Must be in 2NF **AND** no non-prime attribute is **transitively dependent** on the primary key ($X \\to Y$ and $Y \\to Z$).
- **Formal Condition**: For every non-trivial $X \\to Y$, either $X$ is a Super Key or $Y$ is a Prime Attribute.
- **Example**: `Emp(EmpID, DeptID, DeptName)` where `EmpID -> DeptID` and `DeptID -> DeptName`.
  - **Decomposition**: `Emp(EmpID, DeptID)` and `Dept(DeptID, DeptName)`.

#### D. Boyce-Codd Normal Form (BCNF)
- **Rule**: Stricter than 3NF. For EVERY functional dependency $X \\to Y$, **$X$ MUST be a Super Key**.

### 3. Summary Table
| Normal Form | Condition Eliminated |
|---|---|
| **1NF** | Multi-valued & composite attributes |
| **2NF** | Partial Functional Dependencies |
| **3NF** | Transitive Functional Dependencies |
| **BCNF** | Any non-super key determinant |""",
        "key_points": [
            "Define insertion, deletion, and update anomalies",
            "State atomic values requirement for 1NF",
            "Explain partial dependency for 2NF with composite key example",
            "Explain transitive dependency for 3NF with formal conditions",
            "Define BCNF super-key requirement"
        ],
        "exam_tips": [
            "Always write the candidate keys and functional dependencies explicitly before decomposing",
            "Use clear before-and-after tables"
        ],
        "important_terms": ["Functional Dependency", "1NF", "2NF", "3NF", "BCNF", "Transitive Dependency", "Candidate Key"]
    },

    # ── CAP135: Front End Web Development ──────────────────────────────
    {
        "course_code": "CAP135",
        "unit_number": 2,
        "topic_keyword": "Flexbox",
        "question_text": "Compare CSS Flexbox and CSS Grid layout models in detail. Explain main axis vs cross axis in Flexbox, and grid tracks, lines, and areas in Grid with CSS code examples for a modern responsive layout.",
        "marks": 10,
        "difficulty": "MEDIUM",
        "question_type": "THEORY_AND_CODE",
        "answer_outline": [
            "1. Architectural Difference: 1D (Flexbox) vs 2D (Grid)",
            "2. Flexbox Concepts: Main Axis, Cross Axis, justify-content, align-items",
            "3. CSS Grid Concepts: Tracks, Grid Lines, grid-template-columns, fr units",
            "4. Code Implementation of a Responsive Card Grid and Navbar",
            "5. Decision Guide: When to use Flexbox vs Grid"
        ],
        "model_answer": """### 1. Fundamental Difference
- **CSS Flexbox**: **One-dimensional** layout system (deals with either a row OR a column at a time). Ideal for component-level UI like navbars and button groups.
- **CSS Grid**: **Two-dimensional** layout system (handles rows AND columns simultaneously). Ideal for page-level layouts and structured galleries.

### 2. Flexbox Axis & Alignment
- **Main Axis**: Defined by `flex-direction` (`row` or `column`).
- **Cross Axis**: Perpendicular to the main axis.
- **`justify-content`**: Controls distribution along the main axis (`flex-start`, `center`, `space-between`, `space-around`).
- **`align-items`**: Controls alignment along the cross axis (`stretch`, `center`, `flex-start`, `flex-end`).

### 3. Responsive Code Demo
```css
/* Responsive Grid Dashboard */
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    padding: 1rem;
}

/* Flexbox Navbar Header */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    background-color: #60412B;
    color: #FAF8F5;
}

.nav-links {
    display: flex;
    gap: 1rem;
    list-style: none;
}
```

### 4. Summary Matrix
| Feature | Flexbox | CSS Grid |
|---|---|---|
| Dimension | 1D (Row or Column) | 2D (Row and Column) |
| Alignment Approach | Content-first | Layout-first |
| Best Used For | Navbars, toolbars, list items | Full page layouts, dashboards |""",
        "key_points": [
            "Highlight 1D vs 2D distinction clearly",
            "Explain Main Axis vs Cross Axis in Flexbox",
            "Explain grid-template-columns, repeat(auto-fit, minmax(...)) in Grid",
            "Provide clean, responsive CSS examples"
        ],
        "exam_tips": [
            "Draw a quick diagram of Flexbox axes (Main vs Cross) to earn full diagram marks"
        ],
        "important_terms": ["1D Layout", "2D Layout", "Main Axis", "Cross Axis", "auto-fit", "minmax", "fr Unit"]
    },

    # ── CAB213: Applied AI: Computer Vision & NLP ──────────────────────
    {
        "course_code": "CAB213",
        "unit_number": 2,
        "topic_keyword": "CNN",
        "question_text": "Explain the architecture and mathematical operations of Convolutional Neural Networks (CNNs). Discuss Convolution Layers, Kernel Filters, Stride, Padding, ReLU Activation, Max Pooling, and Fully Connected Layers.",
        "marks": 10,
        "difficulty": "HARD",
        "question_type": "THEORY_AND_DERIVATION",
        "answer_outline": [
            "1. Why CNNs over Traditional Dense Neural Networks for Images",
            "2. Convolution Operation and Mathematical Formulation",
            "3. Hyperparameters: Filter Size, Stride, and Zero Padding (Valid vs Same)",
            "4. Activation (ReLU) and Pooling (Max Pooling vs Average Pooling)",
            "5. Feature Extraction to Classification: Flatten & Dense Layers",
            "6. Complete End-to-End CNN Architecture Flow Diagram"
        ],
        "model_answer": """### 1. Motivation for CNNs
Standard Fully Connected Networks fail on high-resolution images because parameter count explodes, causing overfitting and loss of 2D spatial locality. CNNs use **parameter sharing** and **sparse connectivity**.

### 2. Core CNN Layers

#### A. Convolutional Layer
Applies a learnable $K \\times K$ filter over input $W \\times H$.
The output spatial dimension is:
$$\\text{Output Size} = \\left\\lfloor \\frac{W - K + 2P}{S} \\right\\rfloor + 1$$
Where:
- $W$ = Input width/height
- $K$ = Kernel/filter size
- $P$ = Padding (0 for Valid, $\\frac{K-1}{2}$ for Same)
- $S$ = Stride

#### B. ReLU Activation
Introduces non-linearity: $f(x) = \\max(0, x)$. Resolves vanishing gradient problems during backpropagation.

#### C. Pooling Layer (Downsampling)
Reduces spatial resolution while retaining dominant features, providing translation invariance.
- **Max Pooling**: Takes the maximum value in a $2 \\times 2$ window with stride 2.

#### D. Fully Connected (Dense) Layer
Flattens feature maps into a 1D vector and computes final class probabilities using Softmax:
$$P(y = i | x) = \\frac{e^{z_i}}{\\sum_j e^{z_j}}$$

### 3. Architecture Flow
```text
Input Image (224x224x3) 
   ──> [Conv2D + ReLU] ──> [MaxPool] 
   ──> [Conv2D + ReLU] ──> [MaxPool] 
   ──> [Flatten] ──> [Dense (128)] ──> [Softmax Output (C classes)]
```""",
        "key_points": [
            "State output dimension formula: floor((W - K + 2P)/S) + 1",
            "Explain parameter sharing and translation invariance",
            "Describe Max Pooling and ReLU non-linearity",
            "Draw end-to-end CNN layer pipeline diagram"
        ],
        "exam_tips": [
            "Always include the output dimension formula with an explicit numerical example (e.g. 32x32 input with 5x5 filter, stride 1, padding 0 = 28x28)"
        ],
        "important_terms": ["Convolution", "Kernel", "Stride", "Padding", "Max Pooling", "Feature Map", "Softmax"]
    },

    # ── CAB114: Model Optimization ─────────────────────────────────────
    {
        "course_code": "CAB114",
        "unit_number": 2,
        "topic_keyword": "Pruning",
        "question_text": "Explain Model Pruning and Model Quantization techniques for Deep Neural Network optimization. Differentiate Structured vs Unstructured Pruning and Post-Training Quantization (PTQ) vs Quantization-Aware Training (QAT).",
        "marks": 10,
        "difficulty": "HARD",
        "question_type": "THEORY_AND_ANALYSIS",
        "answer_outline": [
            "1. Need for Model Compression (Edge Deployment, Latency, Memory)",
            "2. Neural Network Pruning Mechanics (Magnitude-based, Structured vs Unstructured)",
            "3. Quantization Fundamentals (FP32 to INT8 Mapping Formula)",
            "4. Post-Training Quantization (PTQ) vs Quantization-Aware Training (QAT)",
            "5. Trade-off Analysis: Accuracy vs Inference Speed vs Memory Footprint"
        ],
        "model_answer": """### 1. Objective of Model Optimization
Deep learning models (e.g., Transformers, ResNets) contain hundreds of millions of parameters. Optimization compresses model size and accelerates inference for edge devices (mobile, IoT).

### 2. Model Pruning
Pruning removes redundant weights/neurons with minimal impact on accuracy.
- **Unstructured Pruning**: Individual weights below threshold $\\epsilon$ are set to zero ($|w_{ij}| < \\epsilon$). Yields sparse weight matrices (requires sparse hardware libraries).
- **Structured Pruning**: Entire filters, channels, or attention heads are removed. Yields standard dense smaller matrices with immediate hardware speedups on generic GPUs/CPUs.

### 3. Model Quantization
Reduces precision of weights and activations from FP32 (32-bit float) to lower bitwidth (e.g., INT8, INT4).
Quantization mapping:
$$q = \\text{round}\\left(\\frac{r}{S}\\right) + Z$$
Where $r$ is the real float value, $S$ is the scale factor, and $Z$ is the zero-point offset.

### 4. PTQ vs QAT
| Feature | Post-Training Quantization (PTQ) | Quantization-Aware Training (QAT) |
|---|---|---|
| When Applied | After model training completes | During fine-tuning / retraining |
| Calibration | Uses small calibration dataset | Simulates INT8 quantization noise in forward pass |
| Training Time | Very fast (minutes) | Slower (requires epochs of fine-tuning) |
| Accuracy Retention | Slight drop on sensitive networks | Near-zero accuracy loss |""",
        "key_points": [
            "Define weight pruning vs structured channel pruning",
            "Write the quantization affine transformation formula",
            "Compare PTQ and QAT in a detailed comparison table",
            "Discuss inference speedup and RAM reduction benefits"
        ],
        "exam_tips": [
            "Remember that unstructured pruning requires specialized sparse BLAS libraries to actually speed up runtime"
        ],
        "important_terms": ["Pruning", "Quantization", "PTQ", "QAT", "FP32 to INT8", "Structured Pruning", "Scale Factor"]
    }
]
