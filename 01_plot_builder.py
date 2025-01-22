from typing import List, Optional, Dict
import requests
import json
import sys
import os
from datetime import datetime
import re
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum


@dataclass
class ChapterData:
    number: int
    outline: str
    timestamp: datetime
    act: str
    scenes: Dict[str, str]
    continuity: Dict[str, str]  # Added for tracking chapter connections


class StoryAct(Enum):
    SETUP = "Setup"
    CONFRONTATION = "Confrontation"
    RESOLUTION = "Resolution"


class StoryElement(Enum):
    PLOT_THREAD = "Plot Thread"
    CHARACTER_ARC = "Character Arc"
    THEME_DEVELOPMENT = "Theme Development"
    SETUP_PAYOFF = "Setup and Payoff"


class ChapterGenerationError(Exception):
    """Custom exception for chapter generation errors."""
    pass


class StoryGenerator:
    def __init__(
        self,
        model_name: str = "llama3.3:70b-instruct-q2_K",
        base_url: str = "http://localhost:11434",
    ):
        self.model_name = model_name
        self.base_url = f"{base_url}/api/generate"
        self.plot_dir = Path("plot")
        self.logger = self._setup_logging()
        self.ensure_plot_directory()
        self.story_structure = {}
        self.chapter_contexts = {}  # Store context for each chapter

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("StoryGenerator")
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        fh = logging.FileHandler("story_generator.log")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        return logger

    def ensure_plot_directory(self) -> None:
        self.plot_dir.mkdir(parents=True, exist_ok=True)

    def _make_api_request(self, prompt: str) -> Optional[str]:
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                data = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": True,
                    "context_window": 128000,
                    "max_tokens": 8000,
                }

                response = requests.post(self.base_url, json=data, stream=True)
                response.raise_for_status()

                full_response = self._process_stream_response(response)
                if full_response:
                    return full_response

            except requests.exceptions.RequestException as e:
                self.logger.error(
                    f"API Error (attempt {retry_count + 1}/{max_retries}): {e}"
                )
            except json.JSONDecodeError as e:
                self.logger.error(
                    f"JSON Parsing Error (attempt {retry_count + 1}/{max_retries}): {e}"
                )

            retry_count += 1
            if retry_count < max_retries:
                self.logger.info(f"Retrying... ({retry_count + 1}/{max_retries})")

        return None

    def _process_stream_response(self, response: requests.Response) -> Optional[str]:
        full_response = []
        try:
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    if "response" in json_response:
                        chunk = json_response["response"]
                        full_response.append(chunk)
                        # Печатаем поток, чтобы видеть ответ (можно отключить при желании)
                        print(chunk, end="", flush=True)
            print()

            result = "".join(full_response).strip()
            if not result:
                raise ChapterGenerationError("Empty response from API")
            return result

        except Exception as e:
            self.logger.error(f"Error processing stream response: {e}")
            return None

    def _distribute_chapters_into_acts(self, num_chapters: int) -> Dict[StoryAct, int]:
        act_distribution = {
            StoryAct.SETUP: max(1, int(num_chapters * 0.25)),
            StoryAct.CONFRONTATION: max(1, int(num_chapters * 0.5)),
            StoryAct.RESOLUTION: max(1, int(num_chapters * 0.25)),
        }

        total_assigned = sum(act_distribution.values())
        if total_assigned < num_chapters:
            act_distribution[StoryAct.CONFRONTATION] += num_chapters - total_assigned

        return act_distribution

    def _get_chapter_context(self, chapter_num: int, total_chapters: int) -> Dict[str, Dict]:
        """Get context information for a chapter including previous and next chapters."""
        context = {
            "previous_chapter": self.chapter_contexts.get(chapter_num - 1, {})
            if chapter_num > 1
            else {},
            "next_chapter": self.chapter_contexts.get(chapter_num + 1, {})
            if chapter_num < total_chapters
            else {},
            "current_act": self._determine_current_act(chapter_num, total_chapters),
        }
        return context

    def generate_outline(self, num_chapters: int, book_concept: str) -> Optional[str]:
        """Generate initial story outline with continuity markers."""
        act_distribution = self._distribute_chapters_into_acts(num_chapters)
        self.story_structure = {
            "num_chapters": num_chapters,
            "acts": act_distribution,
            "concept": book_concept,
            "plot_threads": [],  # Track ongoing plot threads
        }

        prompt = (
            f"Create a {num_chapters}-chapter story outline following the three-act structure, "
            f"based on this concept:\n{book_concept}\n\n"
            "Three-Act Structure:\n\n"
            f"Act 1 - Setup ({act_distribution[StoryAct.SETUP]} chapters):\n"
            "- Establish the normal world and protagonist\n"
            "- Show what they want and their current life\n"
            "- Present the inciting incident\n"
            "- Plant seeds for future developments\n\n"
            f"Act 2 - Confrontation ({act_distribution[StoryAct.CONFRONTATION]} chapters):\n"
            "- Build complications and obstacles\n"
            "- Show character growth through challenges\n"
            "- Include a major midpoint reversal\n"
            "- Develop subplots and relationships\n\n"
            f"Act 3 - Resolution ({act_distribution[StoryAct.RESOLUTION]} chapters):\n"
            "- Build to the climax\n"
            "- Show the final challenge\n"
            "- Resolve the main story threads\n\n"
            "For each chapter, include:\n"
            "1. Start with 'Chapter X:' on its own line\n"
            "2. Key events and developments\n"
            "3. Character arcs progression\n"
            "4. Ongoing plot threads\n"
            "5. Setup elements for future chapters\n\n"
            "Ensure each chapter shows clear connections to previous and future events.\n\n"
            "Begin the outline:"
        )

        outline = self._make_api_request(prompt)
        if outline:
            self._analyze_plot_threads(outline)
            self._save_outline(outline, book_concept)
            return outline
        return None

    def _analyze_plot_threads(self, outline: str) -> None:
        """Analyze and store ongoing plot threads from the outline."""
        chapter_outlines = self._parse_chapter_outlines(
            outline, self.story_structure["num_chapters"]
        )

        for chapter_num, chapter_content in enumerate(chapter_outlines, 1):
            # Store context for each chapter
            self.chapter_contexts[chapter_num] = {
                "outline": chapter_content,
                "plot_threads": [],
                "character_arcs": [],
                "setups": [],
            }

    def generate_detailed_chapter_plan(
        self,
        outline: str,
        chapter_num: int,
        book_concept: str,
        current_act: StoryAct,
    ) -> Dict[str, str]:
        """Generate a detailed chapter plan without parsing; store the full text as 'raw_plan'."""
        # Получаем контекст от предыдущих и следующих глав
        context = self._get_chapter_context(chapter_num, self.story_structure["num_chapters"])
        previous_context = context["previous_chapter"]
        next_chapter_outline = context["next_chapter"].get("outline", "")

        prompt = (
            f"Based on this chapter outline and context:\n\n"
            f"CHAPTER OUTLINE:\n{outline}\n\n"
            "Create a detailed plan for this chapter considering:\n\n"
            "1. CONTINUITY FROM PREVIOUS:\n"
            "- Open plot threads to address\n"
            "- Character states and emotions\n"
            "- Previous setups to develop\n\n"
            "2. CHAPTER PROGRESSION:\n"
            "A. Opening Scene:\n"
            "- Connection to previous events\n"
            "- Initial situation and mood\n"
            "- Character goals and tensions\n\n"
            "B. Development Scenes:\n"
            "- Key events and turning points\n"
            "- Character interactions\n"
            "- Plot advancement\n\n"
            "C. Closing Scene:\n"
            "- Resolution of immediate conflicts\n"
            "- Setup for next chapter\n"
            "- Emotional impact\n\n"
            "3. FUTURE SETUPS:\n"
            "- Plot threads to continue\n"
            "- Character arc progression\n"
            "- Questions to leave open\n\n"
            "4. SCENE DETAILS:\n"
            "For each scene specify:\n"
            "- Setting and atmosphere\n"
            "- Character presence and purpose\n"
            "- Key events and dialogues\n"
            "- Connection to overall story\n\n"
        )

        # Добавляем небольшие подсказки под конкретный акт
        act_guidance = {
            StoryAct.SETUP: (
                "SETUP ACT GUIDELINES:\n"
                "- Establish elements that will pay off later\n"
                "- Show normal world before changes\n"
                "- Plant seeds for future conflicts\n"
            ),
            StoryAct.CONFRONTATION: (
                "CONFRONTATION ACT GUIDELINES:\n"
                "- Escalate established conflicts\n"
                "- Deepen character relationships\n"
                "- Create complications that affect future chapters\n"
            ),
            StoryAct.RESOLUTION: (
                "RESOLUTION ACT GUIDELINES:\n"
                "- Begin paying off setups\n"
                "- Show character growth culmination\n"
                "- Resolve ongoing threads\n"
            ),
        }

        prompt += act_guidance[current_act]

        # Прикрепляем контекст предыдущей и следующей главы, если он есть
        if previous_context:
            prompt += f"\nPREVIOUS CHAPTER CONTEXT:\n{previous_context.get('outline', '')}\n"
        if next_chapter_outline:
            prompt += f"\nNEXT CHAPTER EXPECTATIONS:\n{next_chapter_outline}\n"

        detailed_plan = self._make_api_request(prompt)
        if detailed_plan:
            # Сохраняем целиком без парсинга
            return {"raw_plan": detailed_plan}

        return {}

    def _save_chapter_plan(self, chapter_info: Dict[str, any]) -> None:
        """Save the chapter plan with continuity information."""
        try:
            filename = (
                self.plot_dir
                / f"chapter_{chapter_info['chapter_number']}_plan_{chapter_info['timestamp']:%Y%m%d_%H%M%S}.txt"
            )

            with open(filename, "w", encoding="utf-8") as f:
                # Заголовок главы
                f.write(f"=== CHAPTER {chapter_info['chapter_number']} ===\n")
                f.write(f"Act: {chapter_info['act']}\n")
                f.write("=" * 50 + "\n\n")

                # Краткая первоначальная информация об этой главе
                f.write("INITIAL OUTLINE:\n")
                f.write("-" * 30 + "\n")
                f.write(chapter_info["initial_outline"].strip())
                f.write("\n\n")

                # И выводим план главы целиком
                f.write("DETAILED CHAPTER PLAN (UNPARSED):\n")
                f.write("-" * 30 + "\n")
                f.write(chapter_info["scene_plan"].get("raw_plan", ""))

            self.logger.info(
                f"Saved chapter {chapter_info['chapter_number']} plan to {filename}"
            )

        except IOError as e:
            self.logger.error(f"Error saving chapter plan: {e}")
            raise

    def _determine_current_act(self, chapter_num: int, total_chapters: int) -> StoryAct:
        """Determine which act the current chapter belongs to."""
        act_distribution = self.story_structure["acts"]
        act1_end = act_distribution[StoryAct.SETUP]
        act2_end = act1_end + act_distribution[StoryAct.CONFRONTATION]

        if chapter_num <= act1_end:
            return StoryAct.SETUP
        elif chapter_num <= act2_end:
            return StoryAct.CONFRONTATION
        else:
            return StoryAct.RESOLUTION

    def _parse_chapter_outlines(self, outline: str, expected_chapters: int) -> List[str]:
        """Parse chapter outlines from the main outline."""
        chapter_pattern = re.compile(
            r"Chapter \d+:(.*?)(?=Chapter \d+:|$)", re.DOTALL
        )
        chapter_outlines = chapter_pattern.findall(outline)

        if len(chapter_outlines) != expected_chapters:
            self.logger.warning(
                f"Found {len(chapter_outlines)} chapters in outline, expected {expected_chapters}"
            )

        # Записываем основу конспекта в self.chapter_contexts
        for i, chapter_outline in enumerate(chapter_outlines, 1):
            if i not in self.chapter_contexts:
                self.chapter_contexts[i] = {}
            self.chapter_contexts[i]["outline"] = chapter_outline.strip()

        return chapter_outlines

    def _save_outline(self, outline: str, book_concept: str) -> None:
        """Сохранение основного конспекта в файл."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.plot_dir / f"outline_{timestamp}.txt"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("=== MAIN STORY OUTLINE ===\n")
                f.write(f"Book Concept:\n{book_concept}\n\n")
                f.write(outline)
            self.logger.info(f"Outline saved to {filename}")
        except IOError as e:
            self.logger.error(f"Error saving outline: {e}")

    def expand_story(
        self, outline: str, book_concept: str, num_chapters: int
    ) -> List[Dict[str, any]]:
        """Создание детального плана для каждой главы без парсинга."""
        chapter_plans = []
        chapter_outlines = self._parse_chapter_outlines(outline, num_chapters)

        self.logger.info(f"Starting detailed planning for {num_chapters} chapters...")

        for chapter_num, chapter_outline in enumerate(chapter_outlines, 1):
            current_act = self._determine_current_act(chapter_num, num_chapters)
            self.logger.info(f"Planning Chapter {chapter_num} ({current_act.value})...")

            try:
                scene_plan = self.generate_detailed_chapter_plan(
                    chapter_outline.strip(),
                    chapter_num,
                    book_concept,
                    current_act,
                )

                if scene_plan:
                    chapter_info = {
                        "chapter_number": chapter_num,
                        "act": current_act.value,
                        "initial_outline": chapter_outline.strip(),
                        "scene_plan": scene_plan,
                        "timestamp": datetime.now(),
                    }

                    # Обновляем контекст для следующих глав
                    self.chapter_contexts[chapter_num].update(
                        {
                            "detailed_plan": scene_plan,
                            "future_setups": scene_plan.get("raw_plan", ""),
                        }
                    )

                    self._save_chapter_plan(chapter_info)
                    chapter_plans.append(chapter_info)

                    self.logger.info(f"Successfully planned Chapter {chapter_num}")
                else:
                    self.logger.error(
                        f"Failed to generate scene plan for Chapter {chapter_num}"
                    )

            except Exception as e:
                self.logger.error(f"Error planning chapter {chapter_num}: {e}")
                self.logger.exception("Detailed error information:")

        self.logger.info(
            f"Completed planning {len(chapter_plans)} of {num_chapters} chapters"
        )
        return chapter_plans


def main():
    print("=== Story Generator with Chapter Continuity ===")
    print("Using Three-Act Structure and Scene-by-Scene Planning")
    print("All plans will be saved in the 'plot' directory\n")

    try:
        # Get number of chapters
        while True:
            try:
                num_chapters = int(input("Enter the number of chapters (1-20): "))
                if 1 <= num_chapters <= 20:
                    break
                print("Please enter a number between 1 and 20.")
            except ValueError:
                print("Please enter a valid number.")

        # Get book concept with detailed guidance
        print("\nPlease provide your book concept. Include:")
        print("1. Main character(s)")
        print("   - Their initial situation")
        print("   - What they want/need")
        print("   - Their main challenge")
        print("\n2. Story Setting")
        print("   - Time period")
        print("   - Location/world")
        print("   - Important context")
        print("\n3. Main Conflict")
        print("   - Central problem or challenge")
        print("   - Stakes and consequences")
        print("   - Potential complications")
        print("\n4. Themes and Tone")
        print("   - Key themes to explore")
        print("   - Emotional impact desired")
        print("   - Style or genre elements")

        book_concept = input("\nBook concept: ").strip()
        while not book_concept:
            print("Book concept cannot be empty.")
            book_concept = input("Please enter your book concept: ").strip()

        # Initialize generator
        generator = StoryGenerator()

        # Generate initial outline
        print("\nStep 1: Creating story outline...")
        print("- Developing three-act structure")
        print("- Establishing plot threads")
        print("- Planning character arcs")
        outline = generator.generate_outline(num_chapters, book_concept)

        if not outline:
            print("Failed to generate outline. Please check if your API is running.")
            return

        print("\nOutline generated successfully!")
        print(f"Saved to: {generator.plot_dir}/outline_[timestamp].txt")

        # Show structure analysis
        print("\nStep 2: Analyzing story structure...")
        structure = generator.story_structure
        print("\nAct Distribution:")
        for act, count in structure["acts"].items():
            print(f"- {act.value}: {count} chapters")

        # Generate detailed chapter plans
        print("\nStep 3: Creating detailed chapter plans...")
        print("For each chapter, developing:")
        print("- Continuity from previous chapters")
        print("- Detailed scene sequences")
        print("- Character and plot development")
        print("- Setups for future chapters")

        chapter_plans = generator.expand_story(outline, book_concept, num_chapters)

        # Final summary and next steps
        print(f"\nSuccess! Generated {len(chapter_plans)} of {num_chapters} chapter plans")
        print("\nEach chapter plan includes a raw, unparsed text from the model.")
        print("\nFile Organization:")
        print(f"1. Main Story Outline: {generator.plot_dir}/outline_[timestamp].txt")
        print("   - Complete story structure")
        print("   - Act breakdown")
        print("   - Chapter summaries")

        print(f"\n2. Chapter Plans: {generator.plot_dir}/chapter_X_plan_[timestamp].txt")
        print("   - Full raw text of the chapter plan (unparsed)")
        print("   - Outline references and continuity notes")

        print("\nNext Steps:")
        print("1. Review the main outline first")
        print("2. Read chapter plans in sequence")
        print("3. Note the continuity elements between chapters")
        print("4. Use scene details for actual writing")
        print("\nAll files are saved and ready for use!")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        logging.error(f"Unexpected error in main: {e}", exc_info=True)
    finally:
        print("\nNote: You can find all generated files in the 'plot' directory")
        print("Thank you for using the Story Generator!")


if __name__ == "__main__":
    main()
