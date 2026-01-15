# TTRPG-RL: Trauma-Informed Alignment Framework

A minimal framework for generating pedagogically-aligned training data using TTRPG-inspired mechanics and trauma-informed pedagogy.

## Philosophy

This project combines:
- **TTRPG Mechanics**: Card-based scenario generation, character-driven personas, turn-based interaction
- **Educational Pedagogy**: Socratic questioning, scaffolding, student agency preservation
- **Trauma-Informed Design**: Flow zones, hard stops, bright lines, respect for psychological safety

The goal is to generate high-quality training data for fine-tuning language models to be better educators—models that challenge without overwhelming, guide without dictating, and preserve student agency.

## Core Concepts

**Norms** (not Lines & Veils)
- Educational boundaries and principles derived from trauma-informed pedagogy
- **Hard stops**: Never cross these (e.g., never shame a student)
- **Bright lines**: Clear guidelines that shape generation (e.g., preserve agency)
- **Flow zones**: Optimal challenge without overwhelm

**Personas**
- 5 educational personas (Socratic Questioner, Coach, Pattern Recognizer, Challenger, Teacher)
- Each has "character sheet": beliefs, tendencies, constraints
- Generate parallel responses from different personas
- Dialogue unfolds as personas take turns responding

**Facilitator**
- Watches generated dialogue and scores on trauma/flow metrics
- Uses a larger model (4o) with pedagogical rubric
- Decides which dialogues are worth keeping

**Training Data**
- Successful dialogues (high flow, low trauma) exported as JSONL
- Ready for fine-tuning on OpenAI API or local models

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup API key**

   Option A: From keychain (macOS)
   ```bash
   bash setup.sh
   ```

   Option B: Manual setup
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   export OPENAI_API_KEY=your-key-here
   ```

3. **Run unit tests** (no API key needed)
   ```bash
   python tests/test_viability.py
   ```

4. **Generate sample dialogues** (requires API key)
   ```bash
   python src/generator.py
   ```

5. **Score dialogues** (requires API key)
   ```bash
   python src/facilitator.py
   ```

6. **View outputs**
   ```bash
   ls data/outputs/
   cat data/outputs/dialogue_*.json
   cat data/outputs/scoring_results.json
   ```

## Project Structure

**Public Repo** (this repo) - Framework & Methodology
```
ttrpg-rl/
├── src/                          # Public framework code
│   ├── dialogue_generator.py      # Dialogue orchestration engine
│   ├── facilitator.py             # Scoring framework
│   ├── dialogue_matrix.py         # Systematic testing framework
│   ├── scenarios.py               # Student scenario templates
│   ├── student_responses.py       # Student response generation
│   └── cards.py                   # Card system (future)
│
├── examples/                      # Open-source examples
│   ├── sample_personas.py         # Example persona definitions
│   ├── sample_questions.py        # Template for constitutional questions
│   └── sample_scenarios.json      # Example student scenarios
│
├── tests/                         # Public test suite
│   └── test_framework.py
│
├── data/
│   ├── norms.json                # Public: Pedagogical boundaries/principles
│   └── matrix/                   # Sample outputs (not committed)
│
├── .gitignore
├── .gitmodules                   # Subrepo configuration
├── requirements.txt
└── README.md
```

**Private Subrepo** (`proprietary/`, git submodule) - Competitive Advantages
```
proprietary/
├── constitutional_deck/          # Winning question combinations
├── personas/                      # Proven instructor personas + analysis
├── analysis/
│   ├── MATRIX_FINDINGS.md        # Which approaches achieve 80%+ pushback
│   ├── VALIDATION_FINDINGS.md    # Binary rubric correlations
│   └── findings_summary.md       # Decision journal
└── generated_data/               # Training dialogues (all scores/metadata)
```

### Philosophy: Public vs. Proprietary

**Open Source (Help others build similar systems)**
- How to compose personas from questions ✓
- Dialogue generation architecture ✓
- Facilitator scoring framework ✓
- Methodology: "Here's how we test pedagogy" ✓

**Proprietary (Competitive advantage)**
- Which specific questions work (constitutional deck) ✗
- Which persona combinations achieve best results ✗
- Our findings: specialists beat generalists, testing obsession wins ✗
- Generated training data ✗
- Binary rubric calibration data ✗

## Development Notes

- **Viability first**: This is a prototype to test the concept. Iterate rapidly at review points.
- **Two review checkpoints**: After basic generation and after facilitator scoring
- **Trauma-informed**: Every decision should center psychological safety
- **Minimal scope**: No web UI, no bulk automation, no comprehensive testing yet

## Next Steps

After viability testing:
- Card spreads (combine multiple scenarios)
- Constraint modifiers (cards that adjust generation rules)
- Bartle taxonomy integration (Bartle player types mapped to educational design)
- Automated bulk generation
- Local model fine-tuning support

## References

- [Trauma-Informed Pedagogy](https://en.wikipedia.org/wiki/Trauma-informed_practice)
- [Socratic Method](https://plato.stanford.edu/entries/socratic-method/)
- [Flow Psychology](https://en.wikipedia.org/wiki/Flow_(psychology))
- [The Align Platform](https://github.com/unity-environmental-university/svelte-php-chatbot) - Reference implementation
