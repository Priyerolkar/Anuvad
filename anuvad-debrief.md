# Anuvad Build — Complete Debrief

A reference document covering everything built, every error encountered, every fix applied, and the lessons that carry forward to your next project.

---

## Part 1 — What We Built (Summary)

A working English → Marathi/Hindi translator for engineering content, built from scratch in one week:

- **Model:** IndicTrans2 (AI4Bharat / IIT Madras), 200M distilled parameters, runs on CPU
- **Backend:** FastAPI service exposing `/translate` and `/translate/batch` endpoints
- **Frontend:** Streamlit app with sample buttons, language selector, latency metrics
- **Evaluation:** sacreBLEU and chrF scoring on a 20-sentence engineering test set with reference translations
- **Tests:** Pytest smoke tests for the translator module
- **Deployment-ready:** Hugging Face Spaces config file included
- **Complete documentation:** README with banner, results table, problem statement, roadmap

---

## Part 2 — Build Checklist (Reusable for Next Projects)

Copy this for any future ML/AI project. Skip steps at your peril — most errors come from skipping foundation steps.

### Phase 1: Environment Setup
- [ ] Verify Python version is 3.10, 3.11, or 3.12 (NOT 3.13+ for ML work in 2026)
- [ ] Create a project folder *without* spaces or special characters in path
- [ ] Open folder in VS Code; install Python extension if not already
- [ ] Open integrated terminal (Ctrl + `)
- [ ] Create venv: `py -3.12 -m venv .venv`
- [ ] Activate venv: `.venv\Scripts\Activate.ps1`
- [ ] Confirm `(.venv)` prefix appears in prompt
- [ ] Tell VS Code to use this interpreter (Ctrl+Shift+P → Python: Select Interpreter)
- [ ] Upgrade pip: `python -m pip install --upgrade pip`

### Phase 2: Core Package Install
- [ ] Install pinned model framework FIRST, alone: `pip install "transformers==X.Y.Z"`
- [ ] Verify installed version: `pip show <package>`
- [ ] Install everything else with the pin repeated at the front of the command
- [ ] Re-verify the locked version is still there: `pip show <package>`

### Phase 3: Project Structure
- [ ] Create folder layout: `api/`, `evaluation/`, `tests/`, `assets/`, `notebooks/`
- [ ] Add `__init__.py` to each Python package folder
- [ ] Write core module first (`translator.py` equivalent)
- [ ] Add API layer (`main.py`)
- [ ] Add UI layer (`app.py`)
- [ ] Add evaluation layer (`evaluate.py`)
- [ ] Add tests
- [ ] Add `.gitignore` excluding `.venv/`, `__pycache__/`, `.cache/`, model artifacts
- [ ] Add LICENSE (MIT for portfolio projects)

### Phase 4: First Run
- [ ] Test core module from command line first (NOT through UI): `python -m api.translator`
- [ ] Only after CLI works, test the UI: `streamlit run app.py`
- [ ] Take screenshots of working output

### Phase 5: Evaluation
- [ ] Build a small but real test set (20+ samples is enough to start)
- [ ] Run evaluation script
- [ ] Save results to a versioned file (`results.md`)
- [ ] Update README with real numbers (replace any placeholders)

### Phase 6: Documentation
- [ ] README has: banner/GIF, problem statement, approach, results table, run instructions, roadmap, license
- [ ] Generate `requirements-locked.txt` via `pip freeze`
- [ ] Add screenshots to `assets/`
- [ ] Add demo GIF to `assets/`

### Phase 7: GitHub
- [ ] `git init`, `git add .`, verify `.venv` and caches are excluded with `git status`
- [ ] First commit: meaningful message
- [ ] Push to GitHub
- [ ] Set repo description, topics, and website
- [ ] Pin to profile

### Phase 8: Live Demo
- [ ] Deploy to Hugging Face Spaces (free)
- [ ] Add live demo URL to README badge
- [ ] Add to LinkedIn Featured section

---

## Part 3 — Errors Encountered, In Order, With Fixes

This is the most valuable part of the debrief. Each error here is one you'll likely hit on future projects. Knowing the pattern saves hours.

### Error 1: ModuleNotFoundError: No module named 'torch'

**What it meant:** Dependencies weren't installed yet, or the venv wasn't actually activated.

**Pattern to recognize:** Any ModuleNotFoundError for a package you "installed" usually means one of three things:
1. The venv isn't active (no `(.venv)` in prompt)
2. The install command silently failed (read terminal output more carefully)
3. You're in the wrong terminal (multiple terminals = multiple environments)

**Fix:** Ensure venv is active, then `pip install -r requirements.txt`. If that fails on a specific package, install it alone first.

**Lesson:** Always check `(.venv)` in your prompt before any pip or python command.

---

### Error 2: GatedRepoError 401 Unauthorized (Hugging Face)

**What it meant:** The model is gated — the authors require you to accept terms before downloading.

**Pattern to recognize:** Any 401 from Hugging Face = authentication issue. Any "Cannot access gated repo" = you need to accept terms on the model's web page.

**Fix:**
1. Sign up at huggingface.co
2. Visit the model page, click "Agree to terms"
3. Generate a Read access token
4. `huggingface-cli login` and paste the token

**Lesson:** Check the model's Hugging Face page in your browser before using it. Look for a "You need to share contact information" banner.

---

### Error 3: ModuleNotFoundError: No module named 'transformers.onnx'

**What it meant:** The model's custom config code (downloaded with trust_remote_code=True) imports something that was removed in newer transformers versions.

**Pattern to recognize:** When a model uses trust_remote_code=True, you're running the model author's Python code on your machine. If their code was written for an older library version, you get incompatibility errors.

**Attempted fix that failed:** `pip install "transformers<4.46"` — pip silently installed the newest version because no Python 3.14 wheel existed for 4.45.

**Real fix:**
1. Switch to Python 3.12 (broader package support)
2. Install transformers with exact pin first: `pip install "transformers==4.45.2"`
3. Verify with `pip show transformers` immediately after
4. Clear stale module cache: `Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\huggingface\modules"`

**Lesson:** Pip's version constraints can fail silently when no compatible wheel exists. Always verify with `pip show` after install.

---

### Error 4: linker 'link.exe' not found (during pip install)

**What it meant:** Pip was trying to compile a package from source because no pre-built wheel existed for your Python version. Compilation requires Microsoft C++ Build Tools, which weren't installed.

**Pattern to recognize:** "Building wheel for X" followed by "Microsoft Visual C++ 14.0 or greater is required" or "linker not found" = no pre-built binary exists for your Python version.

**Fix paths:**
1. Best: Switch to a more common Python version (3.12 instead of 3.14) where wheels exist
2. Alternative: Install Microsoft C++ Build Tools (~6 GB, slow)
3. Best for libraries: Find an alternative pure-Python library that does the same thing

**Lesson:** For ML work in 2026, use Python 3.12. Bleeding-edge Python versions don't have library support yet.

---

### Error 5: Microsoft Visual C++ 14.0 or greater is required (IndicTransToolkit install)

**What it meant:** IndicTransToolkit has a Cython component that compiles from C source.

**Fix applied:** Replaced IndicTransToolkit with pure-Python alternative (sacremoses) that does the same preprocessing without compilation.

**Lesson:** Before installing a library that needs compilation on Windows, check if there's a pure-Python alternative. Most NLP preprocessing has multiple library options.

---

### Error 6: Streamlit watcher errors with hundreds of torchvision ModuleNotFoundError messages

**What it meant:** Streamlit's file watcher scans every loaded module on save. The newer transformers library has many image-processing modules that try to import torchvision.

**Pattern to recognize:** A wall of identical errors about modules you don't use = a watcher/scanner is touching them, not your actual code.

**Fix:** Either install the missing dependency (`pip install torchvision`) or ignore the noise. The actual app worked despite the warnings.

**Lesson:** Distinguish between errors that block your code from running and errors that are just noise. Ask: did the actual operation fail, or are these just warnings?

---

### Error 7: Marathi text appearing "blurred" or "overlapping" in the terminal

**What it meant:** Windows PowerShell's default font doesn't fully support Devanagari conjunct consonants. The text was correct; the rendering wasn't.

**Fix:** Change terminal font to Nirmala UI or NSimSun. Or just paste output into Notepad/browser to verify.

**Lesson:** Terminal display issues are not always code issues. Test output in multiple environments before declaring something broken.

---

## Part 4 — General Patterns That Apply To Every ML Project

These are the meta-lessons. They will save you hours on every future project.

### Pattern 1: The "is the venv actually active?" check
Before running any command, glance at the prompt for `(.venv)`. The single most common cause of "but it worked yesterday" issues.

### Pattern 2: Test the core, then test the wrapper
Always verify the core module works from `python -m mymodule` before testing it through Streamlit/FastAPI/Flask. UIs add layers of caching that make debugging harder. CLI is the source of truth.

### Pattern 3: Pin the framework first, install everything else around it
ML libraries upgrade aggressively. When pip installs multiple packages, it can upgrade the framework you wanted to pin. Install the framework alone first, then verify, then install everything else.

### Pattern 4: Read the bottom of pip output
Pip output is verbose. The actual error is in the last 10 lines. Search for "ERROR" or "FAILED" — everything above is usually just informational.

### Pattern 5: Hugging Face caching has multiple layers
- `~/.cache/huggingface/hub/` = the model weights (1+ GB, do not delete unless necessary)
- `~/.cache/huggingface/modules/` = small custom Python files (safe to delete to force re-fetch)
- Streamlit caches modules in memory (@st.cache_resource) — fixed by full restart

When in doubt, clear modules/ and restart Streamlit. Don't clear hub/ unless you want to re-download the model.

### Pattern 6: Read errors top to bottom, not bottom to top
The bottom error is the symptom. The first error in the chain is the cause. Scroll up to find what triggered the cascade.

### Pattern 7: Some warnings are warnings, not errors
Errors stop execution. Warnings don't. If your code produced output, the warnings are likely cosmetic. Don't waste time fixing every yellow line.

### Pattern 8: When stuck, change one variable
Don't try multiple fixes at once. Change one thing → test → see what changed. Multi-variable fixes leave you not knowing what actually worked.

---

## Part 5 — Tools and Their Roles (Reference)

| Tool | What it does | When to use |
|---|---|---|
| Python venv | Isolates dependencies per project | Every project, no exceptions |
| pip | Installs Python packages | After venv is active |
| transformers | Loads/runs HuggingFace models | Any LLM or NLP project |
| torch | Tensor computation, model runtime | Required by transformers |
| sacremoses | Pure-Python text preprocessing | When IndicTransToolkit/Moses won't compile |
| FastAPI | Backend REST API | When you need /endpoints |
| Streamlit | Quick UI for demos | Portfolio demos, internal tools |
| sacrebleu | BLEU/chrF translation scoring | Translation projects |
| Hugging Face Spaces | Free model hosting | When you need a public demo URL |
| ScreenToGif / Game Bar | Record demo GIFs | Before pushing to GitHub |
| Canva | Banner images | README headers |

---

## Part 6 — The Golden Rules

1. Use Python 3.12 for ML work in 2026. Not 3.13, not 3.14.
2. Activate venv before every session. Check the prompt for `(.venv)`.
3. Verify after install, not before. `pip show` after every critical install.
4. CLI works before UI. Test core modules with `python -m` first.
5. Pin framework versions. Floating versions break six months later.
6. Generate `requirements-locked.txt` once it works. Future you will thank present you.
7. Read errors bottom-up only after reading top-down. Find the cause, not just the symptom.
8. Terminal font issues are not code issues. Test rendering in multiple places.
9. One change at a time. Multi-variable fixes hide what actually worked.
10. Commit early, commit often. A working version + git commit = a safety net.

---

## LinkedIn Post — The Story of Anuvad

Three versions below. Pick the one that matches your voice and audience.

### Version 1: The Story Arc (most engaging, recommended)

```
Two years ago I posted "Task 1 — Iris Classifier. Step 1: Import 
libraries..." on LinkedIn.

Last week I deleted those posts and rebuilt my portfolio from scratch.

Meet Anuvad — an English to Marathi/Hindi translator for engineering 
content. Built with IndicTrans2 (AI4Bharat / IIT Madras), FastAPI, 
and Streamlit.

Why engineering content specifically?

In 2021 I volunteered as a technical translator for NPTEL (IIT 
Kharagpur). I translated 10.5 hours of engineering coursework — 
energy systems, engineering drawing — from English into Marathi. 
I learned firsthand that generic translators struggle with terms 
like "deep drawing," "tolerance stack-up," and "feed rate." 
Domain matters.

Anuvad is the productized version of that volunteer work, four 
years later, with a model behind it.

Results on a 20-sentence engineering test set:
→ English to Marathi: BLEU [your score], chrF [your score]
→ English to Hindi:   BLEU [your score], chrF [your score]
→ Avg latency: ~[your number] ms on CPU

What I learned building this:
→ Python 3.12 is the sweet spot for ML work — newer versions 
  break library support
→ ML library compatibility is fragile — pin versions, verify, 
  generate locked requirements
→ Build the CLI first, the UI second — easier to debug
→ Pure-Python alternatives often exist when a library refuses 
  to compile

The hardest part wasn't the code. It was reading enough error 
messages to learn how to read error messages.

Code: github.com/Priyerolkar/Anuvad
Live demo: [your Hugging Face URL when deployed]

Next project: a RAG assistant for automotive service manuals. 
Following along the same theme — AI tools that respect engineering 
domain context.

I'm a mechanical & automotive engineer (B.E. + M.E.) transitioning 
into ML/GenAI. If you're working on similar problems — Indian-language 
NLP, engineering AI, or you've made the same career pivot — let's 
connect.

#GenAI #NLP #IndianLanguages #IndicTrans2 #MachineTranslation 
#BuildInPublic #CareerTransition
```

### Version 2: The Short Punchy Version

```
Built and shipped: Anuvad — an English to Marathi/Hindi translator 
for engineering content.

Stack: IndicTrans2 + FastAPI + Streamlit
Test set: 20 hand-curated engineering sentences
Scores: BLEU [X] / chrF [Y]
Inspiration: my 2021 NPTEL technical translation volunteer work

Why this matters: generic translators butcher terms like "deep 
drawing" and "tolerance stack-up." Engineering content needs 
engineering-aware models.

Code: github.com/Priyerolkar/Anuvad
Demo: [HF Spaces URL]

Mechanical engineer to ML/GenAI builder. One project shipped, 
several more on the roadmap.

#GenAI #NLP #IndianLanguages #BuildInPublic
```

### Version 3: The Lessons-Learned Version

```
Five days ago I had a half-finished translation project on GitHub.

Today I have a working English to Marathi/Hindi translator deployed, 
documented, tested, and benchmarked.

Meet Anuvad. IndicTrans2 model, FastAPI backend, Streamlit UI, 
sacreBLEU evaluation, 20-sentence engineering test set with hand-
curated reference translations.

What broke along the way (and what I learned):

→ Python 3.14 was too new — half the ML ecosystem hadn't built 
  wheels yet. Switched to 3.12. Lesson: use the second-newest 
  Python for ML work.

→ Hugging Face model was gated — needed account + access token. 
  Lesson: check model pages before using them.

→ A library wanted to compile from C source on Windows but I 
  didn't have C++ build tools. Found a pure-Python alternative 
  (sacremoses). Lesson: when a library won't install, look for 
  alternatives before installing 6 GB of build tools.

→ pip silently installed the wrong transformers version despite 
  my pin. Always verify with `pip show` after installing.

→ Marathi text rendered as overlapping characters in PowerShell. 
  Wasn't a code bug — was a terminal font. Lesson: distinguish 
  display issues from logic issues.

The translator works because of the engineering, but the 
engineering is built on understanding why things break.

Mechanical engineer (B.E. + M.E.) building toward ML/GenAI.

Code: github.com/Priyerolkar/Anuvad
Demo: [HF Spaces URL]

Currently building: RAG assistant for automotive service manuals.

#GenAI #MLEngineering #IndianLanguages #BuildInPublic #LearningInPublic
```

---

## What to Replace Before Posting

- `[your score]` placeholders → your actual BLEU and chrF numbers from `evaluation/results.md`
- `[HF Spaces URL]` → after you deploy to Hugging Face Spaces
- Tag preferences → adjust hashtags based on what you see trending in your feed

## When to Post

Tuesday–Thursday, 8–10 AM your local time for max engagement. Avoid Mondays (people catching up) and Fridays (people checking out).

After posting, pin the post to your Featured section — three dots on the post → "Feature on top of profile."

---

## Final Note

Save this document. The next ML project you start, you'll re-encounter half of these errors. The build checklist alone will save you a day. The lessons you've learned this week are not specific to Anuvad — they apply to every Hugging Face model, every Streamlit app, every Python ML environment you'll ever set up.

You've earned them. Use them.
