# Dev Preview & Visual-Diff Protocol

Canonical workflow for `fluid-theme-clone` and `fluid-theme-refine`: spin the theme up locally with the fluid CLI, capture matched screenshots of the **live source** and the **localhost build** at desktop / tablet / mobile, walk the page section-by-section, and let the agent classify findings as auto-fix vs flag-for-user.

This document is the single source of truth. Both clone and refine reference it.

---

## Prerequisites

Required before any visual-diff round:

| Tool | Why | Install |
|------|-----|---------|
| Node.js ≥ 18 | Runtime for fluid CLI and Playwright | `brew install node` (macOS) or [nodejs.org](https://nodejs.org) |
| `@fluid-app/fluid-cli` + `@fluid-app/fluid-cli-theme-dev` | The CLI and the `fluid theme *` plugin | `npm install -g @fluid-app/fluid-cli @fluid-app/fluid-cli-theme-dev` |
| Playwright + Chromium | Headless browser for paired screenshots | `npm install -g playwright && npx playwright install chromium` |
| Authenticated fluid profile | `fluid theme dev` proxies to the live company storefront — auth is mandatory | `fluid login` (then optionally `fluid switch <Company>`) |
| A theme directory | `THEME_DIR` with at least one of `templates/`, `assets/`, `config/`, ideally `.fluid-theme.json` | `fluid theme pull` or `fluid theme init` |

See `~/.agents/skills/fluid-theme-cli/SKILL.md` for the full CLI reference (auth model, workspace mode, push/pull semantics).

---

## Preflight check

Run this before each visual-diff round. If anything is missing, **warn the user with the exact install command and ask permission before installing.** Never install silently.

```bash
# 1. Node
node --version

# 2. fluid CLI core
which fluid && fluid --version

# 3. theme-dev plugin (must list `theme` as a subcommand)
fluid theme --help 2>&1 | head -3

# 4. Auth — should print active profile and company
fluid whoami

# 5. Playwright (resolved from any global or local install)
node -e "console.log(require.resolve('playwright/package.json'))" 2>&1

# 6. Chromium browser binary present
node -e "const {chromium}=require('playwright'); chromium.executablePath() && console.log('OK')" 2>&1
```

Print a tidy preflight summary:

```
[Preflight] Node:        OK v22.5.0
[Preflight] fluid CLI:   OK v0.4.2
[Preflight] theme-dev:   OK plugin discovered
[Preflight] auth:        OK Acme Co (chey@acme.co)
[Preflight] Playwright:  MISSING
[Preflight] Chromium:    MISSING
```

If anything reports `MISSING`, surface the install plan and wait for explicit user approval:

```
The visual-diff workflow needs Playwright. To install:

  npm install -g playwright
  npx playwright install chromium

Run these now? (yes / no / let me handle it)
```

Only run installs when the user says yes. If the user opts out, fall back to a single full-page comparison via the existing browser-screenshot tooling and note the missing capability in the final report — never silently skip the visual check without telling the user.

If `fluid whoami` errors, the fix is `fluid login` — not retrying. If `fluid theme --help` says "unknown command," the plugin isn't installed: `npm install -g @fluid-app/fluid-cli-theme-dev`.

---

## Start the dev server

In `THEME_DIR`:

```bash
fluid theme dev --port 9292 &
```

What happens:

- CLI finds or creates a per-machine Development theme (cached as `plugins["theme-dev"].devThemeId` in `~/.fluid/config.json`)
- Initial sync uploads every local file to that dev theme
- Local Node HTTP server binds `127.0.0.1:9292` (override with `--port` if taken)
- Storefront proxies `<company>.fluid.app` but renders local theme files
- Filesystem watcher hot-reloads on save (full-page reload — no section hot-swap)

**Do not pass `--navigate`.** That opens a real browser tab; Playwright drives its own browser.

Wait for the "Server ready" message before moving on (or poll `curl -sS -o /dev/null -w "%{http_code}" http://127.0.0.1:9292/` until it returns `200`).

For specific routes, mirror live-site paths: `/` → `/`, `/products/<handle>` → `/products/<handle>`, `/pages/<slug>` → `/pages/<slug>`. The proxy renders against real storefront data.

When done: `Ctrl-C` (or `kill <pid>` if backgrounded — capture the PID when starting).

---

## The diff script

Save as `tools/visual-diff.mjs` next to `THEME_DIR`. ESM Node, requires Playwright resolvable from the current cwd:

```javascript
// node tools/visual-diff.mjs <SOURCE_URL> <LOCAL_URL> [--label=home] [--out=./diff/home]
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
import { argv, exit } from 'node:process';

const args = argv.slice(2);
const [SOURCE_URL, LOCAL_URL] = args;
if (!SOURCE_URL || !LOCAL_URL) {
  console.error('Usage: node visual-diff.mjs <SOURCE_URL> <LOCAL_URL> [--label=...] [--out=...]');
  exit(1);
}
const LABEL = (args.find(a => a.startsWith('--label=')) || '').split('=')[1] || 'page';
const OUT   = (args.find(a => a.startsWith('--out=')) || '').split('=')[1] || `./diff/${LABEL}`;

const BREAKPOINTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'tablet',  width: 768,  height: 1024 },
  { name: 'mobile',  width: 390,  height: 844 },
];

// Strip overlays, popups, cookie banners, and accessibility widgets that
// would otherwise hide content. Add site-specific selectors here as discovered.
const KILL_OVERLAYS = `(() => {
  const sels = [
    '[data-acsb-custom-trigger]','.acsb-trigger','.acsb-widget','.acsb-overlay',
    '[class*="cookie"]','[id*="cookie"]',
    '[class*="newsletter"][class*="popup"]','[id*="newsletter-popup"]',
    '[class*="modal"]:not([class*="modal-content"])',
    '[role="dialog"]'
  ];
  for (const s of sels) document.querySelectorAll(s).forEach(e => e.remove());
  document.documentElement.style.scrollBehavior = 'auto';
  // Pause CSS animations so screenshots are deterministic.
  const css = document.createElement('style');
  css.textContent = '*, *::before, *::after { animation-duration: 0s !important; transition-duration: 0s !important; }';
  document.head.appendChild(css);
})();`;

mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch();

for (const bp of BREAKPOINTS) {
  const ctx = await browser.newContext({
    viewport: { width: bp.width, height: bp.height },
    deviceScaleFactor: 1,
    reducedMotion: 'reduce',
  });

  for (const [side, url] of [['source', SOURCE_URL], ['built', LOCAL_URL]]) {
    const page = await ctx.newPage();
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
    } catch (e) {
      console.warn(`[${bp.name}/${side}] networkidle timed out, continuing: ${e.message}`);
    }
    await page.evaluate(KILL_OVERLAYS);
    // Trigger lazy-loaded images: scroll once to the bottom, then back up.
    await page.evaluate(async () => {
      await new Promise(r => {
        let y = 0; const step = window.innerHeight;
        const id = setInterval(() => {
          window.scrollTo(0, y); y += step;
          if (y >= document.documentElement.scrollHeight) { clearInterval(id); r(); }
        }, 80);
      });
      window.scrollTo(0, 0);
    });
    await page.waitForTimeout(800);

    // 1. Full-page reference shot
    await page.screenshot({
      path: `${OUT}/${LABEL}-${bp.name}-${side}-full.png`,
      fullPage: true,
    });

    // 2. Section-by-section: scroll one viewport at a time
    const total = await page.evaluate(() => document.documentElement.scrollHeight);
    let y = 0; let i = 1;
    while (y < total) {
      await page.evaluate((v) => window.scrollTo(0, v), y);
      await page.waitForTimeout(200);
      const remaining = total - y;
      await page.screenshot({
        path: `${OUT}/${LABEL}-${bp.name}-${side}-sec${String(i).padStart(2,'0')}.png`,
        clip: { x: 0, y: 0, width: bp.width, height: Math.min(bp.height, remaining) },
      });
      y += bp.height; i++;
    }

    await page.close();
  }
  await ctx.close();
}
await browser.close();
console.log(`Wrote ${OUT}/`);
```

Run it:

```bash
node tools/visual-diff.mjs https://yellowbirdfoods.com http://127.0.0.1:9292/ --label=home
```

Output layout:

```
diff/home/
  home-desktop-source-full.png       home-desktop-built-full.png
  home-desktop-source-sec01.png      home-desktop-built-sec01.png   ← hero
  home-desktop-source-sec02.png      home-desktop-built-sec02.png   ← below hero
  ... (continues until end of page)
  home-tablet-source-full.png        home-tablet-built-full.png
  home-tablet-source-sec01.png       ...
  home-mobile-source-full.png        ...
```

Same `sec##` index on both sides represents the same scroll position at that breakpoint, so pairs line up.

---

## Reading the output (the agent loop)

For every breakpoint, walk the section pairs in order. Use the `Read` tool on each PNG — Claude reads images directly, no diff library needed.

**Read order (one breakpoint at a time):**

1. `home-desktop-source-full.png` + `home-desktop-built-full.png` — overall layout + section count match
2. Then each `sec01` / `sec02` / … pair in order
3. After desktop is exhausted, advance to tablet, then mobile

For each pair, classify findings:

### Auto-fix (apply directly without prompting)

| Finding | Why it's safe to auto-fix |
|--------|---------------------------|
| Background color off (theme token wrong, e.g. primary vs secondary) | Theme tokens are the source of truth; fix is a 1-line change |
| Padding / margin / gap numerically off | Numeric spacing is unambiguous |
| Font-size, line-height, letter-spacing wrong | Same — clear numeric mismatch |
| Border-radius / border-width wrong | Numeric, low-risk |
| Box-shadow missing or wrong | Pure visual property |
| Wrong text content (heading copy, button label, eyebrow) | Source is the canonical content |
| Missing or wrong icon size | Numeric or asset-swap with clear intent |
| Image `object-fit` / `object-position` off | Numeric or enumerated |

### Flag for user (do not fix without explicit confirmation)

| Finding | Why it needs judgement |
|--------|------------------------|
| Different layout structure (rows vs columns, reordered sections) | Restructuring may not match the canonical Section Shell + block pattern; needs design call |
| Image asset swap (source uses a different photo) | DAM upload may be needed; brand call on which asset to use |
| Custom font unavailable in fluid `font_picker` | Substitution choice |
| Whole section conceptually different / missing | May indicate a missing canonical section that needs to be added |
| Animation / interaction behavior differs | Often involves JS — riskier; likely needs a different recipe |
| Source uses a third-party widget (live chat, reviews) we don't replicate | Tradeoff call — substitute with native Fluid block or omit |
| Layout tradeoff (text wraps differently, button stacks earlier) | Often a typographic call |

### Findings table (print after each round)

```
DIFF — home / desktop                               round 2
─────────────────────────────────────────────────────────────
Section  Issue                Source         Built     Action
hero     bg-color             #1B3A4B        #1C3B4C   auto-fix
hero     heading font-size    56px           48px      auto-fix
hero     hero photo           farm           placeholder  FLAG: image asset
features card border          1px solid …    none      auto-fix
testim.  layout               3-col          2-col     FLAG: layout choice
─────────────────────────────────────────────────────────────
Auto-fix queued: 3
Flagged for confirmation: 2
```

Apply the auto-fix queue to the section files in `THEME_DIR`. The `fluid theme dev` watcher uploads on save and the localhost preview hot-reloads. Re-run `visual-diff.mjs` for the same `--label`. Loop until either:

- All findings resolved
- Only flagged items remain — present the list to the user and wait

After 3 rounds with no convergence on a section, freeze that section, document remaining deltas in a comment in the section's Liquid file, and move on. Never silently abandon — log everything in the final report.

---

## Common breakage and recovery

| Symptom | Cause / fix |
|--------|-------------|
| `EADDRINUSE` on `fluid theme dev` | Port 9292 taken. `fluid theme dev --port 9393` |
| `fluid theme: unknown command` | Plugin missing. `npm install -g @fluid-app/fluid-cli-theme-dev` |
| `Auth required` | `fluid login` (and `fluid switch <Company>` if wrong account) |
| Playwright "Executable doesn't exist" | `npx playwright install chromium` |
| Localhost screenshots are blank | Watcher hasn't synced yet — wait for the initial upload to finish, or hard-refresh (`page.reload({ waitUntil: 'networkidle' })`) |
| Source pages have a cookie banner that won't dismiss | Add the selector to `KILL_OVERLAYS` and rerun |
| Fonts differ between source and built (web fonts vs system fallbacks) | Wait longer after `goto` (`waitForTimeout(2000)`); ensure `fluid theme dev` has loaded the merchant's font selections |
| Section count differs between source and built | Don't auto-fix — that's a structural finding, flag for the user |

---

## When NOT to run the visual diff

- The user asked for a structural-only refine (Phase 0 audit) — visual diff comes later
- The change is documentation / schema-only with no rendering impact
- The user explicitly opted out of the visual check (note in the final report)

---

## Quick reference

```bash
# Preflight
node --version && fluid --version && fluid whoami
node -e "console.log(require.resolve('playwright/package.json'))"

# Start dev preview
cd <THEME_DIR> && fluid theme dev --port 9292 &

# Wait for ready
until curl -sf -o /dev/null http://127.0.0.1:9292/; do sleep 1; done

# Run the diff
node tools/visual-diff.mjs <SOURCE_URL> http://127.0.0.1:9292/<route> --label=<page>

# Stop the dev server when done
kill %1   # or Ctrl-C in the foreground
```
