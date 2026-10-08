#!/usr/bin/env node
// usage: node render.mjs notes.html out.pdf
// Renders the HTML to PDF with headless Chromium, after KaTeX has typeset the
// maths. Exits non-zero if anything failed to load or any formula failed to parse.
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [src, out] = process.argv.slice(2);
if (!src || !out) {
  console.error('usage: node render.mjs notes.html out.pdf');
  process.exit(2);
}

const deps = process.env.CALC_NOTES_DEPS || path.join(os.homedir(), '.cache', 'calc-notes-writer');
let chromium;
try {
  ({ chromium } = createRequire(path.join(deps, 'package.json'))('playwright'));
} catch {
  console.error(`Playwright not found in ${deps}. Run scripts/setup.sh first.`);
  process.exit(1);
}

const problems = [];
const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  page.on('pageerror', (e) => problems.push(`script error: ${e.message}`));
  page.on('requestfailed', (r) => problems.push(`failed to load: ${r.url()}`));

  await page.goto(pathToFileURL(path.resolve(src)).href);
  try {
    await page.waitForFunction('window.__mathDone === true', null, { timeout: 30000 });
  } catch {
    problems.push('maths never rendered: KaTeX did not load (check the KATEX_DIST paths in <head>)');
  }
  await page.evaluate(() => document.fonts.ready);

  // With throwOnError:false, KaTeX leaves unparseable formulas as red raw TeX.
  const badMath = await page.$$eval('.katex-error', (els) => els.map((e) => e.textContent));
  for (const tex of badMath) problems.push(`formula failed to parse: ${tex}`);

  // Delimiters auto-render could not pair up (usually unbalanced braces) stay as raw text.
  const rawMath = await page.evaluate(() => {
    const hits = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      if (n.parentElement.closest('.katex, script, style, pre, code')) continue;
      if (/\$|\\\(|\\\[/.test(n.textContent)) hits.push(n.textContent.trim().slice(0, 120));
    }
    return hits;
  });
  for (const text of rawMath) problems.push(`unrendered maths (unbalanced braces or delimiters?): ${text}`);

  await page.pdf({
    path: out,
    preferCSSPageSize: true,
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate:
      '<div style="font-size:9px;width:100%;text-align:center;color:#777"><span class="pageNumber"></span></div>',
  });
} finally {
  await browser.close();
}

const pages = (readFileSync(out, 'latin1').match(/\/Type\s*\/Page(?![a-zA-Z])/g) || []).length;
console.log(`wrote ${out}${pages ? ` (${pages} page${pages === 1 ? '' : 's'})` : ''}`);

if (problems.length) {
  console.error(`\n${problems.length} problem(s) to fix before delivering:`);
  for (const p of problems) console.error(`  - ${p}`);
  process.exit(1);
}
