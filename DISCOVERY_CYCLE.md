# Full Discovery Cycle

Complete end-to-end data generation and analysis pipeline.

## What It Does

### Phase 1: Binary Rubric Validation
- Scores all 50+ existing dialogues against the binary pedagogical rubric
- Validates that high pushback rate correlates with actual teaching quality
- Output: Pass/fail breakdown by criterion

### Phase 2: Dialogue Extension
- Takes short 1-response dialogues and extends them to 2-3 rounds
- Teacher opening → Student response → Teacher response 2 → Student response 2
- Allows us to see actual learning progression, not just initial reactions
- Output: Extended dialogues showing progression

### Phase 3: Procgen Discovery
- Generates N random personas (random question selections) per student/scenario pair
- Runs extended dialogues with each random persona
- Scores with binary rubric
- Aggregates to discover: which constitutional questions work for which pairings
- Output: Patterns showing optimal question combinations

## Running

### Quick Test (10-15 min)
```bash
cd /Users/hallie/Documents/repos/unity/ttrpg-rl
python src/run_discovery_cycle.py 2
```
Runs all 3 phases with 2 procgen iterations per pair (6 procgen tests total).

### Full Run (1-2 hours)
```bash
python src/run_discovery_cycle.py 10
```
Full test with 10 iterations per pair (60 procgen tests).

### Individual Phases

If you want to run phases separately:

**Phase 1 only:**
```bash
python src/binary_rubric_scorer.py
```

**Phase 2 only:**
```bash
python src/dialogue_extender.py
```

**Phase 3 only:**
```bash
python src/procgen_discovery.py
```

## Output Structure

Results saved to `data/discovery_cycles/TIMESTAMP/`:

```
discovery_cycles/2026-01-15T11-30-45/
├── cycle_report.json              # Full cycle summary
├── phase1_rubric_scores.json      # Binary rubric results
├── extended_dialogues/            # Extended dialogues
│   ├── extended_matrix_*.json
│   └── extension_results.json
└── procgen_discovery/
    ├── procgen_results.json       # All procgen tests
    └── procgen_analysis.json      # Aggregated patterns
```

## Key Outputs

### Phase 1 Report
```json
{
  "total": 50,
  "pass": 35,
  "fail": 15,
  "pass_rate": 0.70,
  "by_criterion": {
    "asks_not_tells": 0.82,
    "open_ended": 0.76,
    ...
  }
}
```

### Phase 3 Patterns (Procgen Findings)
```json
{
  "patterns": [
    {
      "pair": "Confused_Beginner_confusion_basics",
      "pass_rate": 0.60,
      "top_questions": ["testing_1", "listening_1", "specificity_2"]
    },
    ...
  ]
}
```

**What this means:** For Confused_Beginner + Confusion scenario, personas with testing_1, listening_1, and specificity_2 questions achieve 60% pass rate. This suggests that testing + listening + specificity is the right combo for this pairing.

## Analysis

After running, look for patterns:

1. **High correlation in Phase 1?**
   - High pushback rate = PASS on rubric = our signal is good

2. **Extended dialogues showing progress?**
   - Student Response 2 should show "Ah!" moment or deeper articulation of confusion
   - This is gold for training data

3. **Procgen patterns emerging?**
   - Which questions appear most in PASS results?
   - Do patterns differ by student type?
   - Are there specialist combos vs. universal combos?

## Next Steps

Once cycle completes:

1. **Move findings to proprietary/**: Analysis and procgen results
2. **Update decision journal**: What did we learn?
3. **If patterns are strong**: Use them to create new specialized personas
4. **Fine-tune on high-confidence data**: Train model on extended dialogues + patterns

## Troubleshooting

**"No dialogues found in data/matrix"**
- Run dialogue matrix first: `python src/dialogue_matrix.py`

**API rate limit errors**
- Reduce `procgen_iterations` to smaller number
- Add delays between API calls if needed

**Memory issues with large datasets**
- Process results in batches
- Stream-write JSON files instead of loading all in memory

## Time Estimates

- Phase 1 (rubric): 1-2 min (1 API call per dialogue, parallel possible)
- Phase 2 (extend): 5-10 min (2 API calls per dialogue)
- Phase 3 (procgen):
  - 2 iterations: 5-10 min
  - 5 iterations: 15-20 min
  - 10 iterations: 30-45 min
  - 20 iterations: 60-90 min

Full cycle (5 iterations): ~30 min
Full cycle (10 iterations): ~60 min

Recommend starting with 2-5 to validate approach, then scale to 10-20 for statistical significance.
