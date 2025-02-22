# NovelGenerator V2.0

<div align="center">

<img src="Banner.jpg" alt="NovelGenerator Banner" width="800"/>

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/KazKozDev/NovelGenerator/blob/master/LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/KazKozDev/NovelGenerator/graphs/commit-activity)
[![GitHub issues](https://img.shields.io/github/issues/KazKozDev/NovelGenerator)](https://github.com/KazKozDev/NovelGenerator/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

</div>

NovelGenerator V2.0 is a sophisticated Python tool for generating complete novels and fanfiction from a short paragraph of user input. Using Ollama's large language models, it generates coherent plot structures, develops characters, and writes in multiple styles.

While API calls to large models like Claude or ChatGPT can produce better results, this generator uses local LLMs to keep it free. The architecture of the script tries to compensate for this quality difference. 

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
```bash
ollama pull mistral-small:24b
```
```bash
ollama pull gemma2:27b
```
2. Run generator:
```bash
python novel_generator.py
```

## 📝 Example Output

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

Built with Ollama mistral-small:24b and gemma2:27b

---
<div align="center">
Made with ❤️ by KazKozDev

[GitHub](https://github.com/KazKozDev) • [Report Bug](https://github.com/KazKozDev/NovelGenerator/issues) • [Request Feature](https://github.com/KazKozDev/NovelGenerator/issues)
</div>
