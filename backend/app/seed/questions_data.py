"""
Question bank seed data.
Strictly mapped to topics of the 5 official subjects:
CAP392 (Java), CAP206 (DBMS), CAP135 (Front End), CAB213 (Applied AI), CAB114 (Model Optimization).
All questions are labeled with source_type="ADDITIONAL_LEARNING".
"""

QUESTION_BANK = [
    # -------------------------------------------------------------
    # CAP392 - Java Programming
    # -------------------------------------------------------------
    {
        "course_code": "CAP392",
        "unit_number": 1,
        "topic_name": "main method",
        "question_text": "Why must the main method in Java be declared as public static void main(String[] args)?",
        "question_type": "MCQ",
        "difficulty": "EASY",
        "explanation": "'public' allows JVM to access it from outside the package, 'static' allows invocation without instantiating the class, and 'void' indicates it returns no value.",
        "options": [
            {"text": "public allows JVM access, static allows execution without object creation, void returns nothing", "is_correct": True},
            {"text": "public is optional, static prevents memory leaks, void is for faster compilation", "is_correct": False},
            {"text": "static makes the method run on multiple CPU threads automatically", "is_correct": False},
            {"text": "main method can only accept integer command-line arguments", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP392",
        "unit_number": 1,
        "topic_name": "ArrayList",
        "question_text": "What is the primary difference between a standard 1D Array and an ArrayList in Java?",
        "question_type": "MCQ",
        "difficulty": "EASY",
        "explanation": "Standard arrays in Java have a fixed size upon initialization, whereas ArrayList dynamically grows and shrinks in capacity.",
        "options": [
            {"text": "ArrayList is dynamic in size while standard arrays are fixed in size", "is_correct": True},
            {"text": "ArrayList can only store primitive data types directly", "is_correct": False},
            {"text": "Standard arrays are part of java.util while ArrayList is a primitive keyword", "is_correct": False},
            {"text": "Standard arrays cannot store objects", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP392",
        "unit_number": 1,
        "topic_name": "Encapsulation",
        "question_text": "How is data encapsulation typically achieved in Java?",
        "question_type": "MCQ",
        "difficulty": "EASY",
        "explanation": "Encapsulation is achieved by declaring class fields as private and providing public getter and setter methods to access and modify them.",
        "options": [
            {"text": "By declaring instance variables private and providing public getter and setter methods", "is_correct": True},
            {"text": "By making all methods static and all variables public", "is_correct": False},
            {"text": "By inheriting from multiple abstract interfaces", "is_correct": False},
            {"text": "By using the final keyword on every class member", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP392",
        "unit_number": 2,
        "topic_name": "method overloading",
        "question_text": "Which of the following conditions is required for valid method overloading in Java?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "Method overloading requires the methods to have the same name but different parameter lists (type, number, or sequence). Changing only the return type is not sufficient.",
        "options": [
            {"text": "Different parameter list (number, type, or order of parameters)", "is_correct": True},
            {"text": "Different return type only with identical parameter list", "is_correct": False},
            {"text": "Different access specifiers (e.g. public vs private) only", "is_correct": False},
            {"text": "Method must be declared static in the child class", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP392",
        "unit_number": 2,
        "topic_name": "runtime polymorphism",
        "question_text": "What mechanism enables runtime polymorphism (dynamic method dispatch) in Java?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "Runtime polymorphism is achieved via method overriding where the call to an overridden method is resolved at runtime based on the actual object instance.",
        "options": [
            {"text": "Method overriding resolved dynamically at runtime using object reference", "is_correct": True},
            {"text": "Method overloading resolved at compile time", "is_correct": False},
            {"text": "Using static methods inside final classes", "is_correct": False},
            {"text": "Automatic type casting during bytecode compilation", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP392",
        "unit_number": 3,
        "topic_name": "super keyword",
        "question_text": "What is the function of super() when used inside a child class constructor?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "super() invokes the direct superclass constructor and must be the very first statement in the child constructor.",
        "options": [
            {"text": "It invokes the constructor of the immediate parent class and must be the first statement", "is_correct": True},
            {"text": "It creates a static copy of the parent class in heap memory", "is_correct": False},
            {"text": "It overrides all parent class private variables", "is_correct": False},
            {"text": "It prevents the class from being inherited further", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP392",
        "unit_number": 3,
        "topic_name": "interfaces",
        "question_text": "Which statement is true regarding interfaces in Java 8 and later?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "Since Java 8, interfaces can contain default and static methods with concrete implementations in addition to abstract method declarations.",
        "options": [
            {"text": "Interfaces can contain default and static methods with implementation bodies", "is_correct": True},
            {"text": "A class can implement only one interface at a time", "is_correct": False},
            {"text": "Interfaces can have constructors and instance variables", "is_correct": False},
            {"text": "Interface variables are private and mutable by default", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP392",
        "unit_number": 4,
        "topic_name": "try block",
        "question_text": "When does the 'finally' block NOT execute in Java exception handling?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "The finally block always executes unless System.exit(0) is called or the JVM terminates abruptly (e.g. fatal hardware failure / kill signal).",
        "options": [
            {"text": "When System.exit(0) is invoked inside try or catch block", "is_correct": True},
            {"text": "When an unhandled RuntimeException is thrown in the catch block", "is_correct": False},
            {"text": "When a return statement is encountered in the try block", "is_correct": False},
            {"text": "When multiple catch blocks are present", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP392",
        "unit_number": 4,
        "topic_name": "Thread class",
        "question_text": "What are the two primary ways to create a multi-threaded task in Java?",
        "question_type": "MCQ",
        "difficulty": "EASY",
        "explanation": "Threads in Java are created either by extending the java.lang.Thread class or by implementing the java.lang.Runnable interface.",
        "options": [
            {"text": "Extending the Thread class OR implementing the Runnable interface", "is_correct": True},
            {"text": "Implementing java.io.Serializable OR extending Object", "is_correct": False},
            {"text": "Calling System.gc() in a background loop", "is_correct": False},
            {"text": "Declaring methods as synchronized without any thread class", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP392",
        "unit_number": 5,
        "topic_name": "FileInputStream",
        "question_text": "What is the difference between FileInputStream/FileOutputStream and FileReader/FileWriter in Java?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "Stream classes (FileInputStream) handle raw 8-bit byte streams (binary data), while Reader/Writer classes handle 16-bit Unicode character streams (text data).",
        "options": [
            {"text": "Streams are byte-oriented (binary), while Readers/Writers are character-oriented (text)", "is_correct": True},
            {"text": "Streams are only for network sockets while Readers are for local files", "is_correct": False},
            {"text": "Readers are synchronous while Streams are asynchronous", "is_correct": False},
            {"text": "Streams cannot be buffered", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP392",
        "unit_number": 6,
        "topic_name": "PreparedStatement",
        "question_text": "Why is PreparedStatement preferred over Statement in JDBC for executing parameterized queries?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "PreparedStatement precompiles the SQL query on the database server, improving performance for repetitive queries and providing robust protection against SQL Injection attacks.",
        "options": [
            {"text": "Precompiles SQL query and protects against SQL injection attacks", "is_correct": True},
            {"text": "PreparedStatement does not require a database connection", "is_correct": False},
            {"text": "PreparedStatement can only execute DDL commands", "is_correct": False},
            {"text": "Statement cannot execute SELECT queries", "is_correct": False}
        ]
    },

    # -------------------------------------------------------------
    # CAP206 - Database Management Systems
    # -------------------------------------------------------------
    {
        "course_code": "CAP206",
        "unit_number": 1,
        "topic_name": "data independence",
        "question_text": "What is Logical Data Independence in a three-tier DBMS architecture?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "Logical data independence is the capacity to change the conceptual schema without having to change external schemas or application programs.",
        "options": [
            {"text": "Ability to modify conceptual schema without changing external schemas or applications", "is_correct": True},
            {"text": "Ability to modify physical storage without altering the conceptual schema", "is_correct": False},
            {"text": "Ability to store database on multiple operating systems simultaneously", "is_correct": False},
            {"text": "Separation of database tables from query logs", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP206",
        "unit_number": 2,
        "topic_name": "joins",
        "question_text": "What is the result of a LEFT OUTER JOIN between table A and table B?",
        "question_type": "MCQ",
        "difficulty": "EASY",
        "explanation": "A LEFT OUTER JOIN returns all rows from table A (left), and matching rows from table B (right). For unmatched rows in A, NULL values are returned for B's columns.",
        "options": [
            {"text": "All rows from table A, with matched columns from B or NULL if no match exists", "is_correct": True},
            {"text": "Only rows that have matching keys in both table A and table B", "is_correct": False},
            {"text": "Cartesian product of all rows in table A and table B", "is_correct": False},
            {"text": "Only rows from table B that have no corresponding row in table A", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP206",
        "unit_number": 3,
        "topic_name": "third normal form (3NF)",
        "question_text": "A relation is in Third Normal Form (3NF) if it is in 2NF and has no:",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "3NF requires a relation to be in 2NF and have no transitive functional dependencies (i.e. no non-prime attribute is transitively dependent on any candidate key).",
        "options": [
            {"text": "Transitive functional dependencies", "is_correct": True},
            {"text": "Partial dependencies on composite keys", "is_correct": False},
            {"text": "Multivalued attributes or repeating groups", "is_correct": False},
            {"text": "Join dependencies", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP206",
        "unit_number": 3,
        "topic_name": "second normal form (2NF)",
        "question_text": "What type of dependency is eliminated when converting a relation from 1NF to 2NF?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "2NF eliminates partial functional dependency, meaning no non-prime attribute should be functionally dependent on a proper subset of any candidate key.",
        "options": [
            {"text": "Partial functional dependencies", "is_correct": True},
            {"text": "Transitive functional dependencies", "is_correct": False},
            {"text": "Multivalued dependencies", "is_correct": False},
            {"text": "Cyclic dependencies", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP206",
        "unit_number": 4,
        "topic_name": "ACID properties",
        "question_text": "Which ACID property guarantees that all operations within a transaction are completed successfully or none are applied?",
        "question_type": "MCQ",
        "difficulty": "EASY",
        "explanation": "Atomicity ensures the 'all-or-nothing' principle for database transactions.",
        "options": [
            {"text": "Atomicity", "is_correct": True},
            {"text": "Consistency", "is_correct": False},
            {"text": "Isolation", "is_correct": False},
            {"text": "Durability", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP206",
        "unit_number": 5,
        "topic_name": "lock-based protocols",
        "question_text": "In Strict Two-Phase Locking (Strict 2PL), when are exclusive locks released?",
        "question_type": "MCQ",
        "difficulty": "HARD",
        "explanation": "In Strict 2PL, all exclusive locks acquired by a transaction must be held until the transaction commits or aborts, preventing cascading aborts.",
        "options": [
            {"text": "Only after the transaction has fully committed or aborted", "is_correct": True},
            {"text": "Immediately after the item is updated in memory", "is_correct": False},
            {"text": "During the growing phase before reading new items", "is_correct": False},
            {"text": "Whenever another transaction requests a shared lock", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP206",
        "unit_number": 6,
        "topic_name": "data fragmentation",
        "question_text": "What is horizontal data fragmentation in a distributed database system?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "Horizontal fragmentation splits a table into subsets of tuples (rows) based on selection conditions (predicates).",
        "options": [
            {"text": "Dividing a relation into subsets of rows (tuples) using horizontal selection predicates", "is_correct": True},
            {"text": "Dividing a relation into subsets of columns (attributes) using projection", "is_correct": False},
            {"text": "Compressing database pages on disk blocks", "is_correct": False},
            {"text": "Distributing duplicate copies of entire tables across all cluster nodes", "is_correct": False}
        ]
    },

    # -------------------------------------------------------------
    # CAP135 - Front End Web Development
    # -------------------------------------------------------------
    {
        "course_code": "CAP135",
        "unit_number": 1,
        "topic_name": "forms",
        "question_text": "What is the difference between GET and POST methods in an HTML form submission?",
        "question_type": "MCQ",
        "difficulty": "EASY",
        "explanation": "GET appends form data to the URL query string and is suitable for idempotent reads, whereas POST sends data in the HTTP request body and is safer for sensitive data/mutations.",
        "options": [
            {"text": "GET appends data to the URL query string; POST sends data in the HTTP body", "is_correct": True},
            {"text": "GET is encrypted by default; POST sends plain text", "is_correct": False},
            {"text": "GET has no character limit; POST is limited to 2048 characters", "is_correct": False},
            {"text": "POST cannot be used with JSON data", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP135",
        "unit_number": 2,
        "topic_name": "web storage",
        "question_text": "How does localStorage differ from sessionStorage in HTML5?",
        "question_type": "MCQ",
        "difficulty": "EASY",
        "explanation": "localStorage persists indefinitely until cleared explicitly, whereas sessionStorage data is cleared when the browser tab/session is closed.",
        "options": [
            {"text": "localStorage has no expiration time; sessionStorage expires when tab is closed", "is_correct": True},
            {"text": "localStorage is stored on the server; sessionStorage is on the client", "is_correct": False},
            {"text": "localStorage is limited to 4KB; sessionStorage allows 5GB", "is_correct": False},
            {"text": "sessionStorage works across different browser origins", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP135",
        "unit_number": 3,
        "topic_name": "CSS syntax",
        "question_text": "In CSS selector specificity, which of the following has the highest specificity?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "ID selectors (#header) have higher specificity than class selectors (.btn), pseudo-classes (:hover), and element selectors (div). Inline styles have even higher specificity.",
        "options": [
            {"text": "ID selector (#main-nav)", "is_correct": True},
            {"text": "Class selector (.button-primary)", "is_correct": False},
            {"text": "Element type selector (article)", "is_correct": False},
            {"text": "Universal selector (*)", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP135",
        "unit_number": 4,
        "topic_name": "CSS box model",
        "question_text": "When box-sizing: border-box is applied to an element, what determines its total rendered width?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "With border-box, the declared width includes content, padding, and border. Margin is still added outside.",
        "options": [
            {"text": "The declared width includes content, padding, and borders", "is_correct": True},
            {"text": "The declared width is only the content area, padding and border are added extra", "is_correct": False},
            {"text": "The width is computed automatically from parent margin alone", "is_correct": False},
            {"text": "Padding is removed completely from the layout", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP135",
        "unit_number": 5,
        "topic_name": "display property",
        "question_text": "What is the difference between display: none and visibility: hidden in CSS?",
        "question_type": "MCQ",
        "difficulty": "EASY",
        "explanation": "display: none removes the element entirely from the document layout flow, whereas visibility: hidden hides the element visually while preserving its layout space.",
        "options": [
            {"text": "display: none removes layout space; visibility: hidden hides element but reserves space", "is_correct": True},
            {"text": "display: none is for mobile only; visibility: hidden is for desktop", "is_correct": False},
            {"text": "visibility: hidden removes the element from the DOM entirely", "is_correct": False},
            {"text": "There is no functional difference in modern browsers", "is_correct": False}
        ]
    },
    {
        "course_code": "CAP135",
        "unit_number": 6,
        "topic_name": "form validation",
        "question_text": "Why should client-side JavaScript form validation always be accompanied by server-side validation?",
        "question_type": "MCQ",
        "difficulty": "EASY",
        "explanation": "Client-side validation enhances UX with instant feedback, but can be easily bypassed by disabling JS or using direct API tools (Postman, curl), requiring server-side validation for security.",
        "options": [
            {"text": "Client-side validation can be bypassed or disabled by users/attackers", "is_correct": True},
            {"text": "JavaScript cannot read input field values reliably", "is_correct": False},
            {"text": "Server-side validation is required only for CSS styles", "is_correct": False},
            {"text": "Client-side validation slows down database indexing", "is_correct": False}
        ]
    },

    # -------------------------------------------------------------
    # CAB213 - Applied AI: Computer Vision and NLP
    # -------------------------------------------------------------
    {
        "course_code": "CAB213",
        "unit_number": 1,
        "topic_name": "Traditional AI vs Applied AI",
        "question_text": "How does Applied AI differ fundamentally from Traditional Rule-Based AI?",
        "question_type": "MCQ",
        "difficulty": "EASY",
        "explanation": "Applied AI uses statistical learning, deep neural nets, and real-world domain data to generalize on unstructured inputs (images, text), unlike hand-crafted symbolic rule engines.",
        "options": [
            {"text": "Applied AI learns patterns from domain data and generalizes on unstructured data", "is_correct": True},
            {"text": "Traditional AI uses neural networks while Applied AI uses expert if-else rules", "is_correct": False},
            {"text": "Applied AI is theoretical only and cannot run on real hardware", "is_correct": False},
            {"text": "Traditional AI only works on image data", "is_correct": False}
        ]
    },
    {
        "course_code": "CAB213",
        "unit_number": 2,
        "topic_name": "edge detection",
        "question_text": "Which steps are involved in the Canny Edge Detection algorithm in OpenCV?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "Canny edge detection consists of: Gaussian smoothing -> Gradient computation -> Non-Maximum Suppression -> Double Thresholding -> Hysteresis Edge Tracking.",
        "options": [
            {"text": "Gaussian Blur -> Gradient Calculation -> Non-Maximum Suppression -> Hysteresis Thresholding", "is_correct": True},
            {"text": "FFT -> Median Filter -> Max Pooling -> Softmax", "is_correct": False},
            {"text": "K-Means Clustering -> PCA -> Haar Cascade -> Bounding Box", "is_correct": False},
            {"text": "Word2Vec -> Cosine Similarity -> Edge Linking", "is_correct": False}
        ]
    },
    {
        "course_code": "CAB213",
        "unit_number": 3,
        "topic_name": "YOLO",
        "question_text": "What makes YOLO (You Only Look Once) architectures suitable for real-time object detection?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "YOLO frames object detection as a single regression problem, processing the full image once in a single forward pass instead of running regional proposal pipelines.",
        "options": [
            {"text": "Single forward pass predicts bounding boxes and class probabilities simultaneously", "is_correct": True},
            {"text": "It uses recurrent LSTM loops across each pixel sequence", "is_correct": False},
            {"text": "It requires separate sliding windows for every possible scale", "is_correct": False},
            {"text": "It only works on grayscale 8x8 images", "is_correct": False}
        ]
    },
    {
        "course_code": "CAB213",
        "unit_number": 4,
        "topic_name": "Word2Vec",
        "question_text": "What are the two training architectures introduced in the Word2Vec framework?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "Word2Vec uses Continuous Bag of Words (CBOW - predicting target word from context) and Skip-gram (predicting context words from target word).",
        "options": [
            {"text": "Continuous Bag of Words (CBOW) and Skip-gram", "is_correct": True},
            {"text": "Encoder and Decoder Transformers", "is_correct": False},
            {"text": "TF-IDF and CountVectorizer", "is_correct": False},
            {"text": "Feed-Forward and Back-Propagation", "is_correct": False}
        ]
    },
    {
        "course_code": "CAB213",
        "unit_number": 5,
        "topic_name": "BERT",
        "question_text": "What does the bidirectional representation in BERT (Bidirectional Encoder Representations from Transformers) mean?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "BERT conditions on both left and right context simultaneously across all transformer encoder layers using Masked Language Modeling (MLM).",
        "options": [
            {"text": "It attends to context from both left and right directions simultaneously in all layers", "is_correct": True},
            {"text": "It translates text from English to French and back to English", "is_correct": False},
            {"text": "It processes text forward in the morning and backward at night", "is_correct": False},
            {"text": "It uses two separate sequential unidirectional LSTMs concatenated together", "is_correct": False}
        ]
    },
    {
        "course_code": "CAB213",
        "unit_number": 6,
        "topic_name": "evaluation metrics",
        "question_text": "When evaluating an imbalanced medical imaging diagnostic model, why is F1-score preferred over raw Accuracy?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "In skewed datasets (e.g. 99% negative cases), raw accuracy can be high simply by predicting all negatives, whereas F1-score harmonic mean balances Precision and Recall.",
        "options": [
            {"text": "Harmonic mean of precision and recall accounts for class imbalance and false negatives", "is_correct": True},
            {"text": "F1 score is always 100% on any neural network", "is_correct": False},
            {"text": "Accuracy cannot be computed for classification tasks", "is_correct": False},
            {"text": "F1 score reduces gradient descent loss directly", "is_correct": False}
        ]
    },

    # -------------------------------------------------------------
    # CAB114 - Model Optimization
    # -------------------------------------------------------------
    {
        "course_code": "CAB114",
        "unit_number": 1,
        "topic_name": "bias-variance tradeoff",
        "question_text": "What does high variance in a machine learning model indicate?",
        "question_type": "MCQ",
        "difficulty": "EASY",
        "explanation": "High variance indicates overfitting: the model fits training noise and performs poorly on unseen test data.",
        "options": [
            {"text": "Overfitting: high sensitivity to training data fluctuations and poor generalization on test data", "is_correct": True},
            {"text": "Underfitting: overly simplistic model failing to learn training patterns", "is_correct": False},
            {"text": "The learning rate is set to zero", "is_correct": False},
            {"text": "Dataset contains duplicate features only", "is_correct": False}
        ]
    },
    {
        "course_code": "CAB114",
        "unit_number": 2,
        "topic_name": "data augmentation",
        "question_text": "Why is data augmentation (rotation, zooming, flipping) used when training deep learning models?",
        "question_type": "MCQ",
        "difficulty": "EASY",
        "explanation": "Data augmentation artificially increases dataset size and diversity, improving invariance and reducing overfitting.",
        "options": [
            {"text": "Artificially increases training variety to improve model generalization and reduce overfitting", "is_correct": True},
            {"text": "Decreases GPU memory usage during forward passes", "is_correct": False},
            {"text": "Replaces the need for backpropagation optimization", "is_correct": False},
            {"text": "Converts continuous regression tasks into classification", "is_correct": False}
        ]
    },
    {
        "course_code": "CAB114",
        "unit_number": 3,
        "topic_name": "dropout",
        "question_text": "How does Dropout regularize a deep neural network during training?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "Dropout randomly sets a fraction of neuron activations to zero during training steps, preventing complex co-adaptations between neurons.",
        "options": [
            {"text": "Randomly deactivates a fraction of neurons at each training step to prevent co-adaptation", "is_correct": True},
            {"text": "Deletes bottom layers of the network permanently", "is_correct": False},
            {"text": "Scales learning rate by half whenever loss increases", "is_correct": False},
            {"text": "Removes low-confidence rows from the training dataset", "is_correct": False}
        ]
    },
    {
        "course_code": "CAB114",
        "unit_number": 3,
        "topic_name": "Adam optimizer",
        "question_text": "How does the Adam optimizer combine the advantages of AdaGrad and RMSprop?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "Adam computes adaptive learning rates for each parameter by maintaining exponentially decaying averages of both past gradients (momentum/first moment) and past squared gradients (second moment).",
        "options": [
            {"text": "Maintains exponential moving averages of both first moment (mean) and second moment (uncentered variance) of gradients", "is_correct": True},
            {"text": "Switches randomly between SGD and L-BFGS based on epoch count", "is_correct": False},
            {"text": "Eliminates the need for calculating backpropagation gradients", "is_correct": False},
            {"text": "Fixes learning rate to a constant integer across all layers", "is_correct": False}
        ]
    },
    {
        "course_code": "CAB114",
        "unit_number": 4,
        "topic_name": "Bayesian optimization",
        "question_text": "Why is Bayesian Optimization more sample-efficient than Grid Search for hyperparameter tuning?",
        "question_type": "MCQ",
        "difficulty": "HARD",
        "explanation": "Bayesian optimization builds a probabilistic surrogate model (e.g. Gaussian Process) of the objective function to select the next hyperparameter set that maximizes an acquisition function.",
        "options": [
            {"text": "Builds a probabilistic surrogate model of the objective function to explore promising hyperparameter regions informed by prior trials", "is_correct": True},
            {"text": "Evaluates all possible combinations simultaneously on quantum computers", "is_correct": False},
            {"text": "Randomly guesses parameters without any tracking of past trials", "is_correct": False},
            {"text": "Only works on models with exactly one hyperparameter", "is_correct": False}
        ]
    },
    {
        "course_code": "CAB114",
        "unit_number": 5,
        "topic_name": "quantization",
        "question_text": "What is post-training quantization in the TensorFlow Model Optimization Toolkit?",
        "question_type": "MCQ",
        "difficulty": "MEDIUM",
        "explanation": "Quantization converts model weights and activations from 32-bit floating point (FP32) to lower precision formats like 8-bit integers (INT8), reducing model size and latency on edge devices with minimal accuracy loss.",
        "options": [
            {"text": "Converting FP32 weights/activations to INT8 precision to reduce memory footprint and inference latency", "is_correct": True},
            {"text": "Splitting the model across multiple TPU pods", "is_correct": False},
            {"text": "Removing layers until the accuracy matches 50%", "is_correct": False},
            {"text": "Encrypting weights using quantum keys", "is_correct": False}
        ]
    },
    {
        "course_code": "CAB114",
        "unit_number": 5,
        "topic_name": "knowledge distillation",
        "question_text": "What is the core principle of Knowledge Distillation in deep learning optimization?",
        "question_type": "MCQ",
        "difficulty": "HARD",
        "explanation": "A compact student model is trained to mimic the soft probability distribution (dark knowledge / logits) output by a large, pre-trained teacher model (or ensemble).",
        "options": [
            {"text": "Training a compact student network to mimic the soft probability outputs (logits) of a large teacher model", "is_correct": True},
            {"text": "Compressing weights into zip files before training", "is_correct": False},
            {"text": "Filtering corrupt images from dataset before passing to GPU", "is_correct": False},
            {"text": "Translating PyTorch weights into C++ bytecode directly", "is_correct": False}
        ]
    }
]
