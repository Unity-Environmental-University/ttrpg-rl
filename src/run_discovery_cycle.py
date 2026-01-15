"""
Master orchestrator for full discovery cycle:
1. Binary rubric validation on existing dialogues
2. Extend dialogues to 2-3 rounds
3. Procgen discovery on extended dialogues
4. Aggregate findings and patterns
"""

import sys
import json
from pathlib import Path
from datetime import datetime

from binary_rubric_scorer import BinaryRubricScorer
from dialogue_extender import DialogueExtender
from procgen_discovery import ProcgenDiscovery


def run_full_cycle(
    score_existing: bool = True,
    extend_dialogues: bool = True,
    run_procgen: bool = True,
    procgen_iterations: int = 5,
):
    """Run full discovery cycle."""

    print("\n" + "="*80)
    print("FULL DISCOVERY CYCLE")
    print("="*80)

    cycle_dir = Path("data/discovery_cycles") / datetime.now().isoformat().replace(":", "-")
    cycle_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "cycle_started": datetime.now().isoformat(),
        "phases": {},
    }

    # PHASE 1: Binary Rubric Validation
    if score_existing:
        print("\n" + "-"*80)
        print("PHASE 1: Binary Rubric Validation")
        print("-"*80)

        scorer = BinaryRubricScorer()
        existing_dialogues = Path("data/matrix")

        if existing_dialogues.exists():
            print(f"Scoring dialogues in {existing_dialogues}...")
            scores = scorer.score_directory(str(existing_dialogues))

            scorer.print_results_summary(scores)

            # Save scores
            scores_file = cycle_dir / "phase1_rubric_scores.json"
            with open(scores_file, "w") as f:
                json.dump({k: {
                    "pass_fail": v.pass_fail,
                    "asks_not_tells": v.asks_not_tells,
                    "open_ended": v.open_ended,
                    "agency_preserved": v.agency_preserved,
                    "references_specific": v.references_specific,
                    "emotional_aware": v.emotional_aware,
                    "visible_progress": v.visible_progress,
                    "pushback_safe": v.pushback_safe,
                    "reasoning": v.reasoning,
                    "confidence": v.confidence,
                } for k, v in scores.items()}, f, indent=2)

            results["phases"]["phase1_rubric"] = {
                "status": "complete",
                "output_file": str(scores_file),
                "total_dialogues": len(scores),
                "pass_count": sum(1 for s in scores.values() if s.pass_fail),
                "pass_rate": sum(1 for s in scores.values() if s.pass_fail) / len(scores) if scores else 0,
            }

            print(f"\nScores saved to: {scores_file}")
        else:
            print(f"Warning: {existing_dialogues} not found. Skipping phase 1.")
            results["phases"]["phase1_rubric"] = {"status": "skipped", "reason": "No existing dialogues"}

    # PHASE 2: Extend Dialogues
    if extend_dialogues:
        print("\n" + "-"*80)
        print("PHASE 2: Dialogue Extension")
        print("-"*80)

        extender = DialogueExtender()
        input_dir = "data/matrix"
        output_dir = cycle_dir / "extended_dialogues"

        if Path(input_dir).exists():
            print(f"Extending dialogues from {input_dir}...")
            extension_results = extender.extend_directory(input_dir, str(output_dir))

            successes = sum(1 for r in extension_results if r.get("status") == "success")
            failures = sum(1 for r in extension_results if r.get("status") != "success")

            print(f"\nExtension complete:")
            print(f"  Success: {successes}/{len(extension_results)}")
            print(f"  Failed: {failures}/{len(extension_results)}")

            results["phases"]["phase2_extend"] = {
                "status": "complete",
                "output_dir": str(output_dir),
                "total": len(extension_results),
                "successes": successes,
                "failures": failures,
            }

            print(f"Extended dialogues saved to: {output_dir}")
        else:
            print(f"Warning: {input_dir} not found. Skipping phase 2.")
            results["phases"]["phase2_extend"] = {"status": "skipped", "reason": "No existing dialogues"}

    # PHASE 3: Procgen Discovery
    if run_procgen:
        print("\n" + "-"*80)
        print("PHASE 3: Procgen Discovery")
        print("-"*80)

        discovery = ProcgenDiscovery()

        print(f"Running procgen discovery ({procgen_iterations} iterations per pair)...")
        print("(This will take a while - generating ~18-36 dialogues)\n")

        procgen_results = discovery.run_discovery_cycle(
            iterations_per_pair=procgen_iterations,
            verbose=True,
        )

        # Analyze patterns
        print("\nAnalyzing procgen patterns...")
        analysis = discovery.analyze_patterns(procgen_results)

        # Save results
        procgen_dir = cycle_dir / "procgen_discovery"
        procgen_dir.mkdir(parents=True, exist_ok=True)

        with open(procgen_dir / "procgen_results.json", "w") as f:
            json.dump([{
                "iteration": r.iteration,
                "student": r.student_name,
                "scenario": r.scenario_id,
                "persona": r.persona_name,
                "questions": r.question_keys,
                "num_questions": r.num_questions,
                "rubric_pass": r.rubric_pass,
                "pushback": r.pushback_detected,
            } for r in procgen_results], f, indent=2)

        with open(procgen_dir / "procgen_analysis.json", "w") as f:
            json.dump(analysis, f, indent=2)

        # Print patterns
        print("\n" + "-"*80)
        print("DISCOVERED PATTERNS")
        print("-"*80)

        for pattern in sorted(analysis.get("patterns", []), key=lambda p: p["pass_rate"], reverse=True):
            print(f"\n{pattern['pair']}: {pattern['pass_rate']:.0%} pass rate")
            top_qs = pattern['top_questions'][:3]
            print(f"  Top questions: {', '.join(top_qs) if top_qs else 'None'}")

        results["phases"]["phase3_procgen"] = {
            "status": "complete",
            "output_dir": str(procgen_dir),
            "total_tests": len(procgen_results),
            "patterns": analysis.get("patterns", []),
        }

        print(f"\nProcgen results saved to: {procgen_dir}")

    # FINAL REPORT
    print("\n" + "="*80)
    print("DISCOVERY CYCLE COMPLETE")
    print("="*80)

    # Save cycle report
    results["cycle_completed"] = datetime.now().isoformat()

    report_file = cycle_dir / "cycle_report.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nFull report saved to: {report_file}")
    print(f"Cycle directory: {cycle_dir}")

    return cycle_dir


if __name__ == "__main__":
    # Default: run all phases
    procgen_iters = 5  # Change this for longer runs

    if len(sys.argv) > 1:
        procgen_iters = int(sys.argv[1])

    cycle_dir = run_full_cycle(
        score_existing=True,
        extend_dialogues=True,
        run_procgen=True,
        procgen_iterations=procgen_iters,
    )

    print("\n✓ Ready for analysis.")
    print(f"Next: Review findings in {cycle_dir}")
