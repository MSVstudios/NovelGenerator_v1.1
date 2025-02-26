import requests
import json
import time
import os
import re


class BookGenerator:
    def __init__(self):
        self.base_url = "http://localhost:11434/api/generate"
        self.model = "gemma2:27b"
        self.story_premise = ""
        self.num_chapters = 0
        self.story_outline = ""
        self.chapters = []
        self.characters = {}  # Changed from list to dictionary for easier lookup
        self.chapter_summaries = {}  # Store detailed summaries of each chapter
        self.settings = {}  # Track settings/locations
        self.plot_events = []  # Track major plot events
        self.world_name = ""  # Consistent world name

    def get_user_input(self):
        """Get the story premise and number of chapters from the user"""
        print(
            """
──────────────────────────────────────────────────────────────────────────────────
                      N O V E L   G E N E R A T O R   2 . 0
──────────────────────────────────────────────────────────────────────────────────
ENGINE: Running on Ollama with gemma2:27b
CAPABILITIES: Creates novels or fanfiction with consistency checks
GENERATION TIME: Up to an hour depending on computational resources
STORY INPUT: One paragraph up to 830 characters with your plot idea
"""
        )
        self.story_premise = input("Please provide a paragraph about what your story is about: ")

        while True:
            try:
                self.num_chapters = int(input("How many chapters would you like (minimum 3): "))
                if self.num_chapters >= 3:
                    break
                else:
                    print("Please enter at least 3 chapters.")
            except ValueError:
                print("Please enter a valid number.")

    def generate_text(self, prompt, system_prompt="You are a creative fiction writer."):
        """Make API call to Ollama with the given prompt"""
        data = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
        }

        try:
            response = requests.post(self.base_url, json=data)
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            print(f"Error making request to Ollama: {e}")
            return None

    def extract_characters(self, text):
        """Extract character information from text and create structured data"""
        characters = {}
        # Look for patterns like "CHARACTER NAME: description"
        pattern = r"([A-Z][A-Za-z\s]+):\s+([^\n]+)"
        matches = re.findall(pattern, text)

        for match in matches:
            name = match[0].strip()
            description = match[1].strip()
            characters[name] = {
                "name": name,
                "description": description,
                "first_appearance": 0,
                "status": "alive",
                "development": [],
                "relationships": {},
            }

        return characters

    def extract_world_name(self, outline):
        """Extract consistent world name from the story outline"""
        # Generic pattern to find world names without hardcoding specific ones
        patterns = [
            r"Neo-[A-Za-z]+",
            r"[A-Z][a-z]+land",
            r"[A-Z][a-z]+ Kingdom",
            r"[A-Z][a-z]+ Empire",
            r"[A-Z][a-z]+ Realm",
            r"[A-Z][a-z]+ World",
            r"[A-Z][a-z]+ City"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, outline)
            if matches:
                # Use the most common name found
                counts = {}
                for match in matches:
                    counts[match] = counts.get(match, 0) + 1
                return max(counts, key=counts.get)
        
        # If no specific world name is found, let the LLM generate one in later steps
        return ""

    def create_story_outline(self):
        """Generate a high-level outline for the entire story with improved structure"""
        system_prompt = """You are a professional novelist and editor. 
        You excel at creating compelling story outlines that maintain coherence and proper narrative structure.
        Pay special attention to character development, consistent world-building, and logical plot progression."""
        prompt = f"""Based on the following story premise, create a detailed story outline for a {self.num_chapters}-chapter book.

Story premise: {self.story_premise}

For each chapter, provide:
1. A chapter title
2. Key plot events (3-4 bullet points with specific details)
3. Character development points (which characters appear and how they develop)
4. Setting/location details (be specific and consistent)

Also create a section titled "WORLD BUILDING" with:
1. The name of the main city/setting (create a unique, memorable name)
2. Key locations that will appear multiple times
3. Important technology or cultural elements

Then create a section titled "CHARACTERS" with:
1. Main protagonist (name, detailed description, motivation, arc)
2. Main antagonist (name, detailed description, motivation)
3. Supporting characters (name, role, connection to protagonist)

The outline should have a clear beginning (chapters 1-2), middle (chapters 3 to {self.num_chapters-2}), and end (final {min(2, self.num_chapters-2)} chapters).
Ensure proper rising action, climax, and resolution structure.

For the climax chapters (chapters {self.num_chapters-2} and {self.num_chapters-1}), provide extra detail about:
1. How the final confrontation unfolds
2. What's at stake for each character
3. Specific steps in the resolution

Make sure all character names, settings, and plot elements remain 100% consistent throughout.
"""
        print("Generating detailed story outline...")
        self.story_outline = self.generate_text(prompt, system_prompt)

        # Extract character information
        char_prompt = f"""Based on this story outline, create a detailed character guide:

{self.story_outline}

For EACH character, format as:
CHARACTER NAME: Brief description, role in story, key personality traits, motivation, background

Include EVERY character mentioned in the outline, even minor ones.
"""
        print("Creating detailed character profiles...")
        character_text = self.generate_text(char_prompt, system_prompt)
        self.characters = self.extract_characters(character_text)

        # Extract world name for consistency
        self.world_name = self.extract_world_name(self.story_outline)
        
        # If no world name was found, ask the LLM to create one
        if not self.world_name:
            world_prompt = f"""Based on this story outline, create a unique and memorable name for the main world/city/setting:

{self.story_outline}

The name should be a single term, creative, and fitting the tone of the story.
Reply with ONLY the world name, nothing else.
"""
            self.world_name = self.generate_text(world_prompt).strip()
            print(f"Generated world name: {self.world_name}")

        # Create detailed chapter-by-chapter plan
        chapter_plan_prompt = f"""Based on the story outline, create a VERY detailed chapter-by-chapter plan.

STORY OUTLINE: {self.story_outline}

For EACH chapter (1 through {self.num_chapters}), provide:
1. Chapter title
2. Chapter summary (250-300 words)
3. Scene breakdown (list each scene with location and characters present)
4. Character development in this chapter
5. Plot advancement in this chapter

Be extremely specific and detailed. This plan will be used to ensure narrative consistency.
"""
        print("Creating detailed chapter plan...")
        chapter_plan = self.generate_text(chapter_plan_prompt, system_prompt)

        # Store this for later reference
        self.chapter_plan = chapter_plan

    def create_chapter_summary(self, chapter_num, chapter_content):
        """Create a detailed summary of a chapter after it's written"""
        system_prompt = """You are a literary analyst specializing in narrative structure and continuity.
Create comprehensive, detailed summaries that capture all key elements."""
        prompt = f"""Create a detailed summary of the following chapter content.
This is Chapter {chapter_num} of a {self.num_chapters}-chapter book.

Include in your summary:
1. All key plot developments
2. Character appearances and development
3. Setting details
4. Important dialogue or revelations
5. How this chapter connects to previous chapters

CHAPTER CONTENT:
{chapter_content}

Your summary should be comprehensive enough that another writer could use it to maintain perfect continuity.
"""
        summary = self.generate_text(prompt, system_prompt)
        self.chapter_summaries[chapter_num] = summary
        return summary

    def update_character_tracking(self, chapter_num, chapter_content):
        """Update character tracking data based on a chapter's content"""
        system_prompt = """You are a narrative continuity expert who specializes in tracking character development.
Extract precise information about characters from text."""
        character_names = list(self.characters.keys())
        characters_str = ", ".join(character_names)
        prompt = f"""Based on the following chapter content, track the development of all characters mentioned.

CHAPTER CONTENT:
{chapter_content}

CHARACTERS TO TRACK: {characters_str}

For each character that appears in this chapter, provide:
1. Current status (alive, dead, injured, etc.)
2. Development in this chapter
3. New relationships formed
4. Current location

Format as:
CHARACTER NAME: status|development|relationships|location

Only include characters who actually appear or are mentioned in this chapter.
"""
        character_updates = self.generate_text(prompt, system_prompt)

        # Parse and update character data
        update_pattern = r"([A-Z][A-Za-z\s]+):\s+([^|]+)\|([^|]+)\|([^|]+)\|([^\n]+)"
        matches = re.findall(update_pattern, character_updates)

        for match in matches:
            name = match[0].strip()
            if name in self.characters:
                self.characters[name]["status"] = match[1].strip()
                self.characters[name]["development"].append({
                    "chapter": chapter_num,
                    "development": match[2].strip()
                })
                # Update relationship data
                new_relationships = match[3].strip()
                if new_relationships:
                    for other_char in character_names:
                        if other_char != name and other_char in new_relationships:
                            self.characters[name]["relationships"][other_char] = chapter_num

                # Record first appearance if not already set
                if self.characters[name]["first_appearance"] == 0:
                    self.characters[name]["first_appearance"] = chapter_num

    def validate_chapter_consistency(self, chapter_num, chapter_content):
        """Check chapter for consistency issues"""
        system_prompt = """You are a literary editor specializing in narrative consistency.
Your job is to identify and flag any inconsistencies in a narrative."""
        # Create context for consistency check
        previous_summaries = ""
        for i in range(1, chapter_num):
            if i in self.chapter_summaries:
                previous_summaries += f"Chapter {i} Summary: {self.chapter_summaries[i]}\n\n"

        character_status = ""
        for name, data in self.characters.items():
            if data["first_appearance"] > 0:  # Only include characters who have appeared
                status = data["status"]
                first_app = data["first_appearance"]
                character_status += f"{name}: First appeared in Chapter {first_app}, Status: {status}\n"

        prompt = f"""Analyze this chapter for consistency issues compared to previous chapters.

STORY PREMISE: {self.story_premise}

WORLD NAME: {self.world_name}

PREVIOUS CHAPTERS:
{previous_summaries}

CHARACTER STATUS:
{character_status}

CURRENT CHAPTER {chapter_num} CONTENT:
{chapter_content}

Identify ANY inconsistencies related to:
1. Character names or backgrounds
2. Setting/location names
3. Timeline/sequence of events
4. Plot contradictions
5. Sudden introduction of new characters without proper context

If any inconsistencies are found, list them in order of severity.
If no inconsistencies are found, respond with "CONSISTENT".
"""
        consistency_check = self.generate_text(prompt, system_prompt)
        return consistency_check

    def fix_chapter_inconsistencies(self, chapter_num, chapter_content, issues):
        """Fix identified consistency issues in a chapter"""
        system_prompt = """You are a professional novelist and editor who excels at maintaining narrative consistency.
Fix all inconsistencies while preserving the core narrative."""
        # Create context for the fix
        previous_summaries = ""
        for i in range(1, chapter_num):
            if i in self.chapter_summaries:
                previous_summaries += f"Chapter {i} Summary: {self.chapter_summaries[i]}\n\n"

        character_status = ""
        for name, data in self.characters.items():
            if data["first_appearance"] > 0:  # Only include characters who have appeared
                status = data["status"]
                first_app = data["first_appearance"]
                dev = "; ".join([d["development"] for d in data["development"]])
                character_status += f"{name}: First appeared in Chapter {first_app}, Status: {status}, Development: {dev}\n"

        prompt = f"""Rewrite this chapter to fix all the identified consistency issues while maintaining the same overall plot and character development.

STORY PREMISE: {self.story_premise}

WORLD NAME: {self.world_name} (use this name consistently for the city/world)

PREVIOUS CHAPTERS:
{previous_summaries}

CHARACTER STATUS:
{character_status}

CURRENT CHAPTER CONTENT:
{chapter_content}

CONSISTENCY ISSUES TO FIX:
{issues}

Guidelines for fixing:
1. Maintain the same overall plot progression and key events
2. Ensure all character names, backgrounds, and statuses match previous chapters
3. Use the established world name ({self.world_name}) consistently
4. Provide proper context for any character that hadn't appeared before
5. Ensure timeline and causality make sense

Rewrite the complete chapter while fixing all issues.
"""
        fixed_chapter = self.generate_text(prompt, system_prompt)
        return fixed_chapter

    def generate_chapter(self, chapter_num):
        """Generate a single chapter with enhanced context awareness and consistency checks"""
        system_prompt = """You are a celebrated novelist known for writing engaging, coherent chapters 
with natural flow and character development. Your chapters have clear narrative structure and 
maintain perfect consistency with previously established elements."""
        # Build context from previous chapters
        context_summaries = []
        for i in range(1, chapter_num):
            if i in self.chapter_summaries:
                context_summaries.append(f"Chapter {i} Summary: {self.chapter_summaries[i]}")
        context = "\n\n".join(context_summaries)

        # Create character context
        character_context = []
        for name, data in self.characters.items():
            if data["first_appearance"] > 0 and data["first_appearance"] < chapter_num:
                # Only include characters who have already appeared
                status = data["status"]
                desc = data["description"]
                character_context.append(f"{name}: {desc}, Status: {status}")
        characters_in_chapter = "\n".join(character_context)

        # Extract relevant part of chapter plan for this chapter
        chapter_plan_prompt = f"""From this detailed chapter plan, extract ONLY the plan for Chapter {chapter_num}:

{self.chapter_plan}

Include ONLY Chapter {chapter_num}'s detailed plan.
"""
        this_chapter_plan = self.generate_text(chapter_plan_prompt)

        prompt = f"""Write Chapter {chapter_num} of a novel based on the following guidelines:

STORY PREMISE: {self.story_premise}

WORLD NAME: {self.world_name} (use this name consistently throughout)

OVERALL STORY OUTLINE: {self.story_outline}

THIS CHAPTER'S DETAILED PLAN:
{this_chapter_plan}

CHARACTERS IN THIS STORY SO FAR:
{characters_in_chapter}

PREVIOUS CHAPTERS SUMMARY:
{context}

GUIDELINES FOR THIS CHAPTER:
- Write a complete chapter with a clear beginning, middle, and end
- Each chapter should be approximately 1500-2000 words
- Include descriptive elements, dialogue, and character development
- Maintain consistent tone, voice, and character personalities
- This is chapter {chapter_num} of {self.num_chapters}, so structure it accordingly
- Each chapter should advance the plot while having its own mini-arc
- Include chapter title at the beginning
- ONLY introduce new characters if they are essential and provide proper context for them
- Refer to the world/city consistently as {self.world_name}

Format the chapter with proper paragraph structure and dialogue formatting. Start with the chapter title.
"""
        print(f"Generating Chapter {chapter_num}...")
        chapter_content = self.generate_text(prompt, system_prompt)

        # Check for consistency issues
        print(f"Validating Chapter {chapter_num} for consistency...")
        consistency_check = self.validate_chapter_consistency(chapter_num, chapter_content)

        # If issues found, fix them
        if "CONSISTENT" not in consistency_check:
            print(f"Consistency issues found in Chapter {chapter_num}. Fixing...")
            chapter_content = self.fix_chapter_inconsistencies(chapter_num, chapter_content, consistency_check)
            print(f"Chapter {chapter_num} fixed for consistency.")
        else:
            print(f"Chapter {chapter_num} is consistent with previous narrative.")

        # Create summary and update character tracking
        self.create_chapter_summary(chapter_num, chapter_content)
        self.update_character_tracking(chapter_num, chapter_content)

        return chapter_content

    def generate_book(self):
        """Generate the complete book with enhanced consistency checks"""
        self.get_user_input()
        self.create_story_outline()

        for i in range(1, self.num_chapters + 1):
            chapter = self.generate_chapter(i)
            self.chapters.append(chapter)

            # Add a delay to prevent overwhelming the API
            if i < self.num_chapters:
                print("Pausing briefly before generating next chapter...")
                time.sleep(3)

        return self.compile_book()

    def compile_book(self):
        """Compile all chapters into a complete book"""
        title_prompt = f"""Create a compelling title for a book with the following premise and chapters:

Premise: {self.story_premise}

Chapter summaries:
{self.story_outline}
"""
        book_title = self.generate_text(title_prompt)
        book = f"# {book_title}\n\n"
        book += f"## Story Premise\n\n{self.story_premise}\n\n"

        for i, chapter in enumerate(self.chapters, 1):
            book += f"{chapter}\n\n"

        return book

    def save_book(self, book_content, filename="generated_book.md"):
        """Save the generated book to a file"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(book_content)
        print(f"Book saved as {filename}")

        # Also save metadata for future reference
        metadata = {
            "premise": self.story_premise,
            "world_name": self.world_name,
            "characters": self.characters,
            "chapter_summaries": self.chapter_summaries,
        }

        with open("book_metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        print("Book metadata saved as book_metadata.json")


if __name__ == "__main__":
    generator = BookGenerator()
    book = generator.generate_book()
    generator.save_book(book)
