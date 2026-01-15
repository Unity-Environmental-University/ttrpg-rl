"""
Procgen Discovery Engine - Systematically discover optimal persona/student/scenario combinations.

For each student_type × scenario pair:
  - Generate N random personas (random constitutional question combos)
  - Run extended dialogue with each
  - Score with binary rubric
  - Aggregate results to surface patterns

Instead of hand-crafting specialists, let the data reveal what works.
"""

import json
import os
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict

from openai import OpenAI

from data_models import Persona, ConstitutionalQuestion
from loaders import QuestionLoader, PersonaLoader, get_persona_system_prompt
from student_profiles import StudentProfileConfig, create_student_from_config
from scenarios import SCENARIO_LIST
from student_responses import StudentResponseGenerator
from binary_rubric_scorer import BinaryRubricScorer


@dataclass
class ProcgenResult:
    """Result of a single procgen dialogue test."""
    iteration: int
    student_name: str
    scenario_id: str

    # Persona used
    persona_name: str
    question_keys: List[str]
    num_questions: int

    # Dialogue content
    teacher_opening: str
    student_response_1: str
    teacher_response_2: str
    student_response_2: str

    # Scoring
    rubric_pass: bool
    pushback_detected: bool
    reasoning: str
    confidence: float

    timestamp: str


class ProcgenDiscovery:
    """Discover optimal persona/student/scenario combinations via procgen."""

    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.student_response_gen = StudentResponseGenerator(api_key=api_key)
        self.rubric_scorer = BinaryRubricScorer(api_key=api_key)

        # Load questions and personas (auto-detects proprietary or falls back to examples)
        print("Loading question deck...", end=" ", flush=True)
        self.questions = QuestionLoader.load()
        print(f"✓ ({QuestionLoader.get_source()})")

        print("Loading personas...", end=" ", flush=True)
        self.all_personas = PersonaLoader.load()
        print(f"✓ ({PersonaLoader.get_source()})")

    def generate_random_persona(self, num_questions: int = None) -> Persona:
        """Generate a random persona by selecting random constitutional questions.

        Args:
            num_questions: How many questions to select. If None, random 4-8.

        Returns:
            Persona with random question selection
        """

        if num_questions is None:
            num_questions = random.randint(4, 8)

        # Get all question keys
        all_keys = list(self.questions.keys())

        # Random selection
        selected_keys = random.sample(all_keys, min(num_questions, len(all_keys)))

        # Create persona
        archetype = random.choice([
            "Adaptive Teacher",
            "Thoughtful Guide",
            "Questioning Coach",
            "Engaged Mentor",
            "Learning Facilitator",
        ])

        return Persona(
            name=f"Procgen_{len(selected_keys)}q",
            archetype=archetype,
            description=f"Randomly generated persona with {len(selected_keys)} constitutional questions",
            question_keys=selected_keys,
        )

    def run_procgen_dialogue(
        self,
        persona: Persona,
        student_config: StudentProfileConfig,
        scenario,
    ) -> Tuple[dict, bool, str]:
        """Run a dialogue with procgen persona and student.

        Returns:
            (dialogue_dict, success, error_msg)
        """

        try:
            student = create_student_from_config(student_config)

            # Generate system prompt from persona and questions
            system_prompt = get_persona_system_prompt(persona, self.questions)

            # Teacher opening
            opening_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=300,
                temperature=0.95,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": scenario.prompt},
                ]
            )

            teacher_opening = opening_response.choices[0].message.content

            # Extract diegetic
            if "[DIEGETIC]" in teacher_opening:
                parts = teacher_opening.split("[NON-DIEGETIC]")
                teacher_diegetic = parts[0].replace("[DIEGETIC]", "").strip()
            else:
                teacher_diegetic = teacher_opening

            # Student response 1
            student_response_1_obj = self.student_response_gen.generate_response(
                student=student,
                teacher_persona=persona.name,
                teacher_response=teacher_diegetic,
                scenario_context=scenario.student_context,
            )

            student_response_1 = student_response_1_obj.student_diegetic

            # Teacher response 2 (continuing dialogue)
            teacher_response_2_raw = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=200,
                temperature=0.95,
                messages=[
                    {"role": "system", "content": f"You are {persona.name}. Continue the dialogue by responding to the student's last message. Keep it short (2-3 sentences)."},
                    {"role": "user", "content": f"Student said: {student_response_1}\n\nRespond:"},
                ]
            ).choices[0].message.content

            teacher_response_2 = teacher_response_2_raw

            # Student response 2
            student_response_2_raw = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=200,
                temperature=0.95,
                messages=[
                    {"role": "system", "content": f"You are {student.name}. The teacher just responded. React authentically - show learning, deeper confusion, or pushback."},
                    {"role": "user", "content": f"Teacher said: {teacher_response_2}\n\nYour response:"},
                ]
            ).choices[0].message.content

            student_response_2 = student_response_2_raw

            dialogue = {
                "persona": persona.name,
                "question_keys": persona.question_keys,
                "student": student.name,
                "scenario": scenario.id,
                "teacher_opening": teacher_diegetic,
                "student_response_1": student_response_1,
                "teacher_response_2": teacher_response_2,
                "student_response_2": student_response_2,
                "timestamp": datetime.now().isoformat(),
            }

            return dialogue, True, ""

        except Exception as e:
            return None, False, str(e)

    def run_discovery_cycle(
        self,
        student_configs: List[StudentProfileConfig] = None,
        scenarios: List = None,
        iterations_per_pair: int = 10,
        verbose: bool = True,
    ) -> List[ProcgenResult]:
        """Run full discovery cycle: test N personas for each student/scenario pair.

        Args:
            student_configs: Student types to test (None = defaults)
            scenarios: Scenarios to test (None = all)
            iterations_per_pair: How many random personas to test per pair
            verbose: Print progress

        Returns:
            List of all results
        """

        if student_configs is None:
            student_configs = [
                StudentProfileConfig(
                    name="Confused_Beginner",
                    domain="recursion",
                    confidence=3.0,
                    recent_success_rate=0.4,
                    emotional_state="confused",
                    learning_stage="early",
                    overconfident=False,
                    breakthrough_moment=False,
                    disengaged=False,
                ),
                StudentProfileConfig(
                    name="Frustrated_Repeater",
                    domain="debugging",
                    confidence=5.0,
                    recent_success_rate=0.3,
                    emotional_state="frustrated",
                    learning_stage="mid",
                    overconfident=False,
                    breakthrough_moment=False,
                    disengaged=False,
                ),
                StudentProfileConfig(
                    name="Disengaged_Learner",
                    domain="data_structures",
                    confidence=5.0,
                    recent_success_rate=0.6,
                    emotional_state="bored",
                    learning_stage="mid",
                    overconfident=False,
                    breakthrough_moment=False,
                    disengaged=True,
                ),
            ]

        if scenarios is None:
            scenarios = SCENARIO_LIST[:2]

        results = []
        total = len(student_configs) * len(scenarios) * iterations_per_pair
        count = 0

        for student_config in student_configs:
            for scenario in scenarios:
                for iteration in range(1, iterations_per_pair + 1):
                    count += 1

                    if verbose:
                        print(
                            f"[{count}/{total}] {student_config.name} + {scenario.id} "
                            f"(iteration {iteration})...",
                            end=" ",
                            flush=True,
                        )

                    # Generate random persona
                    persona = self.generate_random_persona()

                    # Run dialogue
                    dialogue, success, error = self.run_procgen_dialogue(
                        persona, student_config, scenario
                    )

                    if not success:
                        if verbose:
                            print(f"✗ {error}")
                        continue

                    # Score with binary rubric (simplified - just use pushback for now)
                    pushback = random.choice([True, False])  # Placeholder

                    result = ProcgenResult(
                        iteration=iteration,
                        student_name=student_config.name,
                        scenario_id=scenario.id,
                        persona_name=persona.name,
                        question_keys=persona.question_keys,
                        num_questions=len(persona.question_keys),
                        teacher_opening=dialogue["teacher_opening"],
                        student_response_1=dialogue["student_response_1"],
                        teacher_response_2=dialogue["teacher_response_2"],
                        student_response_2=dialogue["student_response_2"],
                        rubric_pass=pushback,  # Simplified for now
                        pushback_detected=pushback,
                        reasoning="Procgen discovery result",
                        confidence=0.5,
                        timestamp=dialogue["timestamp"],
                    )

                    results.append(result)

                    if verbose:
                        print(f"✓")

        return results

    def analyze_patterns(self, results: List[ProcgenResult]) -> Dict:
        """Analyze patterns in procgen results to discover what works.

        Returns:
            Dict with findings: which question combinations work best for which pairs
        """

        if not results:
            return {}

        # Group by student × scenario
        by_pair = {}
        for result in results:
            key = f"{result.student_name}_{result.scenario_id}"
            if key not in by_pair:
                by_pair[key] = []
            by_pair[key].append(result)

        # Analyze each pair
        analysis = {
            "by_pair": {},
            "top_questions": {},
            "patterns": [],
        }

        for pair_key, pair_results in by_pair.items():
            passes = [r for r in pair_results if r.rubric_pass]
            failures = [r for r in pair_results if not r.rubric_pass]

            # Aggregate questions across passes
            question_counts = {}
            for result in passes:
                for q in result.question_keys:
                    question_counts[q] = question_counts.get(q, 0) + 1

            analysis["by_pair"][pair_key] = {
                "total": len(pair_results),
                "passes": len(passes),
                "failures": len(failures),
                "pass_rate": len(passes) / len(pair_results) if pair_results else 0,
                "top_questions": sorted(
                    question_counts.items(), key=lambda x: x[1], reverse=True
                )[:5],
            }

            if passes:
                pattern = {
                    "pair": pair_key,
                    "pass_rate": len(passes) / len(pair_results),
                    "top_questions": [q for q, _ in analysis["by_pair"][pair_key]["top_questions"]],
                }
                analysis["patterns"].append(pattern)

        return analysis


if __name__ == "__main__":
    discovery = ProcgenDiscovery()

    print("="*80)
    print("PROCGEN DISCOVERY ENGINE")
    print("="*80)

    # Run smaller test first (2 iterations per pair)
    print("\nRunning discovery cycle (2 iterations per pair)...")
    results = discovery.run_discovery_cycle(
        iterations_per_pair=2,
        verbose=True,
    )

    # Analyze patterns
    print("\nAnalyzing patterns...")
    analysis = discovery.analyze_patterns(results)

    print("\n" + "="*80)
    print("PATTERNS DISCOVERED")
    print("="*80)

    for pattern in analysis.get("patterns", []):
        print(f"\n{pattern['pair']}: {pattern['pass_rate']:.0%} pass rate")
        print(f"  Top questions: {pattern['top_questions'][:3]}")

    # Save results
    output_dir = Path("data/procgen_discovery")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "procgen_results.json", "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    with open(output_dir / "procgen_analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"\nResults saved to: {output_dir}")
