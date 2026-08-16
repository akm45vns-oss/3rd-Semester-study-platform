# Semester OS — Complete UI / UX Architecture & Design System Specification

> **Purpose**: This document provides the complete, exhaustive specification of the Semester OS frontend architecture, visual design tokens, layout hierarchy, component library, and page wireframes to guide custom UI redesigns, styling overhauls, or mobile adaptations.

---

## 1. Frontend Architecture & Tech Stack

| Layer | Technology | Version | Key Responsibilities |
|---|---|---|---|
| **Core Framework** | React + TypeScript | React 18.3, TS 5.6 | Component tree, hooks, strict type safety |
| **Build Tooling** | Vite | Vite 5.4 | Hot module replacement (HMR), production bundling |
| **Styling Engine** | Tailwind CSS + PostCSS | Tailwind 3.4 | Utility-first CSS, custom design tokens, responsive breakpoints |
| **Icons** | Lucide React | v0.447 | 1,000+ crisp SVG icon components |
| **Charts & Graphs** | Recharts | v2.15 | Subject mastery bars, study streak rings, radar charts |
| **Routing** | React Router DOM | v6.30 | Client-side SPA navigation, route guards, URL params |
| **Client State** | Zustand | v5.0 | Lightweight global auth and session store |
| **HTTP Client** | Axios | v1.19 | REST API consumer with JWT Bearer interceptor |
| **Markdown Engine**| ReactMarkdown + Remark GFM | Latest | Academic notes reader, syntax highlighting, callout rendering |

---

## 2. Global Design System & Token Palette

### A. Color Palette (`tailwind.config.js` & `index.css`)

```css
/* Surface Hierarchy (Dark Theme) */
--surface:      #080b11;  /* Deepest canvas background */
--surface-1:    #0f141f;  /* Primary card / container background */
--surface-2:    #161d2d;  /* Secondary elevated cards, inputs, dropdowns */
--surface-3:    #1f293d;  /* Borders, dividers, subtle active states */
--surface-4:    #2d3a54;  /* Muted borders, hover state backgrounds */

/* Brand & Accent Tokens (Indigo / Electric Purple) */
--brand-400:    #818cf8;  /* Accent highlights, active tabs, icon glows */
--brand-500:    #6366f1;  /* Primary brand buttons, interactive toggles */
--brand-600:    #4f46e5;  /* Button gradient start, solid actions */
--brand-700:    #4338ca;  /* Active / pressed state */

/* Semantic Status Accents */
--success:      #10b981;  /* Green (Learned, Passed, 100% Mastery) */
--warning:      #f59e0b;  /* Amber (Needs Revision, Medium Priority) */
--danger:       #ef4444;  /* Rose / Red (Mistakes, Failed Attempt, High Priority) */
--info:         #38bdf8;  /* Sky Blue (Currently Learning, Active Session) */
```

---

### B. Typography Scale & Fonts

- **Heading Font**: `'Outfit', 'Inter', sans-serif` (Modern geometric sans with strong display presence)
- **Body Text**: `'Inter', sans-serif` (High legibility at 12px–16px)
- **Code & Monospace**: `'JetBrains Mono', monospace` (For code snippets, course codes, shortcuts)

```css
/* Typography Scale */
.page-title     { font-size: 1.875rem; font-weight: 800; line-height: 2.25rem; } /* 30px */
.section-title  { font-size: 1.125rem; font-weight: 700; line-height: 1.75rem; } /* 18px */
.body-text      { font-size: 0.875rem; font-weight: 400; line-height: 1.5rem; }   /* 14px */
.caption-text   { font-size: 0.75rem;  font-weight: 500; line-height: 1rem; }     /* 12px */
.badge-text     { font-size: 0.6875rem; font-weight: 600; text-transform: uppercase; } /* 11px */
```

---

## 3. Application Routing & Navigation Map

```
/ (Root)
│
├── /login ──────────────────────── Auth: Login screen with demo credentials quick-fill
├── /register ───────────────────── Auth: New student registration
│
├── [AuthGuard Protected Layout]
│   │
│   ├── /dashboard ──────────────── Overview: 5 subjects progress, daily streak, recent topics, quick launch
│   ├── /subjects ───────────────── Curriculum Hub: Grid of 5 subjects with credit tags & completion %
│   ├── /subjects/:id ───────────── Subject Detail: 6 Units accordion, all topics list, practicals tab
│   ├── /topics/:id ─────────────── Topic Deep-Dive: Markdown Notes, MCQs, Coding drill, Mistakes, Mastery %
│   │
│   ├── /practice ───────────────── Assessment Hub: Topic/Unit test generator, question bank filter, live test session
│   ├── /coding ─────────────────── Coding Lab: Problem list with language filters (Java, SQL, JS, Python)
│   ├── /coding/:id ─────────────── Interactive IDE: Problem description, Monaco/textarea editor, test runner
│   │
│   ├── /practicals ─────────────── Lab Tracker: 60 syllabus experiments, output notes, completion toggles
│   ├── /revision ───────────────── Spaced Repetition: Priority queue (HIGH/MED/LOW), flashcard revision
│   ├── /mistakes ───────────────── Mistakes Notebook: Error logs from quizzes & coding, resolution tracker
│   │
│   ├── /recommendations ────────── "What to Study Now?": Algorithmic study planner, dynamic 60-min daily schedule
│   ├── /analytics ──────────────── Performance Analytics: Weak topics radar, subject mastery distributions
│   └── /curriculum-audit ───────── Strict Syllabus Validator: 5 subjects, 30 units, 0 forbidden codes verification
```

---

## 4. Master Layout Hierarchy (`src/components/layout.tsx`)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   DESKTOP VIEWPORT                                      │
├───────────────────────┬────────────────────────────────────────────────────────────────┤
│   SIDEBAR (260px)     │   MAIN CONTENT AREA (flex-1)                                   │
│                       │                                                                │
│ 🎓 Semester OS        │   [Sticky Header (Mobile only / Breadcrumb on Desktop)]        │
│    3rd Semester       │   ┌────────────────────────────────────────────────────────┐   │
│                       │   │ Breadcrumb: Dashboard > CAP392 > Unit 1 > Topic        │   │
│ 🔍 [Cmd+K Search Bar] │   └────────────────────────────────────────────────────────┘   │
│                       │                                                                │
│ NAVIGATION:           │   ┌────────────────────────────────────────────────────────┐   │
│ 📊 Dashboard          │   │                                                        │   │
│ 📚 Subjects           │   │                                                        │   │
│ 🎯 Practice & Quizzes │   │                   PAGE CONTENT CONTAINER               │   │
│ 💻 Coding Lab         │   │                   (max-w-6xl mx-auto)                  │   │
│ 🧪 Practical Tracker  │   │                                                        │   │
│ 🔁 Revision Queue     │   │                                                        │   │
│ ⚠️ Mistakes Notebook  │   │                                                        │   │
│ ⚡ What to Study Now? │   │                                                        │   │
│ 📈 Analytics          │   │                                                        │   │
│ 🛡️ Curriculum Audit   │   │                                                        │   │
│                       │   │                                                        │   │
│ FOOTER ACTIONS:       │   │                                                        │   │
│ 🤖 [AI Study Config]  │   │                                                        │   │
│ 👤 Akm45 (Sign Out)   │   │                                                        │   │
└───────────────────────┴───┴────────────────────────────────────────────────────────┘───┘
```

---

## 5. Detailed Component Library & UI Wireframes

### Component 1: `MarkdownViewer.tsx` (Academic Reader)
- **Props**: `content: string`, `topicTitle?: string`
- **Features**:
  - Code blocks wrapped in dark terminal frames with syntax labels & **Copy Code** button.
  - Heading 1 & 2 styled with gradient text and icon decorations.
  - Blockquotes auto-transformed into amber **Exam Pitfalls / Viva Traps** alert boxes.
  - Tables transformed into striped, rounded data tables.
  - "Copy All Notes" utility in header.

---

### Component 2: `TopicPage.tsx` (Core Learning Hub)
1. **Hero Header Card**:
   - Course Code Pill (`CAP392`), Unit Badge (`Unit 1`), Status Tag (`LEARNED`).
   - Topic Title (`H1`) + Circular Mastery SVG Progress Gauge (0–100%).
   - Action Buttons: `[Mark as Learning]`, `[✓ Mark as Learned]`, `[Needs Revision]`, `[Mark Notes Read]`.
2. **Pill Navigation Tabs**:
   - `Academic Notes (1)` — Renders `MarkdownViewer` + Personal Notes drawer.
   - `Practice & Quiz (3)` — Instant MCQ drills with instant feedback + AI Quiz Generator.
   - `Coding & Lab` — Direct link to coding problem runner.
   - `Syllabus Overview` — 4-pillar checklist (Theory, Practice, Quiz, Revision).
   - `Mistakes (0)` — Error entries recorded on this topic.
   - `Mastery` — Breakdown bars (25% Theory + 25% Practice + 25% Assessment + 25% Revision).

---

### Component 3: `SubjectPage.tsx` (Subject Curriculum Hub)
1. **Hero Banner**:
   - Subject Title (`Java Programming`), Course Code (`CAP392`), Credits Badge (`4 Credits`).
   - Overall Subject Completion Bar + 4 Stat Chips (`Learned Topics`, `Learning`, `Needs Revision`, `Practicals Completed`).
2. **Tab Switcher**:
   - `[Units & Topics]` vs `[Practicals (11)]`.
3. **Unit Accordion**:
   - Collapsible cards for all 6 Units.
   - Progress bar per unit + count of completed topics (`8/9`).
   - Clickable Topic rows with status dots and mastery percentage.

---

### Component 4: `Dashboard.tsx` (Command Center)
1. **Greeting & Streak Strip**:
   - Welcome banner + Daily Streak flame icon (`🔥 1 Day Streak`).
   - Quick launch CTA: `[⚡ What to Study Now?]`.
2. **Top Metric Cards (Grid of 4)**:
   - Overall Semester Mastery (%).
   - Topics Learned (`34/344`).
   - Practicals Completed (`11/60`).
   - Revision Items Due (`0`).
3. **5 Subject Cards Grid**:
   - Each subject card shows code, credits, progress bar, and clickable link.
4. **Recent Activity & Weak Topics Split View**:
   - Left: Recently studied topics with quick resume button.
   - Right: Topics with mastery < 50% flagged for immediate review.

---

### Component 5: `CodingPage.tsx` & `CodingRunner.tsx` (Interactive IDE)
1. **Problem Header**:
   - Title, Language badge (`JAVA` / `SQL` / `JAVASCRIPT` / `PYTHON`), Difficulty (`MEDIUM`).
2. **Two-Column Split Layout**:
   - **Left Column**: Problem description, input/output specifications, example test cases, hints accordion.
   - **Right Column**: Code editor (`JetBrains Mono`, tab spacing, dark theme) + `[Run / Submit]` action bar + Terminal output stdout console.

---

## 6. How to Customize & Redesign

1. **Changing Theme Colors**:
   - Edit `tailwind.config.js` ➔ update `theme.extend.colors.brand` and `surface` hex values.
2. **Customizing Component Layouts**:
   - All page components live under `frontend/src/pages/`.
   - Reusable atom components live under `frontend/src/components/ui.tsx`.
   - Layout & Navigation live under `frontend/src/components/layout.tsx`.
3. **Typography & Effects**:
   - Edit `frontend/src/index.css` to add new CSS variables, font families, or glassmorphic blur classes.
