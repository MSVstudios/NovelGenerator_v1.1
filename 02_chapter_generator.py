#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple
from collections import defaultdict

# --- spaCy block ---
try:
    import spacy
    from spacy.tokens import Span
except ImportError:
    print("spaCy is not installed! Please install it via:")
    print("   pip install spacy")
    print("   python -m spacy download en_core_web_sm")
    sys.exit(1)

# Attempt to load the English model for NER
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("The model en_core_web_sm is not installed.")
    print("Please install it via: python -m spacy download en_core_web_sm")
    sys.exit(1)


@dataclass
class PlotEvent:
    chapter: int
    event: str
    characters: Set[str]
    locations: Set[str]
    time_indicators: Set[str]


def process_entity_text(text: str) -> str:
    """Process entity text to normalize its form."""
    # Clean special characters and spaces
    text = text.strip().rstrip('*:.,!?')

    # Normalize case
    if text.isupper():
        text = text.capitalize()
    elif text.startswith('The '):
        text = text[4:]

    # Remove possessive case
    if text.endswith("'s"):
        text = text[:-2]

    return text


def is_valid_entity(text: str, pos_tags: List[str]) -> bool:
    """Check if the text is a valid entity."""
    # Basic checks for single words
    if len(text.split()) == 1:
        return (
            len(text) > 1 and
            text[0].isupper() and
            not any(char.isdigit() for char in text)
        )

    # Check for compound words
    words = text.split()
    # First word should be capitalized
    if not words[0][0].isupper():
        return False

    # Check for verb constructions
    if 'VERB' in pos_tags:
        return False

    return True


def determine_entity_type(text: str, original_type: str, pos_tags: List[str]) -> str:
    """Determine the correct entity type."""
    words = text.split()

    # For organizations
    if any(marker in text for marker in ['Project', 'Syndicate', 'System', 'Corporation', 'Institute', 'University']):
        return "ORG"

    # For locations
    if (
        any(marker in text for marker in ['City', 'Town', 'Street', 'Road', 'Avenue', 'Park']) or
        (len(words) > 1 and words[0] in {'New', 'Old', 'Neo', 'East', 'West', 'North', 'South'})
    ):
        return "GPE"

    # For characters
    if len(words) == 1 and original_type == "PERSON":
        return "PERSON"

    return original_type


def extract_entities_spacy(text: str) -> Set[Tuple[str, str]]:
    """
    Extract and process entities from text.
    Returns a set of tuples (entity, type).
    """
    content_lines = []

    for line in text.split('\n'):
        # Skip metadata and headers
        if not (line.startswith('#') or ':' in line):
            content_lines.append(line)

    main_content = ' '.join(content_lines)
    doc = nlp(main_content)
    entities = set()
    seen_names = set()

    # Filter words list
    filter_words = {
        'Screens', 'Faster', 'Graffiti', 'Finding', 'Focus', 'Anger',
        'Citizens', 'Cybernetics', 'Points', 'Development', 'Emotions',
        'Scenes', 'Arc', 'Motivations', 'Atmosphere', 'Setting'
    }

    for ent in doc.ents:
        if ent.label_ not in {"PERSON", "ORG", "GPE", "LOC"}:
            continue

        # Basic entity text cleaning
        entity_text = process_entity_text(ent.text)

        # Skip service fragments
        if entity_text.startswith('#') or ':' in entity_text:
            continue

        # Check basic conditions
        words = entity_text.split()
        pos_tags = [token.pos_ for token in ent]

        if not is_valid_entity(entity_text, pos_tags):
            continue

        # Determine correct type
        entity_type = determine_entity_type(entity_text, ent.label_, pos_tags)

        # Filter words from filter list
        if entity_text in filter_words:
            continue

        # Skip entities containing filtered words
        if any(word in entity_text for word in filter_words):
            continue

        # Add only unique entities
        if entity_text.lower() not in seen_names:
            entities.add((entity_text, entity_type))
            seen_names.add(entity_text.lower())

    return entities


def get_chapter_number(filename: str) -> int:
    """Extract chapter number from filename."""
    match = re.match(r'chapter_(\d+)_plan_', filename)
    if match:
        return int(match.group(1))
    return 0


def extract_plot_elements(text: str) -> List[str]:
    """Extract key plot elements from text."""
    doc = nlp(text)
    plot_elements = []

    for sent in doc.sents:
        if (
            any(ent.label_ in {"PERSON"} for ent in sent.ents) and
            any(token.pos_ == "VERB" for token in sent)
        ):
            plot_elements.append(sent.text)

    return plot_elements


def save_plot_summary(folder_path: str, chapter_num: int, plot_elements: List[str]):
    """Save plot summary to JSON file."""
    summary_file = Path(folder_path) / f"plot_summary_{chapter_num}.json"
    summary = {
        "chapter": chapter_num,
        "plot_elements": plot_elements
    }
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


def load_plot_summaries(folder_path: str, current_chapter_num: int) -> List[Dict]:
    """Load plot summaries of previous chapters."""
    summaries = []
    pattern = re.compile(r'plot_summary_(\d+)\.json')

    for file in os.listdir(folder_path):
        if match := pattern.match(file):
            chapter_num = int(match.group(1))
            if chapter_num < current_chapter_num:
                with open(Path(folder_path) / file, 'r', encoding='utf-8') as f:
                    summary = json.load(f)
                    summaries.append(summary)

    return sorted(summaries, key=lambda x: x["chapter"])


def scan_known_entities_in_folder(folder_path: str) -> Dict[str, str]:
    """Scan all files in folder and extract known entities."""
    all_entities = {}

    patterns = [
        re.compile(r'completed_chapter_\d+_\d{8}_\d{6}\.txt'),
        re.compile(r'chapter_\d+_plan_\d{8}_\d{6}\.txt')
    ]

    for pattern in patterns:
        chapter_files = [f for f in os.listdir(folder_path) if pattern.match(f)]
        for chapter_file in chapter_files:
            file_path = Path(folder_path) / chapter_file
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            found = extract_entities_spacy(text)
            for entity, entity_type in found:
                if entity in all_entities:
                    continue
                all_entities[entity] = entity_type

    return all_entities


def get_chapter_content(file_path: Path) -> str:
    """Read chapter content from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_all_previous_chapters(folder_path: str, current_chapter_num: int) -> List[Tuple[int, str]]:
    """Get content of all previous chapters."""
    all_files = []
    patterns = [
        re.compile(r'completed_chapter_\d+_\d{8}_\d{6}\.txt'),
        re.compile(r'chapter_\d+_plan_\d{8}_\d{6}\.txt')
    ]

    for pattern in patterns:
        matching_files = [f for f in os.listdir(folder_path) if pattern.match(f)]
        all_files.extend(matching_files)

    seen_chapters = set()
    previous_chapters = []

    for file in sorted(all_files, key=get_chapter_number):
        chapter_num = get_chapter_number(file)
        if chapter_num < current_chapter_num and chapter_num not in seen_chapters:
            file_path = Path(folder_path) / file
            content = get_chapter_content(file_path)
            previous_chapters.append((chapter_num, content))
            seen_chapters.add(chapter_num)

    return sorted(previous_chapters, key=lambda x: x[0])


def format_context_prompt(previous_chapters: List[Tuple[int, str]],
                         current_chapter_num: int,
                         current_chapter: str,
                         known_entities: Dict[str, str],
                         plot_summaries: List[Dict]) -> str:
    """Format prompt for chapter generation with context."""
    prompt = "# Story Context and Guidelines\n\n"

    prompt += "## Writing Style Guidelines:\n"
    prompt += (
        "1. Use vivid sensory details and descriptive language\n"
        "2. Show character emotions through actions and dialogue\n"
        "3. Balance narrative exposition with scene development\n"
        "4. Create engaging dialogue that reveals character personalities\n"
        "5. Maintain a consistent tone and pacing\n\n"
    )

    prompt += "## Known Characters and Entities:\n"
    for entity, entity_type in known_entities.items():
        prompt += f"- {entity} (Type: {entity_type})\n"
    prompt += "\n"

    prompt += "## Previous Plot Points:\n"
    for summary in plot_summaries:
        prompt += f"\nChapter {summary['chapter']}:\n"
        for element in summary['plot_elements']:
            prompt += f"- {element}\n"
    prompt += "\n"

    prompt += "## Previous Chapters:\n\n"
    for prev_num, prev_content in previous_chapters:
        prompt += f"Chapter {prev_num}:\n{prev_content}\n\n"

    prompt += "## Chapter Outline:\n"
    prompt += current_chapter + "\n\n"

    prompt += (
        f"Based on this context and outline, write Chapter {current_chapter_num} "
        f"as a complete, engaging narrative that advances the story while "
        f"maintaining consistency with previous events and character development."
    )

    return prompt


def process_chapters(folder_path: str):
    """
    Process text files using Ollama API with enhanced plot consistency.
    """
    OLLAMA_API = "http://localhost:11434/api/generate"

    print("Analyzing story elements and characters...")
    known_entities = scan_known_entities_in_folder(folder_path)
    print(f"Found {len(known_entities)} characters and entities:")
    for entity, entity_type in known_entities.items():
        print(f"  - {entity} ({entity_type})")

    # Updated pattern for plan files
    chapter_pattern = re.compile(r'chapter_\d+_plan_\d{8}_\d{6}\.txt')
    chapter_files = []
    
    # Collect all chapter plan files
    for file in os.listdir(folder_path):
        if chapter_pattern.match(file):
            chapter_files.append(file)
    
    # Sort files by chapter number
    chapter_files.sort(key=lambda x: get_chapter_number(x))

    if not chapter_files:
        print("\nNo chapter plan files found!")
        return

    print("\nProcessing chapters in sequence:")
    for file in chapter_files:
        print(f"- {file} (Chapter {get_chapter_number(file)})")

    for chapter_file in chapter_files:
        current_chapter_num = get_chapter_number(chapter_file)
        print(f"\nProcessing Chapter {current_chapter_num}...")

        previous_chapters = get_all_previous_chapters(folder_path, current_chapter_num)
        plot_summaries = load_plot_summaries(folder_path, current_chapter_num)

        print(f"Including {len(previous_chapters)} previous chapters")
        print(f"Found {len(plot_summaries)} plot summaries for context")

        file_path = Path(folder_path) / chapter_file
        current_chapter = get_chapter_content(file_path)

        prompt = format_context_prompt(
            previous_chapters,
            current_chapter_num,
            current_chapter,
            known_entities,
            plot_summaries
        )

        payload = {
            "model": "llama3.3:70b-instruct-q2_K",
            "prompt": prompt,
            "stream": True,
            "context_window": 128000,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_length": 8000
        }

        try:
            print("\nGenerating chapter content...")
            response = requests.post(OLLAMA_API, json=payload, stream=True)
            response.raise_for_status()

            generated_text = ""
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    chunk = json_response.get('response', '')
                    if chunk:
                        generated_text += chunk
                        sys.stdout.write(chunk)
                        sys.stdout.flush()

            # Clean up and format the generated text
            generated_text = generated_text.strip()
            if not generated_text.startswith(f"Chapter {current_chapter_num}"):
                generated_text = f"Chapter {current_chapter_num}\n\n{generated_text}"

            print("\n\nExtracted plot elements from generated content...")
            plot_elements = extract_plot_elements(generated_text)
            save_plot_summary(folder_path, current_chapter_num, plot_elements)

            # New output filename with 'completed_' prefix
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"completed_chapter_{current_chapter_num}_{timestamp}.txt"
            output_path = Path(folder_path) / output_file

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(generated_text)

            print(f"Chapter saved to: {output_file}")
            print(f"Plot summary saved to: plot_summary_{current_chapter_num}.json")

        except requests.exceptions.RequestException as e:
            print(f"Error processing chapter: {str(e)}")
            continue


if __name__ == "__main__":
    folder_path = os.path.abspath("plot")
    print(f"Working directory: {folder_path}")
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' not found!")
        sys.exit(1)
        
    print("\nChecking Ollama service...")
    try:
        response = requests.get("http://localhost:11434/api/version")
        if response.ok:
            print(f"Ollama service is running. Version: {response.json()['version']}")
        else:
            print("Ollama service responded, but status is not OK.")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Ollama service is not running. Please start Ollama first.")
        sys.exit(1)
        
    print("\nStarting chapter processing...")
    process_chapters(folder_path)
    print("\nProcessing complete!")