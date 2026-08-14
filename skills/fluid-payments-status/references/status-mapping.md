# Payments status — mapping reference

Lookups and constants for `skills/fluid-payments-status/SKILL.md`.

All tables are copied from the source of truth in the Fluid monorepo:
`apps/fluid-admin/components/views/PaymentsStatusView/constants.ts`
and `apps/fluid-admin/networking/payments-status.api.ts`.

If these drift from production, update the monorepo files first, then
mirror the change here and bump `metadata.version` in the parent SKILL.md.

---

## Status enum

Five values; the API accepts exactly these strings:

| Enum              | UI label               | Badge color |
|-------------------|------------------------|-------------|
| `not_onboarding`  | Not Onboarding         | gray        |
| `pre_onboarding`  | Initial Setup          | amber       |
| `underwriting`    | Underwriting           | amber       |
| `connecting`      | Connecting & Testing   | amber       |
| `live`            | Live                   | green       |

Source: `payments-status.api.ts:6-12`,
`PaymentsStatusView/constants.ts:380-425`.

---

## Utterance → status mapping

Heuristic for parsing operator prose. Always confirm the mapped value
with the user before writing.

| Phrase hint                                                        | Enum              |
|--------------------------------------------------------------------|-------------------|
| "not onboarding," "disabled," "not setting up," "skip"             | `not_onboarding`  |
| "in onboarding," "starting," "initial setup," "just started,"      | `pre_onboarding`  |
| "kicked off," "beginning the process"                              | `pre_onboarding`  |
| "sent forms," "underwriting," "under review," "awaiting approval," | `underwriting`    |
| "submitted," "with compliance," "with the processor"               | `underwriting`    |
| "ready to test," "testing," "connecting," "wired up,"              | `connecting`      |
| "integrating," "in integration," "in QA"                           | `connecting`      |
| "live," "done," "ready for <Company>," "good to go," "shipped"     | `live`            |

---

## PSP adapter_class → display name

The backend response identifies PSPs via `adapter_class`. Use
`display_name` from the response when present; fall back to this
table otherwise.

| `adapter_class`                                    | Display name     |
|----------------------------------------------------|------------------|
| `ActiveMerchant::Billing::StripeGateway`           | Stripe           |
| `ActiveMerchant::Billing::BraintreeGateway`        | Braintree        |
| `ActiveMerchant::Billing::WorldpayGateway`         | Worldpay         |
| `ActiveMerchant::Billing::CheckoutV2Gateway`       | Checkout.com     |
| `ActiveMerchant::Billing::NmiGateway`              | NMI              |
| `ActiveMerchant::Billing::PaypalRestGateway`       | PayPal (PPCP)    |
| `ActiveMerchant::Billing::NuveiGateway`            | Nuvei            |
| `ActiveMerchant::Billing::PlatpayGateway`          | Platpay          |

Source: `ADAPTER_TO_MERCHANT` in `constants.ts:134-142`,
`MERCHANT_NAMES` in `constants.ts:289-298`.

---

## APM integration_class → display name

APMs use `integration_class`. Note that some APMs have multiple backend
class names for the same logical method (e.g. Klarna / KlarnaCitcon).

| `integration_class`  | Display name        |
|----------------------|---------------------|
| `Paypal`             | PayPal              |
| `Klarna`             | Klarna              |
| `KlarnaCitcon`       | Klarna              |
| `Affirm`             | Affirm              |
| `Bread`              | Bread               |
| `Venmo`              | Venmo               |
| `PaypalPayLater`     | PayPal Pay Later    |
| `GCashCitcon`        | GCash               |
| `AliPayCitcon`       | Alipay              |
| `UPIIndiaCitcon`     | UPI India           |
| `OxxoDlocal`         | OXXO                |
| `IdealPpro`          | iDEAL               |

Source: `INTEGRATION_CLASS_TO_APM` in `constants.ts:328-342`,
`APM_NAMES` in `constants.ts:303-323`.

---

## `onboarding_time_estimate` format

Plain string. Accepted values:

- `"1 business day"` — exactly one day
- `"N business days"` — `N >= 2`
- `null` / omit the key — for `not_onboarding` and `live`

Parsing/formatting mirrors the admin drawer:

```ts
// onboarding-management-drawer.tsx:76-83
function parseDays(value) {
  if (!value) return null;
  const m = value.match(/^(\d+)/);
  return m?.[1] ? parseInt(m[1], 10) : null;
}
function formatDays(days) {
  return `${days} business day${days === 1 ? "" : "s"}`;
}
```

Ask the user:

> Days until live? (e.g. 3, 5, 10, or 'skip')

- A plain integer N → `"N business day"` / `"N business days"`
- `skip` → omit the field from the update payload

---

## `payment_account_id` fallback

The admin drawer uses this fallback at
`onboarding-management-drawer.tsx:290`:

```ts
payment_account_id: provider.payment_account_id ?? provider.id
```

Match that behavior exactly. `null` on a provider response means the
provider has not been materialized as a `PaymentAccount` row yet;
using `provider.id` still addresses the same record server-side.

---

## PUT body shape

```json
{
  "updates": [
    {
      "payment_account_id": 87,
      "onboarding_status": "pre_onboarding",
      "onboarding_time_estimate": "5 business days"
    }
  ]
}
```

- `updates` — array, required, min length 1
- `payment_account_id` — required per item
- `onboarding_status` — optional; omit to leave unchanged
- `onboarding_time_estimate` — optional; omit or `null` to clear

Multiple providers for the same company go into one `updates` array,
one request.

Source: `updatePaymentsStatus` + `updateResponseSchema` in
`payments-status.api.ts:111-114, 221-230`.
