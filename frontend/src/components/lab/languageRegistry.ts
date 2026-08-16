export interface ClientLanguageConfig {
  id: string;
  name: string;
  badge: string;
  courseCode: string;
  fileName: string;
  starterCode: string;
  sampleStdin: string;
  supportsStdin: boolean;
  monacoLanguage: string;
  description: string;
}

export const CLIENT_LANGUAGES: ClientLanguageConfig[] = [
  {
    id: 'JAVA',
    name: 'Java',
    badge: 'CAP392 · Java OOP',
    courseCode: 'CAP392',
    fileName: 'Main.java',
    monacoLanguage: 'java',
    supportsStdin: true,
    sampleStdin: '',
    description: 'Java (OpenJDK)',
    starterCode: `import java.util.*;

public class Main {
    public static void main(String[] args) {
        // Write your Java code here
        System.out.println("Hello, World!");
    }
}`,
  },
  {
    id: 'PYTHON',
    name: 'Python 3',
    badge: 'CAB213 · Python & AI',
    courseCode: 'CAB213',
    fileName: 'solution.py',
    monacoLanguage: 'python',
    supportsStdin: true,
    sampleStdin: '',
    description: 'Python 3 (NumPy, Pandas, NLTK, Scikit-learn ready)',
    starterCode: `# Write your Python code here
print("Hello, World!")
`,
  },
  {
    id: 'JAVASCRIPT',
    name: 'JavaScript',
    badge: 'CAP135 · Web Dev',
    courseCode: 'CAP135',
    fileName: 'script.js',
    monacoLanguage: 'javascript',
    supportsStdin: true,
    sampleStdin: '',
    description: 'JavaScript (Node.js)',
    starterCode: `// Write your JavaScript code here
console.log("Hello, World!");
`,
  },
  {
    id: 'SQL',
    name: 'SQL (SQLite)',
    badge: 'CAP206 · DBMS',
    courseCode: 'CAP206',
    fileName: 'query.sql',
    monacoLanguage: 'sql',
    supportsStdin: false,
    sampleStdin: '',
    description: 'SQL Sandbox (Students, Departments)',
    starterCode: `-- Write your SQL query here
SELECT * FROM Students;
`,
  },
];

export const getClientLanguage = (langId: string): ClientLanguageConfig => {
  const found = CLIENT_LANGUAGES.find(l => l.id.toUpperCase() === (langId || '').toUpperCase());
  return found || CLIENT_LANGUAGES[0];
};
