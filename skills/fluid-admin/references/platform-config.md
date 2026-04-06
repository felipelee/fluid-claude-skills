# Platform & Configuration: Admins, Roles, Feature Flags, Droplets & More

---

## Admins

### List Admins
```
GET /api/v2/admins
```

### Create Admin
```
POST /api/v2/admins
```

```json
{
  "admin": {
    "email": "admin@example.com",
    "admin_roles": [1],
    "first_name": "Admin",
    "last_name": "User",
    "phone": "+15551234567",
    "language_code": "en",
    "country_code": "US",
    "active": true
  }
}
```

**Required fields:** `email`, `admin_roles` (array of role IDs)

### Get Admin
```
GET /api/v2/admins/:id
```

### Update Admin
```
PATCH /api/v2/admins/:id
```

### Delete Admin
```
DELETE /api/v2/admins/:id
```

### Add/Remove Self as Admin
```
POST   /api/company_admins    # Add current user as admin
DELETE /api/company_admins    # Remove current user's admin access
```

---

## Roles & Permissions

### List Roles
```
GET /api/company/roles
```

### Create Role
```
POST /api/company/roles
```

```json
{
  "role": {
    "name": "Content Manager",
    "permissions": ["products.read", "products.write", "media.read", "media.write"]
  }
}
```

### Update Role
```
PUT /api/company/roles/:id
```

### Delete Role
```
DELETE /api/company/roles/:id
```

### Duplicate Role
```
POST /api/company/roles/:id/duplicate
```

### Get Roles Structure
```
GET /api/company/roles/structure
```
Returns the full permission tree for the company.

### Get My Permissions
```
GET /api/company/roles/my_permissions
```

---

## Display Settings

### Get Display Settings
```
GET /api/settings/displays
```

### Update Display Settings
```
PATCH /api/settings/displays
```

---

## Feature Flags

### List Feature Flags
```
GET /api/v202506/feature_flags
```

### Create Feature Flag
```
POST /api/v202506/feature_flags
```

```json
{
  "flag_name": "new_checkout_flow",
  "enabled": true
}
```

### Update Feature Flags
```
PUT /api/v202506/feature_flags
```

### Delete Feature Flag
```
DELETE /api/v202506/feature_flags/:flag_name
```

---

## Global Embeds

Inject custom code (scripts, pixels, etc.) across the entire storefront.

### List Global Embeds
```
GET /api/global_embeds
```

### Create Global Embed
```
POST /api/global_embeds
```

```json
{
  "global_embed": {
    "name": "Facebook Pixel",
    "content": "<script>/* FB Pixel code */</script>",
    "placement": "head",
    "status": "active"
  }
}
```

**Fields:**
- `name` (required) — Display name
- `content` (required) — The HTML/script code to inject
- `status` — `"draft"` or `"active"`
- `placement` — `"head"` or `"body"`

### Get / Update / Delete
```
GET    /api/global_embeds/:id
PUT    /api/global_embeds/:id
DELETE /api/global_embeds/:id
```

---

## Sitemap

### Get Sitemap URLs
```
GET /api/v2025-06/sitemap
```

### Update Sitemap URL Visibility
```
PATCH /api/v2025-06/sitemap
```

---

## Shares & Share Statistics

### List Shares
```
GET /api/company/shares
GET /api/shares
```

### Get Share Statistics
Stats available per resource type:
```
GET /api/v2025-06/media/:id/share_stats
GET /api/v2025-06/products/:id/share_stats
GET /api/v2025-06/collections/:id/share_stats
GET /api/v2025-06/categories/:id/share_stats
GET /api/v2025-06/playlists/:id/share_stats
GET /api/v2025-06/posts/:id/share_stats
GET /api/v2025-06/pages/:id/share_stats
GET /api/v2025-06/enrollment_packs/:id/share_stats
```

---

## Droplets (Marketplace Extensions)

### List Droplets
```
GET /api/droplets
```

### Create Droplet
```
POST /api/droplets
```

### Get / Update / Delete Droplet
```
GET    /api/droplets/:uuid
PUT    /api/droplets/:uuid
DELETE /api/droplets/:uuid
```

### List Companies Using Droplet
```
GET /api/droplets/:uuid/companies
```

### Droplet Installations
```
GET    /api/droplet_installations
POST   /api/droplet_installations
GET    /api/droplet_installations/:uuid
PUT    /api/droplet_installations/:uuid
DELETE /api/droplet_installations/:uuid
```

### Droplet Categories
```
GET /api/droplet_categories
```

---

## Drop Zones

Embeddable widget areas for external sites.

```
GET    /api/drop_zones
POST   /api/drop_zones
GET    /api/drop_zones/:uuid
PUT    /api/drop_zones/:uuid
DELETE /api/drop_zones/:uuid
GET    /api/drop_zones/constants
```

---

## Custom Pages

Company dashboard custom pages.

```
GET    /api/company/custom_pages
POST   /api/company/custom_pages
GET    /api/company/custom_pages/:id
PUT    /api/company/custom_pages/:id
DELETE /api/company/custom_pages/:id
GET    /api/company/custom_pages/:id/send_to_top
GET    /api/company/custom_pages/:id/duplicate
```

---

## Tiles

Dashboard tile widgets.

```
GET    /api/company/tiles
POST   /api/company/tiles
GET    /api/company/tiles/:id
PATCH  /api/company/tiles/:id
DELETE /api/company/tiles/:id
```

---

## Mobile Widgets

```
GET    /api/company/mobile_widgets
POST   /api/company/mobile_widgets
GET    /api/company/mobile_widgets/:id
PUT    /api/company/mobile_widgets/:id
DELETE /api/company/mobile_widgets/:id
```

---

## Catch Ups

Custom catch-up/onboarding sequences for reps.

```
GET    /api/company/custom_catch_ups
POST   /api/company/custom_catch_ups
PATCH  /api/company/custom_catch_ups/:id
DELETE /api/company/custom_catch_ups/:id
POST   /api/company/catch_up/custom_catch_ups    # Generate custom catchup
```

---

## Trainings

```
GET    /api/v202506/trainings
POST   /api/v202506/trainings
GET    /api/v202506/trainings/:id
PATCH  /api/v202506/trainings/:id
DELETE /api/v202506/trainings/:id
```

---

## Lighthouse (Product Performance)

```
GET    /api/v202506/products/:product_id/lighthouse           # Latest scan
GET    /api/v202506/products/:product_id/lighthouses          # All scans
POST   /api/v202506/products/:product_id/lighthouses          # New scan
GET    /api/v202506/products/:product_id/lighthouses/:id      # Specific scan
PATCH  /api/v202506/products/:product_id/lighthouses/:id      # Update scan
DELETE /api/v202506/products/:product_id/lighthouses/:id      # Delete scan
```

---

## Impersonation

```
POST   /api/impersonation       # Impersonate a company
DELETE /api/impersonation       # Exit impersonation
```

---

## Prompts

```
GET    /api/prompts              # List prompts for a relatable object
POST   /api/prompts              # Create prompt
PATCH  /api/prompts/:id          # Update prompt
DELETE /api/prompts/:id          # Delete prompt
```

---

## Activities

```
POST /api/company/activities     # Create activity log entry
```
