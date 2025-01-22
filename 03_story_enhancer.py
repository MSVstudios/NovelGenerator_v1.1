import os
from pathlib import Path
import requests
from datetime import datetime
import logging
import re
import time
from typing import List, Dict, Tuple, Optional, Iterator, Any
import json
from dataclasses import dataclass
import sys

@dataclass
class SceneBlock:
    content: str
    scene_type: str
    key_elements: List[str]

class EnhancedCollaborativeImprover:
    def __init__(self, 
                 models: List[str] = ["gemma2:27b", "mistral-nemo:latest"],
                 style_specialist: str = "gemma2:27b",
                 dialogue_specialist: str = "mistral-nemo:latest"):
        self.models = models
        self.style_specialist = style_specialist
        self.dialogue_specialist = dialogue_specialist
        self.ollama_url = "http://localhost:11434/api/generate"

    def _print_dialogue(self, role: str, message: str, model: str = None):
        if model:
            print(f"\n[{role} - {model}]: ", end='', flush=True)
        else:
            print(f"\n[{role}]: ", end='', flush=True)
        print(message)

    def _stream_ollama(self, model: str, prompt: str) -> Iterator[str]:
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "presence_penalty": 0.1,
                "frequency_penalty": 0.1
            }
            
            print(f"\nSending request to Ollama ({model})...")
            response = requests.post(self.ollama_url, json=payload, stream=True)
            response.raise_for_status()
            
            collected_response = []
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    if 'response' in json_response:
                        chunk = json_response['response']
                        collected_response.append(chunk)
                        yield chunk
                        
            return ''.join(collected_response)
            
        except Exception as e:
            print(f"Error in Ollama request: {e}")
            raise

    def _detect_scene_type(self, text: str) -> str:
        text = text.lower()
        
        dialogue_markers = text.count(':') + text.count('"') + text.count('"')
        action_words = len([word for word in text.split() 
                          if word.endswith('ed') or word.endswith('ing')])
        descriptive_words = len([word for word in text.split() 
                              if word.endswith('ly') or word in ['the', 'a', 'an']])
        
        if dialogue_markers > len(text.split()) * 0.1:
            return 'dialogue'
        elif action_words > descriptive_words:
            return 'action'
        else:
            return 'description'

    def _extract_key_elements(self, text: str) -> List[str]:
        elements = []
        
        words = text.split()
        characters = set(word for word in words 
                        if word[0].isupper() and len(word) > 1 
                        and not word.isupper())
        if characters:
            elements.extend(list(characters)[:3])
        
        action_verbs = [word for word in words 
                       if word.endswith('ed') or word.endswith('ing')]
        if action_verbs:
            elements.extend(action_verbs[:3])
        
        return elements

    def _identify_scene_blocks(self, content: str) -> List[SceneBlock]:
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        scenes = []
        current_scene = []
        print("\nIdentifying scenes...")
        
        for paragraph in paragraphs:
            is_header = any([
                paragraph.startswith('Chapter'),
                paragraph.startswith('CHAPTER'),
                len(paragraph.split()) <= 4 and ':' in paragraph,
                paragraph.startswith('#'),
                all(char.isupper() for char in paragraph.replace(' ', ''))
            ])
            
            if is_header:
                print(f"Found header: {paragraph}")
                if current_scene:
                    scene_text = '\n\n'.join(current_scene)
                    scene_type = self._detect_scene_type(scene_text)
                    key_elements = self._extract_key_elements(scene_text)
                    scenes.append(SceneBlock(scene_text, scene_type, key_elements))
                    print(f"Created scene block: {scene_type} with {len(key_elements)} key elements")
                    current_scene = []
                continue
                
            current_scene.append(paragraph)
            
            if len('\n\n'.join(current_scene).split()) >= 100:
                scene_text = '\n\n'.join(current_scene)
                scene_type = self._detect_scene_type(scene_text)
                key_elements = self._extract_key_elements(scene_text)
                scenes.append(SceneBlock(scene_text, scene_type, key_elements))
                print(f"Created scene block: {scene_type} with {len(key_elements)} key elements")
                current_scene = []
        
        if current_scene:
            scene_text = '\n\n'.join(current_scene)
            scene_type = self._detect_scene_type(scene_text)
            key_elements = self._extract_key_elements(scene_text)
            scenes.append(SceneBlock(scene_text, scene_type, key_elements))
            print(f"Created final scene block: {scene_type} with {len(key_elements)} key elements")
        
        print(f"Total scenes identified: {len(scenes)}")
        return scenes

    def generate_improvement_prompt(self, scene: SceneBlock, prev_scene: Optional[SceneBlock] = None) -> str:
        prompt = f"""Improve this {scene.scene_type} scene while maintaining the exact narrative and key elements.
Key elements to preserve: {', '.join(scene.key_elements)}

Previous context: {prev_scene.content if prev_scene else 'Start of text'}

Scene to improve:
{scene.content}

Guidelines:
1. Enhance descriptive language and sensory details
2. Improve dialogue flow and character voices
3. Maintain consistency with context
4. Strengthen emotional impact
5. Keep exact same plot points and events

Provide only the improved scene without any comments or explanations."""
        
        print(f"\nGenerated improvement prompt for {scene.scene_type} scene")
        return prompt

    def _improve_scene(self, scene: SceneBlock, prev_scene: Optional[SceneBlock] = None) -> str:
        print(f"\nImproving {scene.scene_type} scene...")
        print(f"Original content length: {len(scene.content)}")
        
        specialist = (self.dialogue_specialist if scene.scene_type == 'dialogue' 
                     else self.style_specialist)
        
        try:
            # First improvement
            print(f"\nGetting first improvement from {specialist}")
            first_improvement = ""
            for chunk in self._stream_ollama(specialist, 
                self.generate_improvement_prompt(scene, prev_scene)):
                first_improvement += chunk
                print(chunk, end='', flush=True)
            print(f"\nFirst improvement length: {len(first_improvement)}")
            
            # Second model review
            review_prompt = f"""Review and suggest improvements:

Original:
{scene.content}

Improved version:
{first_improvement}

Analyze:
1. Key elements preserved: {scene.key_elements}
2. Style consistency
3. Character consistency
4. Flow improvements needed"""

            second_model = self.models[1] if self.models[1] != specialist else self.models[0]
            print(f"\nGetting review from {second_model}")
            
            review = ""
            for chunk in self._stream_ollama(second_model, review_prompt):
                review += chunk
                print(chunk, end='', flush=True)
            print(f"\nReview completed")

            # Final version
            final_prompt = f"""Create final version incorporating review feedback:

Original: {scene.content}
First improvement: {first_improvement}
Review suggestions: {review}

Provide only the improved text."""

            print(f"\nCreating final version with {specialist}")
            final_improvement = ""
            for chunk in self._stream_ollama(specialist, final_prompt):
                final_improvement += chunk
                print(chunk, end='', flush=True)
            
            if self._verify_quality(scene, final_improvement):
                print(f"\nQuality check passed")
                return final_improvement
            else:
                print(f"\nQuality check failed, using first improvement")
                return first_improvement

        except Exception as e:
            print(f"\nError improving scene: {e}")
            return scene.content

    def _verify_quality(self, scene: SceneBlock, improved: str) -> bool:
        if len(improved) < len(scene.content) * 0.8 or len(improved) > len(scene.content) * 1.5:
            print(f"Length check failed: Original={len(scene.content)}, Improved={len(improved)}")
            return False
            
        for element in scene.key_elements:
            if element.lower() not in improved.lower():
                print(f"Missing key element: {element}")
                return False
                
        return True

    def improve_chapter(self, content: str) -> str:
        print("\nStarting chapter improvement...")
        
        try:
            scenes = self._identify_scene_blocks(content)
            print(f"Found {len(scenes)} scenes to improve")
            
            improved_scenes = []
            prev_scene = None
            
            for i, scene in enumerate(scenes, 1):
                print(f"\nProcessing scene {i}/{len(scenes)}")
                improved = self._improve_scene(scene, prev_scene)
                improved_scenes.append(improved)
                prev_scene = scene
                print(f"Scene {i} completed")
            
            final_text = '\n\n'.join(improved_scenes)
            print(f"\nChapter improvement completed. Final length: {len(final_text)}")
            return final_text
            
        except Exception as e:
            print(f"Error in chapter improvement: {e}")
            return content

    def process_files(self, input_dir: str, output_dir: str):
        """Process all files in the input directory."""
        print(f"\nStarting file processing")
        print(f"Input directory: {os.path.abspath(input_dir)}")
        print(f"Output directory: {os.path.abspath(output_dir)}")
        
        # Check input directory
        if not os.path.exists(input_dir):
            raise ValueError(f"Input directory '{input_dir}' does not exist")
            
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get all files
        all_files = os.listdir(input_dir)
        print(f"\nAll files in directory:")
        for f in all_files:
            print(f"  - {f}")
            
        # Filter chapter files (only new, unprocessed ones)
        input_files = []
        for filename in all_files:
            if not filename.startswith('completed_chapter_') or not filename.endswith('.txt'):
                continue
                
            chapter_num = re.search(r'completed_chapter_(\d+)', filename)
            if not chapter_num:
                continue
                
            chapter_num = chapter_num.group(1)
            input_path = os.path.join(input_dir, filename)
            output_pattern = f"completed_chapter_{chapter_num}_*.txt"
            
            # Check if already processed
            existing_outputs = list(Path(output_dir).glob(output_pattern))
            if not existing_outputs:
                input_files.append(filename)
            else:
                print(f"Skipping {filename} - already processed")
            
        if not input_files:
            raise ValueError("No new chapters found to process!")
            
        # Sort files by chapter number
        input_files.sort(key=lambda x: int(re.search(r'completed_chapter_(\d+)', x).group(1)))
        
        print(f"\nFiles to process:")
        for f in input_files:
            print(f"  - {f}")
            
        # Process each file
        for filename in input_files:
            print(f"\nProcessing: {filename}")
            input_path = os.path.join(input_dir, filename)
            
            try:
                # Read content
                with open(input_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                print(f"Read {len(content)} characters from {filename}")
                
                if not content:
                    print(f"Warning: {filename} is empty, skipping")
                    continue
                    
                # Improve text
                print(f"Starting improvement process for {filename}")
                improved_content = self.improve_chapter(content)
                
                # Save result
                chapter_num = re.search(r'completed_chapter_(\d+)', filename).group(1)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"completed_chapter_{chapter_num}_{timestamp}.txt"
                output_path = os.path.join(output_dir, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(improved_content)
                    
                print(f"Successfully saved improved version to: {output_filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue
                
        print("\nProcessing completed!")

def main():
    INPUT_DIR = "plot"
    OUTPUT_DIR = os.path.join("plot", "improved")
    
    print("\nEnhanced Collaborative Text Improvement Process")
    print("-" * 50)
    print(f"Input directory: {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("\nStarting improvement process...\n")
    
    try:
        improver = EnhancedCollaborativeImprover()
        improver.process_files(INPUT_DIR, OUTPUT_DIR)
        print("\nText improvement completed successfully!")
        
    except Exception as e:
        print(f"\nError: {e}")
        raise

if __name__ == "__main__":
    main()