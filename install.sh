#!/bin/bash

echo "📚 Installing NovelGenerator..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ git is not installed. Please install git."
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "🔄 Installing Ollama..."
    curl https://ollama.ai/install.sh | sh
fi

echo "🔄 Cloning repository..."
git clone https://github.com/KazKozDev/NovelGenerator.git
cd NovelGenerator

echo "🔄 Creating virtual environment..."
python3 -m venv venv

echo "🔄 Activating virtual environment..."
source venv/bin/activate

echo "🔄 Installing dependencies..."
pip install -r requirements.txt

echo "🔄 Installing spaCy model..."
python -m spacy download en_core_web_sm

echo "🔄 Pulling required Ollama models..."
ollama pull command-r:35b
ollama pull aya-expanse:32b
ollama pull qwen2.5:32b

# Create command line alias
echo "🔄 Creating command line alias..."
ALIAS_LINE="alias novel-generator='python3 ${PWD}/novel_generator.py'"
if [[ "$SHELL" == */zsh ]]; then
    echo $ALIAS_LINE >> ~/.zshrc
    source ~/.zshrc
elif [[ "$SHELL" == */bash ]]; then
    echo $ALIAS_LINE >> ~/.bashrc
    source ~/.bashrc
fi

echo "✅ NovelGenerator installed successfully!"
echo "📘 Use 'novel-generator' command to start generating books."
echo "📖 Example: novel-generator --topic \"Space Adventure\" --chapters 5 --style cinematic"