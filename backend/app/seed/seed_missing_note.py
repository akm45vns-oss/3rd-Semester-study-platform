"""Seed missing academic theory note for Topic 149 (blocks in CAP135)."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.curriculum import Topic
from app.models.progress import Note

TOPIC_149_NOTE = """# HTML Block-Level vs Inline Elements

In HTML, elements are categorized into two primary visual formatting models based on their default rendering behavior in the Document Object Model (DOM): **Block-Level Elements** and **Inline Elements**.

---

## 1. Block-Level Elements

A block-level element always starts on a new line and browsers automatically add some space (a margin) before and after the element. A block-level element always takes up the full width available (stretches out to the left and right as far as it can).

### Key Characteristics:
1. **Line Breaks**: Always begins on a new line; subsequent elements are pushed to the next line.
2. **Width Behavior**: Occupies 100% of the parent container's available width by default (`width: 100%`).
3. **Box Model Sizing**: Respects `width`, `height`, `margin`, and `padding` on all four sides (top, bottom, left, right).
4. **Nesting**: Can contain other block-level elements as well as inline elements.

### Common Block-Level HTML Elements:
- `<div>`: Generic container for flow content.
- `<p>`: Paragraph text.
- `<h1>` to `<h6>`: Document headings.
- `<header>`, `<footer>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`: Semantic layout structural containers.
- `<ul>`, `<ol>`, `<li>`: Unordered and ordered lists.
- `<table>`, `<form>`, `<blockquote>`: Complex structural components.

---

## 2. Inline Elements

An inline element does not start on a new line. An inline element only takes up as much width as necessary for its content.

### Key Characteristics:
1. **Flow Behavior**: Renders in-line with surrounding text and other inline elements without forcing line breaks.
2. **Width & Height**: Does **not** respond to CSS `width` and `height` properties. Dimensions are determined strictly by content.
3. **Vertical Margins/Padding**: `margin-top` and `margin-bottom` have **no effect**. `padding-top` and `padding-bottom` apply visually but do not push surrounding elements away.
4. **Nesting**: Should only contain data or other inline elements (cannot nest block elements inside inline elements).

### Common Inline HTML Elements:
- `<span>`: Generic inline text container.
- `<a>`: Anchor hyperlinks.
- `<strong>`, `<b>`: Bold/important text.
- `<em>`, `<i>`: Emphasized/italic text.
- `<img>`: Image element (replaced inline element that can accept width/height).
- `<code>`, `<small>`, `<label>`, `<input>`, `<button>`: Form and formatting inline tags.

---

## 3. Comparison Matrix

| Property / Feature | Block-Level Elements | Inline Elements |
|---|---|---|
| **Default Line Break** | Always starts on a new line | Flows within current line |
| **Default Width** | Full parent width (100%) | Width of content only |
| **Width & Height CSS** | Fully customizable | Ignored (except replaced elements like `<img>`) |
| **Margin & Padding** | Top, bottom, left, right all apply | Horizontal applies; vertical does not push layout |
| **Nesting Rules** | Can contain block & inline | Can only contain inline & text |
| **Primary Examples** | `<div>`, `<p>`, `<h1>`, `<section>` | `<span>`, `<a>`, `<strong>`, `<em>` |

---

## 4. The CSS `display` Property

The default layout behavior of any HTML element can be modified using the CSS `display` property:

```css
/* Make an inline element behave like a block element */
span.highlight-box {
    display: block;
    width: 250px;
    margin: 15px auto;
}

/* Make block elements sit on the same horizontal line */
div.nav-item {
    display: inline-block;
    width: 120px;
    height: 40px;
    padding: 8px;
}
```

### Display Modes:
- `display: block;` — Generates a block element box.
- `display: inline;` — Generates an inline element box.
- `display: inline-block;` — Behaves like an inline element externally (sits on the same line) but respects `width`, `height`, and vertical margins internally.
- `display: none;` — Completely removes the element from document flow.

---

## 5. University Exam Key Points & Viva Tips
- **Viva Question**: *What is the fundamental difference between `<div>` and `<span>`?*
  - `<div>` is a generic block-level container starting on a new line, whereas `<span>` is an inline container styled within text without disrupting document flow.
- **Exam Rule**: In HTML5 standard rendering, anchor tags `<a>` may wrap block elements (like `<div>` or `<h2>`) to create full clickable card links, whereas standard inline tags should not wrap block containers.
"""


async def main():
    async with AsyncSessionLocal() as db:
        topic_res = await db.execute(select(Topic).where(Topic.name == "blocks"))
        topic = topic_res.scalar_one_or_none()
        if not topic:
            print("Topic 'blocks' not found in database!")
            return

        # Check existing note
        note_res = await db.execute(select(Note).where(Note.topic_id == topic.id))
        existing_note = note_res.scalar_one_or_none()

        if existing_note:
            existing_note.content = TOPIC_149_NOTE
            print(f"Updated existing note for Topic {topic.id} ({topic.name})")
        else:
            # Seed system note (user_id = 3 or 1)
            new_note = Note(
                user_id=3,
                topic_id=topic.id,
                content=TOPIC_149_NOTE,
            )
            db.add(new_note)
            print(f"Created new note for Topic {topic.id} ({topic.name})")

        await db.commit()
        print("Note successfully seeded!")


if __name__ == "__main__":
    asyncio.run(main())
