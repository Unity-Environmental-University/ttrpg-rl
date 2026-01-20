# Architecture Update: Parallel Fine-Tuning for Specialized Learners

## What Changed

### Problem Identified
Previous monolithic fine-tuning approach failed:
- **Base model quality:** 0.89
- **Fine-tuned model quality:** 0.61 (−0.28 regression)
- **Root cause:** Models memorized repetitive response patterns ("I completely understand your frustration") instead of learning underlying pedagogy

### Solution Deployed
Stratified parallel fine-tuning with specialized models:
- **6 smaller models** instead of 1 large one
- **Different data** for each model (40-30 samples vs 140-83)
- **Specialization** by context: length, question type, student profile
- **Testing** for neurodivergent and trauma-informed teaching

---

## New Components

### 1. Extended Student Profiles
**File:** `src/student_profiles.py`

Added fields to `StudentProfileConfig`:
```python
neurodivergent: bool = False
bad_prior_teacher: bool = False
rejects_metaphor: bool = False
executive_function_gap: bool = False
hyperfocus_trait: bool = False
```

These generate authentic student profiles for:
- **Neurodivergent students** (ADHD/autism traits)
- **Bad prior teacher trauma** (previous poor instruction)
- **Concrete thinking** (rejects abstract metaphors)
- **Executive function gaps** (can't organize steps)
- **Hyperfocus patterns** (wants to stay on one topic)

### 2. New Scenarios
**File:** `src/scenarios.py`

Added 4 new scenario cards:
- `bad_prior_teacher` - Student recovering from bad teaching ("impossible for visual learners")
- `neurodivergent_exec` - Executive function gap ("can't organize steps but can hold concept")
- `neurodivergent_reject` - Rejects metaphors ("show me line by line, not analogies")
- `neurodivergent_hyperfocus` - Hyperfocus protection ("why are we leaving this topic?")

### 3. Stratified Training Sampler
**File:** `src/stratified_training_sampler.py`

Creates 6 batches from existing training data:
- **Batch 1:** Short dialogues, original questions, high-confidence (40 samples)
- **Batch 2:** Medium dialogues, koans, high-confidence (35 samples)
- **Batch 3:** Long dialogues, mixed questions, medium-confidence (35 samples)
- **Batch 4:** Varied length, original, diverse patterns (40 samples)
- **Batch 5:** Neurodivergent-optimized (30 samples)
- **Batch 6:** Prior trauma recovery (30 samples)

Stratification dimensions:
- **Dialogue length** (short/medium/long)
- **Question type** (original/koans/mixed)
- **Confidence** (high/medium)
- **Student profile** (neurodivergent/trauma)

### 4. Parallel Fine-Tuning Manager
**File:** `src/parallel_finetune.py`

Submits and tracks multiple fine-tuning jobs:
- Uploads 6 training files in parallel
- Submits 6 jobs to OpenAI API
- Tracks status in JSON manifest: `data/finetune_manifest.json`
- Auto-retrieves model IDs when jobs complete

### 5. Orchestration Pipeline
**File:** `procgen_and_train_parallel.py`

CLI for full end-to-end workflow:
```bash
python procgen_and_train_parallel.py discover 50 --include-special
python procgen_and_train_parallel.py batch
python procgen_and_train_parallel.py finetune
python procgen_and_train_parallel.py watch
```

---

## Why This Works

### 1. Lower Pattern Density
Each model sees fewer repetitions of the same pattern:
- Old: One model sees 140 "recursion explanations"
- New: Each model sees 30-40, in different contexts

Result: Models generalize instead of memorizing.

### 2. Specialization
Different models optimized for different situations:
- Model 1: Quick, direct responses (short)
- Model 2: Contemplative, open-ended (koans)
- Model 5: Concrete, no metaphors (neurodivergent)
- Model 6: Validating, trust-building (trauma)

Result: Each model learns appropriate patterns for its context.

### 3. Dialogue Variety
Stratifying by length prevents length-dependent overfitting:
- Model trained on short dialogues might over-shorten responses
- Model trained on long dialogues might over-elaborate
- Batch 4 (diverse lengths) acts as baseline

Result: More robust across different response lengths.

### 4. Iterative Discovery
Test each model independently:
- Which specializations actually improve over base?
- Do neurodivergent-optimized models perform better on abstract tasks?
- Does trauma-informed training transfer to general teaching?

Result: Data-driven decisions about what to scale next.

---

## Testing Strategy

Once all 6 jobs complete, evaluate each model:

```bash
# Test each model's specialization
python compare_models.py batch_1_short_original    # Should excel at short responses
python compare_models.py batch_5_neurodiv          # Should excel at direct, concrete
python compare_models.py batch_6_prior_trauma      # Should excel at validation

# Test cross-specialization
python compare_models.py batch_1_short_original --test-on long_dialogues
python compare_models.py batch_5_neurodiv --test-on abstract_scenarios
```

**Success criteria:**
- At least 2 models show +0.15 improvement over base (vs −0.28 before)
- Neurodivergent model outperforms on abstract rejection scenarios
- Trauma-informed model outperforms on validation-heavy scenarios
- Diverse patterns model generalizes across all contexts

---

## Expected Outcomes

### Best Case
- Multiple models improve (+0.15 to +0.25)
- Specializations are real (each model excels in its niche)
- Parallel approach proves superior to monolithic

**→ Next:** Focus data collection on winning profiles, scale to 200+ samples

### Medium Case
- Some models improve, others neutral
- Parallelization helps but not dramatically

**→ Next:** Increase batch sizes, reduce specialization complexity

### Worst Case
- Small samples hurt generalization, all underperform

**→ Next:** Merge batches, return to fewer larger models but keep stratification strategy

---

## Files Modified/Created

### New Files
- `src/stratified_training_sampler.py`
- `src/parallel_finetune.py`
- `procgen_and_train_parallel.py`
- `PARALLEL_FINETUNING.md` (detailed architecture)
- `QUICKSTART_PARALLEL.md` (usage guide)
- `ARCHITECTURE_UPDATE.md` (this file)

### Modified Files
- `src/student_profiles.py` (added neurodivergent fields)
- `src/scenarios.py` (added 4 new scenarios)

### Unchanged
- All other code and pipelines work as before
- Old monolithic approach can still be used if needed
- `procgen_quick.py` and `dashboard.py` still work

---

## Next Steps

### Immediate (Today)
1. Generate data: `python procgen_and_train_parallel.py discover 50 --include-special`
2. Create batches: `python procgen_and_train_parallel.py batch`
3. Submit jobs: `python procgen_and_train_parallel.py finetune`
4. Monitor: `python procgen_and_train_parallel.py watch`

### When Jobs Complete
1. Check models: `python src/parallel_finetune.py check`
2. Evaluate specializations: `python compare_models.py batch_*`
3. Identify winners: Which models improved most?

### Follow-Up
If successful:
- Scale winning profiles: Generate 100+ iterations specifically for best student types
- Retrain winners: Fine-tune models 5 & 6 with 100+ samples each
- Build ensemble: Route students to appropriate model based on profile
- Custom scenarios: Generate scenarios specifically testing trauma-informed responses

---

## Architecture Decision Tree

```
START: Monolithic fine-tuning failed (−0.28 regression)
   ↓
TRY: Smaller batches with different stratification?
   ├─ YES → You are here (Parallel Stratified Approach)
   └─ NO → Keep monolithic but change data

STRATIFICATION DESIGN:
   Dialogue Length? → Short, Medium, Long
   Question Type?   → Original, Koans, Mixed
   Confidence?      → High (0.7+), Medium (0.5-0.7)
   Student Profile? → Neurodivergent, Trauma, Standard

BATCH COMPOSITION:
   6 models total:
   ├─ Batch 1: Short + Original + High
   ├─ Batch 2: Medium + Koans + High
   ├─ Batch 3: Long + Mixed + Medium
   ├─ Batch 4: Varied + Original + Diverse
   ├─ Batch 5: Neurodivergent-Optimized
   └─ Batch 6: Prior Trauma Recovery

EVALUATION:
   Does specialization work?
   ├─ YES: Scale & ensemble
   ├─ PARTIAL: Keep winners, discard failures
   └─ NO: Increase batch sizes, simplify stratification
```

---

## Open Questions (To Test)

1. **Do smaller batch sizes help generalization?** (vs memorization risk)
2. **Is dialogue length actually a useful stratification dimension?**
3. **Do neurodivergent-optimized models transfer to general students?**
4. **Can trauma-informed training improve overall teaching quality?**
5. **What's the sweet spot for batch size?** (30 vs 50 vs 100 samples)

All answered by evaluation results.
