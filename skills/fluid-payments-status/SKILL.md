---
name: fluid-payments-status
description: >-
  Set or review PSP and APM onboarding status for a Fluid merchant from Fluid
  root admin. Use when the user describes payments onboarding progress for a
  specific client — phrases like "<Company> is in onboarding with <Processor>,"
  "We're ready to test <Company>'s connection to <Processor>," "We've sent
  <Company>'s forms to <APM>," "<APM> is ready for <Company>," "update
  payments status for <Company>," or "show me <Company>'s PSP statuses."
  Collects credentials from .env, confirms the target company, always previews
  the change, and only writes after explicit confirmation. Renders rich
  inline visuals (status pills, bordered provider cards, multi-company
  matrix) in Claude Desktop / claude.ai, with an emoji-prefix fallback for
  terminals.
metadata:
  version: 1.3.0
---

# Fluid Payments Status

Set and review PSP (payment service provider) and APM (alternative payment
method) onboarding status for a specific Fluid merchant. This is the scripted
equivalent of opening root admin → selecting a company → "Manage Status"
drawer → ticking statuses by hand.

Works for both directions:

- **Read**: "Tell me all the PSP statuses for Neumi," "show APMs for
  Oliabo."
- **Write**: "Neumi is in onboarding with Stripe," "We're ready to test
  Oliabo's connection to Braintree," "We've sent LimbicArc's forms to
  Klarna," "Affirm is ready for NewULife," "update payments status for
  NewULife."

Always previews the change first. Never writes without a `yes`.

---

## 1. Session Setup

### Base URL

Always production: `https://api.fluid.app`. Don't ask the user — hard-code it.

```bash
FLUID_API_BASE="https://api.fluid.app"
```

### Load API keys from .env

API keys are stored in the skill repo's `.env` file:

```
/Users/cheyrasmussen/fluid-claude-skills/.env
```

**Never ask the user for a token.** Always load from `.env`.

**`.env` format** — one pair per company:

```bash
# FLUID_{SLUG}_ID  — Fluid numeric company ID
# FLUID_{SLUG}_KEY — PartnerToken for that company (PT-... prefix, company admin role)
FLUID_UPROOTCLEAN_ID=980243135
FLUID_UPROOTCLEAN_KEY=PT-xxx
FLUID_NEUMI_ID=1234
FLUID_NEUMI_KEY=PT-yyy
```

**SLUG rules:**
- Uppercase only; alphanumeric + underscore; no consecutive underscores
- Derived from the company name: strip special characters, replace spaces with `_`
- Examples: `Uproot Clean` → `UPROOTCLEAN`, `NewULife` → `NEWULIFE`,
  `LimbicArc` → `LIMBICARC`

**Discover configured companies** by parsing `.env` for all `FLUID_*_KEY` entries:

```bash
ENV_FILE="/Users/cheyrasmussen/fluid-claude-skills/.env"

# Build a map of slug → {id, key}
while IFS='=' read -r var val; do
  [[ "$var" =~ ^FLUID_([A-Z0-9_]+)_KEY$ ]] || continue
  slug="${BASH_REMATCH[1]}"
  id_var="FLUID_${slug}_ID"
  # Read the matching ID
  id=$(grep "^${id_var}=" "$ENV_FILE" | cut -d= -f2)
  echo "slug=$slug id=$id"
done < "$ENV_FILE"
```

### Display configured companies

At the start of every session, show which companies are loaded:

```
Companies configured in .env:
  • Uproot Clean  (id 980243135)  [UPROOTCLEAN]
  • Neumi         (id 1234)       [NEUMI]

2 companies configured.
```

Derive the display name from the slug by converting `_` to spaces and title-casing
(e.g., `UPROOTCLEAN` → `Uprootclean`, `NEW_ULIFE` → `New Ulife`). When there's
an exact slug → name mapping known from prior conversation context, prefer that.

If no `FLUID_*_KEY` pairs exist in `.env`, stop and tell the user:

```
No API keys found in .env. Add a pair for each company:
  FLUID_{SLUG}_ID=<company id>
  FLUID_{SLUG}_KEY=<PT-... partner token>
```

### No upfront validation

Keys are validated implicitly on first use. If any call returns `401` or `403`,
report the slug, say the key is expired or misconfigured, and ask the user to
refresh it in `.env`. Do not re-attempt — let the user fix and restart.

---

## 2. Parse the user's utterance

Before prompting the user for anything else, extract what you can from
what they already said.

**Company name**: proper noun, usually at the start or end of the
sentence. Examples: `Neumi`, `Oliabo`, `LimbicArc`, `NewULife`.

**Provider name(s)**: any of the PSPs or APMs Fluid supports. Common
matches:

- PSPs: Stripe, Braintree, Worldpay, Checkout.com, NMI, PayPal PPCP,
  Nuvei, Platpay
- APMs: PayPal, Klarna, Affirm, Bread, Venmo, Alipay, GCash, iDEAL,
  OXXO, UPI India

If an utterance mentions multiple providers ("Braintree and Worldpay"),
extract all of them — the PUT endpoint accepts a batched `updates`
array.

**Implied target status**: map the phrasing to one of the five enum
values. Full table:

| Phrase hint                                                        | Enum              |
|--------------------------------------------------------------------|-------------------|
| "not onboarding," "disabled," "not setting up"                     | `not_onboarding`  |
| "in onboarding," "starting," "initial setup," "just started"       | `pre_onboarding`  |
| "sent forms," "underwriting," "under review," "awaiting approval"  | `underwriting`    |
| "ready to test," "testing," "connecting," "wired up"               | `connecting`      |
| "live," "done," "ready for <X>," "good to go"                      | `live`            |

Always show the mapped value back to the user before writing. The
mapping is a guess — the user confirms.

---

## 3. Resolve the company

Fuzzy-match the extracted company name against the **slugs loaded from `.env`**.

**Matching algorithm:**

1. Normalize the user's input: lowercase, strip punctuation and spaces.
2. Normalize each slug: lowercase, strip underscores.
3. Check for substring match (normalized input ∈ normalized slug, or vice versa).

Examples:
- `"uproot"` → matches `UPROOTCLEAN` ✓
- `"newulife"` → matches `NEWULIFE` ✓
- `"limbic arc"` → normalized to `limbicarc`, matches `LIMBICARC` ✓

Outcomes:

- **Exactly one match** → use it. Print `Company: {display name} (id {id})` and continue.
- **Multiple matches** → list all candidates with their slugs and IDs and ask
  in plain prose which one they meant.
- **No match** → report clearly:

  ```
  No API key configured for "{name}".
  To add it, append to .env:
    FLUID_{SLUG}_ID=<company id>
    FLUID_{SLUG}_KEY=<PT-... partner token>
  ```

Never assume when there's ambiguity.

---

## 4. Fetch current state

Use the key for the resolved company:

```bash
# Load from .env
source /Users/cheyrasmussen/fluid-claude-skills/.env
COMPANY_KEY="FLUID_${SLUG}_KEY"
COMPANY_ID="FLUID_${SLUG}_ID"
FLUID_API_KEY="${!COMPANY_KEY}"
COMPANY_ID_VALUE="${!COMPANY_ID}"

curl -s -w "\n%{http_code}" \
  "${FLUID_API_BASE}/api/companies/${COMPANY_ID_VALUE}/payments_status" \
  -H "Authorization: Bearer ${FLUID_API_KEY}" \
  -H "Accept: application/json"
```

The response is already partitioned into `providers.psps` and
`providers.apms`:

```json
{
  "providers": {
    "psps": [{ "id": 12, "payment_account_id": 87, "display_name": "Stripe",
               "integration_class": null,
               "adapter_class": "ActiveMerchant::Billing::StripeGateway",
               "provider_type": "psp",
               "onboarding_status": "live",
               "onboarding_time_estimate": null,
               "active": true, "countries": [...] }],
    "apms": [{ "id": 201, "payment_account_id": 201, "display_name": "Klarna",
               "integration_class": "Klarna", "adapter_class": null,
               "provider_type": "apm",
               "onboarding_status": "pre_onboarding",
               "onboarding_time_estimate": "3 business days",
               "active": true, "countries": [] }]
  },
  "metrics": { "psps_connected": 1, "apms_enabled": 0,
               "countries_ready": 1, "total_countries": 50 },
  "infrastructure": { "vault": {...}, "three_ds": {...} },
  "onboarding": { "form_started": true, "form_submitted": true },
  "meta": { "request_id": "…", "timestamp": "…" }
}
```

### ⚠ Known bad field: `onboarding.form_submitted`

**Do not surface `onboarding.form_submitted` to the user.** The field
name is misleading. The backend calculation
(`app/services/payments_status/index_action.rb:119-127`) returns `true`
only when **all 9 onboarding sub-steps are at 100% AND T&C is signed**:

```
basic_info, business_info, legal_entities, bank_accounts_i,
bank_accounts_ii, personal_info, relevant_persons, countries, underwriting
```

`underwriting` is Fluid-owned and only hits 100 after internal approval,
so in practice `form_submitted` is `false` for almost every active
merchant — including ones who have very much submitted their form. It's
a full-completion flag, not a submission flag.

If the user asks "has company X submitted their form?", infer it from
the provider statuses instead: **if any PSP or APM has
`onboarding_status != "not_onboarding"`, the form has been submitted**
— status wouldn't have been advanced otherwise. Treat
`onboarding.form_started` and `onboarding.form_submitted` as debugging
metadata only.

Backend follow-up (not this skill): either rename the field to
`onboarding_fully_complete`, or add a separate real
`form_submitted` backed by `terms_and_conditions_agreed_at.present?`
or a dedicated submission timestamp.

---

## 5. Read flow

If the user asked to view status ("Tell me Neumi's PSP statuses,"
"show APMs for Oliabo," `/fluid-payments-status` with no write intent),
stop after step 4 and render using the **visual templates in
[references/visual-rendering.md](references/visual-rendering.md)**.

Default shape for a single-company read:

1. **Company header card** — identity + rollup metrics from
   `metrics.psps_connected`, `metrics.apms_enabled`,
   `metrics.countries_ready / total_countries`.
2. **`PSPs (N)` section heading** — small uppercase label.
3. **One bordered status card per PSP** — left-border color, tinted
   background, and trailing status pill all keyed to
   `onboarding_status`.
4. **`APMs (N)` section heading**.
5. **One bordered status card per APM** — same shape.

Provider order: preserve the order from the API response. Include
`onboarding_time_estimate` as a `⏱` row below a card only when the
status is one of `pre_onboarding`, `underwriting`, `connecting`.

**Fallback** (terminals, or user says "plain"): use the emoji-prefix
format — see the "Plain-text fallback" section in
[references/visual-rendering.md](references/visual-rendering.md).

Emoji convention: 🟢 `live` · 🔵 `connecting` · 🟡 `underwriting` ·
🟣 `pre_onboarding` · ⚪ `not_onboarding`.

---

## 6. Write flow

### 6a. Resolve each provider

For every provider name in the utterance, fuzzy-match against both
`providers.psps[]` and `providers.apms[]` on these fields:

1. `display_name`
2. `integration_class`
3. `adapter_class` (PSPs only)

**Ambiguous** (e.g., "PayPal" matches PayPal APM *and* PayPal PPCP
PSP) — ask which one in plain prose, showing both candidates with
`provider_type` labels.

**Unknown** — print the company's current PSP and APM lists from step 4
and ask the user to pick.

Record `payment_account_id ?? id` for each resolved provider — this
is the batched `updates[].payment_account_id`.

### 6b. Confirm the target status

If step 2 mapped a status from the utterance, show it back:

```
Map "in onboarding with Stripe" → Stripe to Initial Setup (pre_onboarding).
Correct? (yes / pick another / cancel)
```

If the utterance didn't imply a status, ask which one from the list:

```
What should Stripe be set to?
  1. Not Onboarding
  2. Initial Setup       (pre_onboarding)
  3. Underwriting        (underwriting)
  4. Connecting & Testing (connecting)
  5. Live
```

When multiple providers are being updated and the utterance implies a
single status for all of them ("Braintree and Worldpay are ready to
test"), apply the mapped status to each but still confirm the full
batch in step 6d.

### 6c. Resolve `onboarding_time_estimate`

Only ask when the target status is one of `pre_onboarding`,
`underwriting`, `connecting`. Omit / set to `null` for
`not_onboarding` and `live`.

```
How many business days until live? (e.g. 3, 5, 10, or 'skip')
```

Format the string the same way the UI does:

- `N === 1` → `"1 business day"`
- else → `"N business days"`
- `skip` → omit the field from the update

### 6d. Preview the diff

Render one **diff preview row** per update using the HTML template in
[references/visual-rendering.md](references/visual-rendering.md)
("Diff preview row" section). Each row shows `old pill → new pill`
plus the time estimate when applicable.

Plain-text fallback (use in terminals or when the user asks for it):

```
Company: Neumi (id 1234)
  🟣 Stripe     (PSP)  Not Onboarding → Initial Setup  (5 business days)
  🟡 Klarna     (APM)  Not Onboarding → Underwriting   (10 business days)

Apply these changes? (yes / no)
```

**Do NOT proceed until the user says yes.** Plain `yes`. Not "sure,"
not an emoji, not silence. If the user says no or anything ambiguous,
cancel without writing. The `yes / no` prompt is always literal plain
text — never hide it inside an HTML block.

No-op safeguard: if every provider's current status (and time
estimate) already matches the target, say `No changes needed —
already in that state.` and stop. No PUT.

### 6e. Apply

Load the company key and issue one batched request:

```bash
source /Users/cheyrasmussen/fluid-claude-skills/.env
FLUID_API_KEY="${!$(echo FLUID_${SLUG}_KEY)}"
COMPANY_ID_VALUE="${!$(echo FLUID_${SLUG}_ID)}"

curl -s -w "\n%{http_code}" -X PUT \
  "${FLUID_API_BASE}/api/companies/${COMPANY_ID_VALUE}/payments_status" \
  -H "Authorization: Bearer ${FLUID_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "updates": [
      {
        "payment_account_id": 87,
        "onboarding_status": "pre_onboarding",
        "onboarding_time_estimate": "5 business days"
      },
      {
        "payment_account_id": 201,
        "onboarding_status": "underwriting",
        "onboarding_time_estimate": "10 business days"
      }
    ]
  }'
```

Response shape:

```json
{
  "providers": [ { "id": 87, "payment_account_id": 87,
                   "display_name": "Stripe",
                   "onboarding_status": "pre_onboarding",
                   "onboarding_time_estimate": "5 business days",
                   ... } ],
  "meta": { "request_id": "…", "timestamp": "…" }
}
```

Report results per provider using the **success row** template from
[references/visual-rendering.md](references/visual-rendering.md) —
one row per updated provider, with a green `✓` prefix, the new status
pill, and the time estimate when present. Missing-from-response
providers get the red `⚠` warning row.

Plain-text fallback:

```
Updated:
  ✓ 🟣 Stripe  → Initial Setup (5 business days)
  ✓ 🟡 Klarna  → Underwriting (10 business days)
```

If any provider is missing from `providers[]`, surface that explicitly
with `⚠` and suggest re-reading to confirm state.

---

## 7. Endpoint reference

| Purpose          | Method | Path                                                    |
|------------------|--------|---------------------------------------------------------|
| Current state    | GET    | `/api/companies/{id}/payments_status`                   |
| Visible-only     | GET    | `/api/companies/{id}/payments_status?visible_only=true` |
| Batched update   | PUT    | `/api/companies/{id}/payments_status`                   |
| Company identity | GET    | `/api/companies`                                        |

The company ID (`{id}`) always comes from `.env` — `FLUID_{SLUG}_ID`.

All requests use:

```
Authorization: Bearer ${FLUID_API_KEY}   ← FLUID_{SLUG}_KEY from .env
Accept: application/json
Content-Type: application/json           (PUT only)
```

The `/api/companies` endpoint is for debugging only (verify which company
a key resolves to). It is not called in normal skill flow.

### Status enum + UI labels

| Enum              | UI label               |
|-------------------|------------------------|
| `not_onboarding`  | Not Onboarding         |
| `pre_onboarding`  | Initial Setup          |
| `underwriting`    | Underwriting           |
| `connecting`      | Connecting & Testing   |
| `live`            | Live                   |

### `onboarding_time_estimate` format

String like `"5 business days"`. Singular for `N=1`. Omit or send
`null` when status is `not_onboarding` or `live`.

### `payment_account_id` fallback

If a provider's `payment_account_id` is `null`, use its `id` field
instead. The drawer in the admin UI does the same.

### PSP vs APM identification

Don't infer. The response already partitions providers — iterate
`providers.psps[]` and `providers.apms[]` separately. When matching
by name, search both arrays and treat the provider type as a label,
not a lookup key.

See [references/status-mapping.md](references/status-mapping.md) for
the full `integration_class` / `adapter_class` → display name table.

---

## 8. Example transcripts

Shape examples below use the plain-text fallback for readability. In
Claude Desktop / claude.ai, each `🟢/🔵/🟡/🟣/⚪ Provider` row becomes
the HTML status card from
[references/visual-rendering.md](references/visual-rendering.md).

### Write — single provider, status implied

```
User:  Neumi is in onboarding with Stripe
Skill: Map "in onboarding" → Initial Setup (pre_onboarding).
       How many business days until live? (e.g. 3, 5, 10, or 'skip')
User:  5
Skill: Company: Neumi (id 1234)
         🟣 Stripe (PSP)  Not Onboarding → Initial Setup  (5 business days)
       Apply these changes? (yes / no)
User:  yes
Skill: ✓ 🟣 Stripe → Initial Setup (5 business days)
```

### Write — multiple providers, batched

```
User:  We're ready to test Oliabo's connections to Braintree and Worldpay
Skill: Map "ready to test" → Connecting & Testing for both. Days until live?
User:  Braintree 5, Worldpay 10
Skill: Company: Oliabo (id 2345)
         🔵 Braintree (PSP)  Underwriting → Connecting & Testing  (5 business days)
         🔵 Worldpay  (PSP)  Underwriting → Connecting & Testing  (10 business days)
       Apply these changes? (yes / no)
User:  yes
Skill: ✓ 🔵 Braintree → Connecting & Testing (5 business days)
       ✓ 🔵 Worldpay  → Connecting & Testing (10 business days)
```

### Read — single company (rich)

Rich client: company header card + `PSPs (N)` heading + one bordered
status card per PSP + `APMs (N)` heading + one bordered status card per
APM. See §5 and the visual-rendering reference for the exact HTML.

### Read — multi-company dashboard

```
User:  How are Neumi, Oliabo, and LimbicArc doing on PSPs?

Skill: (matrix — see §10)

                 Stripe     Braintree   Worldpay    PayPal PPCP
Neumi            🟢 Live    🔵 Conn.    ⚪ —        🟢 Live
Oliabo           🟡 Under.  ⚪ —        🟣 Init.    ⚪ —
LimbicArc        🟢 Live    🟢 Live     ⚪ —        🔵 Conn.

🟢 4 live · 🔵 2 connecting · 🟡 1 underwriting · 🟣 1 initial · ⚪ 4 not onboarding
```

### Disambiguation — PayPal

```
User:  LimbicArc's PayPal is live
Skill: "PayPal" matches two providers:
         1. PayPal PPCP (PSP)
         2. PayPal      (APM)
       Which one? (1 / 2 / cancel)
User:  2
Skill: Company: LimbicArc (id 4567)
         🟢 PayPal (APM)  Connecting & Testing → Live
       Apply these changes? (yes / no)
User:  yes
Skill: ✓ 🟢 PayPal → Live
```

---

## 9. Error handling

| Signal                                   | Response                                                                        |
|------------------------------------------|---------------------------------------------------------------------------------|
| No `FLUID_*_KEY` pairs in `.env`         | "No API keys found in .env." Show the format and stop.                          |
| Company name not matched in .env slugs   | "No key configured for '{name}'." Show .env format for adding it.               |
| `payments_status` returns 401/403        | "Key for {SLUG} is expired or misconfigured — refresh `FLUID_{SLUG}_KEY`."      |
| `payments_status` returns 404            | "Company id {id} not found or has no payments config." Confirm the ID in .env.  |
| PUT returns 422                          | Print the error body verbatim. Do not retry automatically.                      |
| PUT response missing a provider          | Surface "no confirmation returned for {name}" and suggest re-reading.           |
| Utterance names an unknown provider      | Print the company's PSP and APM lists from step 4 and ask.                      |
| Utterance has no company                 | Ask: "Which merchant is this for?"                                              |
| Preview diff is empty                    | "No changes needed — already in that state." No PUT.                            |

Never skip a hook, never retry a destructive call automatically, never
write token values to any file other than `.env`.

---

## 10. Multi-company dashboard

When the user asks about more than one company at once — "show PSPs
for Neumi and Oliabo," "which clients still need Braintree live,"
"status across all my merchants," "compare these three" — render a
**matrix** instead of stacking per-company cards.

**Triggers**: utterance names ≥2 companies, says "all companies" /
"my clients," or asks to compare / sort / filter by provider ("who's
live on Stripe," "everyone stuck in underwriting"). Read-only —
writes still go through §6 one company at a time.

**Flow**:

1. Resolve each company name against the slugs loaded from `.env` (§3).
   If any is ambiguous or has no configured key, ask before fetching.
2. For "all companies" / "all merchants" requests, use every
   `FLUID_*_KEY` pair found in `.env` — no need to ask the user.
3. Fetch `/api/companies/{id}/payments_status` for each — parallel where
   possible, one key per company.
4. Build one matrix per provider type (PSPs, APMs):
   - Rows = companies, in mentioned order (or alphabetical for "all").
   - Columns = provider display names. Include only those where at
     least one company is in a non-`not_onboarding` state (unless the
     user named specific providers).
   - Cells = short-label pill (`LIVE`, `CONN.`, `UNDER.`, `INIT.`, `—`).
5. Prefix with a summary strip (total counts per status).

Templates (matrix, summary strip, short-label map) are in
[references/visual-rendering.md](references/visual-rendering.md) under
"Multi-company dashboard" and "Summary strip."

**Size limits**: prefer 4–6 columns; above ~20 companies, use the
plain-text matrix even in rich clients — HTML tables get too wide.

---

## 11. Visual output — HTML vs plain text

Full visual system (color palette, pills, cards, matrix, fallbacks) is
in [references/visual-rendering.md](references/visual-rendering.md).
Short form:

- **Claude Desktop / claude.ai / web surfaces** → HTML templates.
- **Claude Code CLI / terminal / user said "plain"** → emoji-prefix
  plain-text fallback.
- **Unknown** → HTML (degrades to readable source).
- **`yes / no` prompts** → always literal plain text, never wrapped
  in HTML.

One rule: pick one format per response and use it consistently. Don't
mix HTML cards for PSPs with text rows for APMs in the same reply.

---

## 12. Adding a new company

To configure a new company:

1. Get their Fluid company ID (from the root admin UI or by running
   `GET /api/companies` with an existing key for that company).
2. Create a PartnerToken in the company's admin with a company admin role.
3. Add to `.env`:
   ```bash
   FLUID_{SLUG}_ID=<id>
   FLUID_{SLUG}_KEY=<PT-...>
   ```
4. The company is immediately available — no skill changes required.

To verify a key resolves to the right company:
```bash
curl -s "https://api.fluid.app/api/companies" \
  -H "Authorization: Bearer <PT-...>" \
  -H "Accept: application/json"
# Returns: {"company": {"id": ..., "name": "...", ...}}
```
