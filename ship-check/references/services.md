# Services: AI, payments, email, monitoring, uploads, analytics

**Last checked: 2026-11-23**, against each provider's own pages. Plans, limits and menu names
change: open the linked page before quoting a number or a menu path, and tell the owner when
what you see differs from this file.

Read only the sections the project needs.

## Contents

- AI features
- Payments
- Email
- Error tracking and uptime
- File uploads
- Analytics
- Settings and secrets
- Launch-day essentials

---

## AI features

### The one safe pattern

The browser never talks to the AI provider. It calls a route on the site's own server. That
route checks that the visitor is logged in, checks a per-user limit, and only then calls the
provider with a key read from a server-side setting. The key never appears in browser code,
in the repository, or in a setting with a public prefix (`NEXT_PUBLIC_`, `VITE_` and the
like). A spending limit at the provider is the last line of defence.

All three large providers say this in their own docs; OpenAI's wording is that requests
"should always be routed through your own backend server":
https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety

### Moving an AI call from the browser to the server

This is the fix for the most common red finding in AI-built projects.

1. Create a server route in the project (for example `/api/ai/...`) that receives only what
   the visitor typed.
2. Move the provider call, the prompt and the model choice into that route. Read the key
   from a setting without a public prefix.
3. In the route, reject visitors who are not logged in, limit the size of what they can
   send, and apply a per-user rate limit (below).
4. Change the browser code to call the new route.
5. The owner replaces the old key in the provider's console, because it has already been
   exposed, and enters the new one in the settings file and on the host.
6. The owner sets a spending limit (next table).

### Keys and spending limits

| Provider | Where keys are made | Spending limit | What kind |
|---|---|---|---|
| OpenAI | `platform.openai.com` → Organization settings → API keys | Organization settings → Limits (also per project) | A monthly limit that only sends alerts unless "Enforce a hard limit" is switched on. Credits can be prepaid, with auto-recharge on by default. |
| Anthropic (Claude) | `platform.claude.com` → Settings → API keys | Settings → Spend limits → Monthly spend limit | A hard stop: requests fail until the limit is raised or the month resets. Billing is prepaid credits; auto-reload is optional. |
| Google (Gemini) | `aistudio.google.com/apikey` | `aistudio.google.com/spend` → Monthly spend cap | Per project, and it lags by some minutes, so small overages are possible. Google Cloud "budgets" only send alerts and do not stop spending. |

Docs: OpenAI https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform ·
Anthropic https://platform.claude.com/docs/en/api/rate-limits ·
Google https://aistudio.google.com/docs/billing

For current models and prices, send the owner to the provider's pricing page rather than
naming a model: https://developers.openai.com/api/docs/pricing ·
https://platform.claude.com/docs/en/about-claude/pricing · https://aistudio.google.com/docs/pricing

### Gateways (optional)

A gateway sits between the site's server and the AI providers. It is worth suggesting when
the owner wants one key for several providers, a spending limit per key, or a log of requests.

- **OpenRouter**: one key for most major models, automatic fallback between providers, and a
  credit limit that can be set on each key. Prepaid credits. https://openrouter.ai/docs/faq
- **Vercel AI Gateway**: one endpoint and key, request logs, cost tracking, fallbacks, and
  budgets per project or key. The site does not have to be hosted on Vercel.
  https://vercel.com/docs/ai-gateway
- **Cloudflare AI Gateway**: a proxy in front of the owner's existing provider keys that adds
  logging, caching, rate limiting, retries and fallback. The core features are free.
  https://developers.cloudflare.com/ai-gateway/

### Rate limiting

- **Upstash Ratelimit**: a small library for limiting each user in a few lines; works on
  serverless hosts. https://upstash.com/docs/redis/sdks/ratelimit-ts/overview
- **Vercel firewall**: a rule per path, set in the dashboard, on every plan.
  https://vercel.com/docs/vercel-firewall/vercel-waf/rate-limiting
- **Cloudflare**: rate limiting rules in the dashboard, and a rate-limit binding for per-user
  limits inside Workers. https://developers.cloudflare.com/waf/rate-limiting-rules/
- On a server the owner runs themselves, the framework's own rate-limit package is enough.

---

## Payments

Two kinds of provider:

- **Payment processor** (Stripe by default): the owner is the seller and is responsible for
  sales tax in each country they sell to.
- **Merchant of record** (Paddle, Polar, Stripe Managed Payments): the provider is the seller
  on paper and handles sales tax; it costs more per sale and suits digital products.

| Provider | Kind | Notes | Supported countries |
|---|---|---|---|
| Stripe | Processor; "Managed Payments" is its merchant-of-record option for digital products | The most documented. Test keys start `sk_test_`, live keys `sk_live_`; only publishable keys (`pk_`) belong in the browser. https://docs.stripe.com/keys | https://stripe.com/global |
| Paddle | Merchant of record | The sandbox is a separate account with its own keys. https://developer.paddle.com/build/tools/sandbox | https://www.paddle.com/help/start/intro-to-paddle/which-countries-are-supported-by-paddle |
| Polar | Merchant of record | The sandbox is a separate server with separate tokens. https://polar.sh/docs/integrate/sandbox | https://polar.sh/docs/merchant-of-record/supported-countries |
| Lemon Squeezy | Merchant of record | Its site says it is closed to new sign-ups and is shutting down in 2027. Do not recommend it for a new project. | — |

**Check the country first.** None of these is available to sellers everywhere. Before
recommending one, have the owner open the provider's supported-countries page and confirm
their own country is on it. If it is not, the realistic routes are a local payment gateway
in their country or a company registered where the provider operates; say so plainly instead
of recommending something they cannot sign up for.

What must not be skipped, whichever provider:

- **Verify every webhook.** The provider calls the site to say "this payment succeeded".
  Check the signature on that call with the provider's library before trusting it; without
  the check, anyone can send the site a fake "paid" message. Stripe: https://docs.stripe.com/webhooks
- **Grant access from the webhook, not from the browser.** The page the customer returns to
  can be opened by anyone. Only the verified webhook should switch an account to paid.
- **Prices live on the server.** The browser sends which product was chosen; the server
  decides what it costs.
- **Test and live keys stay apart.** Test keys in development, live keys only in the host's
  production settings.

---

## Email

For sign-up confirmations, password resets and receipts. Every provider requires proof that
the owner controls the sending domain: DNS records (DKIM, SPF) copied from the provider's
dashboard into the domain's DNS settings. Without them, mail goes to spam. Using a subdomain
for sending (such as `mail.example.com`) keeps the main domain's reputation separate.

- **Resend**: free plan; simplest setup for JavaScript projects. https://resend.com/docs/add-a-domain
- **Postmark**: small free allowance; known for reliable delivery.
  https://postmarkapp.com/support/article/1046-how-do-i-verify-a-domain
- **Amazon SES**: cheapest at volume, more setup. New accounts start in a sandbox that can
  only mail verified addresses until production access is requested.
  https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html

If the project uses Supabase or Firebase for login, their built-in email is meant for
testing; connect one of the above before launch (see `backend.md`).

---

## Error tracking and uptime

Two different questions: "did something break inside the site?" and "is the site reachable
at all?". A launch needs an answer to both.

- **Sentry**: records errors with the line that caused them; free plan for one person; also
  includes one uptime check. https://docs.sentry.io/product/
- **Better Stack**: uptime checks, a status page and logs; free plan. https://betterstack.com/pricing
- **UptimeRobot**: uptime checks only; generous free plan. https://uptimerobot.com/pricing/

The smallest useful setup: Sentry in the project, plus one uptime check on the home page
that emails the owner.

---

## File uploads

- **Supabase Storage**: the natural choice when the project is already on Supabase. Buckets
  are private by default; a bucket marked "public" lets anyone with the address read the
  file, so use signed addresses for private files.
  https://supabase.com/docs/guides/storage/buckets/fundamentals
- **Cloudflare R2**: S3-compatible storage with no charge for downloads. Private by default;
  serve public files through a custom domain, not the development address.
  https://developers.cloudflare.com/r2/buckets/public-buckets/
- **Amazon S3**: the standard. New buckets block public access by default; leave that on.
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html
- **UploadThing**: the least code for TypeScript projects. Files are readable by address by
  default; check the user in its middleware. https://docs.uploadthing.com/concepts/regions-acl

Whichever is chosen: limit the file types and size on the server, check who is uploading,
and never store uploads inside the code folder on a host that rebuilds it on every deploy.

---

## Analytics

- **Plausible**: no cookies, so no consent banner; paid after a trial.
  https://plausible.io/privacy-focused-web-analytics
- **Umami**: open source, no cookies, free cloud plan or self-hosted. https://docs.umami.is/docs/
- **PostHog**: product analytics and session replay with a free tier; it uses a cookie by
  default, so it needs either its cookieless mode or a consent banner.
  https://posthog.com/docs/libraries/js/persistence

---

## Settings and secrets

- On the owner's computer, secrets live in a settings file (`.env` or `.env.local`) that is
  listed in `.gitignore` and never committed. An `.env.example` with the names and no values
  is committed instead.
- On the host, the same names are entered in the project's environment-variable settings,
  by the owner. Most hosts apply a change only on the next deploy, so redeploy after editing.
- Frameworks send any setting with a public prefix to every visitor. Next.js:
  https://nextjs.org/docs/app/guides/environment-variables
- Use different values for development and production: a separate database, test payment
  keys, a separate AI key with its own limit.
- When several people or several hosts need the same secrets, a secrets manager keeps them in
  one place: Doppler https://www.doppler.com/ or Infisical https://infisical.com/

---

## Launch-day essentials

Whatever the setup, the plan should end with these, each marked done or not needed:

1. No secret appears in browser code, in the repository, or behind a public prefix.
2. Every AI call goes through the site's own server route, which requires login.
3. Each user has a request limit on the AI routes.
4. A spending limit is set at every paid provider, with the hard stop on where it is optional.
5. Production uses live payment keys, everything else uses test keys, and the webhook
   handler verifies signatures.
6. The payment provider supports the owner's country, and it is clear who handles sales tax.
7. The sending domain is verified and a real test email reached an inbox.
8. Error tracking is installed and an uptime check alerts the owner.
9. Upload storage is private unless files are meant to be public.
10. Database backups are on, and one restore has been tried.
11. The domain loads over HTTPS with and without `www`.
