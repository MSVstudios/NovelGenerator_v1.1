from dataclasses import dataclass, field, asdict
from collections import Counter, defaultdict
import re
from typing import Dict, List, Set, Optional, Tuple, Any, Callable
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum, auto
import spacy
import threading
import queue
import logging
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich import print as rprint
import time
import json
import sys
import requests
import os


class WritingStyle(Enum):
    CINEMATIC = "cinematic"
    LYRICAL = "lyrical"
    DRAMATIC = "dramatic"
    MINIMALISTIC = "minimalistic"


@dataclass
class Character:
    name: str
    role: str  # protagonist, antagonist, supporting
    description: str
    relationships: Dict[str, str] = field(default_factory=dict)  # relations with other characters


@dataclass
class Chapter:
    number: int
    title: str
    theme: str
    outline: str
    characters: List[str]  # characters involved in chapter
    key_events: List[str]  # main plot points
    setting: str  # location/time period


@dataclass
class PlotStructure:
    chapters: List[Chapter]
    characters: List[Character]
    main_theme: str
    settings: List[str]


@dataclass
class TextProcessor:
    """Text processing and enhancement"""
    cliches: Dict[str, List[str]] = field(default_factory=lambda: {
        "сердце билось": ["пульс участился", "кровь стучала в висках", "сердце трепетало"],
        "глаза сверкали": ["взгляд излучал", "в глазах плясали искры", "глаза светились"],
        "руки дрожали": ["пальцы подрагивали", "ладони покрылись испариной", "руки выдавали волнение"],
        "время остановилось": ["мгновение растянулось", "секунды замедлили свой бег", "время словно замерло"]
    })

    emotion_patterns: Dict[str, List[str]] = field(default_factory=lambda: {
        "радость": ["восторг", "ликование", "эйфория", "блаженство", "наслаждение"],
        "грусть": ["тоска", "печаль", "уныние", "скорбь", "меланхолия"],
        "злость": ["ярость", "гнев", "раздражение", "бешенство", "негодование"],
        "страх": ["ужас", "паника", "тревога", "опасение", "испуг"],
        "удивление": ["изумление", "поражение", "шок", "оторопь", "недоумение"]
    })

    def improve_text(self, text: str) -> str:
        """Enhances the quality of the text"""
        seen_paragraphs = set()
        improved_paragraphs = []

        for paragraph in text.split('\n\n'):
            if paragraph not in seen_paragraphs:
                seen_paragraphs.add(paragraph)
                improved_paragraphs.append(paragraph)

        text = '\n\n'.join(improved_paragraphs)

        for cliche, alternatives in self.cliches.items():
            if cliche in text:
                replacement = alternatives[hash(cliche) % len(alternatives)]
                text = text.replace(cliche, replacement)

        for emotion, variants in self.emotion_patterns.items():
            count = text.count(emotion)
            if count > 2:
                for i in range(count - 1):
                    variant = variants[i % len(variants)]
                    text = text.replace(emotion, variant, 1)

        text = self._improve_sentence_structure(text)
        text = self._format_dialogues(text)

        return text

    def _improve_sentence_structure(self, text: str) -> str:
        """Improves sentence structure"""
        sentences = text.split('. ')
        improved_sentences = []

        for i, sentence in enumerate(sentences):
            if i > 0 and sentence.split()[0] == improved_sentences[i-1].split()[0]:
                words = sentence.split()
                if words:
                    words.append(words.pop(0))
                    sentence = ' '.join(words)

            if len(sentence.split()) > 20 and ',' not in sentence:
                parts = sentence.split()
                mid = len(parts) // 2
                sentence = ' '.join(parts[:mid]) + ', ' + ' '.join(parts[mid:])

            improved_sentences.append(sentence)

        return '. '.join(improved_sentences)

    def _format_dialogues(self, text: str) -> str:
        """Formats dialogues"""
        text = re.sub(r'[-–]', '—', text)
        text = re.sub(r'"([^"]+)"', r'—\1', text)
        text = re.sub(r'(?<=\n)—', r'\n—', text)
        return text


class PlotParser:
    """Enhanced parser for plot generation results with improved chapter parsing"""

    def __init__(self):
        # Updated chapter pattern to better handle AI response format
        self.chapter_pattern = re.compile(
            r"(?:Глава|Chapter)\s+(\d+)(?:\s*[:\-—]\s*)?\"?([^\"]*?)\"?\s*[:：]?\s*((?:(?!(?:Глава|Chapter)\s+\d+|4\.\s+Setting).)*)",
            re.MULTILINE | re.DOTALL
        )

        self.character_pattern = re.compile(
            r"(?:Персонаж|Character):\s*([^\n]+)\n"
            r"(?:Роль|Role):\s*([^\n]+)\n"
            r"(?:Описание|Description):\s*([^\n]+)(?:\n|$)"
        )

        # Updated event pattern to handle different bullet point styles
        self.event_pattern = re.compile(r"[-•*]\s*([^\n]+)")

        # Updated settings pattern to handle more variations
        self.settings_pattern = re.compile(
            r"(?:Место действия|Setting|Location|4\.\s+Setting):\s*((?:[^\n]|\n(?!\d))+)"
        )

    def _split_into_sections(self, text: str) -> Dict[str, str]:
        """Splits text into logical sections with improved section detection"""
        sections = {}
        current_section = None
        current_content = []

        # Updated section markers for better detection
        section_markers = {
            'theme': [r'(?:1\.)?\s*(?:Тема|Theme):', r'Основная тема:'],
            'characters': [r'(?:2\.)?\s*(?:Персонажи|Characters):', r'Действующие лица:'],
            'chapters': [r'(?:3\.)?\s*(?:Главы|Chapters):', r'План глав:'],
            'setting': [r'(?:4\.)?\s*(?:Место действия|Setting):', r'Сеттинг:']
        }

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            found_section = None
            for section, markers in section_markers.items():
                for marker in markers:
                    if re.match(marker, line, re.IGNORECASE):
                        found_section = section
                        break
                if found_section:
                    break

            if found_section:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = found_section
                current_content = []
                # Extract content after the marker
                remaining = re.split(':|：', line, 1)[1].strip() if ':' in line else ''
                if remaining:
                    current_content.append(remaining)
            else:
                if current_section:
                    current_content.append(line)

        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def _extract_main_theme(self, theme_section: str) -> str:
        """Extracts the main theme"""
        theme = theme_section.strip()
        if '\n' in theme:
            theme = theme.split('\n')[0]
        return theme

    def _parse_characters(self, characters_section: str) -> List[Character]:
        """Parses the characters section"""
        characters = []
        character_blocks = self.character_pattern.finditer(characters_section)

        for match in character_blocks:
            name, role, description = match.groups()
            character = Character(
                name=name.strip(),
                role=role.strip().lower(),
                description=description.strip(),
                relationships={}
            )

            # Attempt to extract relationships if present
            remaining_text = characters_section[match.end():]
            rel_match = re.match(r"(?:Отношения|Relationships):\s*([^\n]+)", remaining_text)
            if rel_match:
                relationships = rel_match.group(1).split(',')
                for rel in relationships:
                    if ':' in rel:
                        rel_char, rel_type = rel.split(':', 1)
                        character.relationships[rel_char.strip()] = rel_type.strip()

            characters.append(character)

        return characters

    def _parse_chapters(self, chapters_section: str) -> List[Chapter]:
        """Parses the chapters section"""
        chapters = []
        chapter_matches = self.chapter_pattern.finditer(chapters_section)

        for match in chapter_matches:
            number, title, content = match.groups()

            events = [event.group(1).strip() for event in self.event_pattern.finditer(content)]
            characters_mentioned = self._extract_characters_from_content(content)
            setting = self._extract_setting_from_content(content)
            theme = self._extract_theme_from_content(content)

            chapter = Chapter(
                number=int(number),
                title=title.strip() if title else f"Chapter {number}",
                theme=theme,
                outline=content.strip(),
                characters=characters_mentioned,
                key_events=events,
                setting=setting
            )
            chapters.append(chapter)

        return sorted(chapters, key=lambda x: x.number)

    def _extract_characters_from_content(self, content: str) -> List[str]:
        """Extracts character mentions"""
        names = set()
        sentences = content.split('. ')
        for sentence in sentences:
            words = sentence.split()
            for word in words[1:]:  # Skip the first word in the sentence
                if word and word[0].isupper():
                    names.add(word.strip('.,!?()[]{}'))
        return list(names)

    def _extract_setting_from_content(self, content: str) -> str:
        """Extracts the setting description"""
        setting_markers = ['место действия:', 'действие происходит', 'located in', 'setting:']
        lower_content = content.lower()

        for marker in setting_markers:
            if marker in lower_content:
                idx = lower_content.index(marker)
                end_idx = content.find('.', idx)
                if end_idx != -1:
                    return content[idx:end_idx].split(':', 1)[-1].strip()

        return "Not specified"

    def _extract_theme_from_content(self, content: str) -> str:
        """Extracts the chapter theme"""
        theme_markers = ['тема:', 'theme:', 'основная идея:']
        lower_content = content.lower()

        for marker in theme_markers:
            if marker in lower_content:
                idx = lower_content.index(marker)
                end_idx = content.find('.', idx)
                if end_idx != -1:
                    return content[idx:end_idx].split(':', 1)[-1].strip()

        first_sentence = content.split('.')[0].strip()
        return first_sentence

    def _extract_settings(self, setting_section: str) -> List[str]:
        """Extracts a list of settings"""
        settings = []

        setting_matches = self.settings_pattern.finditer(setting_section)
        for match in setting_matches:
            setting = match.group(1).strip()
            if setting:
                locations = [loc.strip() for loc in setting.split(',')]
                settings.extend(locations)

        if not settings:
            location_markers = [
                'in', 'on', 'near', 'beside', 'inside',
                'around', 'at', 'before', 'behind', 'under'
            ]

            words = setting_section.split()
            for i, word in enumerate(words):
                if word.lower() in location_markers and i + 1 < len(words):
                    potential_location = words[i + 1].strip('.,!?()[]{}')
                    if potential_location and potential_location[0].isupper():
                        settings.append(potential_location)

        unique_settings = []
        for setting in settings:
            if setting not in unique_settings:
                unique_settings.append(setting)

        return unique_settings if unique_settings else ["Setting not specified"]

    def parse_plot_outline(self, ai_response: str) -> PlotStructure:
        """Parses the complete AI response with improved error handling"""
        try:
            sections = self._split_into_sections(ai_response)

            # Extract main theme
            main_theme = self._extract_main_theme(sections.get('theme', ''))

            # Parse characters
            characters_section = sections.get('characters', '')
            characters = self._parse_characters(characters_section)

            # Parse chapters with improved extraction
            chapters_section = sections.get('chapters', '')
            chapters = self._parse_chapters(chapters_section)

            # Extract settings
            settings_section = sections.get('setting', '')
            settings = self._extract_settings(settings_section)

            # Add settings from chapters
            chapter_settings = {chapter.setting for chapter in chapters if chapter.setting != "Not specified"}
            all_settings = list(set(settings) | chapter_settings)

            # Create and return plot structure
            plot_structure = PlotStructure(
                chapters=chapters,
                characters=characters,
                main_theme=main_theme,
                settings=all_settings
            )

            logging.info(f"Successfully parsed {len(chapters)} chapters.")
            return plot_structure

        except Exception as e:
            logging.error(f"Error parsing plot outline: {str(e)}")
            raise ValueError(f"Failed to parse plot outline: {str(e)}")


@dataclass
class ChapterAnalytics:
    """Chapter analysis"""
    word_count: int = 0
    unique_words: int = 0
    avg_sentence_length: float = 0
    dialogue_ratio: float = 0
    emotion_intensity: Dict[str, float] = field(default_factory=dict)
    pacing_score: float = 0
    style_markers: Dict[str, int] = field(default_factory=dict)
    scene_transitions: List[str] = field(default_factory=list)
    character_appearances: Dict[str, List[int]] = field(default_factory=lambda: defaultdict(list))

    def calculate_quality_score(self) -> float:
        """Calculates the overall quality score"""
        scores = []

        if self.word_count > 0:
            vocabulary_score = self.unique_words / self.word_count
            scores.append(vocabulary_score)

        if 15 <= self.avg_sentence_length <= 20:
            sentence_score = 1.0
        else:
            sentence_score = 1.0 - abs(self.avg_sentence_length - 17.5) / 17.5
        scores.append(sentence_score)

        if 0.3 <= self.dialogue_ratio <= 0.4:
            dialogue_score = 1.0
        else:
            dialogue_score = 1.0 - abs(self.dialogue_ratio - 0.35) / 0.35
        scores.append(dialogue_score)

        emotion_scores = list(self.emotion_intensity.values())
        if emotion_scores:
            emotion_balance = 1.0 - np.std(emotion_scores)
            scores.append(emotion_balance)

        if 0.3 <= self.pacing_score <= 0.7:
            pacing_score = 1.0
        else:
            pacing_score = 1.0 - abs(self.pacing_score - 0.5) / 0.5
        scores.append(pacing_score)

        return sum(scores) / len(scores) if scores else 0.0


@dataclass
class StoryMetrics:
    """Metrics for tracking story quality"""
    word_frequencies: Counter = field(default_factory=Counter)
    emotion_frequencies: Counter = field(default_factory=Counter)
    character_mentions: Dict[str, int] = field(default_factory=dict)
    scene_transitions: List[str] = field(default_factory=list)
    plot_points: Set[str] = field(default_factory=set)


@dataclass
class ChapterValidator:
    """Validation of generated content"""

    def validate_chapter_content(self, content: str) -> bool:
        """Checks the quality of the generated content"""
        # Minimum length
        if len(content.split()) < 100:
            return False

        # Structure check
        if not re.search(r'## Chapter \d+:', content):
            return False

        # Check for repeated paragraphs
        paragraphs = content.split('\n\n')
        if len(paragraphs) != len(set(paragraphs)):
            return False

        return True


class StoryAnalyzer:
    """Text analyzer with visualization"""

    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy model 'en_core_web_sm' not found. Installing...")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        self.console = Console()

    def analyze_chapter(self, text: str, chapter_num: int) -> ChapterAnalytics:
        """Performs in-depth analysis of a chapter"""
        doc = self.nlp(text)
        analytics = ChapterAnalytics()

        # Basic metrics
        analytics.word_count = len(doc)
        analytics.unique_words = len(set([token.text.lower() for token in doc if not token.is_punct]))

        # Sentence analysis
        sentences = list(doc.sents)
        analytics.avg_sentence_length = np.mean([len(sent) for sent in sentences]) if sentences else 0

        # Dialogue analysis
        dialogue_words = sum(1 for token in doc if token.text.startswith('—'))
        analytics.dialogue_ratio = dialogue_words / analytics.word_count if analytics.word_count > 0 else 0

        # Emotion analysis
        analytics.emotion_intensity = self._analyze_emotions(text)

        # Pacing analysis
        analytics.pacing_score = self._calculate_pacing(doc)

        return analytics

    def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyzes the emotional tone of the text"""
        emotion_words = {
            "joy": ["joy", "happiness", "delight", "elation"],
            "sadness": ["sadness", "sorrow", "melancholy", "grief"],
            "fear": ["fear", "terror", "anxiety", "panic"],
            "anger": ["anger", "rage", "fury", "irritation"],
            "surprise": ["surprise", "amazement", "shock"]
        }

        emotions = defaultdict(float)
        doc = self.nlp(text.lower())
        total_words = len(doc)

        for emotion, words in emotion_words.items():
            count = sum(1 for token in doc if token.text in words)
            emotions[emotion] = count / total_words if total_words > 0 else 0

        return dict(emotions)

    def _calculate_pacing(self, doc) -> float:
        """Calculates the pacing of the narrative"""
        action_verbs = ["run", "jump", "shoot", "fight", "dash"]
        dialogue_markers = ["—", "said", "replied", "asked"]
        description_markers = ["was", "stood", "located", "seemed"]

        action_count = sum(1 for token in doc if token.lemma_ in action_verbs)
        dialogue_count = sum(1 for token in doc if token.text in dialogue_markers)
        description_count = sum(1 for token in doc if token.lemma_ in description_markers)

        total_markers = action_count + dialogue_count + description_count
        if total_markers == 0:
            return 0.5

        return (action_count * 1.5 + dialogue_count) / total_markers

    def visualize_story_structure(self, analytics_data: List[ChapterAnalytics]):
        """Creates a visualization of the story structure"""
        plt.style.use('default')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        # Emotional balance graph
        chapters = range(1, len(analytics_data) + 1)
        emotions = list(analytics_data[0].emotion_intensity.keys())
        for emotion in emotions:
            values = [chapter.emotion_intensity.get(emotion, 0) for chapter in analytics_data]
            ax1.plot(chapters, values, label=emotion, marker='o')
        ax1.set_title('Emotional Balance')
        ax1.legend()

        # Narrative pacing graph
        pacing = [chapter.pacing_score for chapter in analytics_data]
        ax2.plot(chapters, pacing, color='red', marker='o')
        ax2.set_title('Narrative Pacing')

        # Dialogue ratio
        dialogue_ratios = [chapter.dialogue_ratio for chapter in analytics_data]
        ax3.bar(chapters, dialogue_ratios, color='green', alpha=0.7)
        ax3.set_title('Dialogue Ratio')

        # Chapter lengths
        word_counts = [chapter.word_count for chapter in analytics_data]
        ax4.bar(chapters, word_counts, color='blue', alpha=0.7)
        ax4.set_title('Chapter Lengths')

        plt.tight_layout()
        plt.savefig('story_analytics.png')
        plt.close()


class StoryAnalyzerExtended(StoryAnalyzer):
    """Extended text analyzer"""

    def __init__(self):
        super().__init__()
        self.story_metrics = StoryMetrics()


class NovelGenerator:
    """Fiction book generator"""

    def __init__(self, writing_style: WritingStyle = WritingStyle.CINEMATIC):
        self.primary_model = "command-r:35b-08-2024-q5_0"
        self.enhancement_model = "aya-expanse:32b"
        self.analyzer_model = "qwen2.5:32b"
        self.writing_style = writing_style
        self.api_url = "http://localhost:11434/api/generate"

        self.text_processor = TextProcessor()
        self.console = Console()
        self.progress_lock = threading.Lock()
        self.story_analyzer = StoryAnalyzerExtended()
        self.analytics_data = []

        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.console.print("⚠️ spaCy model 'en_core_web_sm' not found. Installing...", style="bold yellow")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

        self._configure_logging()
        self.chapter_validator = ChapterValidator()

    def _configure_logging(self):
        """Configures logging"""
        logging.basicConfig(
            filename='novel_generation.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        metrics_logger = logging.getLogger('metrics')
        metrics_logger.setLevel(logging.DEBUG)
        metrics_handler = logging.FileHandler('generation_metrics.log')
        metrics_logger.addHandler(metrics_handler)

    def stream_response(self, model: str, prompt: str, callback: Optional[Callable[[str], None]] = None) -> str:
        """Gets response from the model"""
        if not model:
            logging.error("Model not specified for text generation.")
            raise ValueError("Model not specified for text generation.")

        logging.info(f"Requesting model {model} with prompt: {prompt[:50]}...")

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 4096
                    }
                },
                stream=True
            )

            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        try:
                            data = json.loads(decoded_line)
                            chunk = data.get("response", "")
                            full_response += chunk
                            if callback:
                                callback(chunk)
                        except json.JSONDecodeError:
                            full_response += decoded_line
                            if callback:
                                callback(decoded_line)
                return full_response
            else:
                raise Exception(f"Ollama API Error: {response.text}")
        except Exception as e:
            logging.error(f"Error during text generation: {str(e)}")
            raise

    def generate_plot_outline(self, topic: str, chapter_count: int) -> Dict:
        """Generates the plot outline"""
        self.console.print("\nCreating plot structure...", style="yellow")

        prompt = f"""
Create a detailed plot outline for a book on the topic: {topic}
Number of chapters: {chapter_count}

The response format should include:

1. Theme:
[Main theme of the work]

2. Characters:
[For each character]:
Character: [name]
Role: [role in the story]
Description: [brief description]
[relationships with other characters]

3. Chapters:
[For each chapter]:
Chapter [number]: [title]
- [main events and plot twists]
- [involved characters]
- [setting]

4. Setting:
[Main locations and their descriptions]
"""

        response = self.stream_response(
            self.primary_model,
            prompt,
            callback=lambda chunk: self.console.print(chunk, end='', style="bold blue")
        )

        # Save the full response for debugging
        self._save_full_ai_response(response)

        # Parse the result
        parser = PlotParser()
        plot_structure = parser.parse_plot_outline(response)

        # Add debug output
        self.console.print("\n🔍 Checking parsed data:", style="bold yellow")
        self.console.print(json.dumps({
            'main_theme': plot_structure.main_theme,
            'characters': [asdict(char) for char in plot_structure.characters],
            'chapters': [asdict(chap) for chap in plot_structure.chapters],
            'settings': plot_structure.settings
        }, ensure_ascii=False, indent=2))

        # Check the number of parsed chapters
        if len(plot_structure.chapters) < chapter_count:
            self.console.print(
                f"\n❌ Not enough chapters in the parsed outline: expected {chapter_count}, got {len(plot_structure.chapters)}",
                style="bold red"
            )
            logging.error("Not enough chapters in the parsed outline.")
            raise ValueError("Not enough chapters in the parsed outline.")

        # Convert to the required format
        chapter_outlines = [
            {
                'theme': chapter.theme,
                'outline': chapter.outline,
                'characters': chapter.characters,
                'setting': chapter.setting,
                'events': chapter.key_events
            }
            for chapter in plot_structure.chapters
        ]

        characters = [
            {
                'name': char.name,
                'role': char.role,
                'description': char.description,
                'relationships': char.relationships
            }
            for char in plot_structure.characters
        ]

        return {
            'chapter_outlines': chapter_outlines,
            'characters': characters,
            'main_theme': plot_structure.main_theme,
            'settings': plot_structure.settings
        }

    def generate_title_and_description(self, plot_data: Dict) -> Dict:
        """Generates the book title and description"""
        prompt = f"""
Based on the following plot outline, create:
1. An attractive book title
2. A subtitle that reveals the essence
3. A brief synopsis (3-4 sentences)

Plot outline:
{json.dumps(plot_data, ensure_ascii=False, indent=2)}

Response format:
Title: [title]
Subtitle: [subtitle]
Synopsis: [synopsis text]
"""

        response = self.stream_response(
            self.primary_model,
            prompt,
            callback=lambda chunk: self.console.print(chunk, end='', style="bold magenta")
        )

        # Parse the response
        lines = response.split('\n')
        title = ""
        subtitle = ""
        description = ""

        for line in lines:
            if line.startswith("Title:"):
                title = line.split(":", 1)[1].strip()
            elif line.startswith("Subtitle:"):
                subtitle = line.split(":", 1)[1].strip()
            elif line.startswith("Synopsis:"):
                description = line.split(":", 1)[1].strip()

        return {
            'title': title or "Book Title",
            'subtitle': subtitle or "Book Subtitle",
            'description': description or "Brief description of the book."
        }

    def _create_primary_prompt(self, chapter_data: Dict, chapter_num: int, total_chapters: int, prev_summary: str) -> str:
        """Creates a prompt for chapter generation"""
        style_prompts = {
            WritingStyle.CINEMATIC: "Write like a cinematographer, creating vivid visual scenes. Use detailed descriptions of the surroundings, convey the atmosphere through all senses. Create dynamic action scenes.",
            WritingStyle.LYRICAL: "Write like a poetic prose writer, using rich metaphors and imagery. Create musicality in the text, delve into the deep internal emotions of the characters.",
            WritingStyle.DRAMATIC: "Write like a playwright, focusing on emotional tension and conflicts. Create vivid dialogues, reveal characters through their actions.",
            WritingStyle.MINIMALISTIC: "Write concisely and accurately, avoiding unnecessary descriptions. Use short, impactful sentences. Create deep subtext through details."
        }

        return f"""
Chapter Theme: {chapter_data.get('theme', '')}
Writing Style: {style_prompts[self.writing_style]}
Current Chapter: {chapter_num} of {total_chapters}
Brief summary of the previous chapter: {prev_summary}

Chapter Outline:
{chapter_data.get('outline', '')}

Involved Characters:
{', '.join(chapter_data.get('characters', []))}

Setting:
{chapter_data.get('setting', 'Not specified')}

Key Events:
{chr(10).join('- ' + event for event in chapter_data.get('events', []))}

Generation Requirements:
1. Create a complete chapter (minimum 3000 words)
2. Use a diverse sentence structure
3. Create vivid and memorable scenes
4. Balance descriptions, dialogues, and actions
5. Develop character personalities
6. Maintain tension
7. End the chapter by setting up the next one

Generate the full text of the chapter.
"""

    def generate_chapter(self, plot_data: Dict, chapter_num: int, total_chapters: int, prev_summary: str = "") -> Tuple[str, str]:
        """Generates a chapter"""
        chapter_data = plot_data['chapter_outlines'][chapter_num - 1]

        # Generate the basic structure
        self.console.print("\n📝 Generating basic structure...", style="bold blue")
        prompt = self._create_primary_prompt(chapter_data, chapter_num, total_chapters, prev_summary)

        content = ""
        def print_content(chunk: str):
            nonlocal content
            content += chunk
            self.console.print(chunk, end='', style="bold blue")

        content = self.stream_response(
            self.primary_model,
            prompt,
            callback=print_content
        )

        # Enhance the text
        content = self.text_processor.improve_text(content)

        # Generate a brief summary
        summary_prompt = f"""
Create a brief summary (3-4 sentences) for the chapter based on this text:

{content}

The summary should reflect the key events and the emotional state of the characters.
"""

        summary = ""
        def print_summary(chunk: str):
            nonlocal summary
            summary += chunk
            self.console.print(chunk, end='', style="bold green")

        summary = self.stream_response(
            self.enhancement_model,
            summary_prompt,
            callback=print_summary
        )

        # Analyze the chapter
        analytics = self.story_analyzer.analyze_chapter(content, chapter_num)
        self.analytics_data.append(analytics)

        return content, summary.strip()

    def generate_book(self, topic: str, chapter_count: int) -> str:
        """Generates a complete book"""
        try:
            self.console.print("🌟 Starting book creation...", style="bold green")

            # Generate the plot structure
            self.console.print("\n📑 Creating the book outline...", style="bold blue")
            plot_data = self.generate_plot_outline(topic, chapter_count)

            # Generate title and description
            self.console.print("\n📝 Generating title and description...", style="bold blue")
            title_data = self.generate_title_and_description(plot_data)

            # Initialize content
            book_content = []
            book_content.append(f"# {title_data['title']}\n")
            book_content.append(f"## {title_data['subtitle']}\n\n")
            book_content.append(f"## Synopsis\n\n{title_data['description']}\n\n")

            # Display the book structure
            self.console.print(f"\n📖 Title: {title_data['title']}", style="bold green")
            self.console.print(f"📖 Subtitle: {title_data['subtitle']}", style="green")
            self.console.print("\n📖 Synopsis:", style="green")
            self.console.print(title_data['description'])

            # Generate chapters
            generated_chapters = {}

            for chapter_num in range(1, chapter_count + 1):
                self.console.print(f"\n\n📝 Generating chapter {chapter_num}/{chapter_count}...", style="bold blue")
                prev_summary = generated_chapters.get(chapter_num - 1, {}).get('summary', '')

                try:
                    chapter_content, chapter_summary = self.generate_chapter(
                        plot_data,
                        chapter_num,
                        chapter_count,
                        prev_summary
                    )

                    # Save the result
                    generated_chapters[chapter_num] = {
                        'content': chapter_content,
                        'summary': chapter_summary
                    }

                    # Show a preview
                    self.console.print(f"\n📑 Chapter {chapter_num}:", style="bold green")
                    preview = chapter_content[:500] + "..." if len(chapter_content) > 500 else chapter_content
                    self.console.print(preview)

                    self.console.print("\n📋 Summary:", style="bold green")
                    self.console.print(chapter_summary)

                except Exception as e:
                    self.console.print(f"\n❌ Error generating chapter {chapter_num}: {e}", style="bold red")
                    logging.error(f"Error generating chapter {chapter_num}: {e}")
                    continue

            # Compile chapters
            for chapter_num in range(1, chapter_count + 1):
                chapter_data = generated_chapters.get(chapter_num)
                if chapter_data:
                    book_content.append(f"\n## Chapter {chapter_num}\n\n{chapter_data['content']}\n\n")
                else:
                    self.console.print(f"❌ Chapter {chapter_num} was not generated.", style="bold red")

            # Create an analytical report
            self.console.print("\n📊 Creating an analytical report...", style="bold blue")
            self.story_analyzer.visualize_story_structure(self.analytics_data)
            book_content.append(self._generate_analytics_report())

            # Save metadata
            self.console.print("\n💾 Saving metadata...", style="bold blue")
            self._save_metadata(plot_data, title_data, self.analytics_data)

            # Compile final content
            final_content = "\n".join(book_content)

            # Save the result
            filename = f"novel_{int(time.time())}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(final_content)

            self.console.print(f"\n✅ Book successfully saved to file: {filename}", style="bold green")
            self.console.print("\n📊 Analytical report created: story_analytics.png")
            self.console.print("\n📋 Metadata saved: book_metadata.json")
            self.console.print("\n🎉 Generation complete! Enjoy reading!", style="bold green")

            return final_content

        except Exception as e:
            logging.error(f"Error generating book: {e}")
            raise

    def _generate_analytics_report(self) -> str:
        """Generates an analytics report for the book"""
        report = ["\n## Analytical Report\n"]

        # Overall statistics
        total_words = sum(a.word_count for a in self.analytics_data)
        avg_chapter_length = total_words / len(self.analytics_data) if self.analytics_data else 0
        unique_words = len(set(w for a in self.analytics_data for w in a.style_markers))

        report.append("### Overall Statistics\n")
        report.append(f"- Total words: {total_words:,}")
        report.append(f"- Average chapter length: {avg_chapter_length:.0f} words")
        report.append(f"- Unique words: {unique_words:,}")

        # Pacing analysis
        report.append("\n### Narrative Dynamics\n")
        pacing_scores = [a.pacing_score for a in self.analytics_data]
        if pacing_scores:
            report.append(f"- Average pacing: {np.mean(pacing_scores):.2f}")
            report.append(f"- Maximum pacing: Chapter {np.argmax(pacing_scores) + 1}")
            report.append(f"- Minimum pacing: Chapter {np.argmin(pacing_scores) + 1}")

        # Emotional analysis
        report.append("\n### Emotional Balance\n")
        if self.analytics_data:
            emotions = self.analytics_data[0].emotion_intensity.keys()
            for emotion in emotions:
                values = [chapter.emotion_intensity.get(emotion, 0) for chapter in self.analytics_data]
                avg_emotion = np.mean(values) if values else 0
                report.append(f"- {emotion.capitalize()}: {avg_emotion:.2%}")

        # Recommendations
        report.append("\n### Recommendations for Improvement\n")
        recommendations = self._generate_recommendations()
        for rec in recommendations:
            report.append(f"- {rec}")

        return "\n".join(report)

    def _generate_recommendations(self) -> List[str]:
        """Generates recommendations for improving the text"""
        recommendations = []

        # Analyze pacing
        pacing_scores = [a.pacing_score for a in self.analytics_data]
        if pacing_scores and np.std(pacing_scores) < 0.1:
            recommendations.append("Consider adding more variations in narrative pacing.")

        # Analyze dialogues
        dialogue_ratios = [a.dialogue_ratio for a in self.analytics_data]
        if dialogue_ratios:
            avg_dialogue = np.mean(dialogue_ratios)
            if avg_dialogue < 0.2:
                recommendations.append("Consider increasing the number of dialogues.")
            elif avg_dialogue > 0.6:
                recommendations.append("Consider adding more descriptions between dialogues.")

        # Analyze emotions
        if self.analytics_data:
            emotions = self.analytics_data[0].emotion_intensity
            for emotion, intensity in emotions.items():
                avg_emotion = np.mean([chapter.emotion_intensity.get(emotion, 0) for chapter in self.analytics_data])
                if avg_emotion < 0.1:
                    recommendations.append(f"Consider diversifying the emotional palette for the emotion: {emotion}.")

        return recommendations if recommendations else ["No specific recommendations for improvement."]

    def _save_metadata(self, plot_data: Dict, title_data: Dict, analytics_data: List[ChapterAnalytics]):
        """Saves the book metadata"""
        metadata = {
            "title": title_data['title'],
            "subtitle": title_data['subtitle'],
            "characters": plot_data['characters'],
            "analytics": {
                "word_count": sum(a.word_count for a in analytics_data),
                "average_pacing": np.mean([a.pacing_score for a in analytics_data]) if analytics_data else 0,
                "emotional_balance": {
                    emotion: np.mean([chapter.emotion_intensity.get(emotion, 0)
                                     for chapter in analytics_data])
                    for emotion in analytics_data[0].emotion_intensity
                } if analytics_data else {}
            },
            "generation_info": {
                "primary_model": self.primary_model,
                "enhancement_model": self.enhancement_model,
                "analyzer_model": self.analyzer_model,
                "writing_style": self.writing_style.value,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        with open('book_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def _generate_debug_info(self, plot_data: Dict):
        """Generates debug information"""
        debug_info = {
            'main_theme': plot_data['main_theme'],
            'characters': plot_data['characters'],
            'chapters': plot_data['chapter_outlines'],
            'settings': plot_data['settings']
        }
        self.console.print("\n🔍 Debug Information:", style="bold yellow")
        self.console.print(json.dumps(debug_info, ensure_ascii=False, indent=2))

    # Added an additional function to save the full AI response for debugging
    def _save_full_ai_response(self, response: str, filename: str = "ai_response_debug.txt"):
        """Saves the full AI response for debugging"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response)
        self.console.print(f"\n💾 Full AI response saved to file: {filename}", style="bold green")


def main():
    """Main function"""
    console = Console()
    console.print("FICTION BOOK GENERATOR v1.0.0", style="bold magenta")
    console.print("Using Ollama. Powered by 'Command-r:35b-08-2024-q5_0'", style="bold magenta")
    console.print("=" * 53)

    # Choose writing style
    styles = [style.value for style in WritingStyle]
    style_choice = console.input("""
Choose a narrative style:
1. cinematic
2. lyrical
3. dramatic
4. minimalistic
> """)

    try:
        writing_style = WritingStyle(styles[int(style_choice) - 1])
    except (IndexError, ValueError):
        console.print("❌ Invalid style choice. Using 'cinematic'.", style="bold red")
        writing_style = WritingStyle.CINEMATIC

    # Create the generator
    generator = NovelGenerator(writing_style=writing_style)

    # Get book parameters
    topic = console.input("\n📚 Enter the topic or idea for the book: ")

    while True:
        try:
            chapter_count = int(console.input("📖 Enter the desired number of chapters (3 to 50): "))
            if 3 <= chapter_count <= 50:
                break
            console.print("❌ Number of chapters must be between 3 and 50", style="bold red")
        except ValueError:
            console.print("❌ Please enter a number", style="bold red")

    try:
        console.print("\n🚀 Starting book generation...", style="bold green")
        book_content = generator.generate_book(topic, chapter_count)
        console.print("\n🎉 Generation complete!", style="bold green")

    except Exception as e:
        console.print(f"\n❌ Critical error: {e}", style="bold red")
        logging.error(f"Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
