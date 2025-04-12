<div align="center">

![logo](https://github.com/user-attachments/assets/c3f3a380-7958-4186-94c1-7e1472ef22b1)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/KazKozDev/NovelGenerator/blob/master/LICENSE)

</div>
<div align="center">
NovelGenerator is an LLM-powered tool that expands brief concepts into full-length novels. <br><br>
From idea to manuscript. Without human intervention.

</div>
<br>
NovelGenerator enables writers, storytellers, and LLM enthusiasts to produce complete fiction using either free local LLMs or commercial API services. The entire generation process runs autonomously while maintaining narrative coherence.<br><br>

An end-to-end novel creation system employs entity relationship modeling for character development while generating structured content at scene-level granularity within a persistent state management framework for world consistency. The pipeline incorporates algorithmic tension control to manage narrative pacing alongside automated semantic validation to identify inconsistencies, culminating in multi-pass quality assurance that ensures overall narrative coherence and artistic integrity.

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
```

install a virrtual env
```bash
python -m venv .venv
# for linux
TODO
# for win
.venv\Scripts\activate
```


```bash
python.exe -m pip install --upgrade pip

pip install -r requirements.txt
```

## 💻 Usage

1. Start Ollama:
```bash
ollama serve
```

--model: Specifies the language model to use (default: gemma3:12b). For best results, use gemma3:27b or a better model.
--synopsis: Provides the story synopsis. If omitted, the program will prompt you to enter it in the console. You can also provide a text file containing the synopsis (e.g., --synopsis path/to/synopsis.txt).
--ollama_url: The URL of your Ollama API (default: http://localhost:11434).
--chapters: The number of chapters you want in your novel (default: 3).
--language: The language of the book (default: en). Supported languages are defined in story_outline_prompt.json.
--genre: The genre of the book (default: fantasy).
--audience: The target audience for the book (default: adult).
--tone: The tone of the book (default: light).
--style: The narrative style of the book (default: third person).
--setting: The setting of the book (default: modern).
--themes: The themes explored in the book (default: love).
--names: The style of character names to use (default: realistic).
--output: The output file name (default: ./output/generated_book.md).


2. Run generator:
```bash
python novel_generator.py --model gemma3:27b --synopsis "A young wizard must stop an ancient evil from destroying the kingdom." --ollama_url http://localhost:11434 --chapters 5 --language en --genre fantasy --audience adult --tone light --style third person --setting modern --themes love --names realistic --output my_novel.md
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

## Changes in v1.5

*   Implemented multi-language support for prompts using a JSON file.
*   Integrated various LLM providers: Ollama, OpenAI, Anthropic, OpenRouter and DeepSeek.
*   Added character and world name extraction using LLMs.

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
