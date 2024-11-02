# Contributing to NovelGenerator

First off, thank you for considering contributing to NovelGenerator! 🎉

## Table of Contents
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Making Changes](#making-changes)
- [Reporting Issues](#reporting-issues)
- [Questions and Support](#questions-and-support)

## How to Contribute

There are many ways to contribute:
- 🐛 Reporting bugs
- 💡 Suggesting enhancements
- 📝 Improving documentation
- 🔧 Submitting fixes
- ✨ Adding new features

## Development Setup

1. Fork the repository:
   - Visit https://github.com/kazkozdev/NovelGenerator
   - Click the "Fork" button in the top right corner

2. Clone your fork:
```bash
git clone https://github.com/YOUR-USERNAME/NovelGenerator
cd NovelGenerator
```

3. Set up development environment:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install spaCy model
python -m spacy download en_core_web_sm
```

## Code Style Guidelines

We keep it simple but consistent:

1. Use clear, descriptive variable names:
```python
# Good
chapter_content = generate_chapter(topic)
word_count = len(text.split())

# Bad
cont = gen(t)
wc = len(t.split())
```

2. Add comments for complex logic:
```python
# Good
# Calculate average emotion intensity across all chapters
avg_emotion = sum(emotions.values()) / len(emotions)

# Bad
avg_emotion = sum(emotions.values()) / len(emotions)  # Calculate average
```

3. Use docstrings for functions:
```python
def improve_text(text: str) -> str:
    """
    Improves the quality of generated text.

    Args:
        text: Input text to improve

    Returns:
        Improved version of the text
    """
```

4. Keep functions focused and reasonably sized

## Making Changes

1. Create a new branch for your changes:
```bash
git checkout -b fix-issue-description
```

2. Make your changes and test them

3. Commit your changes:
```bash
git add .
git commit -m "brief description of changes"
```

4. Push to your fork:
```bash
git push origin fix-issue-description
```

5. Open a Pull Request:
   - Visit your fork on GitHub
   - Click "Pull Request"
   - Fill in description of your changes
   - Submit the PR

### Commit Messages
Keep commit messages clear and descriptive:
```
Good:
- "fix: memory leak in text generation"
- "add: new writing style option"
- "docs: update installation guide"

Bad:
- "fixed stuff"
- "updates"
- "changes"
```

## Reporting Issues

When reporting issues, please include:

1. What you were trying to do
2. What happened instead
3. Steps to reproduce the issue
4. Python version
5. Error messages (if any)

Example:
```
Title: Error when generating large chapters

Description:
- Tried to generate a 10-chapter book
- Program crashed on chapter 3
- Python 3.8.5
- Error: "Memory allocation failed"

Steps to reproduce:
1. Run novel_generator.py
2. Set chapter count to 10
3. Use topic "Epic Fantasy"
```

## Questions and Support

If you have questions:
1. Check existing [issues](https://github.com/kazkozdev/NovelGenerator/issues)
2. Create a new issue with the 'question' label
3. Provide relevant context and examples

---

Made with ❤️ by the NovelGenerator community