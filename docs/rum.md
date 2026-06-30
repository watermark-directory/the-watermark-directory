# Browser RUM — Core Web Vitals + JS errors

Browser-side Real User Monitoring ships Core Web Vitals and unhandled JS errors to
Honeycomb via a `/api/rum` Pages Function beacon (Epic
[#961](https://github.com/watermark-directory/the-watermark-directory/issues/961)).

## Architecture

```
browser (web-vitals + error listeners)
  └─ navigator.sendBeacon("/api/rum", JSON)
       └─ POST /api/rum  (Pages Function)
            ├─ kill switch: RUM_ENABLED
            ├─ per-IP rate limit: RUM_RATE_LIMIT KV (60 events / 60 s)
            └─ POST https://api.honeycomb.io/1/events/watermark-browser
                    X-Honeycomb-Team: HONEYCOMB_API_KEY
```

Two kill switches must both be on for events to reach Honeycomb:

| Switch | Where | Effect when off |
|---|---|---|
| `PUBLIC_RUM_ENABLED=true` | Pages build env | script tag omitted from HTML |
| `RUM_ENABLED=true` | Cloudflare dashboard | beacon returns 204 no-op |

Either switch can disable collection without a code deploy.

## Go-live checklist

1. **Create the rate-limit KV namespace** (one-time):

   ```sh
   npx wrangler kv namespace create RUM_RATE_LIMIT
   ```

   Uncomment the `RUM_RATE_LIMIT` block in `web/wrangler.toml` and fill in the printed ID.

2. **Set dashboard vars** (Cloudflare Pages → Settings → Environment variables):

   ```
   RUM_ENABLED = true
   ```

   `HONEYCOMB_API_KEY` is already set for the OTel integration (#959) — RUM reuses it.
   No new credential is needed.

3. **Set build env var** (Cloudflare Pages → Settings → Build & deployments):

   ```
   PUBLIC_RUM_ENABLED = true
   ```

4. **Trigger a new deploy** so the build picks up `PUBLIC_RUM_ENABLED`.

5. **Smoke test** with Honeycomb Live Tail: open `watermark-browser` dataset → filter
   `metric exists` → load a page → LCP/FCP/TTFB events should appear within ~3 s.

## Shared Honeycomb API key

RUM reuses the `HONEYCOMB_API_KEY` provisioned for the OTel integration in #959.
Both the backend (`watermark-backend`) and the RUM beacon (`watermark-browser`) write
to separate datasets within the same Honeycomb team. No new credential is needed.

If you need to scope the key, create a separate write key in Honeycomb and set it as
`RUM_HONEYCOMB_API_KEY` in the dashboard — the Function uses `HONEYCOMB_API_KEY` by
default; add a fallback in `rum.ts` if you split them.

## Querying CWV in Honeycomb

Suggested columns / derived fields for the `watermark-browser` dataset:

| Query | Use |
|---|---|
| `PERCENTILE(value, 75)` where `metric = LCP` GROUP BY `page.path` | p75 LCP by page |
| `PERCENTILE(value, 75)` where `metric = INP` | p75 Interaction to Next Paint |
| `HEATMAP(value)` where `metric = CLS` | Layout-shift distribution |
| `COUNT` where `metric = error` GROUP BY `error.message` | Top JS errors |
| `COUNT` GROUP BY `navigation.type` | Reload vs back-forward vs navigate split |

Good/needs-improvement/poor thresholds are encoded in the `rating` field on each event
(set by the web-vitals library per the Core Web Vitals spec).

## Disabling

- **Instant** (no deploy): flip `RUM_ENABLED` to `false` in the Cloudflare dashboard.
  Takes effect on the next request.
- **Script removal** (requires deploy): unset `PUBLIC_RUM_ENABLED` in the build env
  and trigger a new deploy. The script tag is then omitted from the HTML entirely.

## Rate limiting and cost

`RUM_RATE_LIMIT` caps each IP at 60 events per 60 seconds. The client also caps JS
errors at 5 per page-load to prevent cascade floods. Honeycomb Events are billed per
event — monitor the `watermark-browser` dataset event count in Honeycomb Settings to
track spend.
