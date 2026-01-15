"""
Dialogue Extender - Take short 1-response dialogues and extend to 2-3 rounds.

Current: Opening → Student Response
Extended: Opening → Student Response → Teacher Response 2 → Student Response 2

This allows us to see actual learning progression rather than single-shot reactions.
"""

import json
import os
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

from openai import OpenAI


@dataclass
class ExtendedDialogue:
    """Extended dialogue with multiple rounds."""
    original_file: str
    instructor_name: str
    student_name: str
    scenario_id: str

    # Round 1 (original)
    teacher_opening: str
    student_response_1: str

    # Round 2 (new)
    teacher_response_2: str
    student_response_2: str

    # Metadata
    timestamp: str


class DialogueExtender:
    """Extend short dialogues to 2-3 rounds showing learning progression."""

    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)

    def extend_dialogue(self, dialogue: dict) -> Tuple[ExtendedDialogue, bool]:
        """Extend a single dialogue by one more round.

        Args:
            dialogue: Original dialogue dict from matrix

        Returns:
            (ExtendedDialogue, success_bool)
        """

        teacher_name = dialogue["instructor"]["name"]
        student_name = dialogue["student"]["name"]
        scenario_id = dialogue["scenario"]["id"]
        student_domain = dialogue["student"]["domain"]

        teacher_opening = dialogue["instructor"]["opening_diegetic"]
        student_response_1 = dialogue["student_response"]["diegetic"]
        student_emotional = dialogue["student"]["name"]  # Use for context

        # Generate teacher's second response (reacting to student pushback/confusion)
        teacher_system = f"""You are {teacher_name}, a {dialogue["instructor"]["archetype"]}.

The student has just responded to your opening. Continue the dialogue by:
1. Acknowledging what the student said
2. Asking a follow-up question or providing a gentle clarification
3. Checking if they're understanding better or still confused

Keep it to 2-3 sentences. Stay in character."""

        teacher_prompt = f"""Student just said: "{student_response_1}"

Respond as {teacher_name} to continue the dialogue. Help them move forward."""

        try:
            teacher_response_2 = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=200,
                messages=[
                    {"role": "system", "content": teacher_system},
                    {"role": "user", "content": teacher_prompt},
                ]
            ).choices[0].message.content
        except Exception as e:
            print(f"Error generating teacher response 2: {e}")
            return None, False

        # Generate student's second response (showing progress, deeper confusion, or pushback)
        student_system = f"""You are {student_name}, a student working on {student_domain}.

In this dialogue, you've already responded once. Now the teacher has responded again.
Respond realistically:
- If the teacher's clarification helped, show understanding shift
- If you're still confused, articulate what specifically confuses you
- If the teaching feels off, push back respectfully

Keep it to 2-3 sentences. Be authentic."""

        student_prompt = f"""Teacher just said: "{teacher_response_2}"

Your previous statement was: "{student_response_1}"

Respond. What's your reaction to the teacher's response?"""

        try:
            student_response_2 = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=200,
                messages=[
                    {"role": "system", "content": student_system},
                    {"role": "user", "content": student_prompt},
                ]
            ).choices[0].message.content
        except Exception as e:
            print(f"Error generating student response 2: {e}")
            return None, False

        extended = ExtendedDialogue(
            original_file=dialogue.get("timestamp", "unknown"),
            instructor_name=teacher_name,
            student_name=student_name,
            scenario_id=scenario_id,
            teacher_opening=teacher_opening,
            student_response_1=student_response_1,
            teacher_response_2=teacher_response_2,
            student_response_2=student_response_2,
            timestamp=datetime.now().isoformat(),
        )

        return extended, True

    def extend_directory(self, input_dir: str, output_dir: str):
        """Extend all dialogues in a directory."""

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        files = sorted(Path(input_dir).glob("matrix_*.json"))
        results = []

        for i, filepath in enumerate(files):
            print(f"[{i+1}/{len(files)}] Extending {filepath.name}...", end=" ", flush=True)

            try:
                with open(filepath) as f:
                    dialogue = json.load(f)

                extended, success = self.extend_dialogue(dialogue)

                if success and extended:
                    # Save extended dialogue
                    output_filename = filepath.name.replace("matrix_", "extended_")
                    output_path = Path(output_dir) / output_filename

                    with open(output_path, "w") as f:
                        json.dump(asdict(extended), f, indent=2)

                    results.append({
                        "original": filepath.name,
                        "extended": output_filename,
                        "status": "success",
                    })

                    print(f"✓")
                else:
                    print(f"✗ Generation failed")
                    results.append({
                        "original": filepath.name,
                        "status": "failed",
                    })

            except Exception as e:
                print(f"✗ {e}")
                results.append({
                    "original": filepath.name,
                    "status": "error",
                    "error": str(e),
                })

        return results

    def print_example(self, extended: ExtendedDialogue):
        """Pretty-print an extended dialogue."""

        print(f"\n{'='*80}")
        print(f"EXTENDED DIALOGUE: {extended.instructor_name} + {extended.student_name}")
        print(f"{'='*80}")

        print(f"\n[ROUND 1]")
        print(f"Teacher: {extended.teacher_opening}")
        print(f"\nStudent: {extended.student_response_1}")

        print(f"\n[ROUND 2]")
        print(f"Teacher: {extended.teacher_response_2}")
        print(f"\nStudent: {extended.student_response_2}")


if __name__ == "__main__":
    extender = DialogueExtender()

    input_dir = "data/matrix"
    output_dir = "data/extended_dialogues"

    if not Path(input_dir).exists():
        print(f"Input directory {input_dir} not found.")
        exit(1)

    print(f"Extending dialogues from {input_dir}...")
    results = extender.extend_directory(input_dir, output_dir)

    # Summary
    successes = sum(1 for r in results if r.get("status") == "success")
    failures = sum(1 for r in results if r.get("status") != "success")

    print(f"\n{'='*80}")
    print(f"Extended dialogues complete")
    print(f"{'='*80}")
    print(f"Success: {successes}/{len(results)}")
    print(f"Failed: {failures}/{len(results)}")
    print(f"Output directory: {output_dir}")

    # Save results index
    with open(Path(output_dir) / "extension_results.json", "w") as f:
        json.dump(results, f, indent=2)
