# The `fluid theme` CLI

The official theme toolchain, maintained by the Fluid platform team and shipped on npm as
[`@fluid-app/fluid-cli-theme-dev`](https://www.npmjs.com/package/@fluid-app/fluid-cli-theme-dev).
It gives you a local dev server with hot reload, a schema validator, and safe push/pull — all
things our raw-API workflow doesn't have on its own.

Use it whenever you're working against a real theme repo on disk. It does not replace the
direct API calls in [theme-upload-api.md](theme-upload-api.md) — those still matter when you're
generating files programmatically — but `lint` and `dev` are strictly better than eyeballing.

## Install

```bash
npm install -g @fluid-app/fluid-cli @fluid-app/fluid-cli-theme-dev
```

```bash
fluid login
```

The theme plugin depends on the core CLI; both are required. Node >= 18.

## Commands

| Command | What it does |
|---------|--------------|
| `fluid theme init [name]` | Scaffold a new theme from the base template |
| `fluid theme dev` | Local dev server, hot reload, proxied to `{company}.fluid.app` |
| `fluid theme lint --json` | Read-only schema validator — **run this constantly** |
| `fluid theme pull` | Download a remote theme to disk |
| `fluid theme push` | Upload local files to a remote theme (does **not** publish) |
| `fluid theme navigate` | Pick a route and open it in the browser |
| `fluid theme skills install` | Drop the platform team's bundled theme skills into `.agents/skills/` |

## `fluid theme lint --json` — the self-check

This is the same validation the editor runs and the same one `push` runs before upload, so
**anything it rejects will block a push.** Treat every error as a blocker.

```bash
fluid theme lint --json
```

**Parse the JSON — don't eyeball the text output.** The payload gives you `ok`, `errors`,
`warnings`, `filesChecked`, a `files[]` array with per-file diagnostics, and `validSettingTypes`
(the authoritative list of every legal setting `type:`).

```bash
fluid theme lint --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['ok'], d['errors'], d['warnings'])"
```

Run it after **every** section you touch, fix what it flags, and run it again until that file is
clean before moving to the next one. What it enforces:

- Schema JSON parses; no duplicate `blocks` keys
- Every setting has a required, unique, non-empty `id` — except `header`, which has none
- Every setting `type:` is in `validSettingTypes` (see [schema-settings-reference.md](schema-settings-reference.md))
- Every block has a `type`; `name` too unless it's `@app`, `@theme`, or a named-block reference
- Block `settings` is an array `[]`, never an object `{}`
- Every `{% section 'name' %}` resolves to a `sections/name/index.liquid` on disk

Section files use `"blocks": []` (array); page templates use `"blocks": {}` (object). Wrong
shape is an error.

## `fluid theme dev` — preview without publishing

```bash
fluid theme dev
```

Serves on `http://127.0.0.1:9292` with hot reload. It creates (or reuses) an **isolated
development theme** — a server-side reference clone of the pulled source that preserves theme
content and DAM/ImageKit references, so startup doesn't reseed every asset. Nothing you do here
touches the live storefront.

This is the best thing to hand a user who wants to see work in progress.

| Flag | Default | Purpose |
|------|---------|---------|
| `--host <host>` | `127.0.0.1` | Local host |
| `--port <port>` | `9292` | Local port |
| `-t, --theme <name-or-id>` | auto | Use a specific theme instead of the dev theme |
| `--live-reload <mode>` | `full-page` | `full-page` or `off` |
| `--navigate` | off | Open the route navigator after start |
| `--root <path>` | `.` | Theme root |

## `push` and `pull` — baselines, not blind overwrites

**`push` uploads; it does not publish.** Publishing is opt-in via `--publish`, and per our
[publishing rule](theme-upload-api.md#publishing--explicit-approval-only) you never pass that
flag without an explicit instruction from the user.

```bash
fluid theme push                     # interactive theme selection
fluid theme push --theme "My Theme"  # by name (or id)
fluid theme push --unpublished       # create a new draft theme and push to it
fluid theme push --nodelete          # keep remote files absent locally
fluid theme push --auto-baseline     # adopt the server's current state as baseline, then push diffs
```

Pushing into an existing theme **requires a local baseline** (recorded by `pull`). Without one,
push refuses rather than silently clobbering the server — that refusal is a safety feature, not
a bug to work around. `--auto-baseline` records the server's current state as the baseline, then
pushes only what differs locally; it never deletes server-only files.

Files containing unresolved `<<<<<<<` / `=======` / `>>>>>>>` conflict markers are never
uploaded. Push lists them and exits.

```bash
fluid theme pull                     # interactive
fluid theme pull --theme "My Theme"
fluid theme pull --resolve remote    # or `local` — auto-resolve instead of writing markers
```

By default, edits that changed both locally and remotely come back with git-style conflict
markers for you to resolve. Before any auto-resolution overwrites local content, the pre-merge
tree is committed to the theme's shadow history (`.fluid-theme/repo`), so the discarded side
stays restorable.

## Theme directory shape

A valid theme root has at least one of `templates/`, `assets/`, `config/`, or `.fluid-assets.json`.
Use `.fluidignore` (same syntax as `.gitignore`) to exclude files from syncing.

### Remote binary assets — `.fluid-assets.json`

`pull` does **not** download binaries (images, fonts, video, PDFs). It records their ImageKit URL
references in `.fluid-assets.json` and leaves the bytes remote. The CLI reads that manifest when
starting a dev theme or pushing elsewhere, so existing `asset_url` calls keep resolving.

Add a new binary during `fluid theme dev` and the CLI uploads it once, records the reference, and
removes the local bytes. A later `push` writes that same URL to the target theme with no second
upload.

Two rules:

- **Binaries must be direct children of `assets/`** — `assets/logo.png`, never `assets/img/logo.png`.
  The theme resource API doesn't support nested asset directories.
- **Never add `.fluid-assets.json` to `.fluidignore`.** It's already excluded from uploads and
  file watching. Commit it with the theme source so every developer gets the same references.

## The platform team's bundled skills

```bash
fluid theme skills install              # → .agents/skills/
fluid theme skills install --dir .claude/skills
```

Ships `themes-review` (the review/fix rubric and its reference catalog),
`themes-cart-feedback` (cart operation events), and
`template-stylesheet-to-asset-migration` (the co-located-CSS migration). These are versioned
with the CLI and are the authoritative source when they disagree with anything here — if you
hit a conflict, follow them and flag it so this skill gets updated.
