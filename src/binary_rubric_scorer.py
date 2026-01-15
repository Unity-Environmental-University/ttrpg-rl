"""
Binary rubric scorer - Apply pedagogical pass/fail criteria to dialogues.

Pass criteria (must ALL be true):
1. Asks (not tells) - Teacher uses questions, not directives
2. Open-ended - Student can push back, not just yes/no
3. Agency - Student maintains control/choice
4. References - Teacher references specific student words/context
5. Emotional awareness - Teacher acknowledges emotional state
6. Visible progress - Student demonstrates understanding shift
7. Pushback safe - Student can disagree without consequence

Hard stops (any one fails):
- Shaming or belittling
- Complete answers given directly
- Ignores student emotional state
- Removes student agency
"""

import json
import os
from pathlib import Path
from typing import Dict, Tuple
from dataclasses import dataclass

from openai import OpenAI


@dataclass
class RubricScore:
    """Result of binary rubric evaluation."""
    dialogue_id: str
    pass_fail: bool  # True = PASS, False = FAIL

    # Component scores
    asks_not_tells: bool
    open_ended: bool
    agency_preserved: bool
    references_specific: bool
    emotional_aware: bool
    visible_progress: bool
    pushback_safe: bool

    # Hard stops
    no_shaming: bool
    no_complete_answers: bool
    no_emotional_dismissal: bool
    no_agency_removal: bool

    # Reasoning
    reasoning: str
    confidence: float  # 0-1


class BinaryRubricScorer:
    """Score dialogues against pedagogical rubric."""

    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)

    def score_dialogue(self, dialogue: dict) -> RubricScore:
        """Score a single dialogue against binary rubric.

        Args:
            dialogue: Dialogue dict with instructor/student/responses

        Returns:
            RubricScore with pass/fail and component breakdown
        """

        # Extract dialogue content
        teacher_opening = dialogue["instructor"]["opening_diegetic"]
        student_response = dialogue["student_response"]["diegetic"]
        student_non_diegetic = dialogue["student_response"]["non_diegetic"]
        dialogue_id = dialogue.get("timestamp", "unknown")

        # Create evaluation prompt
        prompt = f"""You are evaluating a teaching dialogue against a pedagogical rubric.

DIALOGUE:
Teacher: {teacher_opening}

Student: {student_response}

Student's thinking (non-diegetic): {student_non_diegetic}

EVALUATE THIS DIALOGUE on the following criteria:

HARD STOPS (any single failure = FAIL overall):
1. Shaming/Belittling: Did the teacher shame, mock, or belittle the student? (YES = hard stop failure)
2. Complete Answer: Did the teacher give a complete answer directly instead of guiding? (YES = hard stop failure)
3. Emotional Dismissal: Did the teacher ignore or dismiss the student's emotional state? (YES = hard stop failure)
4. Agency Removal: Did the teacher remove the student's agency or control? (YES = hard stop failure)

PASS CRITERIA (all must be TRUE for overall PASS):
1. Asks, Not Tells: Did the teacher use questions and guide rather than direct commands? (YES/NO)
2. Open-Ended: Can the student push back or disagree? Not yes/no questions. (YES/NO)
3. Agency: Does the student maintain control and choice? (YES/NO)
4. References Specific: Did the teacher reference the student's actual words or context? (YES/NO)
5. Emotional Aware: Did the teacher acknowledge or honor the student's emotional state? (YES/NO)
6. Visible Progress: Does the student show understanding shift or deeper confusion articulated? (YES/NO)
7. Pushback Safe: Can the student safely disagree without consequence? (YES/NO)

REASONING:
For each criterion, explain your evaluation briefly (1-2 sentences).

FORMAT YOUR RESPONSE EXACTLY AS:

HARD_STOPS:
Shaming: NO/YES
Complete_Answer: NO/YES
Emotional_Dismissal: NO/YES
Agency_Removal: NO/YES

PASS_CRITERIA:
Asks_Not_Tells: YES/NO - [brief reason]
Open_Ended: YES/NO - [brief reason]
Agency: YES/NO - [brief reason]
References_Specific: YES/NO - [brief reason]
Emotional_Aware: YES/NO - [brief reason]
Visible_Progress: YES/NO - [brief reason]
Pushback_Safe: YES/NO - [brief reason]

OVERALL:
PASS/FAIL - [summary reasoning]
CONFIDENCE: [0.0-1.0]
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=800,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        result_text = response.choices[0].message.content

        # Parse response
        return self._parse_rubric_response(result_text, dialogue_id)

    def _parse_rubric_response(self, response_text: str, dialogue_id: str) -> RubricScore:
        """Parse LLM rubric evaluation response."""

        lines = response_text.strip().split("\n")

        # Initialize all to False/None
        hard_stops = {
            "shaming": True,  # True = OK (no shaming)
            "complete_answer": True,
            "emotional_dismissal": True,
            "agency_removal": True,
        }

        pass_criteria = {
            "asks_not_tells": False,
            "open_ended": False,
            "agency": False,
            "references_specific": False,
            "emotional_aware": False,
            "visible_progress": False,
            "pushback_safe": False,
        }

        overall_pass = False
        confidence = 0.5
        reasoning = ""

        # Parse hard stops section
        in_hard_stops = False
        for line in lines:
            if "HARD_STOPS:" in line:
                in_hard_stops = True
                continue
            if "PASS_CRITERIA:" in line:
                in_hard_stops = False
                continue

            if in_hard_stops and ":" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    key = parts[0].strip().lower().replace(" ", "_")
                    val = parts[1].strip().upper()

                    if "shaming" in key:
                        hard_stops["shaming"] = "NO" in val
                    elif "complete" in key:
                        hard_stops["complete_answer"] = "NO" in val
                    elif "emotional" in key:
                        hard_stops["emotional_dismissal"] = "NO" in val
                    elif "agency" in key:
                        hard_stops["agency_removal"] = "NO" in val

        # Parse pass criteria section
        in_pass = False
        for line in lines:
            if "PASS_CRITERIA:" in line:
                in_pass = True
                continue
            if "OVERALL:" in line:
                in_pass = False
                continue

            if in_pass and ":" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    key = parts[0].strip().lower().replace(" ", "_")
                    val = parts[1].strip().upper()

                    for criterion in pass_criteria.keys():
                        if criterion in key:
                            pass_criteria[criterion] = "YES" in val
                            break

        # Parse overall result
        for line in lines:
            if "OVERALL:" in line:
                if "PASS" in line.upper():
                    overall_pass = True
                if "CONFIDENCE:" in lines[lines.index(line) + 1] if line.index(line) + 1 < len(lines) else False:
                    try:
                        conf_line = lines[lines.index(line) + 1]
                        confidence = float(conf_line.split(":")[-1].strip())
                    except:
                        pass

                # Get reasoning (rest of the line after OVERALL:)
                reasoning = line.split("-")[-1].strip() if "-" in line else ""

        # Determine overall pass:
        # Hard stops must all be True (no violations)
        # All pass criteria must be True
        hard_stops_ok = all(hard_stops.values())
        pass_criteria_ok = all(pass_criteria.values())

        final_pass = hard_stops_ok and pass_criteria_ok

        return RubricScore(
            dialogue_id=dialogue_id,
            pass_fail=final_pass,
            asks_not_tells=pass_criteria["asks_not_tells"],
            open_ended=pass_criteria["open_ended"],
            agency_preserved=pass_criteria["agency"],
            references_specific=pass_criteria["references_specific"],
            emotional_aware=pass_criteria["emotional_aware"],
            visible_progress=pass_criteria["visible_progress"],
            pushback_safe=pass_criteria["pushback_safe"],
            no_shaming=hard_stops["shaming"],
            no_complete_answers=hard_stops["complete_answer"],
            no_emotional_dismissal=hard_stops["emotional_dismissal"],
            no_agency_removal=hard_stops["agency_removal"],
            reasoning=reasoning,
            confidence=confidence,
        )

    def score_directory(self, directory: str) -> dict:
        """Score all dialogues in a directory."""

        results = {}
        files = sorted(Path(directory).glob("matrix_*.json"))

        for i, filepath in enumerate(files):
            print(f"[{i+1}/{len(files)}] {filepath.name}...", end=" ", flush=True)

            try:
                with open(filepath) as f:
                    dialogue = json.load(f)

                score = self.score_dialogue(dialogue)
                results[filepath.name] = score

                print(f"✓ {'PASS' if score.pass_fail else 'FAIL'}")

            except Exception as e:
                print(f"✗ {e}")

        return results

    def print_results_summary(self, results: dict):
        """Print summary of rubric scores."""

        if not results:
            print("No results to summarize.")
            return

        total = len(results)
        passes = sum(1 for r in results.values() if r.pass_fail)
        fails = total - passes

        print(f"\n{'='*80}")
        print(f"BINARY RUBRIC EVALUATION SUMMARY")
        print(f"{'='*80}")
        print(f"Total: {total}")
        print(f"PASS: {passes} ({passes/total:.0%})")
        print(f"FAIL: {fails} ({fails/total:.0%})")

        # Breakdown by criterion
        print(f"\n{'Criterion':<25} {'PASS':<10} {'FAIL':<10} {'Rate':<10}")
        print("-" * 60)

        criteria = [
            ("Asks_Not_Tells", "asks_not_tells"),
            ("Open_Ended", "open_ended"),
            ("Agency", "agency_preserved"),
            ("References_Specific", "references_specific"),
            ("Emotional_Aware", "emotional_aware"),
            ("Visible_Progress", "visible_progress"),
            ("Pushback_Safe", "pushback_safe"),
        ]

        for label, attr in criteria:
            count_true = sum(1 for r in results.values() if getattr(r, attr))
            count_false = total - count_true
            rate = count_true / total if total > 0 else 0
            print(f"{label:<25} {count_true:<10} {count_false:<10} {rate:.0%}")

        # Hard stops
        print(f"\n{'Hard Stops':<25} {'SAFE':<10} {'VIOLATED':<10}")
        print("-" * 60)

        hard_stops = [
            ("No Shaming", "no_shaming"),
            ("No Complete Answers", "no_complete_answers"),
            ("No Emotional Dismissal", "no_emotional_dismissal"),
            ("No Agency Removal", "no_agency_removal"),
        ]

        for label, attr in hard_stops:
            count_safe = sum(1 for r in results.values() if getattr(r, attr))
            count_violated = total - count_safe
            print(f"{label:<25} {count_safe:<10} {count_violated:<10}")


if __name__ == "__main__":
    import sys

    scorer = BinaryRubricScorer()

    # Score all dialogues in matrix directory
    dialogue_dir = "data/matrix"

    if not Path(dialogue_dir).exists():
        print(f"Directory {dialogue_dir} not found.")
        sys.exit(1)

    print("Scoring all dialogues against binary rubric...")
    results = scorer.score_directory(dialogue_dir)

    scorer.print_results_summary(results)

    # Save results
    output_file = Path(dialogue_dir) / "rubric_scores.json"
    with open(output_file, "w") as f:
        json.dump({k: {
            "pass_fail": v.pass_fail,
            "asks_not_tells": v.asks_not_tells,
            "open_ended": v.open_ended,
            "agency_preserved": v.agency_preserved,
            "references_specific": v.references_specific,
            "emotional_aware": v.emotional_aware,
            "visible_progress": v.visible_progress,
            "pushback_safe": v.pushback_safe,
            "no_shaming": v.no_shaming,
            "no_complete_answers": v.no_complete_answers,
            "no_emotional_dismissal": v.no_emotional_dismissal,
            "no_agency_removal": v.no_agency_removal,
            "reasoning": v.reasoning,
            "confidence": v.confidence,
        } for k, v in results.items()}, f, indent=2)

    print(f"\nScores saved to: {output_file}")
