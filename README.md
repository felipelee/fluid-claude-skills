# Fluid Skills

Claude Code skills for [Fluid Commerce](https://fluid.app) — the ecommerce platform built for MLM and social selling companies.

Migrate an entire ecommerce store into Fluid in minutes. Products, images, policies, branding, menus, customers, compliance — all automated.

Created by [Fluid Commerce](https://fluid.app).

---

## See It In Action

### Full site import — 40 products, 248 images, 7 collections, 4 policies, brand, menus, social links

```
> Migrate yellowbirdfoods.com to my Fluid store

[Preflight] Source site: OK yellowbirdfoods.com (Shopify detected)
[Preflight] Fluid API:  OK p.fluid.app (Company ID: 980243068)
[Preflight] Firecrawl:  OK
[Preflight] All checks passed — starting import.

[Assets]      Uploaded 248/248 images to DAM (0 failures)
[Categories]  Created 7 categories
[Collections] Created 6 collections
[Products]    Imported 40/40 products with variants, images, and SEO
[Brand]       Theme created, logo + favicon + OG image uploaded
[Agreements]  4 policies imported (Terms, Privacy, Refund, Shipping)
[Menus]       Main Menu + Footer Menu created
[Social]      Twitter, Facebook, Instagram, TikTok linked

Import complete.
```

### Onboarding pre-fill — scrape a site, fill 15+ KYC fields automatically

```
> Pre-fill the onboarding form for kizik.com

FILLED:
  Legal Name:    Kizik Design LLC
  Trading Name:  Kizik
  Business Type: LLC (us_llc)
  Address:       1172 W 700 N, Suite 200, Lindon, UT 84042, US
  Phone:         +1 (833) 675-0266
  Website:       https://kizik.com
  MCC Code:      5661 (Shoe Stores)
  Description:   Hands-free slip-on shoes, patented technology
  Policies:      Terms of Service, Privacy Policy (links saved)
  Country:       US (USD)

NEEDS USER INPUT:
  Tax ID / EIN, bank accounts, owner personal details,
  financial projections, T&C signature
```

---

## Prerequisites

Before using any Fluid skill, you need:

1. **Source site URL** — The ecommerce site to migrate (e.g. `https://yellowbirdfoods.com`)
2. **Fluid URL** — Your store's base URL (e.g. `https://yourcompany.fluid.app`)
3. **Developer API Token** — From your Fluid admin panel under **Settings > API Tokens**
4. **Firecrawl API Key** — From [firecrawl.dev](https://firecrawl.dev) for brand extraction, page scraping, and non-Shopify sites

Every skill validates all credentials before starting — you'll know within seconds if something is wrong.

---

## Available Skills

### Migration & Import

| Skill | What it does |
|-------|-------------|
| [fluid-full-import](skills/fluid-full-import/) | **Full site migration** — 25-step pipeline: products, categories, collections, images, brand, menus, pages, agreements/policies, checkout settings, tax, shipping zones, customers, inventory, state compliance rules, domains, discounts, redirects, blog posts, webhooks, and compliance scanning |
| [fluid-product-import](skills/fluid-product-import/) | **Product import only** — Product payloads, variant mapping, image upload to DAM, category/collection linking, metafields, and the ImportProduct schema |

### Setup & Onboarding

| Skill | What it does |
|-------|-------------|
| [fluid-onboarding-prefill](skills/fluid-onboarding-prefill/) | **KYC form pre-fill** — Scrapes a company's website for business name, address, phone, team members, policies, MCC code, and operating countries, then pushes it all into the Fluid onboarding API |

---

## What Gets Imported

The full import pipeline covers 25 steps:

| Area | What's included |
|------|----------------|
| **Core Commerce** | Products, variants, categories, collections, images (via DAM), inventory levels |
| **Content & Branding** | Pages, blog posts, menus, brand colors/fonts/logo/favicon/OG image, theme templates |
| **Legal & Compliance** | Terms of service, privacy policy, refund policy as checkout agreements. State/region compliance rules. Post-import compliance scanning. |
| **Store Configuration** | Languages, countries/currencies, checkout settings, tax config, shipping zones/warehouses, domains |
| **Customers & Data** | Customer profiles with addresses, discount codes, URL redirects, webhook subscriptions |

### Platform detection

Skills automatically detect the source platform and use the fastest extraction method:

| Platform | Method | Cost |
|----------|--------|------|
| **Shopify** | Public JSON API (`/products.json`, `/collections.json`) | Free |
| **WooCommerce** | REST API (`/wp-json/wc/v3/`) | Free |
| **Squarespace** | JSON endpoints (`/{slug}?format=json`) | Free |
| **BigCommerce** | GraphQL API | Free |
| **Any other site** | Firecrawl crawl + AI extraction | Firecrawl credits |

---

## Installation

### Option 1: CLI Install (Recommended)

```bash
npx skills add fluidcommerce/fluid-claude-skills
```

Install a specific skill only:

```bash
npx skills add fluidcommerce/fluid-claude-skills --filter fluid-full-import
```

### Option 2: Clone & Copy

```bash
git clone https://github.com/fluidcommerce/fluid-claude-skills.git
cp -r fluid-skills/skills/* your-project/.claude/skills/
```

### Option 3: Git Submodule

```bash
git submodule add https://github.com/fluidcommerce/fluid-claude-skills.git .claude/fluid-skills
```

### Option 4: Fork & Customize

Fork the repo and modify skills to match your team's specific Fluid setup.

---

## Usage

### Slash commands

```
/fluid-full-import
/fluid-product-import
/fluid-onboarding-prefill
```

### Natural language

Claude automatically activates the right skill based on your request:

> "Migrate yellowbirdfoods.com to my Fluid store"

> "Import just the products from teddyfresh.com into Fluid"

> "Pre-fill the onboarding form for kizik.com"

> "Set up state compliance rules — we only operate in 38 states"

> "Import our terms of service and privacy policy as checkout agreements"

Each skill will ask for your credentials, validate them, and start working.

---

## How It Works

1. **You provide 4 things** — source site URL, Fluid URL, Fluid API token, Firecrawl key
2. **Credentials are validated** — all checked in parallel before any work starts
3. **Source platform is detected** — Shopify, WooCommerce, etc. get fast-path extraction
4. **Data is extracted** — products, images, policies, brand assets, menus, metadata
5. **Everything is pushed to Fluid** — 25 import steps run sequentially with progress logging
6. **You get a summary** — what was imported, what needs manual attention

The entire process is resumable. If something fails mid-import, re-run the skill and it picks up where it left off via `id-mapping.json`.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding or modifying skills.

---

## License

MIT
