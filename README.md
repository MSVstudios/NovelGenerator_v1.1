<div align="center">

![logo](https://github.com/user-attachments/assets/c3f3a380-7958-4186-94c1-7e1472ef22b1)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/KazKozDev/NovelGenerator/blob/master/LICENSE)

</div>
<div align="center">
NovelGenerator is an LLM-powered tool that expands brief concepts into full-length novels. <br>
From idea to manuscript. Without human intervention.

</div>
<br>
This tool enables writers, storytellers, and LLM enthusiasts to produce complete fiction using either free local LLMs or commercial API services. The entire generation process runs autonomously while maintaining narrative coherence.<br><br>

- End-to-end pipeline from concept to complete novel
- Entity relationship modeling for character development
- Structured content generation with scene-level granularity
- Persistent state management for consistent world-building
- Algorithmic narrative tension control
- Automated semantic validation with correction protocols
- Multi-pass quality assurance for narrative coherence

## Multi-Agent System
The separate `story_idea_generation.py` script employs a distributed architecture with specialized AI agents (Architect, Visionary, and Critic) that collaboratively refine narrative concepts through iterative debate, transforming simple themes into structured story frameworks.

## 📝 Example Output

<a href="scarlet-priestess.txt" download>
  <img src="scarlet-priestess.jpg" alt="Scarlet Priestess" width="300"/>
</a>


<a href="no-safe-exit.txt" download>
  <img src="no-safe-exit.jpg" alt="Scarlet Priestess" width="300"/>
</a>

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
