import json
import time
import os
import re
from openai import OpenAI

# Setting up the OpenAI client with the provided API key and model
client = OpenAI(api_key='Your API-key is here')


class BookGenerator:
    def __init__(self):
        self.model = "gpt-4o"
        self.story_premise = ""
        self.num_chapters = 0
        self.story_outline = ""
        self.chapters = []
        self.characters = {}  # Store character information in a dictionary for easy access
        self.chapter_summaries = {}  # Detailed chapter summaries
        self.settings = {}  # Settings/locations
        self.plot_events = []  # Main plot events
        self.world_name = ""  # World name for ensuring consistency
        self.chapter_plan = ""  # Detailed chapter plan
        self.timeline = {}  # Timeline information
        self.emotional_arc = {}  # Emotional arc of chapters
        self.transitions = {}  # Transitions between chapters
        self.recurring_motifs = []  # Recurring motifs or symbols for narrative cohesion

    def get_user_input(self):
        """Receives user input: story premise and number of chapters"""
        print(
            """
──────────────────────────────────────────────────────────────────────────────────
                      N O V E L   G E N E R A T O R   2 . 5
──────────────────────────────────────────────────────────────────────────────────
ENGINE: Running on OpenAI with gpt-4o
CAPABILITIES: Creates novels or fanfiction with consistency checks
GENERATION TIME: Up to 20-30 minutes
STORY INPUT: One paragraph (up to 830 characters) with the story idea
"""
        )
        self.story_premise = input("Please enter a paragraph describing your story idea: ")

        while True:
            try:
                self.num_chapters = int(input("How many chapters do you want (minimum 3): "))
                if self.num_chapters >= 3:
                    break
                else:
                    print("Please enter at least 3 chapters.")
            except ValueError:
                print("Please enter a valid number.")

    def generate_text(self, prompt, system_prompt="You are a creative fiction writer."):
        """Sends a request to OpenAI with the given prompt"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error making request to OpenAI: {e}")
            return None

    def extract_characters(self, text):
        """Extracts character information from the text and structures it"""
        characters = {}
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
        """Extracts the world name from the story outline to ensure consistency"""
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
                counts = {}
                for match in matches:
                    counts[match] = counts.get(match, 0) + 1
                return max(counts, key=counts.get)
        
        return ""

    def create_story_outline(self):
        """Generates an overall story outline with detailed descriptions of chapters, world, characters, and motifs"""
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

Also create a section titled "RECURRING MOTIFS" with 3-5 symbols, objects, or phrases that will recur throughout the story to provide thematic continuity.

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

        # Extract the world name
        self.world_name = self.extract_world_name(self.story_outline)
        
        if not self.world_name:
            world_prompt = f"""Based on this story outline, create a unique and memorable name for the main world/city/setting:

{self.story_outline}

The name should be a single term, creative, and fitting the tone of the story.
Reply with ONLY the world name, nothing else.
"""
            self.world_name = self.generate_text(world_prompt).strip()
            print(f"Generated world name: {self.world_name}")

        # Extract recurring motifs
        motif_prompt = f"""Based on this story outline, identify 3-5 recurring motifs, symbols, or objects that appear throughout the story:

{self.story_outline}

Format as a simple list of items, one per line.
These should be concrete objects, symbols, or phrases that can recur throughout chapters.
"""
        print("Identifying recurring motifs...")
        motifs_text = self.generate_text(motif_prompt)
        self.recurring_motifs = [motif.strip() for motif in motifs_text.strip().split('\n') if motif.strip()]
        print(f"Identified motifs: {', '.join(self.recurring_motifs)}")

        # Create a detailed chapter plan
        chapter_plan_prompt = f"""Based on the story outline, create a VERY detailed chapter-by-chapter plan.

STORY OUTLINE: {self.story_outline}

For EACH chapter (1 through {self.num_chapters}), provide:
1. Chapter title
2. Chapter summary (250-300 words)
3. Scene breakdown (list each scene with location and characters present)
4. Character development in this chapter
5. Plot advancement in this chapter
6. Timeline indicators (time of day, date, or how much time has passed since previous chapter)
7. Emotional tone and tension level (1-10) at the end of the chapter
8. How this chapter connects to the next (create a narrative bridge)

Be extremely specific and detailed. This plan will be used to ensure narrative consistency.
"""
        print("Creating detailed chapter plan...")
        self.chapter_plan = self.generate_text(chapter_plan_prompt, system_prompt)

    def create_chapter_summary(self, chapter_num, chapter_content):
        """Creates a detailed chapter summary to ensure narrative continuity"""
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
6. Emotional tone at the beginning and end of the chapter

CHAPTER CONTENT:
{chapter_content}

Your summary should be comprehensive enough that another writer could use it to maintain perfect continuity.
"""
        summary = self.generate_text(prompt, system_prompt)
        self.chapter_summaries[chapter_num] = summary
        return summary

    def update_character_tracking(self, chapter_num, chapter_content):
        """Updates character data based on the chapter content"""
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
5. Emotional state at the end of the chapter

Format as:
CHARACTER NAME: status|development|relationships|location|emotional_state

Only include characters who actually appear or are mentioned in this chapter.
"""
        character_updates = self.generate_text(prompt, system_prompt)

        update_pattern = r"([A-Z][A-Za-z\s]+):\s+([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^\n]+)"
        matches = re.findall(update_pattern, character_updates)

        for match in matches:
            name = match[0].strip()
            if name in self.characters:
                self.characters[name]["status"] = match[1].strip()
                self.characters[name]["development"].append({
                    "chapter": chapter_num,
                    "development": match[2].strip()
                })
                new_relationships = match[3].strip()
                if new_relationships:
                    for other_char in character_names:
                        if other_char != name and other_char in new_relationships:
                            self.characters[name]["relationships"][other_char] = chapter_num

                self.characters[name]["location"] = match[4].strip()
                self.characters[name]["emotional_state"] = match[5].strip()

                if self.characters[name]["first_appearance"] == 0:
                    self.characters[name]["first_appearance"] = chapter_num

    def update_timeline(self, chapter_num, chapter_content):
        """Extracts and updates timeline information for the chapter"""
        system_prompt = """You are a literary analyst specializing in temporal structure in narratives."""
        
        prompt = f"""Based on the following chapter content, determine:
1. How much time has passed in this chapter
2. What time of day/date it ends on
3. Any specific time markers mentioned

CHAPTER CONTENT:
{chapter_content}

Reply only with the time information in this format:
TIME_ELAPSED: [time passed during chapter]
END_TIME: [time of day/date at chapter end]
TIME_MARKERS: [any specific times mentioned]
"""
        
        time_info = self.generate_text(prompt, system_prompt)
        self.timeline[chapter_num] = time_info
        return time_info

    def track_emotional_arc(self, chapter_num, chapter_content):
        """Analyzes the emotional dynamics at the end of the chapter"""
        system_prompt = """You are a literary analyst specializing in emotional arcs in storytelling."""
        
        prompt = f"""Analyze the emotional tone at the end of this chapter:

CHAPTER CONTENT:
{chapter_content}

Determine:
1. The primary emotion at the chapter's end (tension, relief, hope, despair, etc.)
2. The level of tension (1-10 scale)
3. The primary unresolved question or conflict

Reply in this format:
EMOTION: [primary emotion]
TENSION: [level 1-10]
UNRESOLVED: [main unresolved question]
"""
        
        emotional_status = self.generate_text(prompt, system_prompt)
        self.emotional_arc[chapter_num] = emotional_status
        return emotional_status

    def create_chapter_transition(self, chapter_num, chapter_content):
        """Creates a transition from the current chapter to the next"""
        if chapter_num >= self.num_chapters:
            return ""
            
        system_prompt = """You are a master storyteller specializing in creating suspenseful 
chapter endings and smooth transitions between chapters."""
        
        chapter_plan_prompt = f"""From this detailed chapter plan, extract ONLY the plan 
for Chapter {chapter_num + 1}:

{self.chapter_plan}

Include ONLY Chapter {chapter_num + 1}'s detailed plan.
"""
        next_chapter_plan = self.generate_text(chapter_plan_prompt)
        
        emotional_status = self.emotional_arc.get(chapter_num, "")
        timeline_info = self.timeline.get(chapter_num, "")
        
        if self.recurring_motifs:
            chosen_motif = self.recurring_motifs[chapter_num % len(self.recurring_motifs)]
        else:
            chosen_motif = ""
        
        prompt = f"""Create a compelling transition paragraph or two to serve as the ending of Chapter {chapter_num} 
and create anticipation for Chapter {chapter_num + 1}.

CURRENT CHAPTER CONTENT (last 1000 characters):
{chapter_content[-1000:]}
        
NEXT CHAPTER PLAN: 
{next_chapter_plan}
        
EMOTIONAL STATE AT CHAPTER END:
{emotional_status}
        
TIMELINE INFORMATION:
{timeline_info}
        
RECURRING MOTIF TO INCLUDE IF POSSIBLE:
{chosen_motif}
        
The transition should:
1. Conclude the current chapter with a hook, an unanswered question, or tension
2. Create anticipation for what comes next
3. Avoid completely resolving all tension from the current chapter
4. Link to the theme or events of the upcoming chapter without being too explicit
5. Maintain the emotional tone but hint at potential changes in the next chapter
6. Include a subtle reference to the recurring motif if possible
        
Create only 1-2 paragraphs for this transition. These will be the FINAL paragraphs of the current chapter.
"""
        
        transition = self.generate_text(prompt, system_prompt)
        self.transitions[chapter_num] = transition
        return transition

    def create_next_chapter_opener(self, chapter_num):
        """Creates a strong opening for the next chapter that connects seamlessly with the previous events"""
        if chapter_num <= 1:
            return ""
            
        system_prompt = """You are a master storyteller specializing in creating 
engaging chapter openings that connect smoothly to previous events."""
        
        prev_chapter_summary = self.chapter_summaries.get(chapter_num - 1, "")
        prev_transition = self.transitions.get(chapter_num - 1, "")
        prev_emotional_status = self.emotional_arc.get(chapter_num - 1, "")
        prev_timeline = self.timeline.get(chapter_num - 1, "")
        
        timeline_pattern = r"END_TIME:\s*([^\n]+)"
        prev_end_time = ""
        if prev_timeline:
            time_match = re.search(timeline_pattern, prev_timeline)
            if time_match:
                prev_end_time = time_match.group(1).strip()
        
        chapter_plan_prompt = f"""From this detailed chapter plan, extract ONLY the plan 
for Chapter {chapter_num}:

{self.chapter_plan}

Include ONLY Chapter {chapter_num}'s detailed plan.
"""
        this_chapter_plan = self.generate_text(chapter_plan_prompt)
        
        prompt = f"""Create a compelling opening paragraph for Chapter {chapter_num} that connects 
seamlessly with the end of Chapter {chapter_num - 1}.

PREVIOUS CHAPTER SUMMARY:
{prev_chapter_summary}
        
END OF PREVIOUS CHAPTER:
{prev_transition}
        
EMOTIONAL STATE AT END OF PREVIOUS CHAPTER:
{prev_emotional_status}
        
TIME AT END OF PREVIOUS CHAPTER:
{prev_end_time}
        
THIS CHAPTER'S PLAN:
{this_chapter_plan}
        
The opening paragraph should:
1. Establish a clear time connection to the end of the previous chapter
   (e.g., "The next morning...", "Three days later...", "As the sun set on that fateful day...")
2. Provide a smooth transition that builds on the tension or questions from the previous chapter
3. Orient readers immediately in the scene (location, characters present)
4. Avoid summarizing or repeating information from the previous chapter
5. Set the emotional tone for this chapter
        
Create a single strong opening paragraph (3-5 sentences).
"""
        
        opener = self.generate_text(prompt, system_prompt)
        return opener

    def validate_chapter_consistency(self, chapter_num, chapter_content):
        """Checks the chapter for inconsistencies compared to previous parts of the narrative"""
        system_prompt = """You are a literary editor specializing in narrative consistency.
Your job is to identify and flag any inconsistencies in a narrative."""
        previous_summaries = ""
        for i in range(1, chapter_num):
            if i in self.chapter_summaries:
                previous_summaries += f"Chapter {i} Summary: {self.chapter_summaries[i]}\n\n"

        character_status = ""
        for name, data in self.characters.items():
            if data["first_appearance"] > 0:
                status = data["status"]
                first_app = data["first_appearance"]
                character_status += f"{name}: First appeared in Chapter {first_app}, Status: {status}\n"

        timeline_info = ""
        for i in range(1, chapter_num):
            if i in self.timeline:
                timeline_info += f"Chapter {i} Timeline: {self.timeline[i]}\n"

        prompt = f"""Analyze this chapter for consistency issues compared to previous chapters.

STORY PREMISE: {self.story_premise}

WORLD NAME: {self.world_name}

PREVIOUS CHAPTERS:
{previous_summaries}

CHARACTER STATUS:
{character_status}

TIMELINE INFORMATION:
{timeline_info}

CURRENT CHAPTER {chapter_num} CONTENT:
{chapter_content}

Identify ANY inconsistencies related to:
1. Character names or backgrounds
2. Setting/location names
3. Timeline/sequence of events
4. Plot contradictions
5. Sudden introduction of new characters without proper context
6. Time of day or elapsed time inconsistencies

If any inconsistencies are found, list them in order of severity.
If no inconsistencies are found, respond with "CONSISTENT".
"""
        consistency_check = self.generate_text(prompt, system_prompt)
        return consistency_check

    def fix_chapter_inconsistencies(self, chapter_num, chapter_content, issues):
        """Fixes the identified inconsistencies in the chapter"""
        system_prompt = """You are a professional novelist and editor who excels at maintaining narrative consistency.
Fix all inconsistencies while preserving the core narrative."""
        previous_summaries = ""
        for i in range(1, chapter_num):
            if i in self.chapter_summaries:
                previous_summaries += f"Chapter {i} Summary: {self.chapter_summaries[i]}\n\n"

        character_status = ""
        for name, data in self.characters.items():
            if data["first_appearance"] > 0:
                status = data["status"]
                first_app = data["first_appearance"]
                dev = "; ".join([d["development"] for d in data["development"]])
                character_status += f"{name}: First appeared in Chapter {first_app}, Status: {status}, Development: {dev}\n"

        timeline_info = ""
        for i in range(1, chapter_num):
            if i in self.timeline:
                timeline_info += f"Chapter {i} Timeline: {self.timeline[i]}\n"

        prompt = f"""Rewrite this chapter to fix all the identified consistency issues while maintaining the same overall plot and character development.

STORY PREMISE: {self.story_premise}

WORLD NAME: {self.world_name} (use this name consistently for the city/world)

PREVIOUS CHAPTERS:
{previous_summaries}

CHARACTER STATUS:
{character_status}

TIMELINE INFORMATION:
{timeline_info}

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
6. Keep appropriate transitions between scenes within the chapter

Rewrite the complete chapter while fixing all issues.
"""
        fixed_chapter = self.generate_text(prompt, system_prompt)
        return fixed_chapter

    def generate_chapter(self, chapter_num):
        """Generates a single chapter taking into account previous context and performs consistency checks"""
        system_prompt = """You are a celebrated novelist known for writing engaging, coherent chapters 
with natural flow and character development. Your chapters have clear narrative structure and 
maintain perfect consistency with previously established elements."""
        context_summaries = []
        for i in range(1, chapter_num):
            if i in self.chapter_summaries:
                context_summaries.append(f"Chapter {i} Summary: {self.chapter_summaries[i]}")
        context = "\n\n".join(context_summaries)

        character_context = []
        for name, data in self.characters.items():
            if data["first_appearance"] > 0 and data["first_appearance"] < chapter_num:
                status = data["status"]
                desc = data["description"]
                character_context.append(f"{name}: {desc}, Status: {status}")
        characters_in_chapter = "\n".join(character_context)

        timeline_context = ""
        for i in range(1, chapter_num):
            if i in self.timeline:
                timeline_context += f"Chapter {i} Timeline: {self.timeline[i]}\n"

        emotional_context = ""
        if chapter_num > 1 and (chapter_num - 1) in self.emotional_arc:
            emotional_context = f"End of previous chapter emotional state: {self.emotional_arc[chapter_num - 1]}"

        chapter_opener = ""
        if chapter_num > 1:
            chapter_opener = self.create_next_chapter_opener(chapter_num)

        chapter_plan_prompt = f"""From this detailed chapter plan, extract ONLY the plan for Chapter {chapter_num}:

{self.chapter_plan}

Include ONLY Chapter {chapter_num}'s detailed plan.
"""
        this_chapter_plan = self.generate_text(chapter_plan_prompt)

        if self.recurring_motifs:
            chosen_motif = self.recurring_motifs[chapter_num % len(self.recurring_motifs)]
            motif_instruction = f"Include the recurring motif '{chosen_motif}' somewhere in this chapter in a natural way."
        else:
            motif_instruction = ""

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

TIMELINE INFORMATION:
{timeline_context}

EMOTIONAL CONTEXT:
{emotional_context}

SUGGESTED CHAPTER OPENING:
{chapter_opener}

{motif_instruction}

GUIDELINES FOR THIS CHAPTER:
- Write a complete chapter with a clear beginning, middle, and end
- Each chapter should be approximately 2500-3000 words
- Include descriptive elements, dialogue, and character development
- Maintain consistent tone, voice, and character personalities
- This is chapter {chapter_num} of {self.num_chapters}, so structure it accordingly
- Do NOT repeat world-building elements that have been established in previous chapters
- Each chapter should advance the plot while having its own mini-arc
- Include chapter title at the beginning
- ONLY introduce new characters if they are essential and provide proper context for them
- Refer to the world/city consistently as {self.world_name}
- Begin by directly continuing from the previous chapter's events or revealing their consequences
- End the chapter with a compelling hook or unanswered question
- The last paragraph should create tension that leads into the next chapter

CHAPTER STRUCTURE GUIDELINES:
- If this is not the first chapter, begin by using the suggested chapter opening to create a smooth transition
- Don't repeat the world description that was given in previous chapters
- End the chapter with a compelling hook or unanswered question
- The last paragraph should create tension that leads into the next chapter

Format the chapter with proper paragraph structure and dialogue formatting. Start with the chapter title.
"""
        print(f"Generating Chapter {chapter_num}...")
        chapter_content = self.generate_text(prompt, system_prompt)

        print(f"Validating Chapter {chapter_num} for consistency...")
        consistency_check = self.validate_chapter_consistency(chapter_num, chapter_content)

        if "CONSISTENT" not in consistency_check:
            print(f"Consistency issues found in Chapter {chapter_num}. Fixing...")
            chapter_content = self.fix_chapter_inconsistencies(chapter_num, chapter_content, consistency_check)
            print(f"Chapter {chapter_num} fixed for consistency.")
        else:
            print(f"Chapter {chapter_num} is consistent with previous narrative.")

        print(f"Creating detailed summary for Chapter {chapter_num}...")
        self.create_chapter_summary(chapter_num, chapter_content)
        
        print(f"Updating character tracking for Chapter {chapter_num}...")
        self.update_character_tracking(chapter_num, chapter_content)
        
        print(f"Updating timeline information for Chapter {chapter_num}...")
        self.update_timeline(chapter_num, chapter_content)
        
        print(f"Analyzing emotional arc for Chapter {chapter_num}...")
        self.track_emotional_arc(chapter_num, chapter_content)

        if chapter_num < self.num_chapters:
            print(f"Creating transitional ending for Chapter {chapter_num}...")
            transition = self.create_chapter_transition(chapter_num, chapter_content)
            paragraphs = chapter_content.split('\n\n')
            if len(paragraphs) > 1:
                chapter_content = '\n\n'.join(paragraphs[:-1]) + '\n\n' + transition
            else:
                chapter_content = chapter_content + '\n\n' + transition

        return chapter_content

    def check_chapter_transitions(self):
        """Performs a final check on transitions between chapters and improves them if needed"""
        print("Performing final check on chapter transitions...")
        improved_chapters = []
        
        for i in range(len(self.chapters)):
            if i == 0:
                improved_chapters.append(self.chapters[i])
                continue
                
            prev_chapter = self.chapters[i-1]
            current_chapter = self.chapters[i]
            
            system_prompt = """You are a professional editor specializing in narrative flow and chapter transitions."""
            
            prompt = f"""Analyze the transition between these consecutive chapters and improve it if needed:

END OF PREVIOUS CHAPTER:
{prev_chapter[-1000:]}
        
BEGINNING OF CURRENT CHAPTER:
{current_chapter[:1000]}
        
If the transition is already smooth, respond with "TRANSITION: SMOOTH".
        
Otherwise, provide an improved beginning for the current chapter (first 2-3 paragraphs) that:
1. Creates a smoother connection with the previous chapter
2. Avoids repeating information already established
3. Maintains character and plot consistency
4. Progresses the timeline naturally
        
Start with "TRANSITION: REVISED" followed by the revised beginning.
"""
            
            transition_check = self.generate_text(prompt, system_prompt)
            
            if "TRANSITION: REVISED" in transition_check:
                revised_beginning = transition_check.split("TRANSITION: REVISED")[1].strip()
                current_chapter_parts = current_chapter.split('\n\n', 3)
                if len(current_chapter_parts) >= 3:
                    improved_chapter = current_chapter_parts[0] + '\n\n' + revised_beginning + '\n\n' + current_chapter_parts[3]
                    improved_chapters.append(improved_chapter)
                else:
                    improved_chapters.append(current_chapter)
            else:
                improved_chapters.append(current_chapter)
        
        self.chapters = improved_chapters
        print("Chapter transitions have been optimized.")

    def generate_book(self):
        """Generates the entire book with consistency checks"""
        self.get_user_input()
        self.create_story_outline()

        for i in range(1, self.num_chapters + 1):
            chapter = self.generate_chapter(i)
            self.chapters.append(chapter)

            if i < self.num_chapters:
                print("Pausing briefly before generating next chapter...")
                time.sleep(3)

        self.check_chapter_transitions()

        return self.compile_book()

    def compile_book(self):
        """Compiles all chapters into a single book text"""
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
        """Saves the generated book to a file"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(book_content)
        print(f"Book saved as {filename}")

        metadata = {
            "premise": self.story_premise,
            "world_name": self.world_name,
            "characters": self.characters,
            "chapter_summaries": self.chapter_summaries,
            "recurring_motifs": self.recurring_motifs,
            "timeline": self.timeline,
            "emotional_arc": self.emotional_arc,
        }

        with open("book_metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        print("Book metadata saved as book_metadata.json")


if __name__ == "__main__":
    generator = BookGenerator()
    book = generator.generate_book()
    generator.save_book(book)
