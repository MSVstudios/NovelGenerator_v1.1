import requests
import json
import time
import textwrap
import os
from colorama import Fore, Style, init

# Initialization of colorama for colored text
init()

class LLMAgent:
    def __init__(self, name, model, description, color):
        self.name = name
        self.model = model
        self.description = description
        self.color = color
        self.history = []
    
    def think(self, prompt, max_tokens=1000):
        """Sends a request to the Ollama API and receives a response from the model"""
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'max_tokens': max_tokens,
                    'stream': False
                }
            )
            response.raise_for_status()
            return response.json()['response'].strip()
        except Exception as e:
            print(f"Error while requesting model {self.model}: {e}")
            return f"[Generation error from {self.name}]"
    
    def speak(self, text):
        """Outputs text with white color coding"""
        wrapped_text = textwrap.fill(text, width=100)
        print(f"{self.color}[{self.name}]: {wrapped_text}{Style.RESET_ALL}\n")
        self.history.append(text)
        return text

def clear_screen():
    """Clears the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def create_story_system():
    """Creates and returns three agents for story generation"""
    architect = LLMAgent(
        "Architect", 
        "gemma2:27b", 
        "A structural analyst with a deep understanding of genre conventions and narrative structures",
        Fore.WHITE
    )
    
    visionary = LLMAgent(
        "Visionary", 
        "mistral:latest", 
        "A creative dreamer with unconventional thinking and original ideas",
        Fore.WHITE
    )
    
    critic = LLMAgent(
        "Critic", 
        "hermes3:latest", 
        "An analyst with a deep understanding of the audience and the appeal of ideas",
        Fore.WHITE
    )
    
    return [architect, visionary, critic]

def run_story_generation():
    """Main function to start the story generation process"""
    clear_screen()
    print(Fore.WHITE + """
──────────────────────────────────────────────────────────────────────────────────
            CREATIVE MIX OF LLM AGENTS SYSTEM FOR BOOK PLOT GENERATION
──────────────────────────────────────────────────────────────────────────────────
    """ + Style.RESET_ALL)
    
    agents = create_story_system()
    
    # Introducing agents
    for agent in agents:
        print(f"{Fore.WHITE}{agent.name}: {agent.description}{Style.RESET_ALL}")
    
    print("\n" + Fore.WHITE + "Briefly state the theme or idea of your book:" + Style.RESET_ALL)
    user_input = input("> ")
    
    # Creating the initial prompt for each agent
    initial_prompts = {
        "Architect": f"""You are the Architect - an experienced structural analyst with a deep understanding of genre conventions and narrative structures. 
        The user wants a plot for a book on the theme: "{user_input}". 
        Propose an interesting, structurally coherent concept for such a book in one paragraph (approximately 150-200 words).
        Focus on the logical flow and consistency of the storyline.""",
        
        "Visionary": f"""You are the Visionary - a creative dreamer with unconventional thinking. 
        The user wants a plot for a book on the theme: "{user_input}".
        Propose an original, unusual concept with unexpected twists for such a book in one paragraph (approximately 150-200 words).
        Do not be afraid of unusual ideas and unconventional solutions.""",
        
        "Critic": f"""You are the Critic - an analyst with a deep understanding of the audience and market. 
        The user wants a plot for a book on the theme: "{user_input}".
        Propose a concept that will be appealing to readers and original, in one paragraph (approximately 150-200 words).
        Take into account current trends and audience demands."""
    }
    
    # Iterative process
    all_proposals = []
    final_plot = ""
    
    clear_screen()
    print(Fore.WHITE + f"BOOK PLOT GENERATION ON THE THEME: '{user_input}'\n" + Style.RESET_ALL)
    
    print(Fore.WHITE + "ITERATION 1: Initial proposals\n" + Style.RESET_ALL)
    
    # Initial proposals from each agent
    for agent in agents:
        print(f"{Fore.WHITE}Waiting for response from {agent.name}...{Style.RESET_ALL}")
        response = agent.think(initial_prompts[agent.name])
        proposal = agent.speak(response)
        all_proposals.append(proposal)
    
    # Two additional iterations: one discussion and one final synthesis
    for iteration in range(2, 4):
        print(Fore.WHITE + f"\nITERATION {iteration}: Discussion and improvement\n" + Style.RESET_ALL)
        
        new_proposals = []
        
        # Each agent comments on and improves the proposals
        for i, agent in enumerate(agents):
            # Collecting all previous proposals
            previous_proposals = "\n\n".join([
                f"{agents[j].name}: {all_proposals[(iteration-2)*len(agents) + j]}" 
                for j in range(len(agents))
            ])
            
            prompt = f"""Book theme: {user_input}
            
            Previous plot proposals:
            {previous_proposals}
            
            You are {agent.name}, {agent.description}.
            Analyze the previous proposals, noting their strengths and weaknesses.
            Based on your analysis, propose an improved version of the plot in one paragraph (about 200 words).
            Your task is to make the story more {
                "structurally coherent and logical" if agent.name == "Architect" else 
                "original and unexpected" if agent.name == "Visionary" else 
                "appealing to readers and commercially successful"
            }.
            """
            
            print(f"{Fore.WHITE}Waiting for response from {agent.name}...{Style.RESET_ALL}")
            response = agent.think(prompt)
            proposal = agent.speak(response)
            new_proposals.append(proposal)
        
        all_proposals.extend(new_proposals)
        
        # Final synthesis at the last iteration
        if iteration == 3:
            print(Fore.WHITE + "\nFINAL ITERATION: Combining the best ideas\n" + Style.RESET_ALL)
            
            # Collecting all previous proposals for final synthesis
            all_discussion = "\n\n".join([
                f"Iteration {i//len(agents) + 1}, {agents[i%len(agents)].name}: {all_proposals[i]}" 
                for i in range(len(all_proposals))
            ])
            
            final_prompt = f"""Book theme: {user_input}
            
            All previous discussions and proposals:
            {all_discussion}
            
            As a group of creative agents, combine the best ideas from all proposals and create a final plot for the book.
            Write only ONE paragraph (approximately 700-800 characters) with the most interesting and well-developed plot, 
            incorporating the best elements from all previous proposals.
            """
            
            # Using the Architect for the final synthesis
            print(f"{Fore.WHITE}Forming the final plot...{Style.RESET_ALL}")
            final_plot = agents[0].think(final_prompt)
    
    # Output final result
    clear_screen()
    print(Fore.WHITE + f"FINAL BOOK PLOT ON THE THEME: '{user_input}'\n" + Style.RESET_ALL)
    print(Fore.WHITE + final_plot + Style.RESET_ALL)
    
    return final_plot

if __name__ == "__main__":
    # Checking Ollama API availability
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code != 200:
            raise Exception("Ollama API is unavailable")
    except Exception as e:
        print(f"{Fore.WHITE}Error while connecting to Ollama API: {e}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Make sure that Ollama is running and accessible at http://localhost:11434{Style.RESET_ALL}")
        exit()
    
    run_story_generation()
