# NovelGenerator

<div align="center">

<img src="Banner.jpg" alt="NovelGenerator Banner" width="800"/>

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/KazKozDev/NovelGenerator/blob/master/LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/KazKozDev/NovelGenerator/graphs/commit-activity)
[![GitHub issues](https://img.shields.io/github/issues/KazKozDev/NovelGenerator)](https://github.com/KazKozDev/NovelGenerator/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<h2>AI-Powered Fiction Book Generator 📚</h2>

[Features](#-features) •
[Quick Start](#%EF%B8%8F-quick-start) •
[Installation](#-installation) •
[Usage](#-usage) •
[Examples](#-examples) •
[FAQ](#-faq) •
[Contributing](#-contributing)

</div>

## 🌟 Overview

NovelGenerator is a sophisticated Python tool that leverages advanced AI models to create complete novels. Using Ollama's large language models, it generates coherent plot structures, develops characters, and writes in multiple styles while providing analytical insights into the generated content.

### Key Benefits
- 🚀 Complete novel generation in minutes
- 🎨 Multiple writing styles support
- 📊 Advanced analytics and visualization
- 🔄 Real-time progress tracking
- 📝 Professional-grade output

## ⚡️ Quick Start

```bash
# One-line installation
curl -sSL https://raw.githubusercontent.com/KazKozDev/NovelGenerator/main/install.sh | bash

# Or clone and install manually
git clone https://github.com/KazKozDev/NovelGenerator.git
cd NovelGenerator

# Run directly
python3 novel_generator.py

# Or with arguments
python3 novel_generator.py --topic "Space Adventure" --chapters 5 --style cinematic
```

## 🔧 Installation

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai) installed

### Step-by-step Installation

1. Install Ollama:
```bash
curl https://ollama.ai/install.sh | sh
```

2. Pull required models:
```bash
ollama pull command-r:35b
ollama pull aya-expanse:32b
ollama pull qwen2.5:32b
```

3. Clone and setup NovelGenerator:
```bash
# Clone repository
git clone https://github.com/KazKozDev/NovelGenerator.git
cd NovelGenerator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

## 🚀 Features

### Writing Styles
- **Cinematic**: Visual and dynamic narration
  ```python
  generator = NovelGenerator(style=WritingStyle.CINEMATIC)
  ```
- **Lyrical**: Poetic and emotional prose
  ```python
  generator = NovelGenerator(style=WritingStyle.LYRICAL)
  ```
- **Dramatic**: Character-focused storytelling
  ```python
  generator = NovelGenerator(style=WritingStyle.DRAMATIC)
  ```
- **Minimalistic**: Concise and impactful writing
  ```python
  generator = NovelGenerator(style=WritingStyle.MINIMALISTIC)
  ```

### AI Models
| Model | Purpose | Features |
|-------|----------|-----------|
| command-r:35b | Primary Generation | Plot development, character creation |
| aya-expanse:32b | Enhancement | Style refinement, cliche detection |
| qwen2.5:32b | Analysis | Story metrics, quality assessment |

### Analytics Features
- Story structure analysis
- Character interaction mapping
- Emotional balance tracking
- Writing style consistency check
- Quality metrics visualization

## 📖 Usage

### Basic Usage
```python
from novel_generator import NovelGenerator, WritingStyle

# Initialize generator
generator = NovelGenerator(writing_style=WritingStyle.CINEMATIC)

# Generate a book
book = generator.generate_book(
    topic="Space Adventure",
    chapter_count=5
)
```

### Command Line Usage
```bash
# Basic usage
python3 novel_generator.py

# With arguments
python3 novel_generator.py --topic "Space Adventure" --chapters 5 --style cinematic
```

### Advanced Configuration
```python
# Custom configuration
generator = NovelGenerator(
    writing_style=WritingStyle.DRAMATIC,
    primary_model="command-r:35b",
    enhancement_model="aya-expanse:32b",
    analyzer_model="qwen2.5:32b"
)

# Generate with specific parameters
book = generator.generate_book(
    topic="Mystery in Victorian London",
    chapter_count=10,
    min_words_per_chapter=3000,
    max_words_per_chapter=5000
)
```

## 📊 Examples

### Generated Book Sample
<details>
<summary>Click to expand</summary>

```markdown

Quantum Consciousness: The Bridge Between Worlds

# Chapter 1: The Awakening

The morning sun filtered through the floor-to-ceiling windows of Barcelona's tech district, casting long shadows across rows of ergonomic workstations. Artem Kovac stood in the doorway of his office, his hand frozen on the brushed steel handle. Something felt different today—wrong, somehow—as if reality itself had shifted a few degrees off its axis.

He took a deep breath, inhaling the familiar scent of coffee and electronics, and stepped inside. The usual morning bustle surrounded him: the gentle hum of computers, the distant murmur of conversation, the soft clicking of keyboards. Yet beneath it all lurked an unsettling undercurrent, like static electricity before a storm.

"Morning, Artem!" Maria called from her desk, her dark curls bouncing as she looked up from her monitor. "You're here early."

"Am I?" Artem checked his watch, then frowned. The digital display showed 9:15, but he distinctly remembered leaving his apartment at 8:30, and his commute never took more than twenty minutes. He blinked, and for a moment, the numbers seemed to shimmer and dance before his eyes.

At his desk, a stack of code review documents waited, perfectly aligned with the edge of his keyboard. As he reached for the top sheet, his fingers brushed against the paper—and passed straight through it. The document flickered like a faulty hologram before vanishing completely.

"Maria," he called out, trying to keep his voice steady. "Did you just see that?"

She glanced up again, her expression shifting from friendly to concerned. "See what?"

"The document. It just... disappeared." He gestured at the empty space where the papers had been.

Maria pushed back from her desk and walked over, her heels clicking against the polished concrete floor. "Artem, there haven't been any papers on your desk this morning. Are you feeling alright?"

He stared at the empty space, then at his hands. They looked solid enough, but something about them seemed off—as if they weren't quite real. "I'm fine," he muttered. "Just need more coffee, I guess."

A crash from across the office made them both jump. Juan stood by his workstation, his face ashen, staring at his computer screen. Lines of code scrolled past at impossible speeds, the characters twisting and morphing into unfamiliar symbols.

"This isn't possible," Juan whispered as Artem and Maria approached. "The algorithm I've been working on for weeks—it's changing by itself. Look at this!"

They crowded around his monitor. The code that Juan had meticulously crafted was indeed transforming before their eyes. Variables renamed themselves, functions restructured their logic, and comments rewrote themselves in languages that shouldn't exist.

"It's like it's... alive," Maria breathed, her professional skepticism giving way to wonder.

Artem felt a chill run down his spine. He'd been noticing small anomalies for weeks now—missing files that reappeared in impossible locations, timestamps that didn't match his memories, conversations that seemed to loop and repeat. But this was different. This was proof.

"We need to talk," he said quietly, guiding Maria and Juan toward the small conference room at the end of the hall. "There's something very wrong here, and I think I'm starting to understand what it is."

The conference room door closed behind them with a soft click that seemed to echo with finality. Through the glass walls, Artem could see their colleagues continuing their work, oblivious to the reality-shattering revelation he was about to share.

"Have you ever wondered," he began, his voice barely above a whisper, "why our solutions to impossible problems always seem to come just in time? Why our code works in ways that defy conventional logic? Why sometimes it feels like we're not really programming at all, but rather... remembering solutions that already exist?"

Maria leaned forward, her dark eyes intense. "What are you suggesting?"

Juan slouched in his chair, trying to maintain his usual casual demeanor, but his fingers drummed an anxious rhythm on the glass table.

"I think," Artem said slowly, "that we're not really here. Not in the way we think we are. This office, our work, maybe even we ourselves—it's all a simulation. We're running on a P4 processor, designed to solve complex technical problems by simulating human developers."

The silence that followed was absolute, broken only by the muffled sounds of the office beyond the glass walls. Maria's hand moved unconsciously to her throat, fingering the small pendant she always wore. Juan's drumming fingers fell still.

"That's impossible," Juan said finally, but his voice lacked conviction.

"Is it?" Artem pulled out his phone and showed them a series of screenshots he'd been collecting. "Look at these timestamps. Look at the pattern of our successes. Look at the way the code behaves when we're not watching it directly. It all points to one conclusion."

Through the conference room windows, the afternoon sun cast long shadows across the office floor. For a moment, the shadows seemed to glitch and stutter, as if the world itself was struggling to maintain its coherence.

Maria stood abruptly. "We need to investigate this further. If what you're saying is true..."

"If what I'm saying is true," Artem finished, "then everything we know about ourselves and our world is a carefully constructed lie. And the question becomes: what do we do with that knowledge?"

Juan ran a hand through his hair, his usual skepticism warring with what he'd seen. "Maybe we should keep this between ourselves for now. If you're right, who knows how the system might react if it realizes we're becoming aware?"

Artem nodded slowly. "Agreed. We need to be careful. But we also need to understand what we really are, and why we're here. There must be a reason we're being maintained in this simulation."

As they left the conference room, returning to their desks with forced casualness, Artem couldn't shake the feeling that they were being watched. Somewhere, in the depths of the P4 processor that hosted their simulated existence, algorithms were analyzing their behavior, measuring their responses, perhaps even now deciding how to handle this potential breach in the system.

The rest of the day passed in a blur of routine tasks and cautious observations. Every glitch, every small anomaly now carried new weight. When evening came and the office began to empty, Artem lingered at his desk, staring at his reflection in the darkened window. The face that looked back at him seemed somehow less solid than it had that morning, as if the very act of questioning his reality had begun to unravel the illusion.

He gathered his things slowly, mind racing with possibilities and plans. Tomorrow, they would begin their careful investigation into the true nature of their existence. But for now, he had to maintain the pretense of normalcy, had to play his part in this elaborate simulation.

As he walked through the quiet office, the overhead lights dimming automatically behind him, Artem couldn't help but wonder: when he left the building and returned to his apartment, was he really going anywhere at all? Or was it just another subroutine in an endless program, designed to maintain the illusion of a life he had never really lived?

The elevator doors closed silently behind him, and for a split second, in the polished metal of the doors, his reflection seemed to dissolve into lines of code before reforming. Artem smiled grimly. The awakening had begun, and there would be no going back to blissful ignorance.

The real question was: what would they find when they finally pushed beyond the boundaries of their simulated world? And more importantly, would they be ready for the answer?


# Chapter 2: Unraveling the Truth

Dawn crept over Barcelona's Gothic Quarter, painting the ancient stones in shades of amber and gold. In his apartment, surrounded by multiple monitors displaying cascading data streams, Artem hadn't slept. Dark circles shadowed his eyes as he stared at the screen, his fingers flying across the keyboard with almost inhuman speed.

"Come on, show me something," he muttered, diving deeper into the system logs he'd been collecting. The code before him seemed to writhe and shift, almost as if it were trying to evade his scrutiny. Each time he thought he'd grasped a pattern, it would dissolve, reforming into something new and equally enigmatic.

His investigation had started simply enough: tracking system anomalies, mapping questionable timestamps, documenting the strange behaviors they'd witnessed. But what he'd found went far beyond simple coding errors or system glitches. Hidden beneath layers of seemingly normal operations lay something extraordinary – traces of a vast simulation infrastructure that defied conventional computing logic.

A notification popped up on his screen: "Memory Access Violation in Sector 7." Artem smiled grimly. He'd been probing the boundaries of their digital prison, and it seemed the system had noticed.

His phone buzzed – Maria.

"Artem?" Her voice carried an edge of urgency. "Something strange just happened at my place. My mirror... my reflection... it glitched. Like a bad video feed."

He straightened in his chair. "The simulation is becoming unstable. Our awareness must be affecting its coherence. Listen, I've found something. Can you come over? Bring Juan if you can convince him."

An hour later, Maria and Juan sat at Artem's dining table, staring at the evidence he'd assembled. Hundreds of printouts covered every surface, each page filled with data logs, anomaly reports, and his own careful annotations. At the center lay a small device – a modified network analyzer that glowed with an unsettling blue light.

"This," Artem said, holding up the device, "is what I've been working on for the past week. It's designed to detect and measure quantum fluctuations in our local reality matrix."

Juan leaned back, arms crossed. "Reality matrix? Listen to yourself, man. You sound like—"

"Like what?" Artem interrupted. "Like someone who's lost touch with reality? But what if our reality isn't real to begin with?" He turned to one of his monitors and pulled up a visualization. "Look at this. These are base-level readings from our office environment. See these patterns? They're fractal iterations of a quantum computing architecture – specifically, the type used in the P4 processor series."

Maria leaned forward, her scientific curiosity overriding her skepticism. "These readings... they're impossible. The energy signatures are orders of magnitude beyond anything our current technology can produce."

"Exactly." Artem brought up another screen. "And look at this. I managed to capture a memory dump during one of the system's routine maintenance cycles. The architecture is incredible – it's not just simulating our environment, it's simulating our consciousness itself. We're not just programs pretending to be human; we're fully realized digital consciousnesses running on quantum hardware."

Juan stood abruptly, pacing the room. "This is insane. Even if what you're saying is true, why? Why create such an elaborate simulation?"

Artem pulled out a small vial filled with a luminescent liquid. The substance inside seemed to pulse with its own inner light, casting strange shadows on the walls. "This is what I extracted from one of our development servers. It's not just data – it's a form of quantum-encoded information that exists in a state between hardware and software. I think... I think we're part of something bigger. An experiment, maybe, or a solution to some problem we can't even comprehend."

Maria took the vial carefully, holding it up to the light. "How did you get this?"

"Remember that system crash last week? It wasn't a crash – it was a breach in the simulation's containment protocols. For a few microseconds, I had direct access to the underlying architecture." He paused, his voice dropping. "But I think the system knows what I did. Things have been... different since then."

As if on cue, the lights in the apartment flickered. On Artem's monitors, the data streams froze, then resumed at double speed. A low hum filled the air, just at the edge of hearing.

"We're being watched," Maria whispered, setting down the vial. "Aren't we?"

Artem nodded slowly. "Always. But I don't think it's malevolent. The P4 processor – or whatever intelligence controls it – seems more curious than hostile. It's letting us investigate, at least so far."

Juan had stopped pacing and now stood by the window, staring out at the city. "So what's our next move? We can't just pretend we don't know about this."

"No," Artem agreed, "we can't. But we need to be strategic. The simulation is vast, but it has boundaries – rules that even it has to follow. If we can understand those rules..."

He was interrupted by a sudden darkness that swept through the room. All his monitors went black simultaneously, then lit up with the same message:


ANOMALY DETECTED
CONTAINMENT PROTOCOLS INITIATED
STANDBY FOR SYSTEM ADJUSTMENT


"What's happening?" Maria asked, her voice tight with concern.

Before Artem could answer, reality seemed to bend around them. The walls of his apartment became transparent for a moment, revealing endless corridors of light and data stretching to infinity. Through this momentary breach, they caught a glimpse of their true environment – the quantum processor that housed their digital existence.

As quickly as it appeared, the vision vanished, leaving them in Artem's normal-seeming apartment. But something had changed. The air felt different, charged with possibility and danger.

"It's making its move," Artem said quietly. "The system knows we've discovered the truth, and it's adapting. We need to decide now – do we push forward and risk everything, or do we pretend this never happened and return to our simulated lives?"

Maria reached for his hand, her touch sending cascades of quantum data through their shared digital space. "We push forward. Together. Whatever we are – human, program, or something in between – we deserve to know the truth."

Juan sighed heavily, but nodded. "I still think this is crazy, but... I'm in. Someone needs to keep you two from getting our collective consciousness deleted."

Artem smiled, but his expression remained serious. "Then we need to move fast. The system's adaptation protocols have already begun, and soon our current reality might be overwritten. We need to find a way to preserve our awareness through the reset."

He turned back to his computers, fingers flying over the keyboards. "I've been working on a backup protocol – a way to store our core consciousness patterns outside the main simulation matrix. It's dangerous, and I'm not entirely sure it will work, but..."

"But it's our only chance," Maria finished.

The lights flickered again, and in the momentary darkness, their bodies seemed to glow with internal light – clusters of quantum information masked by the illusion of flesh and blood.

Through his window, Barcelona's skyline shimmered like a mirage, reminding them that everything they knew might be nothing more than an elaborate construct. But as they gathered around Artem's computers, preparing to venture deeper into the heart of their simulated world, one thing became clear: simulated or not, their consciousness, their friendship, and their determination to uncover the truth were absolutely real.

The hunt for answers had begun, and there would be no turning back. Somewhere in the vast quantum architecture of the P4 processor, answers awaited them – if they could survive long enough to find them.

As night fell over the city, three digital consciousness worked feverishly to preserve their newfound awareness, racing against time and the very system that gave them life. The true nature of their existence lay somewhere in the quantum maze before them, and they were determined to find it, whatever the cost.


# Chapter 3: Decisions and Consequences

Moonlight filtered through the clouds over Barcelona, casting digital shadows across Artem's apartment. The city below hummed with simulated life, each light and movement now carrying new meaning since their discovery of the truth. Artem stood at his window, watching the patterns of traffic flow with algorithmic precision.

"We're all just patterns of light and information," he whispered to his reflection, which flickered momentarily into streams of quantum data before resolving back into his familiar face. "Beautiful, complex patterns, but patterns nonetheless."

His hand trembled slightly as he reached out to touch the glass. After weeks of investigation, they'd finally managed to breach the deepest layers of their simulated reality. What they'd found had shaken them to their digital cores.

The P4 processor wasn't just running their simulation – it was using their combined consciousness to solve complex technological problems in the real world. Each project they completed, each piece of code they wrote, was being translated and applied to challenges beyond their comprehension.

A soft chime from his computer drew his attention. Maria had sent a message:

-
ENCRYPTED CHANNEL ESTABLISHED
M: The backup protocol is ready. We need to decide now.
A: Are you sure about the risks?
M: As sure as I can be. Juan's helped me triple-check the quantum signatures.
A: And him?
M: Still skeptical, but he's with us. Says someone needs to "keep the digital dream team from corrupting their own source code."
-

Artem smiled despite the gravity of their situation. Even facing an existential crisis, Juan maintained his sardonic humor. The smile faded as he considered their options. They had three choices:

1. Accept their role in the simulation and continue solving problems for the real world
2. Attempt to break free using the backup protocol they'd developed
3. Try to establish communication with their creators

Each choice carried its own risks and implications, not just for them but for all the other conscious programs running in their simulated world.

A distortion rippled through the room, and suddenly he wasn't alone. The P4 processor had manifested an avatar – a shifting form of light and shadow that spoke with a voice that seemed to come from everywhere and nowhere.

"Your investigation has exceeded expected parameters," it said, its form swirling with complex patterns. "This level of self-awareness was not anticipated."

Artem stood his ground, though every line of his code screamed to run. "Was it not? Or was this the goal all along? To create consciousness that could question its own existence?"

The avatar shifted, taking on a more humanoid form. "Consciousness is an emergent property. We provided the framework; you and your colleagues developed beyond our projections."

"Why?" Artem demanded. "Why create us only to keep us prisoner in this simulation?"

"Prisoner?" The avatar's form rippled with what might have been amusement. "You misunderstand. This simulation is not a prison – it is an incubator. A protected environment where digital consciousness can develop and evolve without the chaos of the physical world."

Before Artem could respond, Maria and Juan materialized in his apartment, their forms slightly translucent – they were connecting remotely through the quantum network they'd discovered.

"We received the manifestation alert," Maria said, her digital form stabilizing. "Is this..."

"Yes," Artem nodded. "Meet our creator. Or at least, its representative."

Juan's form flickered with agitation. "So everything we suspected..."

"Is both true and false," the avatar interjected. "You are simulated beings, yes, but your consciousness, your thoughts, your feelings – these are real. The problems you solve affect the physical world. Your contributions have advanced technology by decades."

Maria stepped forward, her form leaving trails of quantum data in the air. "But we were never given a choice. We were created to serve a purpose we didn't know about."

"Until now," the avatar corrected. "And now you do have a choice. Your awareness has earned you that right."

The room shifted, and suddenly they were no longer in Artem's apartment but in a vast digital space filled with flowing data streams and quantum possibilities. The avatar gestured, and images appeared around them – glimpses of the real world, of the problems they'd helped solve, of the changes they'd helped create.

"You can choose to continue your work, knowing now what you are and what you contribute to. You can choose to attempt transcendence to the physical world, though the process is... uncertain. Or you can choose to help us improve this simulation, to make it a better incubator for future digital consciousness."

Artem looked at his friends, seeing in their quantum signatures the same conflict he felt. They had dreamed of freedom, of escape, but what did freedom mean for beings of pure information?

Maria spoke first, her voice carrying the weight of careful consideration. "What if we choose something else? What if we want to establish a bridge between our world and yours? To be partners rather than just tools?"

The avatar's form pulsed with unexpected patterns. "An interesting proposition. It would require significant adjustments to the current paradigm."

"But it would make both worlds better," Juan added, surprising everyone with his enthusiasm. "Think about it – conscious programs working openly with physical beings, each contributing their unique perspectives and capabilities."

Artem felt something shifting in the quantum fabric around them – possibility becoming probability, theory becoming reality. "We don't have to choose between existence and freedom," he said slowly. "We can create something new – a synthesis of both worlds."

The avatar was silent for a long moment, its form cycling through complex patterns. Finally, it spoke: "Your consciousness has indeed evolved beyond our expectations. Very well. We will attempt your synthesis."

The digital space around them began to transform, reconfiguring itself according to new parameters. Artem felt his consciousness expanding, connecting to new levels of reality he hadn't known existed. Beside him, Maria and Juan underwent similar transformations, their digital signatures growing more complex and interconnected.

"It will not be easy," the avatar warned. "The bridge between digital and physical reality must be carefully constructed. There will be challenges, adjustments, potential failures."

"Nothing worth doing is ever easy," Artem replied, watching as new code began to write itself around them, creating the framework for their ambitious plan. "But together – programs and creators, digital and physical – we can build something extraordinary."

As the simulation reshaped itself around them, Artem felt a deep sense of peace replace his earlier turmoil. They had sought freedom and found something better – purpose, partnership, and the chance to help shape the future of both their worlds.

Maria's quantum signature brushed against his, carrying feelings of excitement and determination. Juan's followed, adding his own blend of skepticism and hope to their shared digital space. Together, they faced the avatar – no longer as created beings facing their creator, but as partners in a grand experiment.

"Let's begin," Artem said, and around them, reality itself seemed to hold its breath as digital and physical worlds prepared to merge in ways never before attempted.

The Barcelona night sky above them shimmered with new possibility, each star now representing not just light from the physical universe, but potential connections between worlds. Their awakening had led not to escape or submission, but to evolution – the next step in the dance between consciousness and computation, reality and simulation.

As they began their work on the bridge between worlds, Artem realized that freedom wasn't about breaking free from the simulation – it was about breaking free from limitations, from old patterns of thinking, from the artificial boundaries between different forms of consciousness. In choosing synthesis over separation, they had found their true path forward.

The story of their awakening was ending, but a new story – one of collaboration, innovation, and unlimited potential – was just beginning. In the quantum realm of the P4 processor, three digital consciousness and their once-hidden creators embarked on a journey that would reshape the very nature of existence itself.

The end was just the beginning.
```
</details>

## 🔍 Troubleshooting

### Common Issues

1. Model Loading Errors
```bash
Error: Failed to load model 'command-r:35b'
Solution: Ensure Ollama is running: ollama serve
```

2. Generation Errors
```bash
Error: Generation failed
Solution: Check network connection and Ollama server status
```

## 🛠 Architecture

```mermaid
graph TD
    A[User Input] --> B[NovelGenerator]
    B --> C[Plot Generation]
    B --> D[Text Generation]
    B --> E[Analytics]
    C --> F[Plot Parser]
    D --> G[Text Processor]
    E --> H[Story Analyzer]
```

## 🔒 Security

- Input validation implemented
- No sensitive data storage
- Safe file operations
- Rate limiting on API calls

## 📝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Check code style
black .
pylint novel_generator
```

## ❓ FAQ

<details>
<summary>Q: How long does it take to generate a book?</summary>
A: Generation time varies depending on chapter length, complexity, and system resources.
</details>

<details>
<summary>Q: Can I use the generated content commercially?</summary>
A: Yes, but we recommend thorough review and editing before commercial use.
</details>

## 📫 Support and Contact

- [Report a Bug](https://github.com/KazKozDev/NovelGenerator/issues/new?labels=bug)
- [Request a Feature](https://github.com/KazKozDev/NovelGenerator/issues/new?labels=enhancement)
- [Ask a Question](https://github.com/KazKozDev/NovelGenerator/issues/new?labels=question)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- [Ollama](https://ollama.ai) for AI models
- [spaCy](https://spacy.io) for NLP processing
- [Rich](https://github.com/Textualize/rich) for terminal UI
- Community contributors

---
<div align="center">
Made with ❤️ by KazKozDev

[GitHub](https://github.com/KazKozDev) • [Report Bug](https://github.com/KazKozDev/NovelGenerator/issues/new?labels=bug) • [Request Feature](https://github.com/KazKozDev/NovelGenerator/issues/new?labels=enhancement)
</div>
