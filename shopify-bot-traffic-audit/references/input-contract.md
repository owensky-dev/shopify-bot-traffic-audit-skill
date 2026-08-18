# Audit manifest contract

Create one JSON manifest for every run. The manifest records scope and evidence coverage; it must not contain credentials, raw logs, IP addresses, personal data, or long evidence excerpts.

## Required shape

```json
{
  "schema_version": 2,
  "store": {
    "domain": "shop.example.com",
    "platform": "shopify_hosted",
    "storefront_type": "online_store",
    "timezone": "America/New_York",
    "primary_market": "US"
  },
  "window": {
    "start": "2026-08-01T00:00:00-04:00",
    "end": "2026-08-08T00:00:00-04:00"
  },
  "permission_mode": "browser-authorized-readonly",
  "privacy": {
    "contains_customer_pii": false,
    "ip_handling": "not_collected"
  },
  "sources": [
    {
      "name": "shopify_analytics",
      "layer": "shopify_sessions",
      "access_method": "browser",
      "status": "complete",
      "coverage_start": "2026-08-01T00:00:00-04:00",
      "coverage_end": "2026-08-08T00:00:00-04:00",
      "artifact": "evidence/shopify-human-bot-sessions.png"
    }
  ]
}
```

## Allowed values

- `permission_mode`: `read-only` or `browser-authorized-readonly`.
- `privacy.ip_handling`: `not_collected`.
- Source `layer`: `shopify_sessions`, `measurement`, `behavior`, `ads`, or `commerce`.
- Source `access_method`: `browser`, `export`, or `api`.
- Source `status`: `complete`, `partial`, or `unavailable`.

Every timestamp must be ISO 8601 with a numeric UTC offset. A source marked `complete` or `partial` needs coverage bounds, access method, and an artifact path. Mark missing sources `unavailable`; do not point them at an old artifact.

## Capability interpretation

- `shopify_sessions` supports Shopify's platform-provided Human-or-Bot analysis.
- `measurement` or `behavior` supports browser-session corroboration.
- `commerce` supports revenue impact.
- `ads` plus `shopify_sessions` or `measurement` supports paid-click reconciliation.
- `shopify_sessions`, `measurement`, `ads`, and `commerce` together support a complete paid-traffic audit within hosted-store evidence limits.
- `shopify_sessions` plus `commerce` plus at least one corroborating layer supports a ready hosted-store audit.

Raw request automation is unavailable by design for the supported Shopify-hosted scope. The validator checks structure and source readiness; inspect artifacts before drawing conclusions.
