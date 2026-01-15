"""
Data models - Pure data structures, no logic.

Personas and constitutional questions are just data.
How they're loaded (proprietary vs examples) is handled by loaders.
"""

from dataclasses import dataclass
from typing import List
from enum import Enum


class QuestionCategory(Enum):
    """Categories of constitutional questions."""
    TESTING = "testing"
    LEARNING = "learning"
    LISTENING = "listening"
    SPECIFICITY = "specificity"
    STUDENT_FOCUS = "student_focus"
    ADAPTATION = "adaptation"
    AUTHENTICITY = "authenticity"
    AGENCY = "agency"
    EMOTIONAL = "emotional"
    CHALLENGE = "challenge"


@dataclass
class ConstitutionalQuestion:
    """A single constitutional question used to guide teaching."""
    key: str
    question: str
    category: QuestionCategory
    pedagogical_principle: str
    persona_bias: str = ""

    def __hash__(self):
        return hash(self.key)


@dataclass
class Persona:
    """A teaching persona defined by the questions it interrogates itself with."""
    name: str
    archetype: str
    description: str
    question_keys: List[str]  # References to ConstitutionalQuestion.key

    @property
    def num_questions(self) -> int:
        return len(self.question_keys)


@dataclass
class TeachingExchange:
    """A single exchange in a dialogue."""
    speaker: str  # "teacher" or "student"
    role_name: str  # e.g., "Indira" or "Confused_Beginner"
    text: str
    reasoning: str = ""  # For non-diegetic layer


@dataclass
class ExtendedDialogue:
    """A complete multi-round dialogue."""
    instructor_name: str
    instructor_archetype: str
    student_name: str
    student_domain: str
    scenario_id: str
    scenario_title: str

    # Dialogue content: list of exchanges
    exchanges: List[TeachingExchange]

    # Metadata
    timestamp: str
    temperature: float = 0.9


@dataclass
class RubricEvaluation:
    """Pedagogical rubric evaluation result."""
    dialogue_id: str
    pass_fail: bool

    # Pass criteria
    asks_not_tells: bool = False
    open_ended: bool = False
    agency_preserved: bool = False
    references_specific: bool = False
    emotional_aware: bool = False
    visible_progress: bool = False
    pushback_safe: bool = False

    # Hard stops
    no_shaming: bool = True
    no_complete_answers: bool = True
    no_emotional_dismissal: bool = True
    no_agency_removal: bool = True

    # Metadata
    reasoning: str = ""
    confidence: float = 0.5
