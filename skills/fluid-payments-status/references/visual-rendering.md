# Visual rendering — Fluid Payments Status

Rich inline markup for displaying PSP / APM onboarding status. Used by
`SKILL.md` §5 (read flow), §6d (preview), §6e (success), and §10
(multi-company dashboard).

The templates use inline HTML with hex colors. They render styled in
Claude Desktop, claude.ai web, and any surface that displays
HTML-in-markdown. In terminals (Claude Code CLI), HTML renders as raw
source — use the **plain-text fallback** at the end of this file in
that case, or when the user asks for "text" / "plain" output.

---

## Status color palette

Every pill, border, and cell color derives from a single mapping. All
colors are Tailwind-adjacent hex so they read correctly on light and
dark themes.

| Status            | Hex       | Emoji | UI label              | Used for                    |
|-------------------|-----------|-------|-----------------------|-----------------------------|
| `live`            | `#10b981` | 🟢    | Live                  | done, shipping              |
| `connecting`      | `#3b82f6` | 🔵    | Connecting & Testing  | wired up, QA                |
| `underwriting`    | `#f59e0b` | 🟡    | Underwriting          | with compliance             |
| `pre_onboarding`  | `#8b5cf6` | 🟣    | Initial Setup         | just started                |
| `not_onboarding`  | `#71717a` | ⚪    | Not Onboarding        | inactive / skipped          |

Semi-transparent background convention: append `20` to the hex for a
~12% alpha fill (e.g. `#10b98120`). Solid hex for text and borders.

---

## Status pill (inline)

Use anywhere a status appears in prose, a table cell, or a row.

```html
<span style="display:inline-block;padding:2px 10px;border-radius:999px;background:#10b98120;color:#10b981;font-size:11px;font-weight:600;letter-spacing:0.02em;">LIVE</span>
```

Placeholders:

- `{bg}` — hex + `20` alpha (e.g. `#10b98120`)
- `{fg}` — solid hex (e.g. `#10b981`)
- `{label}` — uppercase UI label (`LIVE`, `UNDERWRITING`, etc.)

---

## Provider row — bordered status card

One card per PSP / APM in a single-company read. The left border and
tint match the provider's current status.

```html
<div style="border-left:3px solid #10b981;background:#10b98110;padding:10px 14px;margin:6px 0;border-radius:4px;">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div>
      <strong style="color:#fafafa;">Stripe</strong>
      <span style="color:#71717a;font-size:11px;margin-left:6px;">PSP</span>
    </div>
    <span style="padding:2px 10px;border-radius:999px;background:#10b98120;color:#10b981;font-size:11px;font-weight:600;">LIVE</span>
  </div>
  <div style="color:#a1a1aa;font-size:12px;margin-top:4px;">ActiveMerchant::Billing::StripeGateway</div>
</div>
```

In-progress providers append a time-estimate row below:

```html
<div style="color:#a1a1aa;font-size:12px;margin-top:4px;">⏱ 5 business days to live</div>
```

---

## Company header card

Rendered once at the top of any single-company view. Shows identity +
rollup metrics (`metrics.psps_connected`, `metrics.apms_enabled`,
`metrics.countries_ready / total_countries` from the API response).

```html
<div style="border:1px solid #27272a;background:#09090b;border-radius:8px;padding:16px;margin:8px 0;">
  <div style="font-size:18px;font-weight:600;color:#fafafa;">Neumi</div>
  <div style="color:#71717a;font-size:12px;margin-top:2px;">Company 1234 · neumi.fluid.app</div>
  <div style="margin-top:14px;display:flex;gap:28px;flex-wrap:wrap;">
    <div>
      <div style="color:#71717a;font-size:10px;text-transform:uppercase;letter-spacing:0.08em;">PSPs Live</div>
      <div style="font-size:20px;font-weight:600;color:#fafafa;margin-top:2px;">3 / 8</div>
    </div>
    <div>
      <div style="color:#71717a;font-size:10px;text-transform:uppercase;letter-spacing:0.08em;">APMs Live</div>
      <div style="font-size:20px;font-weight:600;color:#fafafa;margin-top:2px;">1 / 4</div>
    </div>
    <div>
      <div style="color:#71717a;font-size:10px;text-transform:uppercase;letter-spacing:0.08em;">Countries Ready</div>
      <div style="font-size:20px;font-weight:600;color:#fafafa;margin-top:2px;">1 / 50</div>
    </div>
  </div>
</div>
```

---

## Section heading

Small uppercase label above each provider group:

```html
<div style="font-size:10px;color:#71717a;text-transform:uppercase;letter-spacing:0.08em;margin:16px 0 6px;font-weight:600;">PSPs (4)</div>
```

---

## Diff preview row (write flow)

Old → new, two pills side-by-side. One row per provider in the batched
update.

```html
<div style="border:1px solid #27272a;border-radius:6px;padding:10px 14px;margin:6px 0;">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
    <div>
      <strong style="color:#fafafa;">Stripe</strong>
      <span style="color:#71717a;font-size:11px;margin-left:6px;">PSP</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
      <span style="padding:2px 10px;border-radius:999px;background:#71717a20;color:#a1a1aa;font-size:11px;font-weight:600;">NOT ONBOARDING</span>
      <span style="color:#71717a;">→</span>
      <span style="padding:2px 10px;border-radius:999px;background:#8b5cf620;color:#8b5cf6;font-size:11px;font-weight:600;">INITIAL SETUP</span>
    </div>
  </div>
  <div style="color:#a1a1aa;font-size:12px;margin-top:6px;">⏱ 5 business days to live</div>
</div>
```

After the last row, always end with a literal confirm prompt:

```
Apply these changes? (yes / no)
```

(Plain text. The `yes` check is part of the contract — don't hide it
inside HTML.)

---

## Success row (after PUT)

Same row as the diff preview, but only the new pill, with a green check
prefix:

```html
<div style="padding:8px 14px;margin:4px 0;">
  <span style="color:#10b981;font-weight:600;margin-right:8px;">✓</span>
  <strong style="color:#fafafa;">Stripe</strong>
  <span style="color:#71717a;font-size:11px;margin:0 6px;">PSP</span>
  <span style="padding:2px 10px;border-radius:999px;background:#8b5cf620;color:#8b5cf6;font-size:11px;font-weight:600;margin-left:4px;">INITIAL SETUP</span>
  <span style="color:#a1a1aa;font-size:12px;margin-left:8px;">⏱ 5 business days</span>
</div>
```

Missing-from-response rows use a red warning prefix:

```html
<div style="padding:8px 14px;margin:4px 0;">
  <span style="color:#ef4444;font-weight:600;margin-right:8px;">⚠</span>
  <strong style="color:#fafafa;">Worldpay</strong>
  <span style="color:#a1a1aa;font-size:12px;margin-left:8px;">no confirmation returned — re-read to verify</span>
</div>
```

---

## Multi-company dashboard (matrix)

When the user asks about more than one company at once ("show PSPs for
Neumi and Oliabo," "which of my clients still need Braintree live"),
render an HTML table — companies as rows, providers as columns,
status pills in cells.

One PSP table + one APM table, side by side or stacked. Keep the
pill label short (`LIVE`, `CONN.`, `UNDER.`, `INIT.`, `—`).

```html
<div style="font-size:10px;color:#71717a;text-transform:uppercase;letter-spacing:0.08em;margin:16px 0 6px;font-weight:600;">PSPs</div>
<table style="border-collapse:collapse;margin:8px 0;border:1px solid #27272a;border-radius:6px;overflow:hidden;">
  <thead>
    <tr style="background:#18181b;">
      <th style="text-align:left;padding:8px 12px;color:#a1a1aa;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;">Company</th>
      <th style="text-align:left;padding:8px 12px;color:#a1a1aa;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;">Stripe</th>
      <th style="text-align:left;padding:8px 12px;color:#a1a1aa;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;">Braintree</th>
      <th style="text-align:left;padding:8px 12px;color:#a1a1aa;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;">Worldpay</th>
      <th style="text-align:left;padding:8px 12px;color:#a1a1aa;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;">PayPal PPCP</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-top:1px solid #27272a;">
      <td style="padding:8px 12px;color:#fafafa;font-weight:600;">Neumi</td>
      <td style="padding:8px 12px;"><span style="padding:2px 8px;border-radius:999px;background:#10b98120;color:#10b981;font-size:10px;font-weight:600;">LIVE</span></td>
      <td style="padding:8px 12px;"><span style="padding:2px 8px;border-radius:999px;background:#3b82f620;color:#3b82f6;font-size:10px;font-weight:600;">CONN.</span></td>
      <td style="padding:8px 12px;"><span style="padding:2px 8px;border-radius:999px;background:#71717a20;color:#a1a1aa;font-size:10px;font-weight:600;">—</span></td>
      <td style="padding:8px 12px;"><span style="padding:2px 8px;border-radius:999px;background:#10b98120;color:#10b981;font-size:10px;font-weight:600;">LIVE</span></td>
    </tr>
    <tr style="border-top:1px solid #27272a;">
      <td style="padding:8px 12px;color:#fafafa;font-weight:600;">Oliabo</td>
      <td style="padding:8px 12px;"><span style="padding:2px 8px;border-radius:999px;background:#f59e0b20;color:#f59e0b;font-size:10px;font-weight:600;">UNDER.</span></td>
      <td style="padding:8px 12px;"><span style="padding:2px 8px;border-radius:999px;background:#71717a20;color:#a1a1aa;font-size:10px;font-weight:600;">—</span></td>
      <td style="padding:8px 12px;"><span style="padding:2px 8px;border-radius:999px;background:#8b5cf620;color:#8b5cf6;font-size:10px;font-weight:600;">INIT.</span></td>
      <td style="padding:8px 12px;"><span style="padding:2px 8px;border-radius:999px;background:#71717a20;color:#a1a1aa;font-size:10px;font-weight:600;">—</span></td>
    </tr>
  </tbody>
</table>
```

Short-label map for matrix cells:

| Enum              | Short label |
|-------------------|-------------|
| `live`            | `LIVE`      |
| `connecting`      | `CONN.`     |
| `underwriting`    | `UNDER.`    |
| `pre_onboarding`  | `INIT.`     |
| `not_onboarding`  | `—`         |

Only include provider columns that at least one company has in a
non-`not_onboarding` state — otherwise the table becomes a wall of
dashes. Prefer 4–6 columns; if more providers qualify, split into
multiple matrices (one per provider type, or paginated).

---

## Summary strip (totals)

Above a multi-company dashboard, render a one-line summary with the
aggregate count per status:

```html
<div style="display:flex;gap:12px;flex-wrap:wrap;margin:8px 0 12px;">
  <span style="padding:3px 10px;border-radius:999px;background:#10b98120;color:#10b981;font-size:11px;font-weight:600;">🟢 12 live</span>
  <span style="padding:3px 10px;border-radius:999px;background:#3b82f620;color:#3b82f6;font-size:11px;font-weight:600;">🔵 4 connecting</span>
  <span style="padding:3px 10px;border-radius:999px;background:#f59e0b20;color:#f59e0b;font-size:11px;font-weight:600;">🟡 2 underwriting</span>
  <span style="padding:3px 10px;border-radius:999px;background:#8b5cf620;color:#8b5cf6;font-size:11px;font-weight:600;">🟣 3 initial</span>
  <span style="padding:3px 10px;border-radius:999px;background:#71717a20;color:#a1a1aa;font-size:11px;font-weight:600;">⚪ 19 not onboarding</span>
</div>
```

Counts are summed across both PSPs and APMs unless the user asked for
a specific type.

---

## Plain-text fallback

Use when the user says "text," "plain," "no html," "terminal," or
when the skill is clearly invoked from a CLI context.

Single company:

```
Neumi (id 1234) — Payments Status
PSPs Live 3/8 · APMs Live 1/4 · Countries 1/50

PSPs (4)
  🟢 Stripe          Live
  🔵 Braintree       Connecting & Testing  (5 business days)
  🟢 PayPal PPCP     Live
  ⚪ Worldpay        Not Onboarding

APMs (3)
  🟢 PayPal          Live
  🟡 Klarna          Underwriting          (10 business days)
  ⚪ Affirm          Not Onboarding
```

Multi-company matrix:

```
                 Stripe     Braintree   Worldpay    PayPal PPCP
Neumi            🟢 Live    🔵 Conn.    ⚪ —        🟢 Live
Oliabo           🟡 Under.  ⚪ —        🟣 Init.    ⚪ —
LimbicArc        🟢 Live    🟢 Live     ⚪ —        🔵 Conn.
```

Align on fixed column widths (12–14 chars). Keep labels short.

Diff preview:

```
Company: Neumi (id 1234)
  🟣 Stripe     (PSP)  Not Onboarding → Initial Setup   (5 business days)
  🟡 Klarna     (APM)  Not Onboarding → Underwriting    (10 business days)

Apply these changes? (yes / no)
```

---

## When to use which

| Context                                      | Format                                          |
|----------------------------------------------|-------------------------------------------------|
| Claude Desktop, claude.ai web                | HTML (all templates above)                      |
| Claude Code CLI / terminal                   | Plain-text fallback                             |
| User asked for "plain" / "text" / "no html"  | Plain-text fallback                             |
| Unknown surface                              | HTML first, with a `<details>` block containing the plain-text fallback below |
| Any confirmation prompt (`yes / no`)         | Always plain text — never hidden inside HTML    |

Tokens: HTML output is ~3–4× larger than the plain-text fallback.
For 20+ company dashboards, consider the text matrix even in rich
clients — it scans faster and fits on one screen.
