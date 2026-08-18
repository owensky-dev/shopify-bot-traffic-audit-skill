# Evidence rubric

Classify Shopify-hosted traffic without overstating fraud.

## Keep four questions separate

1. Did Shopify classify the session as Bot?
2. Do other reports suggest automation, tracking failure, or merely low-quality traffic?
3. Did the segment affect paid orders or revenue?
4. Did an advertising platform charge for and confirm invalid traffic?

Evidence for one question does not automatically answer the others.

## Classification rules

### `shopify_classified_bot`

Use only when Shopify Analytics reports `Human or bot session = Bot` for the exact window and segment. Record it as a platform classification, not an independently verified identity.

Do not infer crawler name, intent, maliciousness, or refund eligibility from this label. Shopify Human is not proof that a person controlled the session.

### `suspicious_automation`

Use when at least two independent medium-strength patterns cluster in the same segment, but Shopify does not classify it as Bot or the dimension is unavailable.

Useful patterns include:

- Highly regular timing or navigation sequences across a redacted behavior sample.
- A large platform click or landing-page-view spike concentrated in one placement, country, or device with repeated non-human-looking behavior.
- A persistent Shopify-versus-GA4 or Clarity anomaly isolated to the same referrer, landing page, device, and time range after tracking checks pass.
- An ad platform reports suspected or filtered invalid traffic for the same segment.

Aggregate device, browser, country, zero conversion, or short sessions are never deterministic proof. Without raw request evidence, use at most medium confidence unless a platform confirms invalid traffic.

### `measurement_gap`

Use when the discrepancy is explained more directly by analytics collection or definition differences:

- Redirects strip campaign or click identifiers.
- Consent, tag-manager changes, page errors, slow loads, ad blockers, or browser privacy controls prevent events.
- GA4, Clarity, Shopify, and ad-platform windows or timezones differ.
- Link clicks, landing-page views, and sessions use different definitions.
- Duplicate browser or server events, currency errors, or purchase-tracking gaps distort the funnel.

### `traffic_quality_issue`

Use when traffic appears measurable but has weak commercial intent and evidence does not establish automation. Examples include accidental app clicks, broad targeting, misleading creative, wrong landing pages, deal seekers, and research visits.

### `likely_human`

Use when Shopify reports Human and corroborating behavior shows ordinary continuity, meaningful navigation or product actions, and no material automation signal. This remains a likelihood, not proof of identity.

### `unclassified`

Use when source coverage, time alignment, report availability, or sample size prevents a responsible conclusion.

## Weak signals that never prove bots alone

- Short session or high bounce rate.
- Zero orders, low conversion, or low ROAS.
- Foreign country or unexpected language.
- Direct traffic, `(not set)`, or missing campaign data.
- Mobile-app or Audience Network placement.
- One unusual browser label.
- A discrepancy between two aggregate dashboards.
- Shopify Bot sessions without a matching paid-click segment.

## AI traffic decision table

| Observable visit | Classification | Commercial interpretation |
|---|---|---|
| Shopify labels the session Bot | `shopify_classified_bot` | Automation likely; identity and purpose remain unknown |
| A user-directed agent executes JavaScript and Shopify labels it Human | `unclassified` or `suspicious_automation` with corroboration | May represent genuine user intent |
| A person clicks a link from an AI answer | `likely_human` referral | Treat as ordinary referral traffic unless other evidence disagrees |
| GA4 records an AI-referral session | Not proof of an AI crawler | Usually means a browser followed a referral link |

## Invalid-traffic language

Use these terms precisely:

- `platform_filtered`: The ad platform reports that it filtered or credited traffic.
- `confirmed_invalid_traffic`: The ad platform confirms invalid traffic for the segment.
- `suspected_invalid_traffic`: Evidence justifies an investigation but is not confirmation.
- `traffic_quality_issue`: Traffic converts poorly without sufficient evidence of automation.

Never convert Shopify Bot sessions or suspicious automation directly into a refund amount.
