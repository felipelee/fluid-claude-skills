# Migrate any ecommerce store to Fluid Commerce. One prompt.

Setting up a new store on Fluid used to take days. Exporting products, re-uploading images, recreating menus, copying policies, configuring brand settings — all by hand.

Now you give Claude a URL and walk away.

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

## Getting started

### 1. Install Claude Code

If you don't have it yet:

```bash
npm install -g @anthropic-ai/claude-code
```

Then run `claude` in your terminal to authenticate with your Anthropic account. [Full setup guide](https://docs.anthropic.com/en/docs/claude-code).

### 2. Install Fluid Skills

```bash
npx skills add fluidcommerce/fluid-claude-skills
```

This drops four skills into your project's `.claude/skills/` directory. Claude picks them up automatically.

Or clone manually:

```bash
git clone https://github.com/fluidcommerce/fluid-claude-skills.git
cp -r fluid-claude-skills/skills/* your-project/.claude/skills/
```

### 3. Get your credentials ready

You need four things. Have them handy before you start — the skill asks for all of them upfront and validates each one before doing any work.

| What | Where to get it |
|------|----------------|
| **Source site URL** | The store you're migrating (e.g. `yellowbirdfoods.com`) |
| **Fluid URL** | Your Fluid store (e.g. `yourcompany.fluid.app`) |
| **Fluid API token** | Fluid admin > Settings > API Tokens > Create new token |
| **Firecrawl API key** | [firecrawl.dev](https://firecrawl.dev) > Sign up > API Keys |

Bad token? You'll know in 2 seconds, not 20 minutes. Every skill validates before it starts.

### 4. Run it

Open Claude Code in any project directory where the skills are installed:

```bash
claude
```

Then tell it what you want:

```
> Migrate yellowbirdfoods.com to my Fluid store at p.fluid.app
```

Claude asks for your tokens, checks them, detects the platform, and starts importing. You'll see real-time progress for every step.

---

## Bring your own agent

These skills work with any Claude Code setup — your terminal, your IDE, your workflow. They're just markdown files that teach Claude the Fluid API. No vendor lock-in, no proprietary CLI, no SaaS dashboard.

Fork the repo. Customize the skills. Add your own. Wire them into your existing automation. They're designed to be extended.

Running migrations for multiple clients? Each run is stateless. Different source site, different Fluid account, different credentials — every time. No config files to manage between runs.

---

## What's in the box

Four skills that know the entire Fluid API:

**`/fluid-full-import`** — Full store migration. 25 steps: products, variants, categories, collections, images, brand, menus, pages, policies, checkout settings, tax, shipping zones, customers, inventory, state compliance rules, domains, discounts, redirects, blog posts, webhooks, compliance scanning.

**`/fluid-product-import`** — Products only. Variant mapping, DAM image uploads, category/collection linking, metafields, SEO.

**`/fluid-theme-clone`** — Pixel-perfect site cloning. Scrapes any website, audits visuals via screenshots, uploads images to DAM, builds Liquid sections with exact CSS, assembles page templates, and pushes the theme to Fluid. Ships with a base theme scaffolding and 7 reference files.

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

Shopify, WooCommerce, Squarespace, and BigCommerce use free public APIs — no admin access needed. Unknown platforms fall back to Firecrawl crawling with AI-powered extraction.

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

## Tips for getting the most out of it

**Start with `/fluid-full-import` for new migrations.** It handles everything — you don't need to run the individual skills separately unless you're debugging a specific step.

**Have a Shopify admin token?** The full import can pull extra data (customers, inventory levels, shipping zones, discount codes) that aren't available from the public API. Mention it when Claude asks for credentials.

**Running for a client?** The onboarding pre-fill skill saves real time. Run it before the client fills out their KYC form — it pre-populates business name, address, MCC code, policies, and operating countries from their existing site.

**Want the full visual clone?** Run `/fluid-theme-clone` after the import. It scrapes the source site's design — colors, typography, layout, animations — and rebuilds it as Fluid theme sections. Pixel-perfect, editor-compatible.

**Something break?** Re-run the same skill. It reads `id-mapping.json` and skips everything already imported. Only retries what failed.

**Want to customize?** Fork the repo. The skills are markdown — edit the API endpoints, add new import steps, adjust the extraction logic. They're designed to be modified.

---

Built by [Fluid Commerce](https://fluid.app). MIT License. [Contributing guide](CONTRIBUTING.md).
