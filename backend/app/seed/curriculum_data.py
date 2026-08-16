"""
OFFICIAL SYLLABUS CURRICULUM DATA
===================================
Source of truth: the five supplied semester syllabus PDFs.

SUBJECTS (exactly 5):
  CAP392 - Java Programming
  CAP206 - Database Management Systems
  CAP135 - Front End Web Development
  CAB213 - Applied AI: Computer Vision and NLP
  CAB114 - Model Optimization

EXCLUDED (do NOT add):
  CAP138 - EXCLUDED
  PES209 - EXCLUDED

Each subject has exactly 6 units = 30 units total.
"""

CURRICULUM: list[dict] = [
    # =========================================================
    # CAP392 — JAVA PROGRAMMING
    # =========================================================
    {
        "course_code": "CAP392",
        "name": "Java Programming",
        "credits": 4,
        "description": "Covers core Java programming concepts including OOP, exception handling, multithreading, file I/O, packages, and JDBC.",
        "units": [
            {
                "unit_number": 1,
                "name": "Introduction",
                "description": "Java basics, program structure, OOP fundamentals, arrays, and ArrayList.",
                "topics": [
                    "Java program structure",
                    "main method",
                    "access control",
                    "if statement",
                    "else statement",
                    "switch statement",
                    "for loop",
                    "while loop",
                    "do-while loop",
                    "operators",
                    "identifiers",
                    "Class",
                    "Object",
                    "Encapsulation",
                    "Inheritance",
                    "Polymorphism",
                    "Abstraction",
                    "1D arrays",
                    "2D arrays",
                    "ArrayList",
                ],
            },
            {
                "unit_number": 2,
                "name": "Classes, Objects and Polymorphism",
                "description": "Defining classes and methods, constructors, static members, method overloading, and compile/runtime polymorphism.",
                "topics": [
                    "defining classes and methods",
                    "constructors",
                    "types of constructors",
                    "method arguments",
                    "return values",
                    "static variables",
                    "static methods",
                    "method overloading",
                    "constructor overloading",
                    "compile-time polymorphism",
                    "runtime polymorphism",
                    "method overriding",
                ],
            },
            {
                "unit_number": 3,
                "name": "Inheritance, Abstract Classes and Interfaces",
                "description": "Inheritance types, super and this keywords, abstract classes, final keyword, and interfaces.",
                "topics": [
                    "single inheritance",
                    "multilevel inheritance",
                    "hierarchical inheritance",
                    "super keyword",
                    "this keyword",
                    "method overriding",
                    "abstract classes",
                    "final methods",
                    "final variables",
                    "final classes",
                    "interfaces",
                    "creating interfaces",
                    "implementing interfaces",
                ],
            },
            {
                "unit_number": 4,
                "name": "Exception Handling and Multithreading",
                "description": "Exception types, try-catch-finally, custom exceptions, Thread class, Runnable, lifecycle, and priorities.",
                "topics": [
                    "checked exceptions",
                    "unchecked exceptions",
                    "try block",
                    "catch block",
                    "finally block",
                    "throw keyword",
                    "throws keyword",
                    "user-defined exceptions",
                    "exception propagation",
                    "multiple catch blocks",
                    "Thread class",
                    "Runnable interface",
                    "thread lifecycle",
                    "thread priorities",
                ],
            },
            {
                "unit_number": 5,
                "name": "Packages and File Handling",
                "description": "Creating and using packages, Java standard library packages, and file I/O streams.",
                "topics": [
                    "creating packages",
                    "importing packages",
                    "adding classes to packages",
                    "java.lang package",
                    "java.util package",
                    "java.io package",
                    "input streams",
                    "output streams",
                    "console input/output",
                    "FileInputStream",
                    "FileOutputStream",
                    "FileReader",
                    "FileWriter",
                    "random access files",
                ],
            },
            {
                "unit_number": 6,
                "name": "JDBC",
                "description": "Java Database Connectivity: architecture, drivers, statements, and CRUD operations.",
                "topics": [
                    "Introduction to JDBC",
                    "JDBC architecture",
                    "DriverManager",
                    "Statement",
                    "PreparedStatement",
                    "CallableStatement",
                    "SELECT using JDBC",
                    "INSERT using JDBC",
                    "UPDATE using JDBC",
                    "DELETE using JDBC",
                    "ResultSet",
                    "ResultSet methods",
                ],
            },
        ],
        "practicals": [
            "Basic Java programming — Hello World and simple programs",
            "Access specifiers — public, private, protected, default",
            "Control flow constructs — if/else, switch, loops",
            "Encapsulation — getters, setters, data hiding",
            "Polymorphism — method overloading and overriding",
            "Inheritance — single, multilevel, hierarchical",
            "Nested classes — inner classes and anonymous classes",
            "Interfaces — creating and implementing interfaces",
            "Packages — creating, importing, and using packages",
            "Exception handling — try, catch, finally, custom exceptions",
            "File handling — FileReader, FileWriter, streams",
        ],
    },

    # =========================================================
    # CAP206 — DATABASE MANAGEMENT SYSTEMS
    # =========================================================
    {
        "course_code": "CAP206",
        "name": "Database Management Systems",
        "credits": 3,
        "description": "Covers DBMS fundamentals, relational model, SQL, database design, normalization, transaction management, concurrency control, recovery, and distributed databases.",
        "units": [
            {
                "unit_number": 1,
                "name": "Fundamentals of DBMS",
                "description": "File systems vs DBMS, DBMS components, architecture, data models, and data independence.",
                "topics": [
                    "conventional file system vs DBMS",
                    "components of DBMS",
                    "DBMS architecture",
                    "data models",
                    "data independence",
                    "constraints",
                ],
            },
            {
                "unit_number": 2,
                "name": "Relational Databases Design",
                "description": "Relational model, relational algebra, views, SQL query structure, DDL, DCL, and joins.",
                "topics": [
                    "structure of relational databases",
                    "relational algebra",
                    "views",
                    "basic SQL query structure",
                    "DDL statements",
                    "DCL statements",
                    "joins",
                ],
            },
            {
                "unit_number": 3,
                "name": "Database Design",
                "description": "Design guidelines, normalization forms (1NF through 5NF), and types of dependencies.",
                "topics": [
                    "design guidelines",
                    "pitfalls in relational database design",
                    "DBA",
                    "DBA responsibilities",
                    "need for normalization",
                    "first normal form (1NF)",
                    "second normal form (2NF)",
                    "third normal form (3NF)",
                    "fourth normal form (4NF)",
                    "fifth normal form (5NF)",
                    "types of dependencies",
                ],
            },
            {
                "unit_number": 4,
                "name": "Transaction Management",
                "description": "Transaction concepts, ACID properties, schedules, serializability, and recoverability.",
                "topics": [
                    "transaction concept",
                    "ACID properties",
                    "schedules",
                    "serializability",
                    "recoverability",
                ],
            },
            {
                "unit_number": 5,
                "name": "Concurrency Control and Recovery",
                "description": "Lock-based protocols, deadlock, timestamp protocols, failure classification, and log-based recovery.",
                "topics": [
                    "lock-based protocols",
                    "deadlock handling",
                    "multiple granularity",
                    "timestamp-based protocols",
                    "validation-based protocols",
                    "failure classification",
                    "buffer management",
                    "failure with loss of nonvolatile storage",
                    "log-based recovery",
                    "shadow paging",
                ],
            },
            {
                "unit_number": 6,
                "name": "Distributed Databases",
                "description": "Distributed databases, fragmentation, replication, allocation, distributed transactions, and cloud databases.",
                "topics": [
                    "distributed databases",
                    "client/server databases",
                    "data fragmentation",
                    "replication",
                    "allocation techniques",
                    "semi-join",
                    "homogeneous databases",
                    "heterogeneous databases",
                    "distributed data storage",
                    "distributed transactions",
                    "cloud-based databases",
                ],
            },
        ],
        "practicals": [
            "DDL statements — CREATE, ALTER, DROP",
            "DCL and DML statements — GRANT, REVOKE, INSERT, UPDATE, DELETE",
            "Integrity constraints — PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK",
            "NULL and DEFAULT constraints",
            "Keys — primary key, candidate key, foreign key",
            "INNER JOIN — combining rows from two tables",
            "LEFT JOIN — all rows from left table",
            "RIGHT JOIN — all rows from right table",
            "FULL JOIN — all rows from both tables",
            "SELF JOIN — joining a table to itself",
            "Built-in SQL functions — COUNT, SUM, AVG, MAX, MIN, GROUP BY, HAVING",
        ],
    },

    # =========================================================
    # CAP135 — FRONT END WEB DEVELOPMENT
    # =========================================================
    {
        "course_code": "CAP135",
        "name": "Front End Web Development",
        "credits": 3,
        "description": "Covers HTML, HTML5, CSS, advanced CSS, and JavaScript for building modern front-end web pages.",
        "units": [
            {
                "unit_number": 1,
                "name": "HTML Introduction",
                "description": "HTML editors, elements, attributes, formatting, links, tables, forms, layouts, and basic HTML concepts.",
                "topics": [
                    "HTML introduction",
                    "HTML editors",
                    "HTML basics",
                    "HTML elements",
                    "HTML attributes",
                    "headings",
                    "paragraphs",
                    "formatting",
                    "links",
                    "head element",
                    "images",
                    "tables",
                    "lists",
                    "blocks",
                    "layouts",
                    "forms",
                    "Iframes",
                    "colors",
                    "color names",
                    "color values",
                    "entities",
                    "URL encoding",
                    "XHTML",
                ],
            },
            {
                "unit_number": 2,
                "name": "HTML5 Introduction",
                "description": "HTML5 new elements, canvas, SVG, multimedia, APIs: geolocation, web storage, web workers, and SSE.",
                "topics": [
                    "HTML5 elements",
                    "canvas",
                    "SVG",
                    "drag and drop",
                    "geolocation",
                    "video element",
                    "audio element",
                    "HTML5 input types",
                    "HTML5 form elements",
                    "HTML5 form attributes",
                    "semantic elements",
                    "web storage",
                    "app cache",
                    "web workers",
                    "SSE (Server-Sent Events)",
                ],
            },
            {
                "unit_number": 3,
                "name": "CSS Introduction",
                "description": "CSS basics, syntax, selectors, backgrounds, text, fonts, links, lists, and tables.",
                "topics": [
                    "CSS basics",
                    "CSS syntax",
                    "CSS id selector",
                    "CSS class selector",
                    "backgrounds",
                    "text styling",
                    "fonts",
                    "CSS links",
                    "CSS lists",
                    "CSS tables",
                ],
            },
            {
                "unit_number": 4,
                "name": "CSS Box Model",
                "description": "Box model, border, outline, margin, and padding.",
                "topics": [
                    "CSS box model",
                    "border",
                    "outline",
                    "margin",
                    "padding",
                ],
            },
            {
                "unit_number": 5,
                "name": "Advanced CSS and JavaScript Introduction",
                "description": "Grouping/nesting selectors, layout techniques, pseudo-classes, pseudo-elements, media types, and JavaScript introduction.",
                "topics": [
                    "grouping selectors",
                    "nesting selectors",
                    "dimensions",
                    "display property",
                    "positioning",
                    "floating",
                    "alignment",
                    "pseudo-class",
                    "pseudo-element",
                    "navigation bar",
                    "image gallery",
                    "image opacity",
                    "image sprites",
                    "media types",
                    "what is JavaScript",
                    "JavaScript events",
                    "external JavaScript",
                ],
            },
            {
                "unit_number": 6,
                "name": "JavaScript Basic Elements, Objects, BOM and Validation",
                "description": "JavaScript variables, data types, operators, control flow, functions, arrays, DOM, BOM, and form validation.",
                "topics": [
                    "JavaScript comments",
                    "JavaScript variables",
                    "global variables",
                    "JavaScript data types",
                    "JavaScript operators",
                    "if statement",
                    "switch statement",
                    "for loop",
                    "while loop",
                    "JavaScript functions",
                    "JavaScript objects",
                    "JavaScript arrays",
                    "browser objects",
                    "Window object",
                    "Document object",
                    "getElementById",
                    "getElementsByName",
                    "getElementsByTagName",
                    "innerHTML",
                    "innerText",
                    "form validation",
                    "email validation",
                ],
            },
        ],
        "practicals": [
            "HTML text formatting tags — bold, italic, underline, headings",
            "HTML lists — ordered and unordered lists",
            "External and internal links — anchor tags and navigation",
            "HTML tables — creating tables with rows and columns",
            "HTML forms — input fields, buttons, form elements",
            "HTML frames — frameset and iframe usage",
            "HTML images — embedding and styling images",
            "Image mapping — creating clickable image maps",
            "CSS border properties — border styles, widths, colors",
            "CSS font properties — font-family, size, weight, style",
            "CSS box model — margin, padding, border, content",
            "CSS layout — positioning, floats, flexbox",
            "JavaScript form validation — validating form inputs",
            "External JavaScript — linking external .js files",
            "HTML5 elements — semantic elements and multimedia",
        ],
    },

    # =========================================================
    # CAB213 — APPLIED AI: COMPUTER VISION AND NLP
    # =========================================================
    {
        "course_code": "CAB213",
        "name": "Applied AI: Computer Vision and Natural Language Processing",
        "credits": 3,
        "description": "Covers applied AI including Computer Vision, Deep Learning for Vision, NLP fundamentals, NLP with deep learning, and integrated AI applications.",
        "units": [
            {
                "unit_number": 1,
                "name": "Introduction to Applied AI",
                "description": "Overview of AI, domains, traditional vs applied AI, CV and NLP, deep learning, and real-world applications.",
                "topics": [
                    "overview of Artificial Intelligence",
                    "AI domains",
                    "Traditional AI vs Applied AI",
                    "Computer Vision",
                    "Natural Language Processing (NLP)",
                    "Deep Learning",
                    "real-world applications",
                    "AI in Healthcare",
                    "AI in Retail",
                    "AI in Agriculture",
                    "AI in Education",
                ],
            },
            {
                "unit_number": 2,
                "name": "Computer Vision Basics",
                "description": "Digital image fundamentals, preprocessing, filtering, feature extraction, and object detection with OpenCV.",
                "topics": [
                    "digital image fundamentals",
                    "image preprocessing",
                    "image filtering",
                    "edge detection",
                    "feature extraction",
                    "SIFT",
                    "SURF",
                    "ORB",
                    "object detection",
                    "OpenCV",
                    "Haar Cascades",
                ],
            },
            {
                "unit_number": 3,
                "name": "Deep Learning for Vision",
                "description": "CNNs, transfer learning, object detection (YOLO, SSD), Vision Transformers, and PyTorch/TensorFlow.",
                "topics": [
                    "CNN (Convolutional Neural Network)",
                    "CNN architecture",
                    "CNN layers",
                    "transfer learning",
                    "image classification",
                    "YOLO",
                    "SSD (Single Shot Detector)",
                    "real-time object detection",
                    "Vision Transformers (ViT)",
                    "transfer learning using PyTorch/TensorFlow",
                ],
            },
            {
                "unit_number": 4,
                "name": "Natural Language Processing Fundamentals",
                "description": "Text preprocessing, embeddings, BoW, TF-IDF, Hugging Face Transformers, and vector databases.",
                "topics": [
                    "text preprocessing",
                    "tokenization",
                    "stop words",
                    "stemming",
                    "lemmatization",
                    "Parts of Speech tagging",
                    "Named Entity Recognition (NER)",
                    "word embeddings",
                    "Word2Vec",
                    "GloVe",
                    "Bag of Words (BoW)",
                    "TF-IDF",
                    "Hugging Face Transformers",
                    "semantic search",
                    "vector databases",
                ],
            },
            {
                "unit_number": 5,
                "name": "NLP Using Deep Learning",
                "description": "RNN, LSTM, GRU, sentiment analysis, Transformers, BERT, and LLMs.",
                "topics": [
                    "RNN (Recurrent Neural Network)",
                    "LSTM (Long Short-Term Memory)",
                    "sentiment analysis",
                    "GRU (Gated Recurrent Unit)",
                    "text classification",
                    "sequence labelling",
                    "Transformers",
                    "BERT",
                    "LLMs (Large Language Models)",
                ],
            },
            {
                "unit_number": 6,
                "name": "Integrated Applications and Case Studies",
                "description": "AI in edge/IoT, foundation models, real-time applications, document analysis, and project evaluation metrics.",
                "topics": [
                    "AI in edge devices",
                    "IoT and AI",
                    "foundation models",
                    "real-time applications",
                    "document analysis",
                    "medical imaging",
                    "social media sentiment detection",
                    "project planning",
                    "evaluation metrics",
                    "precision",
                    "recall",
                    "F1-score",
                    "final mini project",
                    "final project demonstration",
                    "final project report",
                ],
            },
        ],
        "practicals": [
            "CNN image classifier using Keras",
            "Real-time object detection using OpenCV",
            "Face detection using Haar Cascades",
            "Emotion recognition",
            "Text preprocessing using NLTK/spaCy",
            "Sentiment analysis",
            "Sequence-to-sequence chatbot",
            "Word2Vec news classification",
            "BERT Named Entity Recognition (NER)",
            "RoBERTa/DistilBERT text classification",
            "CV + NLP mini project",
            "Accuracy, precision, recall evaluation",
        ],
    },

    # =========================================================
    # CAB114 — MODEL OPTIMIZATION
    # =========================================================
    {
        "course_code": "CAB114",
        "name": "Model Optimization",
        "credits": 3,
        "description": "Covers model optimization fundamentals, data preprocessing, optimization techniques, hyperparameter tuning, advanced optimization, and real-world deep learning applications.",
        "units": [
            {
                "unit_number": 1,
                "name": "Introduction to Artificial Intelligence",
                "description": "Model optimization overview, importance, underfitting/overfitting, bias-variance tradeoff, and TensorFlow setup.",
                "topics": [
                    "model optimization overview",
                    "importance and applications of model optimization",
                    "underfitting",
                    "overfitting",
                    "bias-variance tradeoff",
                    "TensorFlow",
                    "TensorFlow optimization capabilities",
                    "TensorFlow environment setup",
                ],
            },
            {
                "unit_number": 2,
                "name": "Data Preprocessing and Augmentation",
                "description": "Data quality, cleaning, preprocessing techniques, data augmentation, and TensorFlow Data API.",
                "topics": [
                    "data quality",
                    "data cleaning",
                    "preprocessing",
                    "data augmentation",
                    "TensorFlow Data API",
                ],
            },
            {
                "unit_number": 3,
                "name": "Basic Optimization Techniques",
                "description": "Optimizers (SGD, Adam, RMSprop), learning rate scheduling, regularization (batch norm, dropout, early stopping).",
                "topics": [
                    "SGD (Stochastic Gradient Descent)",
                    "Adam optimizer",
                    "RMSprop optimizer",
                    "learning rate scheduling",
                    "step decay",
                    "exponential decay",
                    "adaptive learning rate methods",
                    "batch normalization",
                    "dropout",
                    "early stopping",
                ],
            },
            {
                "unit_number": 4,
                "name": "Hyperparameter Tuning",
                "description": "Grid search, random search, Bayesian optimization, Keras Tuner, and automated hyperparameter search.",
                "topics": [
                    "hyperparameter tuning",
                    "grid search",
                    "random search",
                    "Bayesian optimization",
                    "Keras Tuner",
                    "automated hyperparameter search",
                    "evaluating configurations",
                    "comparing configurations",
                ],
            },
            {
                "unit_number": 5,
                "name": "Advanced Optimization Techniques",
                "description": "Model pruning, quantization, knowledge distillation, and TensorFlow Model Optimization Toolkit.",
                "topics": [
                    "model pruning",
                    "model size reduction",
                    "model complexity reduction",
                    "quantization",
                    "reduced precision",
                    "knowledge distillation",
                    "TensorFlow Model Optimization Toolkit",
                    "pruning using TensorFlow",
                    "quantization using TensorFlow",
                    "transfer learning",
                ],
            },
            {
                "unit_number": 6,
                "name": "Deep Learning in Real-World Domains",
                "description": "Deep learning implementation, project planning, documentation, evaluation, and industry applications.",
                "topics": [
                    "deep learning implementation",
                    "project presentation",
                    "project documentation",
                    "project evaluation",
                    "practical deep learning applications across industries",
                ],
            },
        ],
        "practicals": [
            "CNN handwritten digit recognition",
            "8-puzzle AI agent using deep reinforcement learning",
            "Seq2Seq chatbot with attention",
            "Medical image classification",
            "Student performance prediction",
            "English-to-French neural machine translation",
            "RNN temperature control",
            "Grid World deep reinforcement learning",
            "Real-world dataset analysis",
            "Deep-learning classification/regression",
            "AI real-world mini project",
        ],
    },
]

# =========================================================
# CURRICULUM VALIDATION
# =========================================================
EXPECTED_COURSE_CODES = {"CAP392", "CAP206", "CAP135", "CAB213", "CAB114"}
EXCLUDED_COURSE_CODES = {"CAP138", "PES209"}
EXPECTED_SUBJECT_COUNT = 5
EXPECTED_UNITS_PER_SUBJECT = 6
EXPECTED_TOTAL_UNITS = 30


def validate_curriculum() -> dict:
    """Validate curriculum integrity before seeding."""
    errors = []
    warnings = []

    actual_codes = {s["course_code"] for s in CURRICULUM}

    # Check excluded codes are absent
    for excluded in EXCLUDED_COURSE_CODES:
        if excluded in actual_codes:
            errors.append(f"EXCLUDED course code present: {excluded}")

    # Check expected codes are present
    for expected in EXPECTED_COURSE_CODES:
        if expected not in actual_codes:
            errors.append(f"Expected course code missing: {expected}")

    # Check subject count
    if len(CURRICULUM) != EXPECTED_SUBJECT_COUNT:
        errors.append(f"Expected {EXPECTED_SUBJECT_COUNT} subjects, got {len(CURRICULUM)}")

    # Check unit count per subject and total
    total_units = 0
    for subject in CURRICULUM:
        unit_count = len(subject["units"])
        total_units += unit_count
        if unit_count != EXPECTED_UNITS_PER_SUBJECT:
            errors.append(
                f"{subject['course_code']} has {unit_count} units (expected {EXPECTED_UNITS_PER_SUBJECT})"
            )
        for unit in subject["units"]:
            if not unit["topics"]:
                warnings.append(f"{subject['course_code']} Unit {unit['unit_number']} has no topics")

    if total_units != EXPECTED_TOTAL_UNITS:
        errors.append(f"Total units: {total_units} (expected {EXPECTED_TOTAL_UNITS})")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "subject_count": len(CURRICULUM),
        "total_units": total_units,
        "course_codes": sorted(actual_codes),
    }
