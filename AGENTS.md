# Working on mat148-notes-writer

This repository publishes one agent skill, `skills/mat148-notes-writer/`. The skill turns a chapter or section range of a calculus/analysis textbook PDF into an original, intuitive, lean, LaTeX-typeset PDF of notes. Read `skills/mat148-notes-writer/SKILL.md` first; this file records the intent behind it so edits keep the workflow intact.

## Layout

```
skills/mat148-notes-writer/
  SKILL.md                      the workflow the agent follows (intake, locate, recon, wall, plan, write, typeset, check, deliver)
  references/recon-brief.md     what recon subagents read; defines exactly what they record and what they never record
  references/recon-prompts.md   fill-in prompts for the page-locator subagent and the recon subagents, plus follow-up wording
  assets/template.html          HTML/CSS skeleton (KaTeX, theorem/definition/idea/recall/check boxes, tables, figures)
  assets/figs.py                figure library: maths-to-pixel panels, computed curves, bands, dots; {{FIG:name}} substitution
  scripts/setup.sh              installs KaTeX + Playwright Chromium into ~/.cache/mat148-notes-writer (idempotent)
  scripts/render.mjs            HTML -> PDF with headless Chromium; fails on any unparsed formula or missing asset
```

The repo root (`README.md`, `AGENTS.md`, `CLAUDE.md`, `LICENSE`) is packaging only. The skill must stay self-contained under `skills/mat148-notes-writer/` so it installs with `npx skills add Adham-Aly/mat148-notes-writer`.

## The non-negotiables

These are the user's requirements. Every one of them is equally important; do not weaken any of them while editing.

**1. The wall.** The source PDF is looked at only during recon, only by subagents. After the recon file is assembled, nobody opens, views, rasterizes, searches or quotes the source again, for the rest of the task and for any later revision. The notes are written from the recon file alone.

**2. No leakage into the main session.** Recon subagents write their findings to part files and reply with a content-free recap (counts, pages covered, problems met). The page-locator subagent replies with page numbers only. The main session's only contact with the textbook is the assembled recon file. Follow-ups to subagents keep the same rule.

**3. Formal statements verbatim.** Every definition, theorem, proposition, lemma, corollary, named formula and labelled remark is recorded word for word, transcribed from the page image with the maths in LaTeX. Any reference by number to another result ("by Theorem 2.3") is replaced in place by that result's name. No textbook numbering appears anywhere. Only the statement is verbatim; the surrounding prose and the proof are not transcribed.

**4. Proof markers, and proofs only where the source has them.** Each result is marked `[proof included, <approach>]` or `[no proof in text]`. Proofs left to the reader or to exercises count as no proof; partial proofs say exactly which parts are proved. The notes prove exactly what is marked, for exactly the parts marked, and give no proof for anything else.

**5. The proof approach is a bird's-eye paradigm, never a sample.** The approach note exists so the writer's original proof still follows the book's methodology (by contradiction; direct epsilon-delta; via the Squeeze Theorem after a geometric comparison; by the Completeness Axiom on a supremum; by chaining two definitions; by induction). It is one clause. It never contains the choice of delta or epsilon, an inequality, an intermediate claim, the order of steps, or any sentence from the proof. If it mentions a specific quantity from the proof, it is too specific.

**6. Explanation coverage is a level, nothing more.** For each concept the recon records extensive / moderate / brief / none (statement only). Never a sample, quotation or paraphrase of the explanation, never what it says, how it argues, or what analogy or picture it uses. The writer uses the levels to weight depth.

**7. Examples are recorded by type only.** One entry per concept, in the fixed shape "X received an example showing <problem type / setup / scenario nature>", with "(several)" when there were more than one. Never individual examples, their functions, numbers, data or solutions. The writer invents its own example of each recorded type.

**8. Figures are recorded in reproducible detail.** Every content-carrying graph, diagram or table gets an entry describing what is plotted, axes, intercepts, asymptotes, open/filled dots, shaded regions, labels, and which concept it accompanies. During assembly, figure entries that describe one of the book's worked examples (naming its function and numbers) are generalized to the type of thing shown; figures illustrating a definition or theorem keep full detail. The writer draws every figure itself, from computed points.

**9. Everything else is names only.** Methods, cautions and unlabelled remarks are index-style bullets. The source's intuition, motivation and analogies get no bullet at all; they are reflected only in the coverage level.

**10. Exercises are excluded by default.** Textbooks often interleave an exercise set after each section; the page locator reports those ranges and recon subagents skip them. The user can ask for exercises explicitly.

## How the pieces fit

- The user names a PDF and a section range. The main session never opens the PDF; it runs `pdfinfo` for the page count and starts `scripts/setup.sh` in the background.
- One locator subagent maps section numbers to 1-based PDF page indices (not printed page numbers) and exercise ranges.
- Up to 4 recon subagents (same model as the main session, no model override), roughly one per section, each view their pages as images (never text extraction), write a part file, and reply with counts.
- The main session concatenates the part files into `NAME-recon.md` in the output directory, with a heading per section and a two-line conventions header, cleans it up, deletes the part files, and from then on works only from that file.
- Writing: through-line first, then a path through the material in the recon file's broad order; verbatim statements in the boxes (only typo fixes, notation rendering, "Show that" → "Then", and dropping pointers to exercises are permitted, and each edit is reported at delivery); a one-line clarifying note beside a statement that leaves something implicit, never an edit to it; a plan line in the recorded approach before each proof; own examples per example entry; counterexamples per caution; at most one quick check per major section with answers at the end.
- Typesetting: author `src.html` from `assets/template.html` with `{{FIG:name}}` placeholders; add one `f_name()` generator per figure to a copy of `assets/figs.py`; run `python3 -I figs.py src.html out.html` then `node scripts/render.mjs out.html out.pdf`; rasterize with `pdftoppm` and look at every page.
- Checks: coverage against the recon file, statements word for word, every formula and example re-derived, every table recomputed, figures true to their functions, two reader passes (first-time reader, then fluent reader), and the visual pass for overlapping labels, overflowing display maths, orphaned punctuation, split boxes.
- Delivery reports paths, page count, how the recon rules were applied, every statement edit, and anything the subagents flagged (handwriting on scans, a result relabelled from example to theorem).

## Things learned the hard way

- `{{FIG:...}}` placeholders inside HTML comments get substituted too; `figs.py` strips comments first. Keep the template's example as `{{FIG:<name>}}` so it never matches a generator.
- Panel titles belong above the plot (`title=`), not as text floating inside it, or they collide with axes and curves.
- Dense oscillation such as $\sin(1/x)$ must be sampled in $1/x$, not uniformly in $x$.
- A long verbatim statement set as display maths can run past the right margin; break it into lines or set it inline.
- A comma or period after inline maths can wrap to the start of the next line; `figs.py` wraps short `$...$` plus trailing punctuation in a `.nw` span.
- Scanned textbooks may carry a student's handwriting; it is not part of the book and recon ignores it.
- A result that is formally stated and proved inside something the book labels "Example" is still a result: recorded as a theorem, verbatim, with its proof marker.
- No length target. The document's length is set by the recon file and the per-item guide only; never anchor runs to a page count.

## Editing this repo

- Keep the skill self-contained under `skills/mat148-notes-writer/`; nothing in it may reference files outside that directory.
- `SKILL.md`, `references/recon-brief.md` and `references/recon-prompts.md` must stay consistent with each other and with the non-negotiables above; a change to what recon records needs all three updated.
- Test changes to `assets/figs.py` or `assets/template.html` end to end: substitute a placeholder, render with `scripts/render.mjs`, rasterize, and look at the page.
- Commit messages: plain, descriptive, no co-author trailers.
