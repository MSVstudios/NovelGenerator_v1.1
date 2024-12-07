import json
from typing import Dict, List, Optional, Any, Union
import requests
import time
from dataclasses import dataclass
import logging
from pathlib import Path
import re
import sys
import os
from datetime import datetime

# Constants
DEFAULT_CHAPTER_MIN_WORDS = 800
DEFAULT_CHAPTER_MAX_WORDS = 2000
DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_DELAY = 2
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9

# Configuration
MODEL_CONFIG = {
    "default": "gemma2:27b",
    "fast": "gemma2:9b",
    "creative": "command-r:35b-08-2024-q5_0"
}

# Logging setup
class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    COLORS = {
        'grey': "\x1b[38;21m",
        'blue': "\x1b[38;5;39m",
        'yellow': "\x1b[38;5;226m",
        'red': "\x1b[38;5;196m",
        'bold_red': "\x1b[31;1m",
        'reset': "\x1b[0m"
    }

    def __init__(self, fmt: str):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.COLORS['grey'] + self.fmt + self.COLORS['reset'],
            logging.INFO: self.COLORS['blue'] + self.fmt + self.COLORS['reset'],
            logging.WARNING: self.COLORS['yellow'] + self.fmt + self.COLORS['reset'],
            logging.ERROR: self.COLORS['red'] + self.fmt + self.COLORS['reset'],
            logging.CRITICAL: self.COLORS['bold_red'] + self.fmt + self.COLORS['reset']
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_logging() -> logging.Logger:
    """Setup logging configuration"""
    # Create logs directory
    log_dir = Path("generation_logs")
    log_dir.mkdir(exist_ok=True)

    # Current time for filename
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"generation_{current_time}.log"

    # Configure logger
    logger = logging.getLogger('BookGenerator')
    logger.setLevel(logging.DEBUG)

    # File handler
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_formatter = ColoredFormatter('%(levelname)s - %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Data models
@dataclass
class Character:
    name: str
    background: str
    personality: str
    goals: str
    relationships: Dict[str, str]

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "background": self.background,
            "personality": self.personality,
            "goals": self.goals,
            "relationships": self.relationships
        }

@dataclass
class Scene:
    content: str
    pov_character: Optional[str] = None
    location: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "pov_character": self.pov_character,
            "location": self.location
        }

@dataclass
class Chapter:
    number: int
    title: str
    summary: str
    scenes: List[Scene]
    word_count: int

    def to_dict(self) -> Dict:
        return {
            "number": self.number,
            "title": self.title,
            "summary": self.summary,
            "scenes": [scene.to_dict() for scene in self.scenes],
            "word_count": self.word_count
        }

@dataclass
class Book:
    title: str
    genre: str
    target_audience: str
    themes: List[str]
    characters: List[Character]
    chapters: List[Chapter]
    metadata: Dict[str, Any]
    plot: Dict[str, Any] = None  # Добавлено поле plot

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "genre": self.genre,
            "target_audience": self.target_audience,
            "themes": self.themes,
            "characters": [char.to_dict() for char in self.characters],
            "chapters": [chapter.to_dict() for chapter in self.chapters],
            "metadata": self.metadata,
            "plot": self.plot
        }

# Main generator class
class BookGenerator:
    def __init__(self,
                 model_name: str = MODEL_CONFIG["default"],
                 min_words: int = DEFAULT_CHAPTER_MIN_WORDS,
                 max_words: int = DEFAULT_CHAPTER_MAX_WORDS,
                 logger: Optional[logging.Logger] = None):

        self.model_name = model_name
        self.min_words = min_words
        self.max_words = max_words
        self.base_url = "http://localhost:11434/api/generate"
        self.logger = logger or setup_logging()

        self.book_data = {
            "title": "",
            "genre": "",
            "target_audience": "",
            "themes": [],
            "characters": [],
            "chapters": [],
            "metadata": {},
            "plot": {}
        }

    def log_separator(self, message: str) -> None:
        """Print log separator with message"""
        separator = f"\n{'='*50}\n{message}\n{'='*50}\n"
        self.logger.info(separator)

    def get_user_input(self) -> Dict[str, Any]:
        """Get validated user input for book generation"""
        print("\n=== Book Generation Setup ===")

        # Base information
        genre = self._get_validated_input(
            "Enter book genre (e.g., Science Fiction, Fantasy, Romance): ",
            lambda x: len(x.strip()) > 0
        )

        target_audience = self._get_validated_input(
            "Enter target audience (e.g., Young Adult, Adult, Children): ",
            lambda x: len(x.strip()) > 0
        )

        # Theme collection
        print("\nEnter main themes (one per line). Press Enter twice to finish:")
        themes = []
        while True:
            theme = input().strip()
            if not theme:
                if themes:
                    break
                print("Please enter at least one theme")
                continue
            themes.append(theme)

        # Modified chapter count validation
        num_chapters = self._get_validated_input(
            "\nEnter desired number of chapters (3-30): ",
            lambda x: x.isdigit() and 3 <= int(x) <= 30,
            "Please enter a number between 3 and 30",
            transform=int
        )

        # Additional requirements
        print("\nEnter any specific requirements (one per line). Press Enter twice to finish:")
        requirements = []
        while True:
            req = input().strip()
            if not req and requirements:
                break
            if req:
                requirements.append(req)

        # Writing style
        styles = {
            1: "Descriptive and detailed",
            2: "Fast-paced and dynamic",
            3: "Character-focused",
            4: "Plot-driven"
        }

        print("\nSelect writing style (enter number):")
        for num, style in styles.items():
            print(f"{num}. {style}")

        style = self._get_validated_input(
            "Style (1-4): ",
            lambda x: x.isdigit() and 1 <= int(x) <= 4,
            transform=int
        )

        return {
            "genre": genre,
            "target_audience": target_audience,
            "themes": themes,
            "num_chapters": num_chapters,
            "requirements": requirements,
            "writing_style": style,
            "timestamp": time.strftime("%Y%m%d_%H%M%S")
        }

    def _get_validated_input(
        self,
        prompt: str,
        validator: callable,
        error_message: str = "Invalid input, please try again",
        transform: callable = lambda x: x
    ) -> Any:
        """Get validated user input with custom validation"""
        while True:
            try:
                user_input = input(prompt).strip()
                if validator(user_input):
                    return transform(user_input)
                print(error_message)
            except ValueError:
                print(error_message)

    def generate_response(
        self,
        prompt: str,
        retries: int = DEFAULT_RETRY_COUNT,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
        attempt_number: int = 1
    ) -> str:
        """Generate response from Ollama with streaming and error handling"""
        self.log_separator("PROMPT")
        self.logger.info(prompt)
        
        for attempt in range(retries):
            try:
                self.log_separator("GENERATING RESPONSE")
                self.logger.info(f"Attempt {attempt + 1}/{retries}")
                
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": True,
                    "temperature": temperature,
                    "top_p": top_p
                }
                
                response = requests.post(self.base_url, json=payload, stream=True)
                response.raise_for_status()
                
                full_response = []
                print("\nGenerating response:")
                print("-" * 50)
                
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if 'response' in chunk:
                            print(chunk['response'], end='', flush=True)
                            full_response.append(chunk['response'])
                            
                print("\n" + "-" * 50)
                
                complete_response = ''.join(full_response)
                
                # Validate minimum length
                if len(complete_response.split()) < 50:
                    raise ValueError("Response too short")
                    
                self.log_separator("COMPLETE RESPONSE")
                self.logger.info(complete_response)
                
                return complete_response
            
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(DEFAULT_RETRY_DELAY ** attempt)
                    continue
                break
            
        self.logger.error("All attempts failed")
        return ""

    def parse_response_to_json(self, text: str, template: Dict) -> Dict:
        """Parse text response to JSON with validation"""
        # Clean text
        text = text.strip()
        if not text:
            return template.copy()

        try:
            # Find JSON in text
            json_str = re.search(r'\{.*\}', text, re.DOTALL)
            if json_str:
                parsed = json.loads(json_str.group())
                # Validate against template
                self._validate_json_structure(parsed, template)
                return parsed
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse JSON directly")
        except Exception as e:
            self.logger.warning(f"JSON validation failed: {str(e)}")

        # Try parsing through LLM
        parse_prompt = f"""
        Convert this text into valid JSON matching this template:
        {json.dumps(template, indent=2)}

        Text to convert:
        {text}

        Provide ONLY valid JSON, no other text.
        """

        try:
            parsed_response = self.generate_response(parse_prompt, temperature=0.1)
            json_str = re.search(r'\{.*\}', parsed_response, re.DOTALL)
            if json_str:
                parsed = json.loads(json_str.group())
                self._validate_json_structure(parsed, template)
                return parsed
        except Exception as e:
            self.logger.error(f"Failed to parse response through LLM: {str(e)}")

        # Create fallback structure
        self.logger.warning("Creating fallback structure")
        result = template.copy()
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                if key in template:
                    result[key] = value.strip()
        return result

    def _validate_json_structure(self, parsed: Dict, template: Dict) -> None:
        """Validate JSON structure matches template"""
        def check_structure(parsed_part: Any, template_part: Any) -> None:
            if isinstance(template_part, dict):
                if not isinstance(parsed_part, dict):
                    raise ValueError(f"Expected dict, got {type(parsed_part)}")
                for key in template_part:
                    if key not in parsed_part:
                        parsed_part[key] = template_part[key]
                    else:
                        check_structure(parsed_part[key], template_part[key])
            elif isinstance(template_part, list):
                if not isinstance(parsed_part, list):
                    raise ValueError(f"Expected list, got {type(parsed_part)}")
                if template_part and parsed_part:
                    check_structure(parsed_part[0], template_part[0])

        check_structure(parsed, template)

    def initialize_book(self, user_input: Dict[str, Any]) -> Optional[Dict]:
        """Initialize book concept with theme consistency"""
        self.log_separator("INITIALIZING BOOK")
        self.logger.info("User input parameters:")
        for key, value in user_input.items():
            self.logger.info(f"{key}: {value}")

        template = {
            "title": "",
            "premise": "",
            "setting": "",
            "main_conflict": "",
            "style_notes": "",
            "themes": user_input["themes"],
            "audience": user_input["target_audience"]
        }

        # Writing style descriptions
        style_descriptions = {
            1: "descriptive and detailed, with rich world-building and atmosphere",
            2: "fast-paced and dynamic, focusing on action and momentum",
            3: "character-focused, with deep emotional development and relationships",
            4: "plot-driven, with intricate storylines and twists"
        }

        # Build context
        themes_context = ", ".join([f"'{theme}'" for theme in user_input["themes"]])
        requirements_context = ", ".join([f"'{req}'" for req in user_input["requirements"]])

        prompt = f"""Create a unique and compelling book concept with these parameters:

Genre: {user_input['genre']}
Target Audience: {user_input['target_audience']}
Main Themes: {themes_context}
Writing Style: {style_descriptions[user_input['writing_style']]}
Special Requirements: {requirements_context}

Create:
1. A unique and engaging title that reflects the themes and genre
2. A compelling one-paragraph premise that hooks the reader
3. A rich and detailed setting description
4. A complex main conflict that drives the story
5. Specific style notes for maintaining consistent tone and atmosphere

Your response MUST maintain thematic consistency with the provided themes.
Format the response as JSON with these exact fields:
{json.dumps(template, indent=2)}

Provide ONLY the JSON response, no other text.
"""

        response = self.generate_response(prompt)
        book_concept = self.parse_response_to_json(response, template)

        if book_concept and book_concept["title"]:
            self.book_data.update(book_concept)
            self.log_separator("BOOK CONCEPT CREATED")
            self.logger.info(f"Title: {book_concept['title']}")
            self.logger.info(f"Premise: {book_concept['premise']}")
            return book_concept

        self.logger.error("Failed to create book concept")
        return None

    def create_characters(self) -> List[Character]:
        """Generate characters with enhanced relationships and consistency"""
        self.log_separator("CREATING CHARACTERS")

        template = {
            "characters": [
                {
                    "name": "",
                    "background": "",
                    "personality": "",
                    "goals": "",
                    "relationships": {}
                }
            ]
        }

        # Build prompt with richer context
        prompt = f"""Create compelling characters for this book:
Title: {self.book_data['title']}
Premise: {self.book_data['premise']}
Setting: {self.book_data['setting']}
Themes: {', '.join(self.book_data.get('themes', []))}

Create 3-5 unique and detailed characters that:
1. Have distinctive names fitting the setting
2. Possess rich personal backgrounds
3. Display clear personality traits
4. Pursue compelling goals aligned with the themes
5. Have meaningful relationships with other characters
6. Contribute to the main conflict

Each character should:
- Reflect the story's themes
- Have clear motivations
- Present internal and external conflicts
- Show potential for growth
- Have distinct voice and mannerisms

Format the response as JSON with these exact fields:
{json.dumps(template, indent=2)}

Provide ONLY the JSON response, no other text.
"""

        response = self.generate_response(prompt)

        try:
            characters_data = self.parse_response_to_json(response, template)
            if characters_data and "characters" in characters_data:
                # Validate character relationships
                if not self._validate_character_relationships(characters_data["characters"]):
                    self.logger.warning("Character relationships need adjustment")
                    characters_data = self._fix_character_relationships(characters_data)
                
                self.book_data["characters"] = characters_data["characters"]

                self.log_separator("CHARACTERS CREATED")
                for char in characters_data["characters"]:
                    self.logger.info(f"\nCharacter: {char['name']}")
                    self.logger.info(f"Background: {char['background']}")
                    self.logger.info(f"Personality: {char['personality']}")
                    self.logger.info(f"Goals: {char['goals']}")
                    self.logger.info("Relationships:")
                    for rel_name, rel_desc in char['relationships'].items():
                        self.logger.info(f"- {rel_name}: {rel_desc}")

                return [Character(**char_data) for char_data in characters_data["characters"]]
        except Exception as e:
            self.logger.error(f"Error processing characters: {str(e)}")

        return []

    def _validate_character_relationships(self, characters: List[Dict]) -> bool:
        """Validate character relationships are consistent and balanced"""
        # Check each character has relationships
        for char in characters:
            if not char["relationships"]:
                return False

        # Check for reciprocal relationships
        for char1 in characters:
            for char2 in characters:
                if char1 != char2:
                    if char2["name"] in char1["relationships"]:
                        if char1["name"] not in char2["relationships"]:
                            return False

        return True

    def _fix_character_relationships(self, characters_data: Dict) -> Dict:
        """Fix inconsistent character relationships"""
        chars = characters_data["characters"]

        # Ensure all characters have relationships
        for char in chars:
            if not char["relationships"]:
                char["relationships"] = {}
                for other in chars:
                    if other != char:
                        char["relationships"][other["name"]] = "Neutral acquaintance"

        # Fix reciprocal relationships
        for char1 in chars:
            for char2 in chars:
                if char1 != char2:
                    if char2["name"] in char1["relationships"]:
                        if char1["name"] not in char2["relationships"]:
                            char2["relationships"][char1["name"]] = f"Reciprocal: {char1['relationships'][char2['name']]}"

        characters_data["characters"] = chars
        return characters_data

    def create_plot_outline(self, num_chapters: int) -> Dict:
        """Generate plot outline with strict 5-6 sentence chapter summaries"""
        self.log_separator("CREATING PLOT OUTLINE")
        self.logger.info(f"Planning {num_chapters} chapters")

        template = {
            "chapters": [
                {
                    "number": 1,
                    "summary": "",
                    "key_points": [],
                    "character_focus": [],
                    "settings": []
                }
            ] * num_chapters
        }

        # Build context
        character_names = [char['name'] for char in self.book_data["characters"]]
        themes = self.book_data.get('themes', [])

        prompt = f"""Create a {num_chapters}-chapter plot outline for:
Title: {self.book_data['title']}
Premise: {self.book_data['premise']}
Setting: {self.book_data['setting']}
Characters: {', '.join(character_names)}
Themes: {', '.join(themes)}

For EACH chapter, provide EXACTLY 5-6 sentences that:
1. Clearly describe the main events
2. Show how events connect to previous and next chapters
3. Specify which characters are involved
4. Include the location/setting
5. Highlight any major character developments or conflicts

Each chapter summary MUST:
- Be exactly 5-6 complete sentences
- Create clear cause-and-effect links between chapters
- Show logical progression of the overall story
- Include specific character actions and motivations

Format the response as JSON with these exact fields:
{json.dumps(template, indent=2)}

Provide ONLY the JSON response, no other text.
"""

        response = self.generate_response(prompt)
        plot_data = self.parse_response_to_json(response, template)

        if plot_data and "chapters" in plot_data:
            self.book_data["plot"] = plot_data

            self.log_separator("PLOT OUTLINE CREATED")
            for chapter in plot_data["chapters"]:
                self.logger.info(f"\nChapter {chapter['number']}:")
                self.logger.info(f"Summary: {chapter['summary']}")
                self.logger.info(f"Characters: {', '.join(chapter['character_focus'])}")
                self.logger.info(f"Settings: {', '.join(chapter['settings'])}")

            return plot_data

        self.logger.error("Failed to create plot outline")
        return {}

    def generate_chapter(self, chapter_number: int, chapter_summary: str) -> Chapter:
        """Generate chapter strictly following plot outline with no refinement"""
        self.log_separator(f"GENERATING CHAPTER {chapter_number}")
        self.logger.info(f"Summary: {chapter_summary}")

        # Get previous chapter content for context
        previous_chapter_content = ""
        if chapter_number > 1:
            for chapter in self.book_data.get("chapters", []):
                if chapter["number"] == chapter_number - 1:
                    previous_chapter_content = "\n\n".join(
                        scene["content"] for scene in chapter["scenes"]
                    )
                    break

        # Build context with detailed plot points
        context = {
            "chapter_number": chapter_number,
            "total_chapters": len(self.book_data["plot"]["chapters"]),
            "summary": chapter_summary,
            "characters": [char["name"] for char in self.book_data["characters"]],
            "settings": self.book_data["plot"]["chapters"][chapter_number - 1]["settings"],
            "key_points": self.book_data["plot"]["chapters"][chapter_number - 1]["key_points"]
        }

        # Build generation prompt
        prompt = f"""Write Chapter {context['chapter_number']} following this exact summary:
{context['summary']}

Key story points that MUST be included:
{json.dumps(context['key_points'], indent=2)}

Characters to focus on: {', '.join(context['characters'])}
Settings: {', '.join(context['settings'])}

{'Previous chapter content for context:' + previous_chapter_content if previous_chapter_content else ''}

Requirements:
1. Follow the summary and key points EXACTLY
2. Maintain consistent character behavior
3. Create natural transitions between scenes
4. Include necessary descriptions and dialogue
5. Stay within {self.min_words}-{self.max_words} words

Write the complete chapter content directly.
"""

        content = self.generate_response(prompt)
        scenes = self._parse_scenes(content)

        chapter = Chapter(
            number=chapter_number,
            title=f"Chapter {chapter_number}",
            summary=chapter_summary,
            scenes=scenes,
            word_count=len(content.split())
        )

        self.book_data["chapters"].append(chapter.to_dict())
        self.logger.info(f"Chapter {chapter_number} completed: {chapter.word_count} words")
        return chapter

    def _build_chapter_context(self, chapter_num: int, summary: str) -> Dict:
        """Build rich context for chapter generation including full previous chapter"""
        context = {
            "chapter_number": chapter_num,
            "total_chapters": len(self.book_data["plot"]["chapters"]),
            "summary": summary,
            "previous_chapter_content": self._get_previous_chapter_content(chapter_num),
            "characters": self.book_data["characters"],
            "plot_points": self.book_data["plot"]["chapters"][chapter_num - 1],
            "themes": self.book_data.get("themes", [])
        }
        return context

    def _get_previous_chapter_content(self, chapter_num: int) -> str:
        """Get complete content of previous chapter"""
        if chapter_num <= 1:
            return ""
        
        for chapter in self.book_data["chapters"]:
            if chapter["number"] == chapter_num - 1:
                return "\n\n".join(scene["content"] for scene in chapter["scenes"])
        return ""

    def _parse_scenes(self, content: str) -> List[Scene]:
        """Parse content into coherent scenes"""
        # Split on scene breaks
        raw_scenes = re.split(r'\n\s*\n(?=\S)', content)

        scenes = []
        for raw_scene in raw_scenes:
            # Extract location if present
            location_match = re.search(r'\[Location: (.*?)\]', raw_scene)
            location = location_match.group(1) if location_match else None

            # Extract POV if present
            pov_match = re.search(r'\[POV: (.*?)\]', raw_scene)
            pov = pov_match.group(1) if pov_match else None

            # Clean scene content
            clean_content = raw_scene
            if location_match:
                clean_content = clean_content.replace(location_match.group(0), '')
            if pov_match:
                clean_content = clean_content.replace(pov_match.group(0), '')

            scenes.append(Scene(
                content=clean_content.strip(),
                location=location,
                pov_character=pov
            ))

        return scenes

    def export_book(self, output_dir: str = None) -> str:
        """Export book with complete manuscript and supporting files"""
        if output_dir is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_dir = f"generated_book_{timestamp}"

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Create directory structure
        chapters_dir = output_path / "chapters"
        chapters_dir.mkdir(exist_ok=True)
        resources_dir = output_path / "resources"
        resources_dir.mkdir(exist_ok=True)

        # Create complete manuscript
        manuscript_path = output_path / "manuscript.txt"
        with open(manuscript_path, "w", encoding='utf-8') as f:
            # Title page
            f.write(f"{self.book_data['title']}\n\n")
            
            # Table of contents
            f.write("Table of Contents\n\n")
            for chapter in self.book_data["chapters"]:
                f.write(f"Chapter {chapter['number']}: {chapter['title']}\n")
            f.write("\n\n")
            
            # Chapters
            for chapter in self.book_data["chapters"]:
                f.write(f"\nChapter {chapter['number']}: {chapter['title']}\n\n")
                for scene in chapter["scenes"]:
                    if scene["location"]:
                        f.write(f"[Location: {scene['location']}]\n")
                    if scene["pov_character"]:
                        f.write(f"[POV: {scene['pov_character']}]\n")
                    f.write(f"{scene['content']}\n\n")

        # Save metadata and supporting files (keeping existing functionality)
        metadata = {
            "title": self.book_data["title"],
            "premise": self.book_data["premise"],
            "setting": self.book_data["setting"],
            "themes": self.book_data.get("themes", []),
            "characters": self.book_data["characters"],
            "plot": self.book_data["plot"],
            "generation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "word_count": sum(ch["word_count"] for ch in self.book_data["chapters"]),
            "chapter_count": len(self.book_data["chapters"]),
            "generation_parameters": {
                "model": self.model_name,
                "minimum_chapter_words": self.min_words,
                "maximum_chapter_words": self.max_words
            }
        }

        metadata_path = output_path / "metadata.json"
        with open(metadata_path, "w", encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # Save character profiles
        characters_file = resources_dir / "characters.txt"
        with open(characters_file, "w", encoding='utf-8') as f:
            f.write("# Characters\n\n")
            for char in self.book_data["characters"]:
                f.write(f"## {char['name']}\n\n")
                f.write(f"Background: {char['background']}\n")
                f.write(f"Personality: {char['personality']}\n")
                f.write(f"Goals: {char['goals']}\n")
                if char['relationships']:
                    f.write("Relationships:\n")
                    for rel_name, rel_desc in char['relationships'].items():
                        f.write(f"- {rel_name}: {rel_desc}\n")
                f.write("\n")

        # Save plot outline
        plot_file = resources_dir / "plot_outline.txt"
        with open(plot_file, "w", encoding='utf-8') as f:
            f.write("# Plot Outline\n\n")
            for chapter in self.book_data["plot"]["chapters"]:
                f.write(f"## Chapter {chapter['number']}\n\n")
                f.write(f"**Summary:** {chapter['summary']}\n\n")
                f.write(f"**Characters:** {', '.join(chapter['character_focus'])}\n\n")
                f.write(f"**Settings:** {', '.join(chapter['settings'])}\n\n")
                f.write(f"**Key Points:**\n")
                for point in chapter['key_points']:
                    f.write(f"- {point}\n")
                f.write("\n")

        self.log_separator("BOOK EXPORTED")
        self.logger.info(f"Files saved to: {output_path}")
        return str(output_path)

def check_ollama() -> bool:
    """Check Ollama availability"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def print_ollama_error():
    """Print Ollama error message"""
    print("\nError: Ollama is not running or not accessible!")
    print("\nTo start Ollama:")
    print("1. Open a new terminal")
    print("2. Run: ollama serve")
    print("3. Wait for Ollama to start")
    print("4. Run this script again")

def main():
    print("=== Book Generation System ===")
    print("\nChecking Ollama availability...")

    if not check_ollama():
        print_ollama_error()
        sys.exit(1)

    try:
        # Initialize generator
        generator = BookGenerator(
            min_words=DEFAULT_CHAPTER_MIN_WORDS,
            max_words=DEFAULT_CHAPTER_MAX_WORDS
        )

        # Get user input
        user_input = generator.get_user_input()

        generator.log_separator("STARTING BOOK GENERATION")

        # Initialize book concept
        book_concept = generator.initialize_book(user_input)
        if not book_concept:
            raise ValueError("Failed to create book concept")

        # Create characters
        characters = generator.create_characters()
        if not characters:
            raise ValueError("Failed to create characters")

        # Create plot outline
        plot = generator.create_plot_outline(user_input["num_chapters"])
        if not plot:
            raise ValueError("Failed to create plot outline")

        # Generate chapters
        for i in range(user_input["num_chapters"]):
            chapter_num = i + 1
            chapter_summary = plot["chapters"][i]["summary"]
            
            try:
                # Generate chapter (no refinement)
                chapter = generator.generate_chapter(chapter_num, chapter_summary)
                
                # Progress update
                print(f"\nCompleted chapter {chapter_num}/{user_input['num_chapters']}")
                print(f"Word count: {chapter.word_count}")
                
            except Exception as e:
                generator.logger.error(f"Error in chapter {chapter_num}: {str(e)}")
                continue

            # Brief pause between chapters
            time.sleep(1)

        # Export completed book
        output_path = generator.export_book()

        generator.log_separator("GENERATION COMPLETED")
        generator.logger.info(f"Book saved to: {output_path}")

        print("\nGenerated files:")
        print(f"1. Complete manuscript: {output_path}/manuscript.txt")
        print(f"2. Character profiles: {output_path}/resources/characters.txt")
        print(f"3. Plot outline: {output_path}/resources/plot_outline.txt")
        print(f"4. Book metadata: {output_path}/metadata.json")

    except KeyboardInterrupt:
        # Handle user interruption
        generator.log_separator("GENERATION INTERRUPTED BY USER")
        print("\nSaving partial results...")
        try:
            if 'generator' in locals():
                output_path = generator.export_book("partial_book")
                print(f"Partial book saved to: {output_path}")
        except Exception as e:
            generator.logger.error(f"Failed to save partial results: {str(e)}")
        sys.exit(0)

    except Exception as e:
        # Handle unexpected errors
        if 'generator' in locals():
            generator.logger.error(f"Unexpected error: {str(e)}")
        print("\nAn error occurred during generation.")
        if hasattr(generator, 'logger'):
            print("Check the log file for details")
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)
