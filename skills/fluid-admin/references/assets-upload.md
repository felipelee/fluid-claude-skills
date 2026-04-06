# Image & Asset Upload API

## DAM (Digital Asset Management)

All images in Fluid must go through the DAM. Never hotlink external URLs directly in product/brand/theme fields.

### Upload Asset

```
POST https://upload.fluid.app/upload
Authorization: Bearer {FLUID_TOKEN}
Content-Type: multipart/form-data
```

**Option A: Upload from local file**
```bash
curl -s -X POST "https://upload.fluid.app/upload" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -F "file=@/path/to/image.jpg" \
  -F "fileName=product-hero.jpg" \
  -F "name=Product Hero Image" \
  -F "description=Main hero image for product page" \
  -F "tags=product,hero"
```

**Option B: Upload from external URL**
```bash
curl -s -X POST "https://upload.fluid.app/upload" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -F "external_asset_url=https://example.com/image.jpg" \
  -F "fileName=product-hero.jpg" \
  -F "name=Product Hero Image"
```

**Response:**
```json
{
  "asset": {
    "id": "asset-abc123",
    "code": "product-hero-abc",
    "default_variant_url": "https://ik.imagekit.io/fluid/company-name/product-hero.jpg"
  }
}
```

The `default_variant_url` is what you use in product `image_url`, brand `logo_url`, etc.

**Fields:**
- `file` — Binary file upload (mutually exclusive with `external_asset_url`)
- `external_asset_url` — Source URL to fetch from (mutually exclusive with `file`)
- `fileName` — Filename with extension (required)
- `name` — Display name in DAM
- `description` — Optional description
- `tags` — Optional comma-separated tags

**Important:** The upload endpoint is `https://upload.fluid.app/upload` — note this is NOT the company subdomain.

---

## Theme Resources

Theme files (Liquid, CSS, JS, images) are uploaded through the theme API.

### Upload Text Resource (Liquid, CSS, JSON, JS)
```
PUT /api/application_themes/:theme_id/resources
```

```json
{
  "key": "sections/hero/index.liquid",
  "content": "{% comment %} Hero section {% endcomment %}\n<div class=\"hero\">...</div>"
}
```

### Upload Binary Resource (Images)
```
PUT /api/application_themes/:theme_id/resources
```

```json
{
  "key": "assets/logo.png",
  "dam_asset": "https://ik.imagekit.io/fluid/company-name/logo.png"
}
```

For binary assets in themes, first upload to DAM, then reference the DAM URL in `dam_asset`.

**Key naming conventions:**
- `sections/{name}/index.liquid` — Section templates
- `sections/{name}/index.css` — Section styles
- `sections/{name}/index.js` — Section scripts
- `templates/{name}.liquid` — Page templates
- `layout/theme.liquid` — Main layout
- `assets/{filename}` — Static assets (images, fonts)
- `config/settings_schema.json` — Theme settings schema
- `config/settings_data.json` — Theme settings values

---

## Upload Workflow

### Product image upload
```bash
# 1. Upload to DAM
ASSET=$(curl -s -X POST "https://upload.fluid.app/upload" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -F "external_asset_url=https://example.com/product.jpg" \
  -F "fileName=product-main.jpg" \
  -F "name=Product Main Image")

IMAGE_URL=$(echo "$ASSET" | jq -r '.asset.default_variant_url')

# 2. Use in product creation
curl -s -X POST "${FLUID_URL}/api/company/v1/products" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"product\": {
      \"title\": \"New Product\",
      \"image_url\": \"${IMAGE_URL}\",
      ...
    }
  }"
```

### Bulk image upload (parallel)
```bash
# Upload up to 5-10 images concurrently
for URL in "${IMAGE_URLS[@]}"; do
  curl -s -X POST "https://upload.fluid.app/upload" \
    -H "Authorization: Bearer ${FLUID_TOKEN}" \
    -F "external_asset_url=${URL}" \
    -F "fileName=$(basename ${URL})" &
done
wait
```

**Rate limit:** 10 requests/second. For large batches, use 5-10 concurrent workers.
