<div align="center">

![logo](https://github.com/user-attachments/assets/00339b68-eb07-44ab-9375-dc77d2748791)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/KazKozDev/NovelGenerator/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/KazKozDev/NovelGenerator)](https://github.com/KazKozDev/NovelGenerator/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

</div>

# NovelGenerator

NovelGenerator is a Python tool that transforms brief inputs into complete novels using language model technology.

- Leverages Ollama's local LLMs (free) or enterprise APIs (ChatGPT, Claude)
- Implements asynchronous processing for background operation
- Features modular design for configurable literary styles

## Technical Capabilities
- End-to-end pipeline from concept to complete novel
- Entity relationship modeling for character development
- Structured content generation with scene-level granularity
- Persistent state management for consistent world-building
- Algorithmic narrative tension control
- Automated semantic validation with correction protocols
- Multi-pass quality assurance for narrative coherence

## Multi-Agent System
The separate `story_idea_generation.py` script employs a distributed architecture with specialized AI agents (Architect, Visionary, and Critic) that collaboratively refine narrative concepts through iterative debate, transforming simple themes into structured story frameworks.

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
Alternative Options:
Two additional scripts are available for different API providers:

- ChatGPT Option: novel_generator_chat_gpt.py

- Sonet Option: novel_generator_sonet.py

## 📝 Example Output

<a href="scarlet-priestess.txt" download>
  <img src="scarlet-priestess.jpg" alt="Scarlet Priestess" width="300"/>
</a>


<a href="no-safe-exit.txt" download>
  <img src="no-safe-exit.jpg" alt="Scarlet Priestess" width="300"/>
</a>


## Literary Analysis - Melisandre Origin Story (Scarlet Priestess)

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
