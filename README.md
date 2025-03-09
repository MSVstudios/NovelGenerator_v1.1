# NovelGenerator V2.5

<div align="center">

<img src="Banner.jpg" alt="NovelGenerator Banner" width="800"/>

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/KazKozDev/NovelGenerator/blob/master/LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/KazKozDev/NovelGenerator/graphs/commit-activity)
[![GitHub issues](https://img.shields.io/github/issues/KazKozDev/NovelGenerator)](https://github.com/KazKozDev/NovelGenerator/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

</div>

NovelGenerator V2.5 is a sophisticated Python tool for generating complete novels and fanfiction from just a short paragraph of user input. Using Ollama's large language models, it creates coherent plot structures, develops nuanced characters, and writes in multiple literary styles. You can choose a script variant with a different API provider. Options available include Ollama, ChatGPT, and Claude Sonnet.

While API calls to commercial models like Claude or ChatGPT can produce better results, Ollama version leverages local LLMs to keep it completely free. The innovative architecture of the script cleverly compensates for this quality difference. Simply launch the script and go about your business—your book generates completely automatically in the background without requiring your attention or intervention, leaving your hands free for other tasks.

Optional: You can run story_idea_generation.py first - Creative LLM Agents creates book plots by orchestrating three specialized AI models (Architect, Visionary, and Critic) that debate and refine ideas over multiple iterations, transforming a simple user theme into a cohesive narrative concept. This system functions as a sophisticated idea generator, producing well-developed plot foundations that serve as optimal input for the main book generation engine.

## ✨ Features

- 🔄 Full generation pipeline
- 👥 Rich character development with relationships 
- 📝 Chapter generation with scenes
- 📊 Progress tracking and logging

## 🛠️ Requirements

- Python 3.8+
- Ollama 
- Dependencies: requests, dataclasses

## 🚀 Installation

```bash
git clone https://github.com/KazKozDev/NovelGenerator.git
cd NovelGenerator
pip install -r requirements.txt
```

## 💻 Usage

1. Start Ollama:
```bash
ollama serve
```
2. Run generator:
```bash
python novel_generator.py
```

## 📝 Example Output

<a href="scarlet-priestess.txt" download>
  <img src="scarlet-priestess.jpg" alt="Scarlet Priestess" width="300"/>
</a>


<a href="no-safe-exit.txt" download>
  <img src="no-safe-exit.jpg" alt="Scarlet Priestess" width="300"/>
</a>


## Literary Analysis - Melisandre Origin Story

Quantitative analysis of a fan-fiction text depicting Melisandre's origin story from ASOIAF.

## Core Metrics

| Metric | Value | | Metric | Value |
|--------|-------|-|--------|-------|
| Word Count | 6,723 | | Flesch Reading Ease | 70.2 |
| Chapters | 8 | | Flesch-Kincaid Grade | 9.4 |
| Avg Words/Chapter | 840 | | Lexical Density | 58.3% |
| Dialogue Ratio | 22% | | Description Density | 49.8% |

## Literary Devices (per 1000 words)
Metaphors: 4.0 | Similes: 2.1 | Imagery: 12.8 | Symbolism: 4.8

## Genre Alignment (1-10)
Fantasy: 8.2 | ASOIAF: 8.5 | Thematic: 8.4 | Character: 8.0

## Key Findings
- Professional-quality writing with strong descriptive language
- Above-average imagery and symbolism metrics
- Heavy emphasis on narration over dialogue
- Strong world-building consistency with ASOIAF universe

## ❓ FAQ

<details>
<summary>Frequently Asked Questions</summary>

- Q: How long does it take to generate a book?
  A: Generation time varies depending on chapter length, complexity, and system resources.

- Q: Can I use the generated content commercially?
  A: Yes, but I recommend thorough review and editing before commercial use.

- Q: What makes NovelGenerator different from other text generators?
  A: The tool focuses on complete novel generation with coherent plot structures, character development, and professional-grade writing quality.

- Q: Any technical challenge?
  A: The main technical challenge, requiring multiple code revisions, was ensuring narrative consistency - both between scenes within chapters and between chapters throughout the manuscript, while maintaining an engaging plot. The system aims to generate chapters with lengths comparable to published books.
</details>

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Submit pull request

## 📄 License

MIT

## 🙏 Acknowledgments

Built with Ollama and gemma2:27b

---
<div align="center">
Made with ❤️ by KazKozDev

[GitHub](https://github.com/KazKozDev) • [Report Bug](https://github.com/KazKozDev/NovelGenerator/issues) • [Request Feature](https://github.com/KazKozDev/NovelGenerator/issues)
</div>
