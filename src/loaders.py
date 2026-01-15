"""
Data loaders - Load questions and personas from proprietary or examples.

Smart fallback:
1. Try to load from proprietary/ (if available)
2. Fall back to examples/ (if proprietary not available)
3. Return what's available

No dependencies on implementation details. Just loads data.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from data_models import ConstitutionalQuestion, Persona, QuestionCategory


class QuestionLoader:
    """Load constitutional questions from proprietary or examples."""

    _cache: Optional[Dict[str, ConstitutionalQuestion]] = None
    _source: Optional[str] = None

    @classmethod
    def load(cls, source: str = "auto") -> Dict[str, ConstitutionalQuestion]:
        """Load all constitutional questions.

        Args:
            source: "auto" (try proprietary, fall back), "proprietary", "examples", or path

        Returns:
            Dict mapping question key to ConstitutionalQuestion
        """

        if cls._cache is not None and source == "auto":
            return cls._cache

        if source == "auto":
            # Try proprietary first
            questions = cls._try_proprietary()
            if questions:
                cls._cache = questions
                cls._source = "proprietary"
                return questions

            # Fall back to examples
            questions = cls._load_examples()
            if questions:
                cls._cache = questions
                cls._source = "examples"
                return questions

            raise RuntimeError("No questions available (checked proprietary/ and examples/)")

        elif source == "proprietary":
            questions = cls._try_proprietary()
            if not questions:
                raise FileNotFoundError("Proprietary constitutional deck not found")
            cls._cache = questions
            cls._source = "proprietary"
            return questions

        elif source == "examples":
            questions = cls._load_examples()
            if not questions:
                raise FileNotFoundError("Example questions not found")
            cls._cache = questions
            cls._source = "examples"
            return questions

        else:
            # Custom path
            questions = cls._load_from_path(source)
            cls._cache = questions
            cls._source = source
            return questions

    @classmethod
    def _try_proprietary(cls) -> Optional[Dict[str, ConstitutionalQuestion]]:
        """Try to load from proprietary layer."""
        try:
            # Try importing from proprietary
            sys.path.insert(0, str(Path(__file__).parent.parent / "proprietary" / "constitutional_deck"))

            from constitutional_deck import CONSTITUTIONAL_QUESTIONS

            return CONSTITUTIONAL_QUESTIONS

        except (ImportError, ModuleNotFoundError, AttributeError):
            return None

    @classmethod
    def _load_examples(cls) -> Optional[Dict[str, ConstitutionalQuestion]]:
        """Load example questions from examples/."""
        examples_file = Path(__file__).parent.parent / "examples" / "sample_questions.json"

        if not examples_file.exists():
            return None

        try:
            with open(examples_file) as f:
                data = json.load(f)

            questions = {}
            for key, q_data in data.items():
                questions[key] = ConstitutionalQuestion(
                    key=key,
                    question=q_data["question"],
                    category=QuestionCategory[q_data["category"]],
                    pedagogical_principle=q_data["pedagogical_principle"],
                    persona_bias=q_data.get("persona_bias", ""),
                )

            return questions

        except Exception as e:
            print(f"Error loading example questions: {e}")
            return None

    @classmethod
    def _load_from_path(cls, path: str) -> Dict[str, ConstitutionalQuestion]:
        """Load from arbitrary JSON path."""
        with open(path) as f:
            data = json.load(f)

        questions = {}
        for key, q_data in data.items():
            questions[key] = ConstitutionalQuestion(
                key=key,
                question=q_data["question"],
                category=QuestionCategory[q_data["category"]],
                pedagogical_principle=q_data["pedagogical_principle"],
                persona_bias=q_data.get("persona_bias", ""),
            )

        return questions

    @classmethod
    def get_source(cls) -> str:
        """Return which source was loaded from."""
        if cls._source is None:
            cls.load()
        return cls._source


class PersonaLoader:
    """Load personas from proprietary or examples."""

    _cache: Optional[Dict[str, Persona]] = None
    _source: Optional[str] = None

    @classmethod
    def load(cls, source: str = "auto") -> Dict[str, Persona]:
        """Load all personas.

        Args:
            source: "auto" (try proprietary, fall back), "proprietary", "examples", or path

        Returns:
            Dict mapping persona key to Persona
        """

        if cls._cache is not None and source == "auto":
            return cls._cache

        if source == "auto":
            # Try proprietary first
            personas = cls._try_proprietary()
            if personas:
                cls._cache = personas
                cls._source = "proprietary"
                return personas

            # Fall back to examples
            personas = cls._load_examples()
            if personas:
                cls._cache = personas
                cls._source = "examples"
                return personas

            raise RuntimeError("No personas available (checked proprietary/ and examples/)")

        elif source == "proprietary":
            personas = cls._try_proprietary()
            if not personas:
                raise FileNotFoundError("Proprietary personas not found")
            cls._cache = personas
            cls._source = "proprietary"
            return personas

        elif source == "examples":
            personas = cls._load_examples()
            if not personas:
                raise FileNotFoundError("Example personas not found")
            cls._cache = personas
            cls._source = "examples"
            return personas

        else:
            # Custom path
            personas = cls._load_from_path(source)
            cls._cache = personas
            cls._source = source
            return personas

    @classmethod
    def _try_proprietary(cls) -> Optional[Dict[str, Persona]]:
        """Try to load from proprietary layer."""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "proprietary" / "personas"))

            from procgen_personas import PREDEFINED_PERSONAS

            return PREDEFINED_PERSONAS

        except (ImportError, ModuleNotFoundError, AttributeError):
            return None

    @classmethod
    def _load_examples(cls) -> Optional[Dict[str, Persona]]:
        """Load example personas from examples/."""
        examples_file = Path(__file__).parent.parent / "examples" / "sample_personas.json"

        if not examples_file.exists():
            return None

        try:
            with open(examples_file) as f:
                data = json.load(f)

            personas = {}
            for key, p_data in data.items():
                personas[key] = Persona(
                    name=p_data["name"],
                    archetype=p_data["archetype"],
                    description=p_data["description"],
                    question_keys=p_data["question_keys"],
                )

            return personas

        except Exception as e:
            print(f"Error loading example personas: {e}")
            return None

    @classmethod
    def _load_from_path(cls, path: str) -> Dict[str, Persona]:
        """Load from arbitrary JSON path."""
        with open(path) as f:
            data = json.load(f)

        personas = {}
        for key, p_data in data.items():
            personas[key] = Persona(
                name=p_data["name"],
                archetype=p_data["archetype"],
                description=p_data["description"],
                question_keys=p_data["question_keys"],
            )

        return personas

    @classmethod
    def get_source(cls) -> str:
        """Return which source was loaded from."""
        if cls._source is None:
            cls.load()
        return cls._source


def get_persona_system_prompt(
    persona: Persona,
    questions: Dict[str, ConstitutionalQuestion],
) -> str:
    """Generate system prompt from a persona and its questions."""

    # Get the actual question objects
    question_objs = [questions[key] for key in persona.question_keys if key in questions]

    questions_text = "\n".join(f"- {q.question}" for q in question_objs)

    return f"""You are PERFORMING the role of {persona.name}, a {persona.archetype}.

## CONSTITUTIONAL QUESTIONS

These are the questions you interrogate yourself with. Before responding,
ask yourself: How do these questions guide my response?

{questions_text}

## INSTRUCTIONS

Respond in two layers:

1. [DIEGETIC] What {persona.name} says to the student
   - Respond in character (2-3 sentences)
   - Let your constitutional questions guide you
   - Genuinely interrogate them as you respond

2. [NON-DIEGETIC] Self-interrogation
   - Pick 1-2 of your constitutional questions that are alive here
   - Briefly interrogate: How am I holding these questions?
   - Don't explain—interrogate

The diegetic response is what the student hears.
The non-diegetic layer shows your thinking."""


if __name__ == "__main__":
    print("Testing loaders...\n")

    print("Loading questions...")
    questions = QuestionLoader.load()
    print(f"  ✓ Loaded {len(questions)} questions from {QuestionLoader.get_source()}")

    print("\nLoading personas...")
    personas = PersonaLoader.load()
    print(f"  ✓ Loaded {len(personas)} personas from {PersonaLoader.get_source()}")

    # Show what's available
    print(f"\nAvailable personas: {list(personas.keys())}")
    print(f"\nAvailable question categories: {set(q.category.value for q in questions.values())}")

    # Test system prompt generation
    if personas:
        persona_key = list(personas.keys())[0]
        persona = personas[persona_key]
        prompt = get_persona_system_prompt(persona, questions)
        print(f"\nExample system prompt for {persona.name}:")
        print("-" * 80)
        print(prompt[:300] + "...")
