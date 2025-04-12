import argparse
import requests
import json
import time
import os
import re
import datetime
from openai import OpenAI
import anthropic


class BookGenerator:
    def __init__(
        self,
        model="gemma3:12b",
        base_url="http://localhost:11434",
        story_premise="",
        num_chapters=3,
        language="en",
        genre="fantasy",
        audience="adult",
        tone="light",
        style="third person",
        setting="modern",
        themes="love",
        names="realistic",
    ):
        self.base_url = base_url + "/api/generate"  # whe can implement a check
        self.model = model # whe can implement a check
        self.api_key = None # 
        self.language = language # to be done
        self.language_settings = None # to be done
        # advanced promts
        self.genre = genre # to be done
        self.audience = audience # to be done
        self.tone = tone # to be done
        self.style = style # to be done
        self.setting = setting # to be done
        self.themes = themes # to be done
        self.names = names # to be done
        # Prompt template for generating story outline
        self.story_premise = story_premise
        self.max_premisw_lengh = 900
        self.num_chapters = num_chapters
        self.story_outline = ""
        self.chapters = []
        self.characters = {}
        self.chapter_summaries = {}
        self.settings = {}
        self.plot_events = []
        self.world_name = ""
        self.chapter_plan = ""
        self.timeline = {}
        self.emotional_arc = {}
        self.transitions = {}
        self.recurring_motifs = []
        

    def get_user_input(self):
        """Get the story premise and number of chapters from the user"""
        print(
            f"""
──────────────────────────────────────────────────────────────────────────────────
                      N O V E L   G E N E R A T O R   2 . 8
──────────────────────────────────────────────────────────────────────────────────
ENGINE: Running on Ollama with {self.model}
CAPABILITIES: Creates novels or fanfiction with consistency checks
GENERATION TIME: Up to an hour depending on computational resources
STORY INPUT: One paragraph up to {self.max_premisw_lengh} characters with your plot idea
"""
        )
        # we check if --synopsis is passed as an argument
        if not self.story_premise:
            self.story_premise = input("Please provide a paragraph about what your story is about: ")
        else:
            print(f"Using provided story premise: {self.story_premise}\n")
            # check if the self.story_premise is a file path
            if os.path.isfile(self.story_premise):
                # load the story promise file
                self.story_premise = open(self.story_premise, "r", encoding="utf-8").read() 
                print(f"Loaded story premise from file:\n {self.story_premise}\n")
            else:
                print(f"Using provided story premise: {self.story_premise}\n") 

        if len(self.story_premise) > self.max_premisw_lengh:
            print(f"Story premise is too long, we will limit it to {self.max_premisw_lengh} characters.")
            self.story_premise = self.story_premise[:self.max_premisw_lengh]
            print(f"Story premise limited to {self.max_premisw_lengh} characters: {self.story_premise}")

        try:
            if isinstance(self.num_chapters, str):
                self.num_chapters = int(self.num_chapters)
            if not isinstance(self.num_chapters, int) or self.num_chapters < 3:
                print("Number of chapters not valid, setting default to 3.")
                self.num_chapters = 3
        except ValueError:
            print("Invalid input for number of chapters, setting default to 3.")
            self.num_chapters = 3

        # Select the apropiate language for prompts
        with open("./json/story_outline_prompt.json", "r") as f:
            prompt_data = json.load(f)

        # Load the correct language settings
        language_settings = None
        for setting in prompt_data["prompts"]:
            if setting["language"] == self.language:
                language_settings = setting
                break

        if language_settings is None:
            print(f"No story outline settings found for language: {self.language}. Using default 'en'.")
            for setting in prompt_data["prompts"]:
                if setting["language"] == "en":
                    language_settings = setting
                    break
            if language_settings is None:
                raise ValueError("No default 'en' language settings found in story_outline_prompt.json!")

        # Load the language settings     
        self.language_settings = language_settings

    # API Call to LLMs
    def generate_text(self, prompt, system_prompt="You are a creative fiction writer."):
        """Make API call to different LLMs based on base_url"""

        data = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
        }
        headers = {}

        try:
            if self.is_local_ollama(self.base_url):
                # Ollama API
                # Retry the request up to 3 times to handle potential Ollama loading delays.
                for attempt in range(3):
                    try:
                        response = requests.post(self.base_url, json=data, timeout=300)  # timeout set to 5 minutes
                        response.raise_for_status()
                        return response.json()["response"]
                    except requests.exceptions.RequestException as e:
                        print(f"Attempt {attempt + 1} failed: {e}")
                        time.sleep(2)  # Wait before retrying
                print("Max retries exceeded. Request failed.")
                return None
            elif "openai" in self.base_url:
                # OpenAI API
                from openai import OpenAI

                client = OpenAI(api_key=self.api_key)
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ]
                response = client.chat.completions.create(model=self.model, messages=messages, stream=False)
                return response.choices[0].message.content
            elif "anthropic" in self.base_url:
                # Anthropic API
                import anthropic

                client = anthropic.Anthropic(api_key=self.api_key)
                combined_prompt = system_prompt + "\n" + prompt
                response = client.messages.create(
                    model=self.model, max_tokens=8192, messages=[{"role": "user", "content": combined_prompt}]
                )
                return response.content[0].text
            elif "openrouter" in self.base_url:
                # OpenRouter API uses OpenAI client
                openai_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,  # Use the stored API key
                )
                try:
                    response = openai_client.chat.completions.create(
                        model=self.model,
                        max_tokens=8192,
                        extra_body={
                            "models": ["anthropic/claude-3.5-sonnet", "gryphe/mythomax-l2-13b"],
                        },
                        messages=[{"role": "user", "content": prompt}],
                        timeout=60,  # Add a timeout
                    )
                    return response.choices[0].message.content  # Extract content
                except Exception as e:
                    print(f"OpenRouter API error: {e}")
                    return None
            elif "deepseek" in self.base_url: # https://api.deepseek.com/chat/completions
                # DeepSeek API
                from openai import OpenAI

                client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "system", "content": "You are a helpful assistant"}, {"role": "user", "content": prompt}],
                    stream=False,
                )
                return response.choices[0].message.content
            else:
                raise ValueError(f"Unsupported API in base_url: {self.base_url}")

        except Exception as e:
            print(f"Error making request: {e}")
            return None
    
    def is_local_ollama(self, base_url):
        """Check if the base_url is a local Ollama instance."""
        return (
            "localhost" in base_url
            or "127.0.0.1" in base_url
            or re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", base_url.split(":")[1].strip("/"), re.IGNORECASE) # check if is a local ip adress
        )

    def extract_characters(self, text, method_llm=True):
        """Extract character information from text and create structured data"""
        if method_llm:
            system_prompt = """You are an expert at extracting characters information from text.
    Your task is to identify all characters mentioned in the text and provide a brief description for each.
    The output MUST be in JSON format. Ensure the JSON is valid and parsable."""
            prompt = f"""Extract all characters information from the following text.
    The output MUST be a JSON array of character objects. Each object should have the following keys:
    - name: The character's name (string)
    - description: A brief description of the character (string)
    - first_appearance: 0,
    - status: "alive",
    - development: [],
    - relationships: {{}}
    
    TEXT:
    {text}
    
    Ensure the output is valid JSON. Start with '[' and end with ']'. Do not include any text outside of the JSON structure.
    Here is an example of the desired output format:
    [
      {{
        "name": "Character A",
        "description": "A brave warrior",
        "first_appearance": 1,
        "status": "alive",
        "development": [],
        "relationships": {{}}
      }},
      {{
        "name": "Character B",
        "description": "A wise wizard",
        "first_appearance": 2,
        "status": "alive",
        "development": [],
        "relationships": {{}}
      }}
    ]
    """
            try:
                json_output = self.generate_text(prompt, system_prompt)
                print(f"LLM JSON Output: {json_output}")
                if json_output:
                    try:
                        # Remove any markdown code blocks if they exist
                        json_output = json_output.replace('```json', '').replace('```', '').strip()
                        characters_list = json.loads(json_output)
                        print(f"Extracted characters list: {characters_list}")
    
                        # Convert the list to a dictionary with character names as keys
                        characters = {}
                        for character in characters_list:
                            name = character["name"]
                            characters[name] = character  # Assign the entire character dictionary
                        print(f"Extracted characters dict: {characters}")
                        return characters
    
                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"Error decoding JSON from LLM: {e}. JSON Output: {json_output}")
                        return {}
                else:
                    print("LLM returned empty output for character extraction.")
                    return {}
            except Exception as e:
                print(f"Error during LLM character extraction: {e}")
                return {}
        else:
            characters = {}  # Keep as a dictionary
            pattern = r"([A-Z][A-Za-z\s]+):\s+([^\n]+)"
            matches = re.findall(pattern, text)
    
            for match in matches:
                name = match[0].strip()
                description = match[1].strip()
                characters[name] = {  # Assign to dictionary using character name as key
                    "name": name,
                    "description": description,
                    "first_appearance": 0,
                    "status": "alive",
                    "development": [],
                    "relationships": {},
                }
            return characters

    def extract_world_name(self, outline, method_llm=True):
        """Extract consistent world name from the story outline"""
        if method_llm:
            system_prompt = """You are an expert at extracting world names from text.
    Your task is to identify the world name mentioned in the text.
    The output MUST be a single string with the world name."""
            prompt = f"""Extract the world name from the following text.
    The output MUST be a single string with the world name.
    
    TEXT:
    {outline}"""
            try:
                world_name = self.generate_text(prompt, system_prompt)
                if world_name:
                    # Remove any markdown code blocks if they exist
                    world_name = world_name.replace('```json', '').replace('```', '').strip()
                    # Check if the world name is empty or contains only whitespace
                    if not world_name or len(world_name) < 3:
                        print("LLM returned an empty or invalid world name.")
                        return ""
                    # Check if the world name is too long
                    if len(world_name) > 50:
                        print("LLM returned a world name that is too long.")
                        return ""
                    # Check if the world name contains invalid characters
                    if not re.match(r"^[A-Za-z0-9\s\-]+$", world_name):
                        print("LLM returned a world name with invalid characters.")
                        return ""
                    # if contain nuber can be an options
                    print(f"LLM extract world name: {world_name}")    
                    return world_name.strip()
                else:
                    print("LLM returned empty output for world name extraction.")
                    # generate one ?
                    return ""
            except Exception as e:
                print(f"Error during LLM world name extraction: {e}")
                return ""
        else:
            if not outline:
                print("No outline provided to extract world name from.")
                return ""
    
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
                    # Check if counts is empty before calling max
                    if counts:
                        return max(counts, key=counts.get)
                    else:
                        continue  # No matches for this pattern, try the next
    
            # If no specific world name is found, let the LLM generate one in later steps
            print("No world name found using patterns. Will attempt LLM generation later.")
            return ""

    def create_story_outline(self):
        """Generate a high-level outline for the entire story with improved structure"""

        # Calculate variables for the prompt
        middle_chapter_end = self.num_chapters - 2
        end_chapter_count = min(2, self.num_chapters - 2)
        climax_chapter_1 = self.num_chapters - 2
        climax_chapter_2 = self.num_chapters - 1

        system_prompt = self.language_settings["system_prompt"]

        if any([self.genre, self.audience, self.tone, self.style, self.setting, self.themes, self.names]) and "prompt_improved" in self.language_settings:
            prompt_template = self.language_settings["prompt_improved"]
            prompt = prompt_template.format(
            num_chapters=self.num_chapters,
            story_premise=self.story_premise,
            middle_chapter_end=middle_chapter_end,
            end_chapter_count=end_chapter_count,
            climax_chapter_1=climax_chapter_1,
            climax_chapter_2=climax_chapter_2,
            genre=self.genre,
            audience=self.audience,
            tone=self.tone,
            style=self.style,
            setting=self.setting,
            themes=self.themes,
            names=self.names,
            )
        else:
            prompt_template = self.language_settings["prompt"]
            prompt = prompt_template.format(
                num_chapters=self.num_chapters,
                story_premise=self.story_premise,
                middle_chapter_end=middle_chapter_end,
                end_chapter_count=end_chapter_count,
                climax_chapter_1=climax_chapter_1,
                climax_chapter_2=climax_chapter_2
            )

        print("----------------- Generating detailed story outline... ----------------- \n")
        self.story_outline = self.generate_text(prompt, system_prompt)
        print(f"-----------------  Generated story outline:\n {self.story_outline} ----------------- \n")

        if self.story_outline is None:
            print("Failed to generate story outline. Aborting.")
            # end the script for CLI version
            # or return None for GUI version
            # or raise an exception
            # depending on the context of usage
            # For CLI version, we can simply exit the script
            import sys
            sys.exit(1)
            # For GUI version, we can just return None or raise an exception
            # return None # or raise an exception

        # Extract character information
        story_outline = self.story_outline.replace("\n", " ")

        # Load the character prompt from the JSON file
        char_prompt = self.language_settings["char_prompt"].format(
             story_outline=story_outline
        )

        print(f"----------------- Creating detailed character profiles... ----------------- \n")
            
        character_text = self.generate_text(char_prompt, system_prompt)
        
        if character_text:
            # Extract characters from the generated text
            print(f"----------------- Character text: {character_text} ----------------- \n")
            self.characters = self.extract_characters(character_text)
        else:
            self.characters = {}
            print("Failed to generate character profiles. Aborting.")
            # end the script for CLI version
            import sys
            sys.exit(1)
            # or return None for GUI version
            # or raise an exception
        
        if self.characters and isinstance(self.characters, dict) and len(self.characters) > 0:
            print("----------------- Extracted characters: -----------------")
            for character_name, character_data in self.characters.items():
                print(f"- {character_name}: {character_data['description']}")
            print("---------------------------------------------------------\n")
        else:
            print("----------------- No characters were extracted. ----------------- \n")
        # Extract world name for consistency
        self.world_name = self.extract_world_name(self.story_outline)
        
        # If no world name was found, ask the LLM to create one
        if not self.world_name:
            world_prompt = self.language_settings["world_prompt"].format(
                story_outline=self.story_outline
            )
            print("Generating world name...")
            self.world_name = self.generate_text(world_prompt).strip()
            print(f"----------------- Generated world name: {self.world_name} ----------------- \n")

        print(f"----------------- World name: {self.world_name} -----------------\n")
        
        # Extract recurring motifs 
        motif_prompt = self.language_settings["motif_prompt"].format(
            story_outline=self.story_outline
        )
        print("----------------- Identifying recurring motifs... -----------------")
        motifs_text = self.generate_text(motif_prompt)
        self.recurring_motifs = [motif.strip() for motif in motifs_text.strip().split('\n') if motif.strip()]
        print("----------------- Identified motifs: -----------------")
        for motif in self.recurring_motifs:
            print(f"- {motif}")
        print("---------------------------------------------------------\n")

        # Create detailed chapter-by-chapter plan
        chapter_plan_prompt = self.language_settings["motif_prompt"].format(
            story_outline=self.story_outline, 
            num_chapters=self.num_chapters
        )
        
        print("----------------- Creating detailed chapter plan... ----------------- \n")
        self.chapter_plan = self.generate_text(chapter_plan_prompt, system_prompt)

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
6. Emotional tone at the beginning and end of the chapter

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
5. Emotional state at the end of the chapter

Format as:
CHARACTER NAME: status|development|relationships|location|emotional_state

Only include characters who actually appear or are mentioned in this chapter.
"""
        character_updates = self.generate_text(prompt, system_prompt)

        # Parse and update character data
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
                # Update relationship data
                new_relationships = match[3].strip()
                if new_relationships:
                    for other_char in character_names:
                        if other_char != name and other_char in new_relationships:
                            self.characters[name]["relationships"][other_char] = chapter_num

                # Update location and emotional state
                self.characters[name]["location"] = match[4].strip()
                self.characters[name]["emotional_state"] = match[5].strip()

                # Record first appearance if not already set
                if self.characters[name]["first_appearance"] == 0:
                    self.characters[name]["first_appearance"] = chapter_num

    def update_timeline(self, chapter_num, chapter_content):
        """Extract and update timeline information for chapter"""
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
        """Track emotional tone and tension at the end of the chapter"""
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
        """Create a transition from current chapter to the next"""
        if chapter_num >= self.num_chapters:
            return ""  # No transition needed for the last chapter
            
        system_prompt = """You are a master storyteller specializing in creating suspenseful 
        chapter endings and smooth transitions between chapters."""
        
        # Extract relevant part of chapter plan for the next chapter
        chapter_plan_prompt = f"""From this detailed chapter plan, extract ONLY the plan 
        for Chapter {chapter_num + 1}:

        {self.chapter_plan}

        Include ONLY Chapter {chapter_num + 1}'s detailed plan.
        """
        next_chapter_plan = self.generate_text(chapter_plan_prompt)
        
        # Get emotional status
        emotional_status = self.emotional_arc.get(chapter_num, "")
        
        # Get timeline info
        timeline_info = self.timeline.get(chapter_num, "")
        
        # Choose a recurring motif to include
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
        """Create a strong opening for the next chapter that connects to the previous one"""
        if chapter_num <= 1:
            return ""  # First chapter doesn't need a special opener
            
        system_prompt = """You are a master storyteller specializing in creating 
        engaging chapter openings that connect smoothly to previous events."""
        
        # Get information about the previous chapter
        prev_chapter_summary = self.chapter_summaries.get(chapter_num - 1, "")
        prev_transition = self.transitions.get(chapter_num - 1, "")
        prev_emotional_status = self.emotional_arc.get(chapter_num - 1, "")
        prev_timeline = self.timeline.get(chapter_num - 1, "")
        
        # Extract timeline info to know how much time has passed
        timeline_pattern = r"END_TIME:\s*([^\n]+)"
        prev_end_time = ""
        if prev_timeline:
            time_match = re.search(timeline_pattern, prev_timeline)
            if time_match:
                prev_end_time = time_match.group(1).strip()
        
        # Extract relevant part of chapter plan for this chapter
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

        # Add timeline information
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
                dev = "; ".join(data["development"]) if isinstance(data["development"], list) else data["development"]
                character_status += f"{name}: First appeared in Chapter {first_app}, Status: {status}, Development: {dev}\n"

        # Add timeline information
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

        # Add timeline information
        timeline_context = ""
        for i in range(1, chapter_num):
            if i in self.timeline:
                timeline_context += f"Chapter {i} Timeline: {self.timeline[i]}\n"

        # Add emotional arc information
        emotional_context = ""
        if chapter_num > 1 and (chapter_num - 1) in self.emotional_arc:
            emotional_context = f"End of previous chapter emotional state: {self.emotional_arc[chapter_num - 1]}"

        # Create chapter opener for chapters after the first
        chapter_opener = ""
        if chapter_num > 1:
            chapter_opener = self.create_next_chapter_opener(chapter_num)

        # Extract relevant part of chapter plan for this chapter
        chapter_plan_prompt = f"""From this detailed chapter plan, extract ONLY the plan for Chapter {chapter_num}:

{self.chapter_plan}

Include ONLY Chapter {chapter_num}'s detailed plan.
"""
        this_chapter_plan = self.generate_text(chapter_plan_prompt)

        # Choose a recurring motif to include
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
        print(f"Creating detailed summary for Chapter {chapter_num}...")
        self.create_chapter_summary(chapter_num, chapter_content)
        
        print(f"Updating character tracking for Chapter {chapter_num}...")
        self.update_character_tracking(chapter_num, chapter_content)
        
        print(f"Updating timeline information for Chapter {chapter_num}...")
        self.update_timeline(chapter_num, chapter_content)
        
        print(f"Analyzing emotional arc for Chapter {chapter_num}...")
        self.track_emotional_arc(chapter_num, chapter_content)

        # Add transition if not the last chapter
        if chapter_num < self.num_chapters:
            print(f"Creating transitional ending for Chapter {chapter_num}...")
            transition = self.create_chapter_transition(chapter_num, chapter_content)
            
            # Extract the last paragraph
            paragraphs = chapter_content.split('\n\n')
            # Replace the last paragraph with our transition
            if len(paragraphs) > 1:
                chapter_content = '\n\n'.join(paragraphs[:-1]) + '\n\n' + transition
            else:
                chapter_content = chapter_content + '\n\n' + transition

        return chapter_content

    def check_chapter_transitions(self):
        """Check and improve transitions between all chapters after generation"""
        print("Performing final check on chapter transitions...")
        improved_chapters = []
        
        for i in range(len(self.chapters)):
            if i == 0:
                improved_chapters.append(self.chapters[i])
                continue
                
            # Get current and previous chapters
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
                # Extract and apply the revised beginning
                revised_beginning = transition_check.split("TRANSITION: REVISED")[1].strip()
                # Replace the beginning of the chapter with the revised version
                current_chapter_parts = current_chapter.split('\n\n', 3)
                if len(current_chapter_parts) >= 3:
                    # Keep the chapter title and then replace the beginning
                    improved_chapter = current_chapter_parts[0] + '\n\n' + revised_beginning + '\n\n' + current_chapter_parts[3]
                    improved_chapters.append(improved_chapter)
                else:
                    improved_chapters.append(current_chapter)
            else:
                improved_chapters.append(current_chapter)
        
        self.chapters = improved_chapters
        print("Chapter transitions have been optimized.")

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

        # Perform final check on transitions between chapters
        self.check_chapter_transitions()

        return self.compile_book()

    def compile_book(self):
        """Compile all chapters into a complete book""" 
        #
        title_prompt = self.language_settings["title_prompt"].format(
            story_premise=self.story_premise,
            story_outline=self.story_outline
        )
    
        book_title = self.generate_text(title_prompt)
        book = f"# {book_title}\n\n"
        book += f"## Story Premise\n\n{self.story_premise}\n\n"
    
        for i, chapter in enumerate(self.chapters, 1):
            book += f"{chapter}\n\n"
    
        return book

    def save_book(self, book_content, filename="./output/generated_book.md"):
        """Save the generated book to a file"""
        # append data time to the file name before the extension
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename.replace(".md", f"_{timestamp}.md")
        # check if the directory exist if not make one
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        # Save the book content to a markdown file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(book_content)
        print(f"Book saved as {filename}")

        # Also save metadata for future reference
        metadata = {
            "premise": self.story_premise,
            "world_name": self.world_name,
            "characters": self.characters,
            "chapter_summaries": self.chapter_summaries,
            "recurring_motifs": self.recurring_motifs,
            "timeline": self.timeline,
            "emotional_arc": self.emotional_arc,
        }
        # Save metadata to a JSON file
        metadata_filename = filename.replace(".md", "_metadata.json")
        with open(metadata_filename, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        print(f"Book metadata saved as {metadata_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a book using a language model.")
    # model (gemma3:12b, gemma3:27b, llama3:7b, llama3:13b, mistral:7b, etc.)
    parser.add_argument("--model", type=str, default="gemma3:12b", help="The language model to use.")
    parser.add_argument("--synopsis", type=str, default="./premise.txt", help="The story synopsis. If omitted, it will be requested in the console.")
    parser.add_argument("--ollama_url", type=str, default="http://localhost:11434", help="The URL of the Ollama API.")
    parser.add_argument("--chapters", type=int, default="3", help="How many chapters would you like (Default3)")
    # language (it, en,fr,es)
    parser.add_argument("--language", type=str, default="en", help="Language of the book (default: en)")
    # genre (fantasy, sci-fi, romance, etc.)    
    parser.add_argument("--genre", type=str, default="fantasy", help="Genre of the book (default: fantasy)")
    # audience target (adult, young adult, children, womaen, romantic, erotic, etc.)
    parser.add_argument("--audience", type=str, default="adult", help="Target audience for the book (default: adult)")
    # tone (dark, light, serious, humorous, etc.)
    parser.add_argument("--tone", type=str, default="light", help="Tone of the book (default: light)")
    # style (first person, third person, etc.)
    parser.add_argument("--style", type=str, default="third person", help="Narrative style of the book (default: third person)")
    # setting (historical, modern, futuristic, etc.)
    parser.add_argument("--setting", type=str, default="modern", help="Setting of the book (default: modern)")
    # themes (love, friendship, betrayal, etc.)
    parser.add_argument("--themes", type=str, default="love", help="Themes of the book (default: love)")
    # character names (crealistic, fictionary, anagrams, etc.)
    parser.add_argument("--names", type=str, default="realistic", help="Character names style (default: realistic)")
    # output file name
    parser.add_argument("--output", type=str, default="./output/generated_book.md", help="Output file name (default: ./output/generated_book.md)")

    args = parser.parse_args()

    generator = BookGenerator(
        model=args.model,
        base_url=args.ollama_url,
        story_premise=args.synopsis,
        num_chapters=args.chapters,
        language=args.language,
        genre=args.genre,
        audience=args.audience,
        tone=args.tone,
        style=args.style,
        setting=args.setting,
        themes=args.themes,
        names=args.names,
    )

    book = generator.generate_book()

    generator.save_book(book, filename=args.output)
