# Theme Upload API Reference

Push locally built theme files to the Fluid theme system.

## Step 1: Create or Find the Application Theme

### Create a new theme

```
POST /api/application_themes
Authorization: Bearer <FLUID_TOKEN>
Content-Type: application/json

{
  "application_theme": {
    "name": "My Clone Theme",
    "description": "Cloned from yellowbirdfoods.com",
    "status": "active"
  }
}
```

Response: `{ "application_theme": { "id": 55697, "name": "My Clone Theme", ... } }`

Save the `id` — this is your `themeId` for all subsequent uploads.

### Find an existing theme

```
GET /api/application_themes
Authorization: Bearer <FLUID_TOKEN>
```

Returns `{ "application_themes": [...] }`. Find the one you want and use its `id`.

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

## Notes

- `PUT` is idempotent — uploading the same key twice overwrites the previous version
- Upload order doesn't matter — Fluid resolves references at render time
- The theme must have `status: "active"` to be visible on the storefront
- Config files (`settings_schema.json`, `settings_data.json`) are uploaded the same way as any text resource
