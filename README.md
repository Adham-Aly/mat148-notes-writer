# calc-notes-writer

An agent skill that turns a chapter (or a run of sections) of a calculus/analysis textbook PDF into an original, intuitive, lean, LaTeX-typeset PDF of notes.

It is not a summariser. Subagents inspect the textbook once and record what it covers: every definition and theorem **verbatim**, which results are proved and by what overall approach, how much explanation and what kinds of worked example each concept received, and every figure in reproducible detail. The notes are then written from that record alone, from scratch, with the textbook never opened again. The result keeps the book's exact statements, proves only what the book proves (in the book's approach), and explains everything else the way a good tutor would.

## Install

```bash
npx skills add Adham-Aly/calc-notes-writer
```

Requirements on the machine running the skill: `node`/`npm` (KaTeX and headless Chromium are installed on first use into `~/.cache/calc-notes-writer`), `python3`, and poppler (`pdfinfo`, `pdftoppm`).

## Use

Hand the agent a textbook PDF and a section range:

> /calc-notes-writer source material: textbook.pdf. sections to cover: 2.1–2.5. do not include end-of-chapter exercises.

You get `NAME.pdf`, the `NAME.html` it was printed from, and `NAME-recon.md`, the record the notes were written from.

## Layout

```
skills/calc-notes-writer/
  SKILL.md                      the workflow
  references/recon-brief.md     rules for the recon subagents
  references/recon-prompts.md   prompts for the page locator and the recon subagents
  assets/template.html          HTML/CSS skeleton with KaTeX
  assets/figs.py                figure library and {{FIG:name}} substitution
  scripts/setup.sh              installs KaTeX + Chromium
  scripts/render.mjs            HTML -> PDF, fails on any unparsed formula
```

See `AGENTS.md` for the design requirements behind the skill.

## License

MIT
