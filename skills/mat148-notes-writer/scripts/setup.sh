#!/usr/bin/env bash
# Idempotent install of the typesetting toolchain (KaTeX + Playwright Chromium)
# into a per-user cache. Prints one line on stdout: the KaTeX base URL to put
# in place of KATEX_DIST in assets/template.html.
set -euo pipefail

DEPS="${MAT148_NOTES_DEPS:-$HOME/.cache/mat148-notes-writer}"
mkdir -p "$DEPS"
cd "$DEPS"
[ -f package.json ] || echo '{"private":true}' > package.json

if [ ! -f node_modules/katex/dist/katex.min.js ] || [ ! -d node_modules/playwright ]; then
  npm install --silent --no-fund --no-audit katex playwright >&2
fi

if ! node -e "process.exit(require('fs').existsSync(require('playwright').chromium.executablePath()) ? 0 : 1)"; then
  npx playwright install chromium >&2
fi

node -e "console.log(require('url').pathToFileURL(process.argv[1]).href)" "$DEPS/node_modules/katex/dist"
