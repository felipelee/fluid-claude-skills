# Move your entire store to Fluid Commerce. One sentence.

Setting up a new store on Fluid used to take days. Exporting products, re-uploading images, recreating menus, copying policies, configuring brand settings — all by hand.

Now you type one sentence and it handles everything.

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

## What gets moved

Everything you'd spend days doing by hand:

| | |
|---|---|
| **Your products** | Every product with all its variants, images, pricing, and descriptions |
| **Your branding** | Logo, favicon, app icon, colors, fonts — your store looks like yours from day one |
| **Your content** | Pages, blog posts, navigation menus, and footer links |
| **Your policies** | Terms of service, privacy policy, refund policy, shipping policy — set up as checkout agreements |
| **Your store settings** | Languages, currencies, checkout options, tax settings, shipping zones |
| **Your customers** | Customer profiles with addresses and contact info |
| **Your promotions** | Discount codes, URL redirects, and more |

If something fails halfway through, just run it again — it picks up where it left off.

---

## It also clones your website's look

After your products and settings are imported, a second tool can rebuild your current website's design inside Fluid — section by section, pixel by pixel.

It takes screenshots of your existing site, matches every color, font, and spacing value, then builds it as an editable Fluid theme. A third tool does a polish pass — re-screenshotting and fixing any remaining differences until it's an exact match.

---

## Pre-fills your payments paperwork too

Getting set up for payments processing means filling out a long form with your business details. Instead of doing it by hand, this tool scrapes your existing website and fills in what it can:

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

You still need to fill in the sensitive stuff (bank details, tax ID, signatures), but the basics are done for you.

---

## Works no matter where your store is today

| Moving from | How it works |
|-------------|-------------|
| **Shopify** | Pulls your data directly — fast and free |
| **WooCommerce** | Pulls your data directly — fast and free |
| **Squarespace** | Pulls your data directly — fast and free |
| **BigCommerce** | Pulls your data directly — fast and free |
| **Any other platform** | Crawls your site with AI to extract everything |

For Shopify, WooCommerce, Squarespace, and BigCommerce, it reads your store's public data automatically. No login needed. For other platforms, it uses [Firecrawl](https://firecrawl.dev) (a web scraping service) to crawl your site and extract the data with AI.

---

## Getting started

### 1. Install Claude Code

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) is Anthropic's AI coding assistant that runs in your terminal. Install it by opening your terminal and running:

```bash
npm install -g @anthropic-ai/claude-code
```

Then type `claude` and follow the prompts to sign in with your Anthropic account.

### 2. Add the Fluid skills

In your terminal, run:

```bash
npx skills add fluidcommerce/fluid-claude-skills
```

This gives Claude everything it needs to know about the Fluid platform.

### 3. Gather your credentials

You'll need four things before starting. The tool asks for all of them upfront and checks each one before doing any work — so you'll know immediately if something is wrong.

| What you need | Where to find it |
|---------------|-----------------|
| **Your current store URL** | The address of the store you're migrating (e.g. `yellowbirdfoods.com`) |
| **Your Fluid store URL** | Your new Fluid store address (e.g. `yourcompany.fluid.app`) |
| **Your Fluid developer token** | In your Fluid admin panel: Settings > API Tokens > Create new token |
| **A Firecrawl key** | Sign up at [firecrawl.dev](https://firecrawl.dev) and copy your key from the dashboard |

### 4. Tell Claude what to do

Open Claude Code and type what you want in plain English:

```
> Migrate yellowbirdfoods.com to my Fluid store at p.fluid.app
```

It asks for your credentials, verifies everything works, then starts moving your store. You'll see progress for every step in real time.

---

## The five tools included

| Tool | What it does |
|------|-------------|
| **Product & Settings Import** | Moves your products, images, categories, collections, brand, menus, pages, policies, checkout settings, tax, shipping, customers, inventory, discounts, redirects, and blog posts |
| **Theme Clone** | Rebuilds your current website's design inside Fluid — every section, every color, every font |
| **Theme Refine** | Takes fresh screenshots and compares your Fluid site against the original, fixing differences until they're identical |
| **Onboarding Pre-Fill** | Scrapes your website for business info and fills in your payments onboarding form automatically |

---

## Tips

**Start with the Product & Settings Import.** It handles the heavy lifting — getting all your data into Fluid.

**Then run Theme Clone** to match your current site's look and feel inside Fluid.

**Use Theme Refine** to polish the details. It compares screenshots side-by-side and fixes anything that's off.

**Run Onboarding Pre-Fill** before your payments setup meeting. It saves time by pulling your business info from your existing site.

**Migrating multiple stores?** Each run is completely independent. Different source store, different Fluid account — just provide the new credentials each time.

---

## For developers

These skills are open source and designed to be extended. They're markdown files that teach Claude the Fluid platform — every endpoint, every schema, every edge case.

Fork the repo. Customize the workflows. Add new import steps. Wire them into your own automation. [Contributing guide](CONTRIBUTING.md).

---

Built by [Fluid Commerce](https://fluid.app). MIT License.
