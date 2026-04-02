# Migrate any ecommerce store to Fluid Commerce. One prompt.

Give Claude a URL. Get back a fully configured Fluid store — products, images, branding, policies, menus, customers, compliance. Everything.

```
> Migrate yellowbirdfoods.com to my Fluid store
```

```
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

40 products. 248 images. 7 collections. 4 policies. Brand assets. Navigation. Social links. Done.

---

## What's in the box

Three [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills that know the entire Fluid API:

**`/fluid-full-import`** — Full store migration. 25 steps: products, variants, categories, collections, images, brand, menus, pages, policies, checkout settings, tax, shipping zones, customers, inventory, state compliance rules, domains, discounts, redirects, blog posts, webhooks, compliance scanning.

**`/fluid-product-import`** — Products only. Variant mapping, DAM image uploads, category/collection linking, metafields, SEO.

**`/fluid-onboarding-prefill`** — Scrapes a company's site and pre-fills 15+ fields on the Fluid payments onboarding form:

```
> Pre-fill the onboarding form for kizik.com

FILLED:
  Legal Name:    Kizik Design LLC
  Trading Name:  Kizik
  Business Type: LLC (us_llc)
  Address:       1172 W 700 N, Suite 200, Lindon, UT 84042, US
  Phone:         +1 (833) 675-0266
  MCC Code:      5661 (Shoe Stores)
  Description:   Hands-free slip-on shoes, patented technology
  Policies:      Terms of Service, Privacy Policy (links saved)
  Country:       US (USD)

NEEDS USER INPUT:
  Tax ID / EIN, bank accounts, owner details,
  financial projections, T&C signature
```

---

## Works with every major platform

| Platform | Extraction | Cost |
|----------|-----------|------|
| Shopify | Public JSON API | Free |
| WooCommerce | REST API | Free |
| Squarespace | JSON endpoints | Free |
| BigCommerce | GraphQL | Free |
| Everything else | Firecrawl + AI | Firecrawl credits |

Shopify, WooCommerce, Squarespace, and BigCommerce stores use free public APIs. No admin access needed for product extraction. Unknown platforms fall back to Firecrawl crawling with AI-powered data extraction.

---

## Install

```bash
npx skills add fluidcommerce/fluid-claude-skills
```

Or clone it:

```bash
git clone https://github.com/fluidcommerce/fluid-claude-skills.git
cp -r fluid-claude-skills/skills/* your-project/.claude/skills/
```

---

## What you need

1. **Source site URL** — the store you're migrating
2. **Fluid URL** — your Fluid store (`yourcompany.fluid.app`)
3. **Fluid API token** — from Settings > API Tokens in Fluid admin
4. **Firecrawl API key** — from [firecrawl.dev](https://firecrawl.dev)

Every skill validates all four before doing any work. Bad token? You'll know in 2 seconds, not 20 minutes.

---

## The full import covers 25 steps

| | |
|---|---|
| **Commerce** | Products, variants, categories, collections, images, inventory |
| **Content** | Pages, blog posts, menus, brand, logo, favicon, theme templates |
| **Legal** | Terms, privacy policy, refund policy as checkout agreements. State compliance rules. Post-import compliance scan. |
| **Config** | Languages, currencies, checkout settings, tax, shipping zones, warehouses, domains |
| **Data** | Customers, discounts, redirects, webhooks |

Resumable. If something fails mid-import, re-run and it picks up where it left off.

---

## Usage

Slash commands:

```
/fluid-full-import
/fluid-product-import
/fluid-onboarding-prefill
```

Or just talk to Claude:

> "Migrate teddyfresh.com to Fluid"

> "Import products from yellowbirdfoods.com"

> "Pre-fill onboarding for kizik.com"

> "We only operate in 38 states — set up compliance rules"

---

Built by [Fluid Commerce](https://fluid.app). MIT License. [Contributing guide](CONTRIBUTING.md).
