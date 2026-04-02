# Batch Upload Script

## Copy-Paste Ready Script

Copy this script, update the token and image list, and run.

```bash
#!/bin/bash
# ============================================================
# Fluid DAM Batch Upload Script
# Uses https://upload.fluid.app for single-step uploads
# Usage: chmod +x upload.sh && bash upload.sh
# ============================================================

FLUID_TOKEN="<YOUR_FLUID_TOKEN>"
RESULTS_FILE="/tmp/dam_upload_results.txt"
> "$RESULTS_FILE"

upload_image() {
  local URL="$1" NAME="$2"
  echo "--- Uploading: $NAME ---"

  local RESP=$(curl -s -X POST https://upload.fluid.app/upload \
    -H "Authorization: Bearer $FLUID_TOKEN" \
    -F "external_asset_url=$URL" \
    -F "name=$NAME" \
    -F "description=Uploaded from source")

  local DAM=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('asset',{}).get('default_variant_url',''))" 2>/dev/null)
  local CODE=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('asset',{}).get('code',''))" 2>/dev/null)

  if [ -n "$DAM" ] && [ "$DAM" != "" ] && [ "$DAM" != "None" ]; then
    echo "SUCCESS [$CODE]: $DAM"
    echo "$NAME|$DAM" >> "$RESULTS_FILE"
  else
    local ERR=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('error','Unknown error'))" 2>/dev/null)
    echo "FAILED: $ERR"
    echo "$NAME|FAILED: $ERR" >> "$RESULTS_FILE"
    return 1
  fi
}

# ============================================================
# ADD YOUR IMAGES HERE
# Format: upload_image "SOURCE_URL" "display-name"
# ============================================================

upload_image "https://example.com/cdn/hero.jpg" "hero-desktop"
upload_image "https://example.com/cdn/team-photo.png" "team-photo"
upload_image "https://example.com/cdn/icon-star.svg" "icon-star"
# ... add all images ...

echo ""
echo "=== ALL UPLOADS COMPLETE ==="
cat "$RESULTS_FILE"
echo ""
echo "Total: $(wc -l < "$RESULTS_FILE") images"
```

## Running the Script

```bash
chmod +x /tmp/upload.sh
bash /tmp/upload.sh
```

## Results Format

The results file (`/tmp/dam_upload_results.txt`) contains lines like:

```
hero-desktop|https://ik.imagekit.io/fluid/980243104/hero-desktop_abc123.jpg
team-photo|https://ik.imagekit.io/fluid/980243104/team-photo_def456.png
icon-star|https://ik.imagekit.io/fluid/980243104/icon-star_ghi789.svg
```

Use the URLs after the `|` in your section templates.

## Upload API Fields

| Field | Required | Description |
|-------|----------|-------------|
| `file` | * | The file to upload (required if no `external_asset_url`) |
| `external_asset_url` | * | URL to fetch the file from (required if no `file`) |
| `fileName` | ** | Filename with extension (required with `file`, auto-detected from URL) |
| `name` | No | Display name for the DAM asset |
| `description` | No | Asset description |
| `tags` | No | Comma-separated tags (e.g. `"en,product,featured"`) |
| `useUniqueFileName` | No | `true` (default) or `false` |
| `create_media` | No | `true` to also create a Fluid Media resource (for videos) |

## Uploading a Local File

```bash
curl -s -X POST https://upload.fluid.app/upload \
  -H "Authorization: Bearer <FLUID_TOKEN>" \
  -F "file=@/tmp/my-image.png" \
  -F "fileName=my-image.png" \
  -F "name=My Image" \
  -F "description=Hero background image"
```
