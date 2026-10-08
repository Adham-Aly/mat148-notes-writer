# Recon brief

You are doing the recon pass for a rewrite of a chapter of a maths textbook. Look through the pages you were assigned and write a record of **what they cover** to the part file named in your task. Nothing goes into your reply except a content-free recap.

Someone else writes the new document from the assembled record alone. They will never see the source, on purpose: the new document has to be written from scratch out of the writer's own knowledge of the mathematics, and any explanation, example or structure that leaks through from the source pulls the writing toward a paraphrase of it. The one exception is formal statements, which the reader will be examined on in the book's own words: those you record **verbatim**. Everything else is recorded as names, levels and types, never as content.

Two things follow:
- **Too much in the record spoils the document.** A sample of an explanation, a worked example's details or a proof's steps becomes the source's voice in the output.
- **Anything missing from the record is lost for good.** Nobody goes back to the source after you. Completeness is your responsibility.

## Looking at the source

Look only at the pages assigned to you. Skip the exercise pages your task names; on a boundary page, record only the main-text material.

**Look, never extract.** Do not use OCR, `pdftotext`, the PDF's text layer, or any other text extraction. Extraction mangles formulas and silently drops graphs, diagrams, tables and margin notes. Rasterize into a temp directory of your own and view every page, one at a time, as an image:

```bash
WORK=$(mktemp -d)
pdftoppm -r 150 -f FIRST -l LAST -png INPUT.pdf "$WORK/pg"
```

View each `pg-*.png` in order with your image-viewing tool; skip nothing except blank pages. If small print or a formula is hard to read, re-render that page at `-r 300`; a verbatim statement must be exact. For a long range, work in batches: view a run of pages, add to the file, continue.

**Handwritten annotations** on scanned pages (a student's notes, underlining, translations) are not part of the textbook. Record nothing from them.

## What to record

Markdown, in the order the source covers things, under plain topic headings of your own wording (never the book's headings). Then three fixed subsections at the end: `### Explanation coverage`, `### Examples`, `### Figures`.

### Formal statements: verbatim

Every definition, theorem, proposition, lemma, corollary, named formula, and remark that the book sets off with a label is recorded word for word as it appears, with the maths transcribed in LaTeX (`$...$` inline, `$$...$$` display), from the page image.

```
- definition: <Name> — "<verbatim statement>"
- theorem: <Name> — "<verbatim statement>" [proof included, <approach>]
- theorem: <Name> — "<verbatim statement>" [no proof in text]
- remark (labelled, verbatim): "<verbatim remark>"
- formula: <name> — "$$...$$"
```

Rules:
- **Name.** Use the book's name for the result if it has one ("Squeeze Theorem"); otherwise a short descriptive label of your own saying what it is about ("Local boundedness of a function with a finite limit"). Never the book's number.
- **No numbering anywhere.** Not in the name, not in the statement, not in your headings. If a statement refers to another result by number ("by Theorem 2.3", "see Definition 1.4.2"), replace the reference in place with the **name** of that result, in square brackets if you are supplying the name yourself ("by the Mean Value Theorem", "by [the limit result for rational functions]"). If the referenced result lies outside your pages, view the page where it is stated only to learn its name, and record nothing else from it. A reference to an exercise becomes "[an exercise]".
- **Typos stay.** Copy the statement exactly, typos and all. The writer decides what to fix and reports it.
- **Only the statement is verbatim.** Not the sentences around it, not the proof, not the discussion.
- **A result stated and proved inside something labelled "Example"** is still a result: record it as a theorem, verbatim, with its proof marker, and also under Examples.
- **Unlabelled remarks** made in passing (a fact noted in a sentence of prose) are recorded by name only: `- remark: changing a function at one point does not change its limit`.

### Proof markers

Every theorem, proposition, lemma and corollary carries one of:
- `[proof included, <approach>]` when the book gives a proof;
- `[no proof in text]` when it does not. A proof left to the reader or to an exercise counts as no proof. A proof that is only a pointer to an earlier result is `[proof included, by appeal to <name of that result>]`.
- Partial proofs say exactly which parts are proved: `[proof included for parts 1–2, via the Limit Laws; parts 3–4 left to exercises]`, `[proof included for the maximum, ...; minimum left to an exercise]`, `[proof included for c = 1, ...; general c left to an exercise]`.

**The approach** is a bird's-eye description of the proof's overall methodology, so that the writer, producing an original proof, still proves the theorem the way the book does. It is one clause: the paradigm, not the steps. Good: "by contradiction", "direct epsilon-delta", "by the Squeeze Theorem after a geometric area comparison", "by the Completeness Axiom applied to the supremum of a set, then contradiction", "by chaining the epsilon-delta definitions of the two functions", "by induction on n", "via the angle-sum identity and the limits of sine and cosine at zero". Bad, and never allowed: the choice of delta or epsilon, any inequality, any intermediate claim, the order of the steps, any sentence from the proof. Test: if your approach note mentions a specific quantity, inequality or formula from the proof, cut it back until it could describe the proof of some other theorem too.

### Explanation coverage

Under `### Explanation coverage`, one entry per concept, definition, theorem or idea, stating only how much explanatory text the book gave it:

```
- coverage: <concept name> — extensive | moderate | brief | none (statement only)
```

Never, under any circumstances, include a sample, a quotation or a paraphrase of the explanation, nor say what it says, how it argues, what analogy or picture it uses. The level is the whole entry.

### Examples

Under `### Examples`, one entry per concept that received a worked example or walkthrough, in exactly this shape:

```
- example: <concept> received an example showing <problem type / setup / scenario nature>
```

Add "(several)" if more than one example of that type was given. Never name individual examples, never list them one by one, never give their functions, numbers, data, steps or solutions. "showing a limit of a bounded oscillating factor times a power" is right; the actual function is not.

### Figures

Under `### Figures`, one entry per graph, diagram, table of values or picture that carries content, noting what it depicts in enough detail that it could be reproduced: what is plotted, the axes and their ranges or ticks, key features (intercepts, asymptotes, open and filled dots, shaded regions, labelled points, arrows), and which concept it accompanies. Describe the mathematics shown, not the book's surrounding text or its styling. A purely decorative image gets no entry.

### Everything else: names only

Methods, techniques, cautions and unlabelled remarks are recorded by name, one bullet each, where they occur:

```
- method: multiplying by the conjugate for differences involving square roots
- caution: the limit laws require the component limits to exist
```

Rules for these bullets:
- A name or a short identifying label of a few words. Never the statement, a formula, a worked solution, or an explanation.
- The source's intuition, analogies, motivation, pictures-in-words and "idea of the proof" comments are its explanation: they get no bullet (they are reflected only in the coverage level).
- Be unambiguous: a mathematician reading the bullet must know exactly which technique is meant. Add a qualifier when needed.
- Leave out logistics, history asides, digressions, repetition, and exercise sets unless your task says otherwise.
- Miss nothing: every method, caution and passing remark in your pages gets a bullet.

## Before you finish

1. Go through your pages once more against the file and add anything missing. Check every verbatim statement against the page image character by character.
2. Reread the file against the rules: numbers replaced by names, proof markers on every result, approach notes cut to a paradigm, coverage entries carrying only a level, example entries carrying only a type, nothing from the book's explanations anywhere.
3. Delete your temp directory of page images.
4. Reply with a content-free recap only, in the form your task specifies: counts of what you recorded, the pages covered, and anything that could not be done or that the main session should decide. No statement, name of a result, quotation, paraphrase, or description of the material may appear in your reply.
