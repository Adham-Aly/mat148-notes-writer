---
name: "mat148-notes-writer"
description: "Turn a chapter or run of sections of a calculus/analysis textbook PDF into an original, intuitive, lean, LaTeX-typeset PDF of notes. A recon pass by subagents records what the source covers: every definition, theorem, lemma and formula verbatim (back-references by number replaced with names), which results are proved and by what overall approach, how much explanation and which kinds of worked example each concept received, and every figure in reproducible detail. The notes are then written from scratch from that recon file alone, with the verbatim statements kept, proofs only where the source has them (in the source's approach), and the source never looked at again. Use when the user names a textbook PDF and a chapter or section range and wants notes made from it."
---

# Textbook chapter -> original, intuitive, lean typeset notes (verbatim statements kept)

## The idea

A textbook is thorough but long, written for every reader at once, and its own explanations are rarely the clearest ones possible. This skill produces the document the reader actually wants: the same mathematics, with the book's exact definitions and theorem statements, explained the way an excellent tutor would explain it starting from a blank page, with ideas arriving one at a time and each one understood before the next.

**This is not a condenser.** The output is not a summary, a paraphrase, or a tightened edit of the source. The source is consulted for exactly one thing, during recon: a record of *what is covered*. Formal statements are kept verbatim because the reader will be examined on the book's wording; everything else, every explanation, proof, example and picture, is written from your own knowledge of the mathematics, as though the source did not exist.

The reason is quality, not style. A paraphrase inherits the source's structure, its gaps and its rhythm. A condensation strips out the connecting reasoning that made the original followable. Both are worse to read than the source itself. Rebuilding from the ideas up is the only way the result ends up clearer than what it came from.

| Comes from the source (recorded during recon) | Never comes from the source |
|---|---|
| The exact wording of every definition, theorem, lemma, corollary, formula and labelled remark | The wording of anything else: explanations, motivation, proofs, transitions |
| Which results are proved, and the bird's-eye approach each proof takes | The proofs themselves: their steps, choices, inequalities |
| How much explanation each concept received (a level, not the content) | Any sample, quote or paraphrase of those explanations |
| Which concepts received worked examples, and what kind of problem each shows | Its actual worked examples: their functions, numbers, solutions |
| What each figure depicts, in reproducible detail | Its numbering and headings: theorem, definition, example, section and page numbers |
| The broad order of topics, and the level | Its paragraph structure and rhythm |

The target reader is a student who has never seen the source. After reading, they should understand not just *what* each result says but *why* it's true and *how* it fits with the others, without the document being any longer than it needs to be.

Promises, in priority order:
1. **Nothing lost.** Everything in the recon file is in the output.
2. **Statements verbatim, everything else from scratch.** Guaranteed by the wall described below, which is never crossed.
3. **Proofs only where the source proves.** A result the source states without proof gets no proof here. A result the source proves gets an original proof that follows the source's overall approach, so the reader learns to prove things the way the book does.
4. **Intuitive.** Clearly easier to follow than a typical treatment of the same material. Depth tracks the source's emphasis: concepts the source explained at length get the fullest treatment.
5. **Lean.** Every sentence must earn its place by removing a real confusion. No introductions, recaps, padding, motivational fluff, or explaining things the reader already gets.
6. **Nothing big added.** No theorems or techniques beyond what is in the recon file.

## The workflow

Three steps with a wall after the second.

```
LOCATE    one subagent finds the PDF page indices of the requested sections (replies with numbers only)
RECON     subagents view the pages  ->  part files  ->  NAME-recon.md (the only record of the source)
=====     THE WALL: the source is never looked at again, by anyone
WRITING   the main session plans, writes, typesets and checks, from the recon file alone
```

**The wall.** This is the most important rule in the skill. Once the recon file is written, the source is off limits for good, to the main session and to every subagent, for the rest of the task and for any later revisions. "The source" means all of it: the PDF, page images, text layers, and any notes about them. Do not open, view, rasterize, search, skim or quote it, not even to check a single statement. The source is inspected only during recon, which happens separately from and independently of the writing.

Why so strict: any contact with the source while writing pulls the writing toward it. The structure creeps in, then the examples, then the sentences. The only reliable protection is that the writer has nothing of the source to lean on except the recon file.

**No leakage into the main session.** The wall also runs between the recon subagents and the main session's context. Recon subagents write their findings to files; their replies to the main session contain nothing from the textbook, only a recap of what they did (counts, pages covered, problems met). The main session's only contact with the source is the assembled recon file.

If the recon file turns out not to be enough (an ambiguous entry, say), settle it from the neighbouring entries and the level of the material. If that fails, ask the user what was meant. The source is not an option. The only way anything further comes out of the source is the user explicitly asking for another recon pass; that is run by a fresh recon subagent and adds entries to the file.

**Subagents.**
- At most **4** recon subagents at a time (the page locator runs before them and does not count). The user can raise or lower this number; use theirs if they give one.
- Subagents run on the **same model as the main session**. Spawn them with no model override.
- Subagents do the locating and the recon and nothing else. The main session writes the whole document itself unless the user asks for the writing to be split among subagents (section 3).

## 0. Intake (main session)

- **Source.** A textbook PDF and a chapter or list of sections. **Do not open or view the PDF yourself.** Collect only mechanical facts: `pdfinfo FILE | grep Pages`.
- **Scope.** The sections the user names. End-of-section and end-of-chapter exercise sets are excluded by default; the user can ask for them. If the user names a whole textbook with no chapter, ask which part.
- **Output directory.** Use the one the user gives. If none is given, use the workspace (the directory you are running in). The final `.pdf`, the `.html` it was built from, and `NAME-recon.md` all go there, with the same descriptive kebab-case name (e.g. `limits-and-continuity.pdf`). Don't overwrite a file you didn't create; pick another name. Scratch files (part files, figure script, page images) go in the scratchpad or a temp directory.
- **Setup.** Start `bash scripts/setup.sh` (section 4) in the background now; it is idempotent and fast after the first run.
- **User instructions.** Everything in this skill is the default. The user may override any part of it: include the exercises, cover only some sections, aim for a different length, change the number of subagents, split the writing among subagents, record something extra during recon. Apply an override to precisely what it names and keep the defaults everywhere else. An override that needs more from the source is carried out during recon, by passing the instruction to the recon subagents. It does not open the wall.
- **Don't interview the user.** Ask only when the scope can't be determined. Otherwise proceed.

## 1. Locate and recon (subagents)

### 1a. Locate the pages

Spawn one subagent with the page-locator prompt in `references/recon-prompts.md`. It finds, for each requested section, the 1-based PDF page index (as used by `pdftoppm -f/-l`, not the printed page number) where the section begins, where the main text ends, where each exercise set lies, and where the next chapter begins. Its reply is numbers only, in the fixed format given in the prompt, so nothing of the book reaches the main session. Textbooks often interleave an exercise set after each section; the locator reports these so the recon subagents can skip them.

### 1b. Recon

Recon produces one file, `NAME-recon.md`, in the output directory, assembled from part files written by the subagents. It is the complete record of the source and the writer's only reference.

**Split.** One recon subagent per section is the natural split; merge two short adjacent sections into one subagent, or split a very long section (more than about 20 pages) across two, to stay at or under the cap. Each subagent gets a contiguous page range, told exactly which pages are exercise sets to skip and which boundary pages hold only the tail of a neighbouring exercise set.

**Spawn** them in parallel with the recon prompt in `references/recon-prompts.md`, filled in with the page range, the part-file path, and any user instructions affecting recon. The prompt tells each subagent to read `references/recon-brief.md` and to write its findings to its own part file in the scratchpad, never into its reply.

The brief has the subagents record, in source order under their own plain topic headings:
- every **definition, theorem, proposition, lemma, corollary, formula and labelled remark verbatim**, transcribed from the page images with the maths in LaTeX, with each back-reference by number ("by Theorem 2.3") replaced in place by the name of the result referred to, and no textbook numbering anywhere;
- for every result, a **proof marker**: `[proof included, <bird's-eye approach>]` or `[no proof in text]`, with partial proofs saying which parts are proved and which are left to exercises;
- an **explanation coverage** level for every concept (extensive / moderate / brief / none), with no sample, quote or paraphrase of the explanation itself;
- an **examples** entry per concept that received a worked example, of the exact shape "X received an example showing <problem type / setup / scenario nature>", never naming or listing individual examples;
- a **figures** entry for every content-carrying graph, diagram or table, in enough detail to reproduce it;
- everything else (methods, cautions, unlabelled remarks) by name only.

**Wait for all replies**, then act on anything they flag. Two cases that came up and how to handle them: a result that is formally stated and proved but labelled as an example in the book is recorded as a theorem, verbatim, with `[proof included]` (ask the subagent to amend its file; its reply stays content-free). Handwritten annotations on scanned pages are not part of the textbook and are ignored.

**Assemble.** Concatenate the part files in source order into `NAME-recon.md`, under one top-level heading per section in your own words, with a title line naming the subject and level and a two-line header explaining the conventions (statements verbatim; `[proof included]` / `[no proof in text]`; `[no proof in text]` results get no proof in the notes). Then clean it up:
- merge duplicate entries where two parts met mid-topic; make headings and style uniform;
- **generalize figure entries that describe a worked example** (they name the book's own example function and its numbers): rewrite them to the type of thing shown ("two-sided table of values of a rational function near a removable point, settling on a finite value"), keeping the mathematical features. Figure entries for a definition or theorem (bands, regions, unit-circle constructions) keep their full detail, since those are the pictures you must reproduce;
- cut anything else that echoes the book beyond what the brief allows: an example's specific function, a sample of an explanation, a page or theorem number.
Delete the part files once the recon file is written.

**Then the wall comes down.** From this point on, nobody looks at the source.

If no subagent mechanism is available, or the user set the number of subagents to zero, do the recon yourself by following `references/recon-brief.md`, write the file, and then hold yourself to the wall exactly the same: write from the file, not from your memory of the pages.

## 2. Find the through-line and plan the path (silently)

Work from `NAME-recon.md` and your own knowledge of the subject.

**Through-line.** Find the single idea that ties the material together, usually one picture or one sentence. For limits and continuity: "an opponent names a tolerance around a target; you must find a window of inputs that keeps the outputs inside it. Every kind of limit, and continuity, is this one game with the windows changed." This becomes a 1-3 sentence opening, and later sections refer back to it. It's the biggest intuition win and costs almost no space.

**Path.** Design the shortest chain of ideas from what the reader already holds to where the material ends, each link small enough to explain in a few sentences. Follow the recon file's broad order of topics so the document lines up with the reader's course, but the sectioning, and how each idea is introduced, motivated and sequenced, are your own design: picture first, then plan, then the formal statement; move an item earlier if later material leans on it. Where the book states a result informally first and precisely later, do the same: the informal version with tables and pictures, then the precise one.

**Depth from coverage.** The coverage levels set the weight of each concept. `extensive` means the book considered it the hard part: give it the fullest intuition, a picture if spatial, and your own worked example. `brief` or `none (statement only)` means a statement with a one- or two-sentence lead-in is enough. Never skip a concept because its coverage is low.

**Proofs from the approach notes.** For each `[proof included, ...]` result, plan a proof that follows the recorded approach (by contradiction; direct ε–δ; via a named theorem; by the Completeness Axiom on a supremum; by chaining two definitions; by induction). The steps, the choices and the explanations are yours. A result marked as proved for some parts or cases only is proved for exactly those parts.

**Notation.** Choose standard notation for the level and keep it consistent throughout. Use the names the recon file uses for things.

**Gaps.** For each entry, find what a first-time reader will need beyond the bare result:
- **Missing prerequisite.** A term or axiom from earlier material (e.g. the Completeness Axiom). One-sentence Recall where first needed.
- **Purpose.** Why is this result here? One sentence before the statement, only if it isn't obvious.
- **Unexplained choices in proofs.** A specific epsilon, delta, interval, N, substitution or case split: say why it works.
- **Imprecise statements.** The verbatim statement is kept as written; if it leaves something implicit (a sign that depends on parity, "for all x in I" that must exclude the point itself), add a one-line note in parentheses right after the box. Never edit the statement's content to fix it.

## 3. Write

The main session writes the whole document, from the recon file and its own understanding of the mathematics. The tools, each used only where it removes a confusion:

- **Verbatim statements in the boxes.** Each definition, theorem and labelled remark goes into its box exactly as recorded, with the book's name for it if it has one and your descriptive label otherwise ("Theorem (Local boundedness)"). Permitted edits, and only these: fix an obvious typo ("defined in on"); render notation properly (`L+` as $L_+$); turn an exercise-style opening into a statement ("Show that there must exist" becomes "Then there must exist"); drop a clause that points the reader to an exercise. Report every such edit in the delivery note.
- **One new idea per paragraph or box.** If it needs "and also", split it.
- **Concrete before abstract.** A table of values, a few actual numbers or a number line, then the symbols. Compute every number in a table with a few lines of code; never guess digits.
- **A picture where the idea is spatial.** Every `figure` entry gets a picture of that thing, of your own design, built with `assets/figs.py` (section 4). Beyond those, definitions involving bands, windows, regions or growth usually deserve a small clean figure. Skip pictures that just decorate.
- **Intuition before formal.** One or two plain sentences saying what the statement means, then the box.
- **Proof plan before every non-trivial proof.** One line naming the strategy, in the approach the recon file recorded: "If there were two limits, put disjoint bands around them; near $c$ the graph would have to lie in both." Then the proof, with the reasoning filled in as short steps and each choice explained. Prove exactly what is marked `[proof included]`, for exactly the parts marked. For `[no proof in text]` results, write no proof: at most one sentence of orientation before the box ("the punctured window is the union of two half-windows, which is why..."), never an argument.
- **Your own examples.** For each `example` entry, invent a clean instance of that problem type and work it, saying why each step is the natural one. "(several)" means two or three short instances. Walkthroughs are laid out to be read: one step per line, with display maths for the working and a short sentence on each move, never a solution run together into one paragraph. Examples from earlier sections can be reused later when the recon file says the later section revisits them (e.g. earlier limits reread as continuity).
- **Non-examples where a hypothesis matters.** For each `caution` entry, and wherever a hypothesis can't be dropped, give a small counterexample right after the result and say which hypothesis it shows is needed.
- **Jargon explained in passing**, inside the sentence.
- **Quick checks, sparingly.** At most one per major section, a question that makes the reader use the idea. Answers in a few lines at the end.
- **Confident textbook voice.** No hedging. The document stands alone: never mention a source ("the textbook says", "the book proves").
- **No borrowed numbering.** Results are labelled by name. The document's own plain section numbers are fine. Cross-reference by name or by your own section number ("the Limit Laws", "Section 2").

Style distinction: formal statements and proofs look formal (Definition/Theorem boxes, Proof ... end mark); intuition sits in lighter Idea and Recall boxes or in plain lead-in sentences; verbatim labelled remarks go in an Idea-style box headed Remark.

**Leanness rules.**
- Length is set by the recon file: each entry gets the space a first-time reader needs to understand it, weighted by its coverage level, and no more. As a guide, a definition with its intuition takes a few lines; a theorem with its plan and proof, a third to half a page.
- Each explanation is as short as it can be while still working. Usually one or two sentences; three only if a proof step needs it.
- Say each thing once. No restating a theorem, no end recap, no "in this section we will".
- Don't explain what the reader already understands.
- If it runs long, cut the weakest explanations first. Never cut something that is in the recon file.

**Only if the user asks for the writing to be split among subagents.** Do section 2 yourself first, then hand each writing subagent (same cap, same model) everything you are working from:
- the path to this `SKILL.md`, with the instruction to follow "The wall" and section 3;
- the complete `NAME-recon.md`, not just their part of it;
- your full plan: through-line, section outline with the entries assigned to each section, notation, any user overrides;
- which section(s) they are to write, and the building blocks in `assets/template.html` and `assets/figs.py`. They return an HTML fragment for the body only, with `{{FIG:name}}` placeholders and the matching generator functions.

Do not give them the source or tell them where it is; the wall binds them too. When the fragments come back, combine them in order and consolidate the document as a whole: one voice, one notation, no repeated Recalls or duplicated explanations, cross-references and call-backs to the through-line in place, trimmed to the leanness rules. Then typeset and check it as a single document.

## 4. Typeset (LaTeX look via HTML + KaTeX -> PDF)

The document is authored as a single HTML file and printed to PDF with headless Chromium. Not Markdown, not LaTeX.

Setup (idempotent; fast after the first run). Paths are relative to this skill's directory:

```bash
bash scripts/setup.sh        # installs KaTeX + Chromium into ~/.cache/mat148-notes-writer, prints the KaTeX URL
```

Start the HTML from `assets/template.html`: read it, replace `KATEX_DIST` (three places) with the URL that `setup.sh` printed, and write the document into the body using the template's building blocks. Author it as a *source* file in the scratchpad (`src.html`) with `{{FIG:name}}` placeholders where figures go. The CSS uses `KaTeX_Main`, a Computer Modern lookalike, for body text so prose and maths match. Maths goes in `$...$` (inline) and `$$...$$` (display). Write `\lt` and `\gt` for `<` and `>` inside maths so the HTML parser never sees a bare angle bracket.

**Figures.** Copy `assets/figs.py` into the scratchpad and add one generator function per figure (`def f_name(): ... return svg(...)`), using its `Panel` helper: it maps mathematical coordinates to pixels, draws axes with ticks, plots a function from computed points with clipping at the panel edges (so asymptotes are never crossed), and places dots, dashed guide lines, shaded bands and labels. Then

```bash
python3 -I figs.py src.html OUTDIR/name.html
```

substitutes every placeholder, fails loudly if one is left, and wraps inline maths followed by punctuation in a no-wrap span so a comma or period never starts a line on its own. Conventions the helper enforces or expects: thin black strokes, one accent colour for the key object (the band, the squeezed function, the arc), panel titles above the plot area via `title=` rather than labels floating in the plot, labels in plain Unicode (ε, x², ≤) since KaTeX does not typeset inside SVG, a white halo behind SVG text so labels stay legible over curves, 130-210px tall. Side-by-side panels go in one SVG with `ox=` offsets. Every curve is computed, never eyeballed: a parabola that isn't symmetric or an asymptote that gets crossed teaches the wrong thing. Dense oscillation ($\sin(1/x)$) needs sampling in $1/x$, not in $x$.

Render:

```bash
node scripts/render.mjs OUTDIR/name.html OUTDIR/name.pdf
```

It prints the page count, and exits non-zero listing anything that failed to load and every formula KaTeX couldn't parse or left as raw text. Fix those and re-render until it is clean.

If `setup.sh` can't install (no npm or no network), use `https://cdn.jsdelivr.net/npm/katex@latest/dist` as `KATEX_DIST` and any headless Chromium for printing. If neither works, say so plainly rather than delivering a PDF with raw TeX in it.

## 5. Check

The source stays closed. Every check is against the recon file or your own mathematics.

- **Coverage.** Walk `NAME-recon.md`; every definition, theorem, remark, formula, method, caution, example entry and figure entry is in the output. Every `[proof included]` result has a proof in the recorded approach and every `[no proof in text]` result has none. Nothing substantial is in the output that isn't in the file.
- **Statements.** Each boxed statement matches the recon file word for word apart from the permitted edits.
- **Maths.** Re-derive every formula and proof step written. Test each of your own examples: do the worked examples actually come out to the answers given, are all hypotheses present, do the counterexamples fail for the stated reason? Recompute every table of values. A wrong intuitive rewrite is worse than no rewrite.
- **Figures.** Each graph is true to the function it claims to show: shape, intercepts, asymptotes, labels, and the caption describes what is actually drawn.
- **First-time-reader pass.** Reread the draft top to bottom as a student new to the material. Wherever a step jumps (a symbol used before it's explained, a "clearly" that isn't clear, two new ideas in one sentence), fix it. Then reread as a student who *did* follow: cut anything that explains the obvious. Both passes matter; the second keeps it lean.
- **Look at it.** `pdftoppm -r 70 -png OUTDIR/name.pdf "$(mktemp -d)/out"`, view every page. Things that go wrong and need fixing: a panel title or label printed over an axis or a curve; two labels colliding; a long display-math statement running past the right margin (break it into lines, or set it inline); a lone comma or period at the start of a line after a formula; a box or figure split across pages; a caption that no longer matches a changed figure. Re-render and re-check the pages you changed.

## 6. Deliver

Report in a few lines: the paths of the PDF, its HTML and the recon file, the page count, and how the recon rules were applied (statements verbatim, proofs only where marked, partial proofs limited to the proved parts). List every edit made to a verbatim statement. Mention anything the subagents flagged (handwriting on scans, a result relabelled from example to theorem) and any user override applied, and nothing else unless something couldn't be done.
