import json
from typing import Dict, List, Optional, Any, Union, Set
import requests
import time
from dataclasses import dataclass, field
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
    log_dir = Path("generation_logs")
    log_dir.mkdir(exist_ok=True)
    
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"generation_{current_time}.log"
    
    logger = logging.getLogger('BookGenerator')
    logger.setLevel(logging.DEBUG)

    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    console_formatter = ColoredFormatter('%(levelname)s - %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# New continuity tracking classes
@dataclass
class LocationState:
    character_locations: Dict[str, str] = field(default_factory=dict)
    valid_transitions: Dict[str, List[str]] = field(default_factory=dict)
    travel_time: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def validate_movement(self, character: str, new_location: str, time_passed: int = 1) -> bool:
        current = self.character_locations.get(character)
        if not current:
            return True
            
        if new_location not in self.valid_transitions.get(current, []):
            return False
            
        required_time = self.travel_time.get(current, {}).get(new_location, 1)
        return time_passed >= required_time

    def add_location_path(self, from_loc: str, to_loc: str, time_required: int = 1):
        if from_loc not in self.valid_transitions:
            self.valid_transitions[from_loc] = []
        self.valid_transitions[from_loc].append(to_loc)
        
        if from_loc not in self.travel_time:
            self.travel_time[from_loc] = {}
        self.travel_time[from_loc][to_loc] = time_required

@dataclass
class PlotThread:
    name: str
    status: str  # 'active', 'resolved', 'abandoned'
    related_characters: List[str]
    key_events: List[str]
    dependencies: List[str] = field(default_factory=list)
    resolution_conditions: List[str] = field(default_factory=list)

    def can_resolve(self, completed_events: List[str]) -> bool:
        return all(event in completed_events for event in self.resolution_conditions)

# Data models
@dataclass
class Character:
    name: str
    background: str
    personality: str
    goals: str
    relationships: Dict[str, str]
    current_location: str = field(default="")
    active_goals: List[str] = field(default_factory=list)
    character_arc_stage: str = field(default="introduction")
    motivation_strength: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "background": self.background,
            "personality": self.personality,
            "goals": self.goals,
            "relationships": self.relationships,
            "current_location": self.current_location,
            "active_goals": self.active_goals,
            "character_arc_stage": self.character_arc_stage,
            "motivation_strength": self.motivation_strength
        }

@dataclass
class Scene:
    content: str
    pov_character: Optional[str] = None 
    location: Optional[str] = None
    time_passed: int = 0
    active_characters: List[str] = field(default_factory=list)
    plot_threads_advanced: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "pov_character": self.pov_character,
            "location": self.location,
            "time_passed": self.time_passed,
            "active_characters": self.active_characters,
            "plot_threads_advanced": self.plot_threads_advanced
        }

@dataclass
class Chapter:
    number: int
    title: str
    summary: str
    scenes: List[Scene]
    word_count: int
    active_plot_threads: List[str] = field(default_factory=list)
    character_developments: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "number": self.number,
            "title": self.title,
            "summary": self.summary,
            "scenes": [scene.to_dict() for scene in self.scenes],
            "word_count": self.word_count,
            "active_plot_threads": self.active_plot_threads,
            "character_developments": self.character_developments
        }

@dataclass
class Book:
    title: str
    genre: str
    target_audience: str
    themes: List[str]
    characters: List[Character]
    chapters: List[Chapter] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    plot_threads: Dict[str, PlotThread] = field(default_factory=dict)
    world_state: LocationState = field(default_factory=LocationState)
    timeline: Dict[int, List[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "genre": self.genre,
            "target_audience": self.target_audience,
            "themes": self.themes,
            "characters": [char.to_dict() for char in self.characters],
            "chapters": [chapter.to_dict() for chapter in self.chapters],
            "metadata": self.metadata,
            "plot_threads": {k: vars(v) for k, v in self.plot_threads.items()},
            "world_state": vars(self.world_state),
            "timeline": self.timeline
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
        
        self.book = Book(
            title="",
            genre="",
            target_audience="",
            themes=[],
            characters=[]
        )
        
        self.location_state = LocationState()
        self.plot_threads = {}
        self.completed_events = []
        self.timeline = {}
        self.current_time = 0
        self.character_arcs = {}
        self.book_data = self.book.to_dict()

    def log_separator(self, message: str) -> None:
        """Print log separator with message"""
        separator = f"\n{'='*50}\n{message}\n{'='*50}\n"
        self.logger.info(separator)

    def get_user_input(self) -> Dict[str, Any]:
        """Get validated user input for book generation"""
        print("\n=== Book Generation Setup ===")

        genre = self._get_validated_input(
            "Enter book genre (e.g., Science Fiction, Fantasy, Romance): ",
            lambda x: len(x.strip()) > 0
        )

        target_audience = self._get_validated_input(
            "Enter target audience (e.g., Young Adult, Adult, Children): ",
            lambda x: len(x.strip()) > 0
        )

        print("\nEnter main themes (one per line). Press Enter twice to finish:")
        themes = []
        while True:
            theme = input().strip()
            if not theme:
                if themes:
                    break
                print("Please enter at least один theme")
                continue
            themes.append(theme)

        num_chapters = self._get_validated_input(
            "\nEnter desired number of chapters (3-30): ",
            lambda x: x.isdigit() and 3 <= int(x) <= 30,
            "Please enter a number between 3 and 30",
            transform=int
        )

        print("\nEnter any specific requirements (one per line). Press Enter twice to finish:")
        requirements = []
        while True:
            req = input().strip()
            if not req and requirements:
                break
            if req:
                requirements.append(req)

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
            "Please enter a number between 1 and 4",
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
        """Get validated input with proper error handling"""
        while True:
            try:
                user_input = input(prompt).strip()
                if validator(user_input):
                    try:
                        return transform(user_input)
                    except Exception as e:
                        print(f"Error processing input: {str(e)}")
                        print(error_message)
                else:
                    print(error_message)
            except Exception as e:
                print(f"Input error: {str(e)}")
                print(error_message)

    def _fix_character_locations(self, characters_data: Dict) -> Dict:
        """Fix invalid character locations with proper error handling"""
        if not isinstance(characters_data, dict):
            return {"characters": []}
            
        valid_locations = list(self.location_state.valid_transitions.keys())
        if not valid_locations:
            valid_locations = ["starting_location"]
            
        if "characters" not in characters_data:
            return {"characters": []}
            
        for char in characters_data["characters"]:
            if not isinstance(char, dict):
                continue
                
            if "current_location" not in char or not char["current_location"] or char["current_location"] not in valid_locations:
                char["current_location"] = valid_locations[0]
                    
        return characters_data

    def _find_valid_path(self, start: str, end: str) -> List[str]:
        """Find valid path between locations with proper validation"""
        if not isinstance(start, str) or not isinstance(end, str):
            return []
            
        if start == end:
            return [start]
            
        if not hasattr(self, 'location_state') or not hasattr(self.location_state, 'valid_transitions'):
            return []
            
        queue = [(start, [start])]
        visited = {start}
        
        while queue:
            current, path = queue.pop(0)
            
            # Safely get transitions
            transitions = self.location_state.valid_transitions.get(current, [])
            if not isinstance(transitions, list):
                continue
                
            for next_loc in transitions:
                if not isinstance(next_loc, str):
                    continue
                    
                if next_loc == end:
                    return path + [end]
                    
                if next_loc not in visited:
                    visited.add(next_loc)
                    queue.append((next_loc, path + [next_loc]))
                        
        return []

    def _extract_locations(self, event: str) -> Dict[str, str]:
        """Extract character location changes with proper validation"""
        if not isinstance(event, str):
            return {}
            
        locations = {}
        
        if not hasattr(self, 'book_data') or not isinstance(self.book_data, dict):
            return locations
            
        characters = self.book_data.get("characters", [])
        if not isinstance(characters, list):
            return locations
            
        valid_locations = set()
        if hasattr(self, 'location_state') and hasattr(self.location_state, 'valid_transitions'):
            valid_locations = set(self.location_state.valid_transitions.keys())
        
        for char in characters:
            if not isinstance(char, dict):
                continue
                
            char_name = char.get("name")
            if not char_name or not isinstance(char_name, str):
                continue
                
            if char_name in event:
                for loc in valid_locations:
                    if loc in event:
                        locations[char_name] = loc
                        break
                        
        return locations

    def generate_response(
        self,
        prompt: str,
        retries: int = DEFAULT_RETRY_COUNT,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
        attempt_number: int = 1
    ) -> str:
        self.log_separator("PROMPT")
        self.logger.info(prompt)
        
        for attempt in range(retries):
            try:
                self.log_separator("GENERATING RESPONSE")
                self.logger.info(f"Attempt {attempt + 1}/{retries}")
                
                payload = {
                    "model": self.model_name,
                    "prompt": prompt + "\nProvide ONLY raw JSON without any markdown formatting, code blocks or extra text.",
                    "stream": True,
                    "temperature": temperature,
                    "top_p": top_p,
                    "context_length": 8192
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
                        prompt = f"""
                        The previous response was too short. Please generate a more extensive and detailed response based on the following content:
                        {complete_response}
                        """
                    continue
                break
            
        self.logger.error("All attempts failed")
        return ""

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
            "audience": user_input["target_audience"],
            "locations": [],  # Added for location tracking
            "initial_plot_threads": []  # Added for plot thread tracking
        }

        style_descriptions = {
            1: "descriptive and detailed, with rich world-building and atmosphere",
            2: "fast-paced and dynamic, focusing on action and momentum",
            3: "character-focused, with deep emotional development and relationships",
            4: "plot-driven, with intricate storylines and twists"
        }
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
3. A rich and detailed setting description with key locations and their connections
4. A complex main conflict that drives the story
5. Specific style notes for maintaining consistent tone and atmosphere
6. List of key locations and their relationships/travel times
7. Initial major plot threads that will drive the story

Your response MUST maintain thematic consistency with the provided themes.
Format the response as JSON with these exact fields:
{json.dumps(template, indent=2)}

Provide ONLY the JSON response, no other text.
"""

        response = self.generate_response(prompt)
        book_concept = self.parse_response_to_json(response, template)
        
        if book_concept and book_concept.get("title"):
            self.book.title = book_concept["title"]
            self.book.genre = user_input["genre"]
            self.book.target_audience = user_input["target_audience"]
            self.book.themes = user_input["themes"]
            self.book.metadata = {
                "premise": book_concept.get("premise", ""),
                "setting": book_concept.get("setting", ""),
                "main_conflict": book_concept.get("main_conflict", ""),
                "style_notes": book_concept.get("style_notes", ""),
            }
            
            # Initialize location tracking
            if "locations" in book_concept:
                for loc in book_concept["locations"]:
                    if isinstance(loc, dict) and "connections" in loc:
                        for conn in loc["connections"]:
                            if isinstance(conn, dict):
                                self.location_state.add_location_path(
                                    loc["name"],
                                    conn.get("to", ""),
                                    conn.get("travel_time", 1)
                                )
                                
            # Initialize plot threads
            if "initial_plot_threads" in book_concept:
                for thread in book_concept["initial_plot_threads"]:
                    if isinstance(thread, dict):
                        self.plot_threads[thread.get("name", "")] = PlotThread(
                            name=thread.get("name", ""),
                            status="active",
                            related_characters=thread.get("characters", []),
                            key_events=[],
                            dependencies=thread.get("dependencies", []),
                            resolution_conditions=thread.get("resolution_conditions", [])
                        )
                        
            self.log_separator("BOOK CONCEPT CREATED")
            self.logger.info(f"Title: {self.book.title}")
            self.logger.info(f"Premise: {self.book.metadata.get('premise', '')}")
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
                    "relationships": {},
                    "current_location": "",
                    "active_goals": [],
                    "character_arc_stage": "introduction",
                    "motivation_strength": {}
                }
            ]
        }
        
        prompt = f"""Create compelling characters for this book:
Title: {self.book.title}
Premise: {self.book.metadata.get('premise', '')}
Setting: {self.book.metadata.get('setting', '')}
Themes: {', '.join(self.book.themes)}
Available Locations: {', '.join(self.location_state.valid_transitions.keys())}
Active Plot Threads: {', '.join(self.plot_threads.keys())}

Create 3-5 unique and detailed characters that:
1. Have distinctive names fitting the setting
2. Possess rich personal backgrounds
3. Display clear personality traits
4. Pursue compelling goals aligned with the themes
5. Have meaningful relationships with other characters
6. Start in logical initial locations
7. Connect to active plot threads through their goals
8. Show potential for growth and development

Each character should:
- Reflect the story's themes
- Have clear motivations with quantified strength (0.0-1.0)
- Present internal and external conflicts
- Show potential for growth
- Have distinct voice and mannerisms
- Be placed in a valid starting location

Format the response as JSON with these exact fields:
{json.dumps(template, indent=2)}

Provide ONLY the JSON response, no other text.
"""

        response = self.generate_response(prompt)
        
        try:
            characters_data = self.parse_response_to_json(response, template)
            if characters_data and "characters" in characters_data:
                # Validate character relationships and locations
                if not self._validate_character_relationships(characters_data["characters"]):
                    self.logger.warning("Character relationships need adjustment")
                    characters_data = self._fix_character_relationships(characters_data)
                    
                if not self._validate_character_locations(characters_data["characters"]):
                    self.logger.warning("Character locations need adjustment")
                    characters_data = self._fix_character_locations(characters_data)
                    
                characters = []
                for char_data in characters_data["characters"]:
                    character = Character(
                        name=char_data["name"],
                        background=char_data["background"],
                        personality=char_data["personality"],
                        goals=char_data["goals"],
                        relationships=char_data["relationships"],
                        current_location=char_data["current_location"],
                        active_goals=char_data["active_goals"],
                        character_arc_stage=char_data["character_arc_stage"],
                        motivation_strength=char_data["motivation_strength"]
                    )
                    characters.append(character)
                    
                self.book.characters = characters
                
                # Initialize character arcs
                for character in characters:
                    self.character_arcs[character.name] = {
                        "stage": "introduction",
                        "development_points": 0,
                        "completed_goals": [],
                        "relationship_changes": {},
                        "location_history": [character.current_location],
                        "recent_developments": []
                    }
                    
                self.log_separator("CHARACTERS CREATED")
                for character in characters:
                    self.logger.info(f"\nCharacter: {character.name}")
                    self.logger.info(f"Location: {character.current_location}")
                    self.logger.info(f"Background: {character.background}")
                    self.logger.info(f"Goals: {character.goals}")
                    self.logger.info("Active Goals:")
                    for goal in character.active_goals:
                        self.logger.info(f"- {goal}")
                    self.logger.info("Relationships:")
                    for rel_name, rel_desc in character.relationships.items():
                        self.logger.info(f"- {rel_name}: {rel_desc}")
                    self.logger.info("Motivation Strengths:")
                    for mot, strength in character.motivation_strength.items():
                        self.logger.info(f"- {mot}: {strength}")
                        
                return characters
            
        except Exception as e:
            self.logger.error(f"Error processing characters: {str(e)}")
            
        return []
        
    def create_plot_outline(self, num_chapters: int) -> Dict:
        """Generate plot outline with improved structure and pacing"""
        self.log_separator("CREATING PLOT OUTLINE")
        self.logger.info(f"Planning {num_chapters} chapters")
        
        template = {
            "acts": [
                {
                    "act_number": 1,
                    "description": "",
                    "key_events": ["" for _ in range(num_chapters)],
                    "character_developments": {},
                    "themes_exploration": [],
                    "pacing_notes": "",
                    "location_changes": {},
                    "required_plot_progressions": []
                }
            ],
            "subplot_threads": [],
            "story_arcs": {},
            "timeline_markers": []
        }
        
        character_names = [char.name for char in self.book.characters]
        active_plots = [name for name, thread in self.plot_threads.items() if thread.status == "active"]
        
        prompt = f"""Create a detailed {num_chapters}-chapter plot outline for:
Title: {self.book.title}
Premise: {self.book.metadata.get('premise', '')}
Setting: {self.book.metadata.get('setting', '')}
Characters: {', '.join(character_names)}
Themes: {', '.join(self.book.themes)}
Active Plot Threads: {', '.join(active_plots)}

Requirements:
1. Create EXACTLY {num_chapters} key events (one per chapter)
2. Divide story into three acts with clear narrative progression
3. Include character development arcs for all main characters
4. Advance all active plot threads logically
5. Ensure consistent pacing and tension
6. Explore and develop all main themes
7. Build towards a satisfying climax
8. Consider travel times between locations
9. Balance character focus and plot advancement

Timeline markers should track:
- Character locations and movements
- Plot thread progression
- Key relationship changes
- Theme development points

Format the response as JSON with these exact fields:
{json.dumps(template, indent=2)}

Each key_events array MUST contain exactly {num_chapters} events.
Provide ONLY the JSON response, no other text.
"""

        response = self.generate_response(prompt)
        plot_data = self.parse_response_to_json(response, template)
        
        if plot_data and "acts" in plot_data:
            plot_data = self._balance_plot_structure(plot_data, num_chapters)
            
            # Initialize timeline from plot data
            if "timeline_markers" in plot_data:
                for marker in plot_data["timeline_markers"]:
                    if isinstance(marker, dict):
                        chapter = marker.get("chapter", 0)
                        if chapter not in self.timeline:
                            self.timeline[chapter] = []
                        self.timeline[chapter].append(marker.get("event", ""))
                        
            self.book.metadata["plot"] = plot_data
            
            self.log_separator("PLOT OUTLINE CREATED")
            for act in plot_data["acts"]:
                self.logger.info(f"\nAct {act['act_number']}")
                self.logger.info(f"Description: {act['description']}")
                for i, event in enumerate(act['key_events'], 1):
                    self.logger.info(f"Chapter {i}: {event}")
                    
            return plot_data

        self.logger.error("Failed to create plot outline")
        return {}
        
    def generate_chapter(self, chapter_number: int, chapter_summary: str) -> Chapter:
        """Generate chapter with enhanced continuity checks"""
        self.log_separator(f"GENERATING CHAPTER {chapter_number}")
        self.logger.info(f"Summary: {chapter_summary}")
        
        # Build rich context
        context = self._build_chapter_context(chapter_number, chapter_summary)
        prompt = self._build_chapter_prompt(context)
        
        # First attempt
        content = self.generate_response(prompt)
        
        # Validate content
        word_count = len(content.split())
        if word_count < self.min_words:
            self.logger.warning(f"First attempt too short ({word_count} words). Retrying...")
            
            improvement_prompt = f"""
            Expand this chapter while maintaining consistency:
            
            Previous version:
            {content}
            
            Chapter Summary: {chapter_summary}
            Current Context:
            {json.dumps(context, indent=2)}
            
            Requirements:
            1. Expand to at least {self.min_words} words
            2. Maintain all plot continuity
            3. Keep character locations and movements logical
            4. Advance relevant plot threads
            5. Show character development
            """
            
            content = self.generate_response(improvement_prompt)
            word_count = len(content.split())
            
        # Parse scenes and validate continuity
        scenes = self._parse_scenes(content)
        if not self._validate_chapter_continuity(scenes, context):
            self.logger.warning("Continuity issues detected. Attempting fix...")
            scenes = self._fix_continuity_issues(scenes, context)
            
        # Create chapter
        chapter = Chapter(
            number=chapter_number,
            title=f"Chapter {chapter_number}",
            summary=chapter_summary,
            scenes=scenes,
            word_count=word_count,
            active_plot_threads=self._extract_active_plot_threads(content),
            character_developments=self._extract_character_developments_from_content(content)
        )
        
        # Update world state
        self._update_world_state(chapter)
        
        # Store chapter
        self.book.chapters.append(chapter)
        
        self.logger.info(f"Chapter {chapter_number} completed: {word_count} words")
        return chapter

    def export_book(self, output_dir: str = None) -> str:
        """Export book with complete manuscript and supporting files"""
        if output_dir is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_dir = f"generated_book_{timestamp}"
            
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        chapters_dir = output_path / "chapters"
        chapters_dir.mkdir(exist_ok=True)
        resources_dir = output_path / "resources"
        resources_dir.mkdir(exist_ok=True)
        
        # Create complete manuscript
        manuscript_path = output_path / "manuscript.txt"
        with open(manuscript_path, "w", encoding='utf-8') as f:
            f.write(f"{self.book.title}\n\n")
            
            # Table of contents
            f.write("Table of Contents\n\n")
            for chapter in self.book.chapters:
                f.write(f"Chapter {chapter.number}: {chapter.title}\n")
            f.write("\n\n")
            
            # Chapters
            for chapter in self.book.chapters:
                f.write(f"\nChapter {chapter.number}: {chapter.title}\n\n")
                for scene in chapter.scenes:
                    if scene.location:
                        f.write(f"[Location: {scene.location}]\n")
                    if scene.pov_character:
                        f.write(f"[POV: {scene.pov_character}]\n")
                    f.write(f"{scene.content}\n\n")
                    
        # Save enhanced metadata
        metadata = {
            "title": self.book.title,
            "genre": self.book.genre,
            "target_audience": self.book.target_audience,
            "themes": self.book.themes,
            "characters": [char.to_dict() for char in self.book.characters],
            "metadata": self.book.metadata,
            "character_arcs": self.character_arcs,
            "timeline": self.timeline,
            "generation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "word_count": sum(ch.word_count for ch in self.book.chapters),
            "chapter_count": len(self.book.chapters),
            "generation_parameters": {
                "model": self.model_name,
                "minimum_chapter_words": self.min_words,
                "maximum_chapter_words": self.max_words
            }
        }
        
        metadata_path = output_path / "metadata.json"
        with open(metadata_path, "w", encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            
        # Save detailed character profiles
        characters_file = resources_dir / "characters.txt"
        with open(characters_file, "w", encoding='utf-8') as f:
            f.write("# Characters\n\n")
            for char in self.book.characters:
                f.write(f"## {char.name}\n\n")
                f.write(f"Background: {char.background}\n")
                f.write(f"Personality: {char.personality}\n")
                f.write(f"Goals: {char.goals}\n")
                f.write(f"Current Location: {char.current_location}\n")
                f.write("Active Goals:\n")
                for goal in char.active_goals:
                    f.write(f"- {goal}\n")
                if char.relationships:
                    f.write("Relationships:\n")
                    for rel_name, rel_desc in char.relationships.items():
                        f.write(f"- {rel_name}: {rel_desc}\n")
                f.write("\n")
                
        # Save plot outline
        plot_file = resources_dir / "plot_outline.txt"
        with open(plot_file, "w", encoding='utf-8') as f:
            f.write("# Plot Outline\n\n")
            
            # Plot Threads
            f.write("## Active Plot Threads\n\n")
            for name, thread in self.plot_threads.items():
                f.write(f"### {name}\n")
                f.write(f"Status: {thread.status}\n")
                f.write("Key Events:\n")
                for event in thread.key_events:
                    f.write(f"- {event}\n")
                f.write("\n")
                
            # Acts and Chapter Summaries
            plot_data = self.book.metadata.get("plot", {})
            if "acts" in plot_data:
                for act in plot_data["acts"]:
                    f.write(f"## Act {act['act_number']}\n\n")
                    f.write(f"Description: {act['description']}\n\n")
                    f.write("Key Events:\n")
                    for i, event in enumerate(act['key_events'], 1):
                        f.write(f"{i}. {event}\n")
                    if act.get('character_developments'):
                        f.write("\nCharacter Developments:\n")
                        for char, dev in act['character_developments'].items():
                            f.write(f"- {char}: {dev}\n")
                    if act.get('location_changes'):
                        f.write("\nLocation Changes:\n")
                        for char, changes in act['location_changes'].items():
                            f.write(f"- {char}: {changes['from']} -> {changes['to']}\n")
                    f.write("\n")
                    
        # Save timeline
        timeline_file = resources_dir / "timeline.txt"
        with open(timeline_file, "w", encoding='utf-8') as f:
            f.write("# Story Timeline\n\n")
            for chapter, events in sorted(self.timeline.items()):
                f.write(f"## Chapter {chapter}\n")
                for event in events:
                    f.write(f"- {event}\n")
                f.write("\n")
                
        self.log_separator("BOOK EXPORTED")
        self.logger.info(f"Files saved to: {output_path}")
        return str(output_path)

    def check_ollama(self) -> bool:
        """Check Ollama availability"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
        
    def print_ollama_error(self):
        """Print Ollama error message"""
        print("\nError: Ollama is not running or not accessible!")
        print("\nTo start Ollama:")
        print("1. Open a new terminal")
        print("2. Run: ollama serve")
        print("3. Wait for Ollama to start")
        print("4. Run this script again")
        
    def main(self):
        print("=== Book Generation System ===")
        print("\nChecking Ollama availability...")
        
        if not self.check_ollama():
            self.print_ollama_error()
            sys.exit(1)
            
        try:
            user_input = self.get_user_input()
            self.log_separator("STARTING BOOK GENERATION")
            
            book_concept = self.initialize_book(user_input)
            if not book_concept:
                raise ValueError("Failed to create book concept")
                
            characters = self.create_characters()
            if not characters:
                raise ValueError("Failed to create characters")
                
            plot = self.create_plot_outline(user_input["num_chapters"])
            if not plot:
                raise ValueError("Failed to create plot outline")
                
            for i in range(user_input["num_chapters"]):
                chapter_num = i + 1
                events = []
                for act in plot["acts"]:
                    if isinstance(act, dict) and "key_events" in act:
                        events.extend(act["key_events"])
                        
                chapter_summary = events[i] if i < len(events) else f"Chapter {chapter_num} events"
                
                try:
                    chapter = self.generate_chapter(chapter_num, chapter_summary)
                    # Assuming refine_chapter is defined elsewhere
                    # refined_chapter = self.refine_chapter(chapter)
                    
                    print(f"\nCompleted chapter {chapter_num}/{user_input['num_chapters']}")
                    print(f"Word count: {chapter.word_count}")
                    
                except Exception as e:
                    self.logger.error(f"Error in chapter {chapter_num}: {str(e)}")
                    continue
                
                time.sleep(1)
                
            output_path = self.export_book()
            
            self.log_separator("GENERATION COMPLETED")
            self.logger.info(f"Book saved to: {output_path}")
            
            print("\nGenerated files:")
            print(f"1. Complete manuscript: {output_path}/manuscript.txt")
            print(f"2. Chapter files: {output_path}/chapters/")
            print(f"3. Character profiles: {output_path}/resources/characters.txt")
            print(f"4. Plot outline: {output_path}/resources/plot_outline.txt")
            print(f"5. Book metadata: {output_path}/metadata.json")
            print(f"6. Story timeline: {output_path}/resources/timeline.txt")
            
        except KeyboardInterrupt:
            self.log_separator("GENERATION INTERRUPTED BY USER")
            print("\nSaving partial results...")
            try:
                output_path = self.export_book("partial_book")
                print(f"Partial book saved to: {output_path}")
            except Exception as e:
                self.logger.error(f"Failed to save partial results: {str(e)}")
            sys.exit(0)
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            print("\nAn error occurred during generation.")
            if hasattr(self, 'logger'):
                print("Check the log file for details")
            raise

    def parse_response_to_json(self, response: str, template: Dict) -> Optional[Dict]:
        """Parse the AI response into JSON, ensuring it matches the template structure"""
        try:
            # Очищаем ответ от маркеров форматирования
            cleaned_response = response.replace('```json', '').replace('```', '').strip()
            
            parsed = json.loads(cleaned_response)
            # Basic validation: check if all top-level keys in template are present
            for key in template:
                if key not in parsed:
                    self.logger.error(f"Missing key in response: {key}")
                    return None
            return parsed
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {str(e)}")
            return None

    def _validate_character_relationships(self, characters: List[Dict]) -> bool:
        """Validate that character relationships reference existing characters"""
        character_names = {char['name'] for char in characters if 'name' in char}
        for char in characters:
            relationships = char.get('relationships', {})
            for rel in relationships.keys():
                if rel not in character_names:
                    self.logger.warning(f"Character {rel} in relationships does not exist.")
                    return False
        return True

    def _fix_character_relationships(self, characters_data: Dict) -> Dict:
        """Attempt to fix character relationships by removing invalid references"""
        if not isinstance(characters_data, dict):
            return {"characters": []}
            
        character_names = {char['name'] for char in characters_data.get("characters", []) if 'name' in char}
        for char in characters_data.get("characters", []):
            relationships = char.get("relationships", {})
            valid_relationships = {rel: desc for rel, desc in relationships.items() if rel in character_names}
            char["relationships"] = valid_relationships
        return characters_data

    def _validate_character_locations(self, characters: List[Dict]) -> bool:
        """Validate that characters are in valid starting locations"""
        valid_locations = set(self.location_state.valid_transitions.keys())
        if not valid_locations:
            valid_locations = {"starting_location"}
        for char in characters:
            loc = char.get("current_location", "")
            if loc not in valid_locations:
                self.logger.warning(f"Character {char.get('name', 'Unknown')} has invalid location: {loc}")
                return False
        return True

    def _build_chapter_context(self, chapter_number: int, summary: str) -> Dict:
        """Build rich context for chapter generation"""
        previous_chapter = self._get_previous_chapter(chapter_number)
        
        context = {
            "chapter_number": chapter_number,
            "total_chapters": len(self.book.metadata["plot"]["acts"][0]["key_events"]),
            "summary": summary,
            "previous_chapter": previous_chapter.to_dict() if previous_chapter else None,
            "active_plot_threads": {
                name: thread for name, thread in self.plot_threads.items()
                if thread.status == "active"
            },
            "character_states": {
                char.name: {
                    "location": char.current_location,
                    "arc_stage": self.character_arcs[char.name]["stage"],
                    "active_goals": char.active_goals,
                    "recent_developments": self.character_arcs[char.name].get("recent_developments", [])
                }
                for char in self.book.characters
            },
            "timeline_markers": self.timeline.get(chapter_number, []),
            "themes": self.book.themes,
            "style_notes": self.book.metadata.get("style_notes", "")
        }
        
        return context

    def _get_previous_chapter(self, chapter_num: int) -> Optional[Chapter]:
        """Get previous chapter if available"""
        if chapter_num <= 1:
            return None
        
        return next((chapter for chapter in self.book.chapters 
                    if chapter.number == chapter_num - 1), None)
    
    def _parse_scenes(self, content: str) -> List[Scene]:
        """Parse content into scenes with enhanced metadata"""
        if not content:
            return []
        
        raw_scenes = re.split(r'\n\s*\n(?=\S)', content)
        scenes = []
        
        for raw_scene in raw_scenes:
            # Extract metadata
            location_match = re.search(r'\[Location: (.*?)\]', raw_scene)
            location = location_match.group(1) if location_match else None

            pov_match = re.search(r'\[POV: (.*?)\]', raw_scene)
            pov = pov_match.group(1) if pov_match else None
            
            time_match = re.search(r'\[Time: (\d+)\]', raw_scene)
            time_passed = int(time_match.group(1)) if time_match else 0
            
            # Extract active characters
            active_chars = []
            for char in self.book.characters:
                if char.name in raw_scene:
                    active_chars.append(char.name)
                    
            # Extract plot threads
            plot_threads = []
            for thread_name, thread in self.plot_threads.items():
                if thread_name.lower() in raw_scene.lower():
                    plot_threads.append(thread_name)
                    
            # Clean scene content
            clean_content = raw_scene
            if location_match:
                clean_content = clean_content.replace(location_match.group(0), '')
            if pov_match:
                clean_content = clean_content.replace(pov_match.group(0), '')
            if time_match:
                clean_content = clean_content.replace(time_match.group(0), '')
                
            scenes.append(Scene(
                content=clean_content.strip(),
                location=location,
                pov_character=pov,
                time_passed=time_passed,
                active_characters=active_chars,
                plot_threads_advanced=plot_threads
            ))

        return scenes

    def _validate_chapter_continuity(self, scenes: List[Scene], context: Dict) -> bool:
        """Validate continuity within the chapter scenes"""
        # Placeholder for actual continuity checks
        # Implement checks based on context and scenes
        return True

    def _fix_continuity_issues(self, scenes: List[Scene], context: Dict) -> List[Scene]:
        """Attempt to fix continuity issues within the chapter scenes"""
        # Placeholder for actual continuity fixes
        # Implement logic to adjust scenes based on context
        return scenes

    def _extract_active_plot_threads(self, content: str) -> List[str]:
        """Extract active plot threads from chapter content"""
        active_threads = []
        for thread_name in self.plot_threads.keys():
            if thread_name.lower() in content.lower():
                active_threads.append(thread_name)
        return active_threads

    def _extract_character_developments_from_content(self, content: str) -> Dict[str, str]:
        """Extract character developments from chapter content"""
        developments = {}
        for char in self.book.characters:
            pattern = re.compile(rf"{re.escape(char.name)}.*?(?=\n|$)", re.IGNORECASE)
            match = pattern.search(content)
            if match:
                developments[char.name] = match.group(0)
        return developments

    def _update_world_state(self, chapter: Chapter):
        """Update the world state based on the chapter's events"""
        for scene in chapter.scenes:
            for char in scene.active_characters:
                if scene.location:
                    self.location_state.character_locations[char] = scene.location
                    self.character_arcs[char]["location_history"].append(scene.location)

    def _balance_plot_structure(self, plot_data: Dict, num_chapters: int) -> Dict:
        """Ensure that the plot structure is balanced across chapters"""
        # Placeholder for actual balancing logic
        return plot_data

    def _build_chapter_prompt(self, context: Dict) -> str:
        """Build the prompt for generating a chapter based on context"""
        prompt = f"""Generate Chapter {context['chapter_number']} for the book "{self.book.title}" with the following summary and context:

Chapter Summary:
{context['summary']}

Context:
{json.dumps(context, indent=2)}

Requirements:
1. Maintain continuity with previous chapters
2. Develop active plot threads
3. Show character development and interactions
4. Adhere to the writing style and themes
5. Ensure logical character movements and location changes
6. Keep within the word count limits ({self.min_words}-{self.max_words} words)

Provide the chapter content with scene breaks as needed.
"""
        return prompt

    def _validate_character_relationships(self, characters: List[Dict]) -> bool:
        """Validate that character relationships reference existing characters"""
        character_names = {char['name'] for char in characters if 'name' in char}
        for char in characters:
            relationships = char.get('relationships', {})
            for rel in relationships.keys():
                if rel not in character_names:
                    self.logger.warning(f"Character {rel} in relationships does not exist.")
                    return False
        return True

    def _fix_character_relationships(self, characters_data: Dict) -> Dict:
        """Attempt to fix character relationships by removing invalid references"""
        if not isinstance(characters_data, dict):
            return {"characters": []}
            
        character_names = {char['name'] for char in characters_data.get("characters", []) if 'name' in char}
        for char in characters_data.get("characters", []):
            relationships = char.get("relationships", {})
            valid_relationships = {rel: desc for rel, desc in relationships.items() if rel in character_names}
            char["relationships"] = valid_relationships
        return characters_data

    def _validate_character_locations(self, characters: List[Dict]) -> bool:
        """Validate that characters are in valid starting locations"""
        valid_locations = set(self.location_state.valid_transitions.keys())
        if not valid_locations:
            valid_locations = {"starting_location"}
        for char in characters:
            loc = char.get("current_location", "")
            if loc not in valid_locations:
                self.logger.warning(f"Character {char.get('name', 'Unknown')} has invalid location: {loc}")
                return False
        return True

    def refine_chapter(self, chapter: Chapter) -> Chapter:
        """Placeholder for chapter refinement process"""
        # Implement any refinement logic here
        return chapter

# Utility functions
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
    generator = BookGenerator(
        min_words=DEFAULT_CHAPTER_MIN_WORDS,
        max_words=DEFAULT_CHAPTER_MAX_WORDS
    )
    generator.main()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)
        
