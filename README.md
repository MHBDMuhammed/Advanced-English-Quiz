# Advanced English Quiz

This project offers a browser-based English quiz and a desktop editor for managing the questions behind it.

## Prerequisites
- Python 3.8 or later (with Tkinter)
- [ttkthemes](https://pypi.org/project/ttkthemes/) for the question editor (`pip install ttkthemes`)
- A modern web browser

## Launch the Quiz
1. Start a local web server in the repository root:
   ```bash
   python3 -m http.server
   ```
2. Visit <http://localhost:8000/index.html> in your browser.

## Edit Questions
1. Run the graphical editor:
   ```bash
   python3 question_editor.py
   ```
2. Use the interface to add, modify, or delete questions.
3. Press **Save All Changes to JSON** to write updates back to `questions.json`.

### Manual JSON Editing
- Questions live in `questions.json` as a list of objects with the keys `question`, `options` (exactly four), and `correctAnswer`.
- After making manual edits, ensure the file remains valid JSON before relaunching the quiz.

## Purpose
The quiz aims to provide an engaging way to practice English skills, while the editor simplifies maintaining the question set.
