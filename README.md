# NovelGenerator V2.5

<div align="center">

![logo](https://github.com/user-attachments/assets/00339b68-eb07-44ab-9375-dc77d2748791)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/KazKozDev/NovelGenerator/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/KazKozDev/NovelGenerator)](https://github.com/KazKozDev/NovelGenerator/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

</div>

NovelGenerator V2.5 is an advanced Python tool that transforms a brief user input into a complete novel or fanfiction. By leveraging Ollama’s large language models, it builds coherent plots, develops rich characters, and adapts to various literary styles. You can also choose alternative API providers like ChatGPT or Claude Sonnet.

While commercial models may offer higher quality, the Ollama version remains free by using local LLMs—its innovative design bridges any quality gap, generating your book automatically in the background without requiring your attention.

Additionally, running story_idea_generation.py engages Creative LLM Agents—Architect, Visionary, and Critic—who collaboratively debate and refine ideas over several iterations. This process turns a simple theme into a well-structured narrative, providing the perfect foundation for the main book generator.

## ✨ Features

- 🔄 Full generation pipeline from premise to complete novel
- 👥 Rich character development with relationships, arcs, and consistent tracking
- 📝 Chapter generation with detailed scenes and natural transitions
- 📊 Progress tracking and logging throughout creation process
- 🌍 Consistent world-building with recurring motifs and locations
- 📈 Emotional arc tracking and narrative tension management
- ⏱️ Timeline consistency between chapters
- 🔍 Automatic consistency validation and correction
- 🔄 Smooth chapter-to-chapter transitions
- 📚 Final quality assurance for narrative flow

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
