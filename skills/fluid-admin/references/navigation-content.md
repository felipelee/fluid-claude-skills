# Navigation, Pages & Policies API

## Menus

### Create Menu
```
POST /api/menus
```

```json
{
  "menu": {
    "title": "Main Menu",
    "active": true,
    "country_ids": [214],
    "menu_items_attributes": [
      {
        "title": "Shop",
        "linkable_type": "Url",
        "order": 1,
        "url": "/collections",
        "sub_menu_items_attributes": [
          {
            "title": "New Arrivals",
            "linkable_type": "Url",
            "order": 1,
            "url": "/collections/new-arrivals"
          },
          {
            "title": "Best Sellers",
            "linkable_type": "Url",
            "order": 2,
            "url": "/collections/best-sellers"
          }
        ]
      },
      {
        "title": "About",
        "linkable_type": "Url",
        "order": 2,
        "url": "/pages/about"
      },
      {
        "title": "Contact",
        "linkable_type": "Url",
        "order": 3,
        "url": "/pages/contact"
      }
    ]
  }
}
```

**Critical: `country_ids` uses the nested `country.id` from `GET /api/settings/company_countries`, NOT the top-level `id`.** This is the opposite of agreements.

**Key fields:**
- `menu_items_attributes` — Top-level nav items
- `sub_menu_items_attributes` — Dropdown/nested items under a parent
- `linkable_type` — Usually `"Url"` for custom links. Can also be `"Collection"`, `"Category"`, `"Page"`
- `order` — Integer controlling display order (1-based)
- `url` — Relative path for the link

### Update Menu
```
PUT /api/menus/:id
```

When updating a menu, you replace the entire `menu_items_attributes` array. Existing items not included will be removed.

To **add** items to an existing menu, first GET the current menu, modify the items array, then PUT back.

### List Menus
```
GET /api/menus
```

### Get Single Menu
```
GET /api/menus/:id
```

### Delete Menu
```
DELETE /api/menus/:id
```

---

## Pages

### Create Page
```
POST /api/company/v1/pages
```

```json
{
  "page": {
    "title": "About Us",
    "slug": "about",
    "publish": true,
    "source": "code",
    "html_code": "<div class=\"about-page\"><h1>About Us</h1><p>Our story...</p></div>",
    "search_engine_optimizer_attributes": {
      "title": "About Us | Acme Co",
      "description": "Learn about Acme Co and our mission."
    }
  }
}
```

**Key fields:**
- `slug` — URL path (e.g., `about` becomes `/pages/about`)
- `source` — Set to `"code"` for custom HTML content
- `html_code` — Full HTML content of the page
- `publish` — Set `true` to make visible, `false` for draft
- `search_engine_optimizer_attributes` — SEO meta title and description

### Update Page
```
PUT /api/company/v1/pages/:id
```
Same structure. Only include fields you want to change.

### List Pages
```
GET /api/company/v1/pages
```

### Delete Page
```
DELETE /api/company/v1/pages/:id
```

---

## Policies & Agreements

### Create Agreement
```
POST /api/agreements
```

```json
{
  "agreement": {
    "title": "Terms of Service",
    "description": "<p>These terms govern your use of our platform...</p>",
    "active": true,
    "show_at_checkout": true,
    "required_on_checkout": true,
    "default_checked": false,
    "required": true,
    "company_country_ids": [55938],
    "language_iso": "en"
  }
}
```

**Critical: `company_country_ids` uses the TOP-LEVEL `id` from `GET /api/settings/company_countries`, NOT the nested `country.id`.** This is the opposite of menus.

**Key fields:**
- `description` — Full HTML content of the policy
- `show_at_checkout` — Display as a checkbox at checkout
- `required_on_checkout` — Customer must check the box to proceed
- `default_checked` — Whether the checkbox starts checked
- `required` — Whether acceptance is mandatory
- `company_country_ids` — Array of country IDs this applies to
- `language_iso` — Language code (e.g., `"en"`, `"es"`)

### List Agreements
```
GET /api/agreements
```

### Update Agreement
```
PATCH /api/agreements/:id
```
Only include fields you want to change.

### Delete Agreement
```
DELETE /api/agreements/:id
```

### Clone Agreement
```
POST /api/agreements/:id/clone
```
Creates a copy of an existing agreement. Useful for creating translations.

---

## Common Patterns

### Build a complete navigation

```bash
# 1. Get current countries
COUNTRIES=$(curl -s "${FLUID_URL}/api/settings/company_countries" \
  -H "Authorization: Bearer ${FLUID_TOKEN}")
COUNTRY_ID=$(echo "$COUNTRIES" | jq '.[0].country.id')

# 2. Create main menu
curl -s -X POST "${FLUID_URL}/api/menus" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"menu\": {
      \"title\": \"Main Menu\",
      \"active\": true,
      \"country_ids\": [${COUNTRY_ID}],
      \"menu_items_attributes\": [...]
    }
  }"

# 3. Create footer menu (same pattern, different title/items)
curl -s -X POST "${FLUID_URL}/api/menus" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"menu\": {
      \"title\": \"Footer Menu\",
      \"active\": true,
      \"country_ids\": [${COUNTRY_ID}],
      \"menu_items_attributes\": [...]
    }
  }"
```

### Add a nav item to existing menu

```bash
# 1. GET current menu
MENU=$(curl -s "${FLUID_URL}/api/menus/123" \
  -H "Authorization: Bearer ${FLUID_TOKEN}")

# 2. Parse existing items, add new one
# 3. PUT back with updated items array
```
