# Subagent prompts

Fill in the capitalised fields. Both prompts are designed so that nothing from the textbook reaches the main session's context: the locator replies with numbers only, and the recon subagents write to files and reply with counts only.

## Page locator (one subagent, before recon)

```
You are a page locator for a PDF. Your reply must contain ONLY page numbers — absolutely no textbook prose, titles, headings, definitions, or any content from the book. Do not quote or paraphrase anything.

File: /ABS/PATH/textbook.pdf (N PDF pages).

Task: find the PDF page indices (1-based, as used by `pdftoppm -f/-l`, NOT the printed page numbers) where each of sections SECTION LIST begins, where the chapter's main text ends, and where the end-of-chapter exercise set (if any) begins and ends. Also tell me the PDF page where the next chapter begins.

Method: you may use `pdftotext -f X -l Y` on a few pages, or rasterize pages with `pdftoppm -r 60` into a temp dir (mktemp -d) and view them, to locate the table of contents and the page offset; then verify by checking the actual start pages. Delete any temp files afterwards.

Reply format exactly (numbers only, nothing else):
2.1: <pdf page>
2.2: <pdf page>
...
main text ends: <pdf page>
exercises: <first>-<last> (or "none" / "per-section, interleaved" if exercises appear at the end of each section — in that case give each section's exercise page range as "2.x exercises: a-b")
next chapter starts: <pdf page>
```

## Recon subagent (one per section, up to the cap, in parallel)

```
Read SKILL_DIR/references/recon-brief.md and follow it exactly, EXCEPT where the instructions below override it (they win wherever they conflict with the brief).

Source: /ABS/PATH/textbook.pdf, PDF pages FIRST-LAST of N (the main text of one section; 1-based PDF page indices as used by pdftoppm -f/-l). [Page FIRST may also contain the tail of the previous section's exercise set: ignore it and start where this section begins.] This section's exercise set occupies pages A-B: do NOT record the exercises (on page A, record only the material before the exercises begin).

Output: write your record to SCRATCHPAD/recon-parts/part-K.md

Instructions affecting recon:

1. VERBATIM STATEMENTS. Every definition, theorem, proposition, lemma, corollary, named formula and labelled remark is recorded VERBATIM, exactly as worded in the textbook, with the maths transcribed in LaTeX ($...$ inline, $$...$$ display), by viewing the page images (no text extraction). Use the textbook's name for the result if it has one; otherwise a short descriptive label. Do NOT include the textbook's ID numbers (e.g. "Theorem 2.1.3") anywhere. If a statement refers to another definition/theorem/lemma by its ID, replace that reference in place with the NAME of the referenced item; if it lies outside your page range, view the page where it is stated solely to learn its name and record nothing else from it. Only the formal statements are verbatim; proofs are NOT transcribed.

2. PROOF MARKER. Mark every theorem/proposition/lemma/corollary that the textbook actually proves with "[proof included, <bird's-eye approach>]", where the approach is one clause naming the proof's overall methodology (e.g. "by contradiction", "direct epsilon-delta", "by the Squeeze Theorem after a geometric area comparison", "by the Completeness Axiom on a supremum, then contradiction") and NEVER the steps, the choices of delta/epsilon, any inequality or any sentence of the proof. If it is not proved in the textbook, mark it "[no proof in text]"; proofs left to the exercises or the reader count as no proof. Partial proofs say exactly which parts/cases are proved and which are left to exercises.

3. EXPLANATION COVERAGE. Under a heading "### Explanation coverage", add entries stating which concepts/definitions/theorems/ideas received extensive, moderate, brief, or no explanation. CRITICAL: never, under any circumstances, include any sample, quotation or paraphrase of those explanations, nor say what the explanation says or how it argues. Only the level. Format exactly:
   - coverage: <concept name> — extensive | moderate | brief | none (statement only)

4. EXAMPLES. Under a heading "### Examples", record which definitions/theorems/concepts received worked examples or walkthroughs. NEVER name individual examples, never list them one by one, never give their specific functions, numbers, data or solutions. One entry per concept, exactly:
   - example: <concept> received an example showing <problem type / setup / scenario nature>
   (add "(several)" if more than one example of that type was given.)

5. FIGURES. Under a heading "### Figures", add an entry for every graph/visual/diagram/table that carries content, noting what it depicts in enough detail that it could be reproduced (what is plotted, axes, key features like intercepts, asymptotes, shaded regions, open/filled dots, labelled points, arrows) and which concept it accompanies. Describe the mathematics shown, not the surrounding text.

6. Everything else (methods, cautions, unlabelled remarks) stays names-only per the brief, under your own plain topic headings, in source order.

7. NO LEAKAGE IN YOUR REPLY. Your final reply must NOT contain any textbook content whatsoever — no statements, names of results, prose, quotes or paraphrases. Reply only with a short recap in this form: "Wrote part-K.md: N definitions, N theorems (N with proof), N coverage entries, N example entries, N figure entries. Pages covered: X-Y." plus a note on anything that could not be done or that needs a decision (describe the situation, not the content). Delete your temp directory before finishing.

[USER INSTRUCTIONS AFFECTING RECON, if any, e.g. "also record the exercises as example types".]
```

For a subagent covering two sections, give both page ranges and both exercise ranges, and ask for the two sections under separate top-level headings in the one part file.

## Follow-ups

Follow-ups to a recon subagent (via SendMessage) keep the same rule: "Your reply is a one-line recap with no textbook content." Example, for a result the subagent found formally stated and proved inside an example: "Record that result as a theorem, verbatim (ID references replaced by names), marked [proof included, <approach>]. Keep its Examples and method entries as they are."
