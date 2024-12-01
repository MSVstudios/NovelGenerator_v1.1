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
    "fast": "gemma2:27b",
    "creative": "gemma2:27b"
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

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "genre": self.genre,
            "target_audience": self.target_audience,
            "themes": self.themes,
            "characters": [char.to_dict() for char in self.characters],
            "chapters": [chapter.to_dict() for chapter in self.chapters],
            "metadata": self.metadata
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
            "metadata": {}
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
                    if attempt_number == 2:
                        # On the second attempt, use the previously generated content and prompt for more extensive content
                        prompt = f"""
                        The previous response was too short. Please generate a more extensive and detailed response based on the following content:
                        {complete_response}
                        """
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

    def _build_chapter_context(self, chapter_num: int, summary: str) -> Dict:
        """Build rich context for chapter generation"""
        return {
            "chapter_number": chapter_num,
            "total_chapters": len(self.book_data["plot"]["acts"][0]["key_events"]),
            "summary": summary,
            "previous_chapter": self._get_previous_chapter(chapter_num),
            "characters": self.book_data["characters"],
            "themes": self.book_data.get("themes", []),
            "style_notes": self.book_data.get("style_notes", ""),
            "character_arcs": self._get_character_arcs(chapter_num)
        }

    def _get_previous_chapter(self, chapter_num: int) -> Optional[Dict]:
        """Get previous chapter data if available"""
        if chapter_num <= 1:
            return None
        for chapter in self.book_data["chapters"]:
            if chapter["number"] == chapter_num - 1:
                return chapter
        return None

    def _get_character_arcs(self, chapter_num: int) -> Dict[str, str]:
        """Get character development arcs for current chapter"""
        arcs = {}
        total_chapters = len(self.book_data["plot"]["acts"][0]["key_events"])
        progress = chapter_num / total_chapters

        for character in self.book_data["characters"]:
            if progress < 0.3:
                stage = "introduction and establishment"
            elif progress < 0.6:
                stage = "development and challenges"
            elif progress < 0.9:
                stage = "growth and transformation"
            else:
                stage = "resolution and conclusion"
            arcs[character["name"]] = stage

        return arcs

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
        """Generate plot outline with improved structure and pacing"""
        self.log_separator("CREATING PLOT OUTLINE")
        self.logger.info(f"Planning {num_chapters} chapters")

        template = {
            "acts": [
                {
                    "act_number": 1,
                    "description": "",
                    "key_events": [""] * num_chapters,
                    "character_developments": {},
                    "themes_exploration": [],
                    "pacing_notes": ""
                }
            ],
            "subplot_threads": [],
            "story_arcs": {}
        }

        # Build context
        character_names = [char['name'] for char in self.book_data["characters"]]
        themes = self.book_data.get('themes', [])

        prompt = f"""Create a detailed {num_chapters}-chapter plot outline for:
Title: {self.book_data['title']}
Premise: {self.book_data['premise']}
Setting: {self.book_data['setting']}
Characters: {', '.join(character_names)}
Themes: {', '.join(themes)}

Requirements:
1. Create EXACTLY {num_chapters} key events (one per chapter)
2. Divide story into three acts with clear narrative progression
3. Include character development arcs for all main characters
4. Weave subplot threads that enhance the main plot
5. Ensure consistent pacing and tension
6. Explore and develop all main themes
7. Build towards a satisfying climax
8. Balance action, dialogue, and introspection

Format the response as JSON with these exact fields:
{json.dumps(template, indent=2)}

Each key_events array MUST contain exactly {num_chapters} events.
Provide ONLY the JSON response, no other text.
"""

        response = self.generate_response(prompt)
        plot_data = self.parse_response_to_json(response, template)

        if plot_data and "acts" in plot_data:
            # Validate and balance acts
            plot_data = self._balance_plot_structure(plot_data, num_chapters)

            self.book_data["plot"] = plot_data

            self.log_separator("PLOT OUTLINE CREATED")
            for act in plot_data["acts"]:
                self.logger.info(f"\nAct {act['act_number']}")
                self.logger.info(f"Description: {act['description']}")
                for i, event in enumerate(act['key_events'], 1):
                    self.logger.info(f"Chapter {i}: {event}")

            return plot_data

        self.logger.error("Failed to create plot outline")
        return {}

    def _balance_plot_structure(self, plot_data: Dict, num_chapters: int) -> Dict:
        """Balance plot structure across acts"""
        acts = plot_data["acts"]
        if not isinstance(acts, list):
            acts = [acts]

        # Calculate ideal act lengths based on total chapters
        if num_chapters <= 3:
            # For very short stories (3 chapters)
            ideal_lengths = [1, 1, 1]  # One chapter per act
        else:
            # Standard distribution but adjusted for shorter works
            first_act = max(1, round(num_chapters * 0.25))
            third_act = max(1, round(num_chapters * 0.25))
            second_act = num_chapters - first_act - third_act
            ideal_lengths = [first_act, second_act, third_act]

        # Adjust to match total chapters
        while sum(ideal_lengths) < num_chapters:
            ideal_lengths[1] += 1
        while sum(ideal_lengths) > num_chapters:
            if ideal_lengths[1] > 1:
                ideal_lengths[1] -= 1
            elif ideal_lengths[0] > 1:
                ideal_lengths[0] -= 1
            else:
                ideal_lengths[2] -= 1

        # Redistribute events
        current_chapter = 0
        adjusted_acts = []

        for i, length in enumerate(ideal_lengths):
            act_events = []
            for _ in range(length):
                if current_chapter < len(plot_data["acts"][0]["key_events"]):
                    act_events.append(plot_data["acts"][0]["key_events"][current_chapter])
                    current_chapter += 1
                else:
                    act_events.append(f"Chapter {current_chapter + 1} events")
                    current_chapter += 1

            adjusted_acts.append({
                "act_number": i + 1,
                "description": acts[0]["description"] if i == 0 else f"Act {i + 1}",
                "key_events": act_events,
                "character_developments": acts[0].get("character_developments", {}),
                "themes_exploration": acts[0].get("themes_exploration", []),
                "pacing_notes": acts[0].get("pacing_notes", "")
            })

        plot_data["acts"] = adjusted_acts
        return plot_data

    def generate_chapter(self, chapter_number: int, chapter_summary: str) -> Chapter:
        """Generate chapter with one retry attempt if needed"""
        self.log_separator(f"GENERATING CHAPTER {chapter_number}")
        self.logger.info(f"Summary: {chapter_summary}")

        # First attempt
        context = self._build_chapter_context(chapter_number, chapter_summary)
        prompt = self._build_chapter_prompt(context)
        content = self.generate_response(prompt)
        
        # Validate first attempt
        word_count = len(content.split())
        if word_count < self.min_words:
            self.logger.warning(f"First attempt for Chapter {chapter_number} is too short ({word_count} words). Attempting one retry.")
            
            # Build improvement prompt using first attempt
            improvement_prompt = f"""
            The previous version of Chapter {chapter_number} needs improvement. Here's what needs to be enhanced:
            
            1. Expand the content to meet minimum length ({self.min_words} words)
            2. Add more detailed descriptions and character interactions
            3. Maintain consistency with the story and characters
            
            Previous version:
            {content}
            
            Chapter Summary: {chapter_summary}
            
            Please provide an improved version that maintains the same story elements but with better development and more detail.
            """
            
            # Second and final attempt
            content = self.generate_response(improvement_prompt)
            word_count = len(content.split())
            
            if word_count < self.min_words:
                self.logger.warning(f"Second attempt still short ({word_count} words). Using best version.")
    
        # Create scenes from the best version
        scenes = self._parse_scenes(content)
        
        # Create chapter
        chapter = Chapter(
            number=chapter_number,
            title=f"Chapter {chapter_number}",
            summary=chapter_summary,
            scenes=scenes,
            word_count=len(content.split())
        )
        
        # Store chapter regardless of validation
        self.book_data["chapters"].append(chapter.to_dict())
        self.logger.info(f"Chapter {chapter_number} completed: {chapter.word_count} words")
        return chapter

    def refine_chapter(self, chapter: Chapter) -> Chapter:
        """Refine chapter with one improvement attempt"""
        self.log_separator(f"REFINING CHAPTER {chapter.number}")

        # Check if refinement is needed
        original_content = "\n".join(scene.content for scene in chapter.scenes)
        weak_points = self._analyze_chapter_weak_points(original_content)
        
        if not weak_points:
            return chapter

        # Build refinement prompt
        refinement_prompt = f"""
        Improve this chapter while maintaining its core story and character elements:

        Original Chapter:
        {original_content}

        Areas to improve:
        {json.dumps(weak_points, indent=2)}

        Requirements:
        1. Keep the same plot points and character interactions
        2. Enhance descriptions and dialogue
        3. Maintain consistent tone and style
        4. Ensure proper pacing
        
        Word count target: {self.min_words}-{self.max_words} words
        """

        # Generate refined content - single attempt
        refined = self.generate_response(refinement_prompt, temperature=0.7)

        # Create new chapter from refined content
        refined_scenes = self._parse_scenes(refined)
        refined_word_count = len(refined.split())
        
        # Use refined version only if it's better
        if refined_word_count >= self.min_words and refined_word_count <= self.max_words:
            refined_chapter = Chapter(
                number=chapter.number,
                title=chapter.title,
                summary=chapter.summary,
                scenes=refined_scenes,
                word_count=refined_word_count
            )
            
            # Update storage with refined version
            for i, stored_chapter in enumerate(self.book_data["chapters"]):
                if stored_chapter["number"] == chapter.number:
                    self.book_data["chapters"][i] = refined_chapter.to_dict()
                    break
                    
            self.logger.info(f"Chapter {chapter.number} successfully refined: {refined_word_count} words")
            return refined_chapter
        
        self.logger.warning(f"Refinement didn't improve chapter {chapter.number}. Keeping original version.")
        return chapter

    def _analyze_chapter_weak_points(self, content: str) -> Dict:
        """Analyze chapter content for weak points"""
        # Implement analysis logic here
        # For simplicity, let's assume it returns some dummy weak points
        return {
            "description_richness": False,
            "dialogue_quality": False,
            "theme_consistency": False
        }

    def _build_refinement_prompt(self, chapter: Chapter, weak_points: Dict) -> str:
        """Build prompt for refining a chapter"""
        # Not used in the updated method, but kept for potential future use
        pass

    def _build_chapter_prompt(self, context: Dict) -> str:
        """Build detailed prompt for chapter generation"""
        return f"""Write Chapter {context['chapter_number']} of {context['total_chapters']}:

Title: {self.book_data['title']}
Summary: {context['summary']}
Previous Chapter: {context['previous_chapter']['summary'] if context['previous_chapter'] else 'None'}
Style Notes: {context['style_notes']}
Themes to Explore: {', '.join(context['themes'])}

Character Development Stage:
{json.dumps(context['character_arcs'], indent=2)}

Requirements:
1. Follow established style and tone
2. Maintain character consistency
3. Write natural, engaging dialogue
4. Include vivid sensory descriptions
5. Create smooth scene transitions
6. Advance character development
7. Explore relevant themes
8. Maintain narrative tension

Target Length: {self.min_words}-{self.max_words} words

Write the complete chapter content directly.
"""

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

    def _expand_chapter_content(self, content: str, context: Dict) -> str:
        """Expand chapter content to meet minimum length"""
        self.logger.info("Expanding chapter content")

        # Analyze current content
        analysis = self._analyze_chapter_content(content)

        # Build expansion prompt
        expand_prompt = f"""
        Expand this chapter by adding:
        1. More detailed sensory descriptions
        2. Natural dialogue and character interactions
        3. Character internal monologue and emotions
        4. Smoother scene transitions
        5. Deeper exploration of themes
        Current content:
        {content}

        Context:
        {json.dumps(context, indent=2)}

        Target word count: {self.min_words}-{self.max_words}
        """

        # Generate expanded content
        expanded = self.generate_response(expand_prompt, temperature=0.8)

        # Validate length
        if len(expanded.split()) < self.min_words:
            self.logger.warning("Expansion failed to meet minimum length")
            return self._expand_chapter_content(expanded, context)

        return expanded

    def _analyze_chapter_content(self, content: str) -> Dict:
        """Analyze chapter content for weak points"""
        analysis = {
            "word_count": len(content.split()),
            "dialogue_count": len(re.findall(r'"([^"]*)"', content)),
            "scene_count": len(re.split(r'\n\s*\n(?=\S)', content)),
            "description_score": self._calculate_description_score(content),
            "character_mentions": self._count_character_mentions(content),
            "theme_coverage": self._check_theme_coverage(content)
        }

        return analysis

    def _calculate_description_score(self, content: str) -> float:
        """Calculate descriptive richness score"""
        sensory_words = {
            'sight': ['saw', 'looked', 'watched', 'observed', 'gazed'],
            'sound': ['heard', 'listened', 'echoed', 'whispered', 'roared'],
            'touch': ['felt', 'touched', 'brushed', 'grasped', 'held'],
            'smell': ['smelled', 'scented', 'wafted', 'lingered'],
            'taste': ['tasted', 'savored', 'bitter', 'sweet']
        }

        score = 0
        words = content.lower().split()
        total_words = len(words)

        for sense_words in sensory_words.values():
            for word in sense_words:
                score += content.lower().count(word)

        return score / total_words if total_words > 0 else 0

    def _count_character_mentions(self, content: str) -> Dict[str, int]:
        """Count mentions of each character"""
        mentions = {}
        for character in self.book_data["characters"]:
            name_variants = self._get_name_variants(character["name"])
            count = 0
            for variant in name_variants:
                count += len(re.findall(rf'\b{variant}\b', content, re.IGNORECASE))
            mentions[character["name"]] = count

        return mentions

    def _get_name_variants(self, name: str) -> List[str]:
        """Get possible variants of character name"""
        parts = name.split()
        variants = [name]  # Full name

        if len(parts) > 1:
            variants.append(parts[0])  # First name
            variants.append(parts[-1])  # Last name

        return variants

    def _check_theme_coverage(self, content: str) -> Dict[str, bool]:
        """Check coverage of book themes"""
        coverage = {}
        for theme in self.book_data.get("themes", []):
            # Create theme keywords
            keywords = self._get_theme_keywords(theme)
            covered = False
            for keyword in keywords:
                if re.search(rf'\b{keyword}\b', content, re.IGNORECASE):
                    covered = True
                    break
            coverage[theme] = covered

        return coverage

    def _get_theme_keywords(self, theme: str) -> List[str]:
        """Generate keywords for theme detection"""
        # Split theme into words
        words = theme.lower().split()
        keywords = [theme.lower()]  # Full theme

        # Add individual significant words
        for word in words:
            if len(word) > 3:  # Skip short words
                keywords.append(word)

        # Add common variations
        for word in words:
            # Add plurals
            if word.endswith('y'):
                keywords.append(word[:-1] + 'ies')
            else:
                keywords.append(word + 's')

            # Add -ing forms
            if word.endswith('e'):
                keywords.append(word[:-1] + 'ing')
            else:
                keywords.append(word + 'ing')

        return keywords

    def _validate_chapter(self, chapter: Chapter) -> bool:
        """Validate chapter meets quality requirements"""
        # Check length
        if not (self.min_words <= chapter.word_count <= self.max_words):
            self.logger.warning(f"Chapter length {chapter.word_count} words outside target range")
            return False

        # Check theme consistency
        themes_covered = self._check_theme_coverage("\n".join(
            scene.content for scene in chapter.scenes
        ))
        if not all(themes_covered.values()):
            self.logger.warning("Not all themes covered in chapter")
            return False

        # Check character consistency
        if not self._check_character_consistency(chapter):
            self.logger.warning("Character inconsistencies detected")
            return False

        # Check dialogue quality
        if not self._check_dialogue_quality(chapter):
            self.logger.warning("Dialogue quality issues detected")
            return False

        return True

    def _check_character_consistency(self, chapter: Chapter) -> bool:
        """Check character names and voices are consistent"""
        chapter_text = "\n".join(scene.content for scene in chapter.scenes)
        characters = self.book_data["characters"]

        # Check names consistent
        for char in characters:
            name_variants = self._get_name_variants(char["name"])
            found_variants = set()
            for variant in name_variants:
                if re.search(rf'\b{variant}\b', chapter_text, re.IGNORECASE):
                    found_variants.add(variant)
            if len(found_variants) > 1:
                self.logger.warning(f"Inconsistent naming for character: {char['name']}")
                return False

        return True

    def _check_dialogue_quality(self, chapter: Chapter) -> bool:
        """Check dialogue is natural and character-appropriate"""
        chapter_text = "\n".join(scene.content for scene in chapter.scenes)

        # Extract dialogue
        dialogue = re.findall(r'"([^"]*)"', chapter_text)

        if len(dialogue) < 5:
            self.logger.warning("Insufficient dialogue")
            return False

        # Check dialogue length variation
        lengths = [len(d.split()) for d in dialogue]
        if max(lengths) / min(lengths) < 2:
            self.logger.warning("Dialogue lacks natural variation")
            return False

        return True

    def _balance_plot_structure(self, plot_data: Dict, num_chapters: int) -> Dict:
        """Balance plot structure across acts"""
        acts = plot_data["acts"]
        if not isinstance(acts, list):
            acts = [acts]

        # Calculate ideal act lengths based on total chapters
        if num_chapters <= 3:
            # For very short stories (3 chapters)
            ideal_lengths = [1, 1, 1]  # One chapter per act
        else:
            # Standard distribution but adjusted for shorter works
            first_act = max(1, round(num_chapters * 0.25))
            third_act = max(1, round(num_chapters * 0.25))
            second_act = num_chapters - first_act - third_act
            ideal_lengths = [first_act, second_act, third_act]

        # Adjust to match total chapters
        while sum(ideal_lengths) < num_chapters:
            ideal_lengths[1] += 1
        while sum(ideal_lengths) > num_chapters:
            if ideal_lengths[1] > 1:
                ideal_lengths[1] -= 1
            elif ideal_lengths[0] > 1:
                ideal_lengths[0] -= 1
            else:
                ideal_lengths[2] -= 1

        # Redistribute events
        current_chapter = 0
        adjusted_acts = []

        for i, length in enumerate(ideal_lengths):
            act_events = []
            for _ in range(length):
                if current_chapter < len(plot_data["acts"][0]["key_events"]):
                    act_events.append(plot_data["acts"][0]["key_events"][current_chapter])
                    current_chapter += 1
                else:
                    act_events.append(f"Chapter {current_chapter + 1} events")
                    current_chapter += 1

            adjusted_acts.append({
                "act_number": i + 1,
                "description": acts[0]["description"] if i == 0 else f"Act {i + 1}",
                "key_events": act_events,
                "character_developments": acts[0].get("character_developments", {}),
                "themes_exploration": acts[0].get("themes_exploration", []),
                "pacing_notes": acts[0].get("pacing_notes", "")
            })

        plot_data["acts"] = adjusted_acts
        return plot_data

    def _analyze_chapter_content(self, content: str) -> Dict:
        """Analyze chapter content for weak points"""
        analysis = {
            "word_count": len(content.split()),
            "dialogue_count": len(re.findall(r'"([^"]*)"', content)),
            "scene_count": len(re.split(r'\n\s*\n(?=\S)', content)),
            "description_score": self._calculate_description_score(content),
            "character_mentions": self._count_character_mentions(content),
            "theme_coverage": self._check_theme_coverage(content)
        }

        return analysis

    def _analyze_chapter_weak_points(self, content: str) -> Dict:
        """Analyze chapter content for weak points"""
        # Implement analysis logic here
        # For simplicity, let's assume it returns some dummy weak points
        return {
            "description_richness": False,
            "dialogue_quality": False,
            "theme_consistency": False
        }

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
            for act in self.book_data["plot"]["acts"]:
                f.write(f"## Act {act['act_number']}\n\n")
                f.write(f"Description: {act['description']}\n\n")
                f.write("Key Events:\n")
                for i, event in enumerate(act['key_events'], 1):
                    f.write(f"{i}. {event}\n")
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

            # Get chapter summary
            events = []
            for act in plot["acts"]:
                events.extend(act.get("key_events", []))

            chapter_summary = events[i] if i < len(events) else f"Chapter {chapter_num} events"

            try:
                # Generate and refine chapter
                chapter = generator.generate_chapter(chapter_num, chapter_summary)
                refined_chapter = generator.refine_chapter(chapter)

                # Progress update
                print(f"\nCompleted chapter {chapter_num}/{user_input['num_chapters']}")
                print(f"Word count: {refined_chapter.word_count}")

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
        print(f"2. Chapter files: {output_path}/chapters/")
        print(f"3. Character profiles: {output_path}/resources/characters.txt")
        print(f"4. Plot outline: {output_path}/resources/plot_outline.txt")
        print(f"5. Book metadata: {output_path}/metadata.json")

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
