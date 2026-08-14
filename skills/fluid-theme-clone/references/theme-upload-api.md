# Theme Upload API Reference

Push locally built theme files to the Fluid theme system.

> **⚠️ Never publish without being asked.** Uploading files and publishing a theme are two
> different operations. Uploading resources is safe and reversible; publishing swaps the
> live storefront. Build and push into an **unpublished** theme, hand the user a preview,
> and only publish when they explicitly say so. See [Publishing](#publishing--explicit-approval-only).

## Step 1: Create or Find the Application Theme

### Create a new theme — always `draft`

```
POST /api/application_themes
Authorization: Bearer <FLUID_TOKEN>
Content-Type: application/json

{
  "application_theme": {
    "name": "My Clone Theme",
    "description": "Cloned from yellowbirdfoods.com",
    "status": "draft"
  }
}
```

Response: `{ "application_theme": { "id": 55697, "name": "My Clone Theme", ... } }`

Save the `id` — this is your `themeId` for all subsequent uploads.

`status: "draft"` creates the theme **unpublished** — it exists, you can push to it and preview
it, and it is not serving the storefront. This is the correct default for every clone, rebuild,
or experiment. `status: "active"` makes the theme visible on the storefront; do not set it
unless the user has asked you to take the theme live.

### Find an existing theme

```
GET /api/application_themes
Authorization: Bearer <FLUID_TOKEN>
```

Returns `{ "application_themes": [...] }`. Find the one you want and use its `id`.

### Working on a theme that is already live

Do **not** push edits straight into the published theme — every `PUT` lands on the live
storefront immediately. Clone it for development first and work on the copy:

```
POST /api/application_themes/{id}/clone_for_development
Authorization: Bearer <FLUID_TOKEN>
```

This is the same operation `fluid theme dev` performs. It returns a development theme that
preserves the source theme's content and DAM/ImageKit references, so you get an isolated,
unpublished copy without reseeding assets.

## Step 2: Upload Theme Resources

Each file in the theme becomes a resource. The `key` is the file path relative to the theme root.

### Text files (.liquid, .css, .js, .json, .html, .txt)

```
PUT /api/application_themes/{themeId}/resources
Authorization: Bearer <FLUID_TOKEN>
Content-Type: application/json

{
  "key": "sections/exact-hiya-hero/index.liquid",
  "content": "<style>\n  .eh-hero { ... }\n</style>\n\n<section class=\"eh-hero\" {{ section.fluid_attributes }}>\n  ...\n</section>\n\n{% schema %}\n...\n{% endschema %}"
}
```

The `key` maps directly to the theme directory structure:

| File path | Key |
|-----------|-----|
| `layouts/theme.liquid` | `layouts/theme.liquid` |
| `home_page/default/index.liquid` | `home_page/default/index.liquid` |
| `page/about/index.liquid` | `page/about/index.liquid` |
| `product/default/index.liquid` | `product/default/index.liquid` |
| `sections/exact-hiya-hero/index.liquid` | `sections/exact-hiya-hero/index.liquid` |
| `config/settings_schema.json` | `config/settings_schema.json` |
| `assets/product.js` | `assets/product.js` |

### Binary files (.png, .jpg, .woff2, .svg, etc.)

Binary files must be uploaded to DAM first, then referenced:

```bash
# 1. Upload binary to DAM
curl -s -X POST https://upload.fluid.app/upload \
  -H "Authorization: Bearer <FLUID_TOKEN>" \
  -F "file=@/tmp/theme/assets/logo.png" \
  -F "fileName=logo.png" \
  -F "name=Theme Logo"
# Returns: { "asset": { "default_variant_url": "https://ik.imagekit.io/fluid/..." } }

# 2. Register as theme resource
curl -s -X PUT "https://<FLUID_URL>/api/application_themes/{themeId}/resources" \
  -H "Authorization: Bearer <FLUID_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{ "key": "assets/logo.png", "dam_asset": "https://ik.imagekit.io/fluid/..." }'
```

## Step 3: Upload All Files

Process every file in the theme directory:

```python
import os, requests, json

FLUID_URL = "https://companyname.fluid.app"
FLUID_TOKEN = "PT-xxx"
THEME_ID = 55697
THEME_DIR = "/tmp/fluid-theme-yellowbirdfoods"

TEXT_EXTENSIONS = {'.liquid', '.css', '.js', '.json', '.html', '.txt', '.svg'}

headers = {
    "Authorization": f"Bearer {FLUID_TOKEN}",
    "Content-Type": "application/json"
}

for root, dirs, files in os.walk(THEME_DIR):
    for fname in files:
        if fname.startswith('.'):
            continue
        filepath = os.path.join(root, fname)
        key = os.path.relpath(filepath, THEME_DIR)
        ext = os.path.splitext(fname)[1].lower()

        if ext in TEXT_EXTENSIONS:
            with open(filepath, 'r') as f:
                content = f.read()
            resp = requests.put(
                f"{FLUID_URL}/api/application_themes/{THEME_ID}/resources",
                headers=headers,
                json={"key": key, "content": content}
            )
            status = "OK" if resp.ok else f"FAILED {resp.status_code}"
            print(f"[Upload] {key} — {status}")
        else:
            # Binary: upload to DAM first
            with open(filepath, 'rb') as f:
                dam_resp = requests.post(
                    "https://upload.fluid.app/upload",
                    headers={"Authorization": f"Bearer {FLUID_TOKEN}"},
                    files={"file": (fname, f)},
                    data={"fileName": fname, "name": fname}
                )
            dam_url = dam_resp.json().get("asset", {}).get("default_variant_url", "")
            if dam_url:
                resp = requests.put(
                    f"{FLUID_URL}/api/application_themes/{THEME_ID}/resources",
                    headers=headers,
                    json={"key": key, "dam_asset": dam_url}
                )
                status = "OK" if resp.ok else f"FAILED {resp.status_code}"
                print(f"[Upload] {key} (binary via DAM) — {status}")
            else:
                print(f"[Upload] {key} — DAM UPLOAD FAILED")
```

## Publishing — explicit approval only

Publishing is a **separate endpoint**, never a side effect of uploading:

```
POST /api/application_themes/{id}/publish
Authorization: Bearer <FLUID_TOKEN>
```

(The CLI equivalent is `fluid theme push --publish`. Plain `fluid theme push` uploads without
publishing — that is the behavior to mirror.)

**Rules:**

1. **Never call `/publish` on your own.** Not at the end of a build, not "to check it works,"
   not because the theme looks finished. It swaps the live storefront for every visitor.
2. **Default to unpublished.** Create with `status: "draft"`; clone live themes with
   `clone_for_development` before editing.
3. **Finish by handing over a preview, not a live site.** When the build is done, report the
   theme id and preview URL and stop. Let the user look.
4. **Publish only on an unambiguous instruction** — "publish it", "make it live", "go live".
   "Looks good" / "nice" / "ship the section" is not approval to publish.
5. **Say what you did.** After any publish, state plainly that the live storefront changed.

### Handing over a preview

**Uploaded ≠ published.** Once you `PUT` the resources, the template is live *in preview* —
the code is on the server and renderable — while the storefront keeps serving the published
theme. That gap is the whole workflow: push freely, preview freely, publish only on request.

Three ways to let the user see it — give them whichever fits:

```
# Local dev server, hot reload, nothing touched remotely (best while iterating)
fluid theme dev                    # → http://127.0.0.1:9292

# Visual editor for a specific template
https://admin.fluid.app/templates/{template_id}?editor=visual&themeable_type={home_page|product}&from=themes

# Rendered storefront preview of a template
https://{company}.fluid.app/{path}?preview=true&theme_template_id={template_id}&version={n}
```

Real example: `https://p.fluid.app/home?preview=true&theme_template_id=5339803&version=22`

Three things to get right:

- **It keys on `theme_template_id`, not the theme id.** Preview the specific template you changed.
- **`version={n}` is a real Fluid parameter**, not a cache-buster — it pins the saved template
  version being rendered. Bump it as you push new versions. It busts the preview cache as a
  side effect, which is why it's the one to reach for.
- **`{path}` is a storefront route** — `/home`, `/home/products/{slug}` — not the template id.

If you're navigating the **editor iframe** (`admin.fluid.app/templates/...`) rather than the
storefront preview, that surface caches hard and has no `version` param. Append a throwaway
`&cb={unique}` there, changing the value on every navigation, or you'll stare at a stale render
convinced the push failed. See playbook gotcha #28.

## Notes

- `PUT` is idempotent — uploading the same key twice overwrites the previous version
- Upload order doesn't matter — Fluid resolves references at render time
- Uploading resources never publishes; `status` and `/publish` control storefront visibility
- Config files (`settings_schema.json`, `settings_data.json`) are uploaded the same way as any text resource
