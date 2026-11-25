# Hosting: where the site runs, domain, HTTPS

**Last checked: 2026-11-23**, against each provider's own pages. Plans, prices, limits and
commands change: open the linked page before quoting a number or a command, and tell the
owner when what you see differs from this file.

Read "Choosing", then only the sections for the hosts in play.

## Contents

- Choosing
- The four questions that rule hosts out
- Managed platforms: Vercel, Netlify, Cloudflare, Firebase, GitHub Pages
- Servers that stay on: Render, Railway, Fly.io, DigitalOcean App Platform
- A server of the owner's own: DigitalOcean Droplet, Hostinger
- Domain and HTTPS
- Letting Claude deploy (official connectors)

---

## Choosing

| The project | Recommend | Alternatives | Why |
|---|---|---|---|
| Only files: plain HTML, or a built single-page app | Cloudflare | Netlify; GitHub Pages for a non-commercial site | Static files on Cloudflare are free without a traffic limit. |
| Next.js, Nuxt, SvelteKit or similar, with server routes | Vercel | Netlify; Cloudflare Workers | These run the framework with no setup. Vercel's free plan is for non-commercial use only. |
| A server that must stay running (Express, FastAPI, Django, Laravel) | Railway or Render, on a paid plan | DigitalOcean App Platform | A few dollars a month for a server that does not sleep. Free plans on these sleep or stop. |
| Data kept in a local file (SQLite) | Railway or Fly.io with a volume, or the owner's own server | Move the data to a hosted database first (`backend.md`) | Most platforms erase local files on every deploy; only a volume or a real server keeps them. |
| A front end (including Flutter web) that talks to Supabase or Firebase | Cloudflare | Firebase Hosting when the backend is Firebase; Netlify | There are only files to serve; the backend is elsewhere. |
| Owner wants one inexpensive server for everything | Hostinger VPS or a DigitalOcean Droplet, with Coolify or Dokploy | — | Cheapest per month and fully theirs, but updates, backups and security become their job. |

Each host offers a short list of regions; open its region list and choose the one nearest
to most visitors, and put the database in the same region.

Free plans are for trying a site, not for running a business on it. If the site takes money
or holds customers' data, plan for the lowest paid plan and say so.

## The four questions that rule hosts out

1. **Does anything need to keep running?** Static files and on-demand functions fit the
   managed platforms. A process that must stay up (a queue worker, a WebSocket server, a
   bot) needs a server that stays on.
2. **Does the project write to its own folder?** A database file or uploaded files saved next
   to the code are erased on the managed platforms. Either move them out (`backend.md`,
   `services.md`) or choose a host with a permanent disk.
3. **How long can one request take?** Managed platforms stop long requests. A slow AI call
   or a large upload may need a streaming response, a background job, or a real server.
4. **Is the site commercial?** Vercel's free plan and GitHub Pages do not allow it.

---

## Managed platforms

No server to look after: connect the code repository and each push goes live.

### Vercel

- **Fits:** Next.js and the other server-rendered frameworks, static sites, scheduled jobs.
- **Does not keep files:** the folder is read-only apart from a temporary area; a SQLite
  file cannot live here.
- **Free plan:** personal, non-commercial use only. Scheduled jobs run at most daily.
- **Deploy:** import the repository in the dashboard, or the `vercel` command. Settings go
  in the project's Environment Variables; a change applies from the next deploy.
- **Watch for:** a time limit on each request and a size limit on what a request can carry;
  pick a region near the visitors and the database.
- **Start:** https://vercel.com/docs/getting-started-with-vercel · Plans: https://vercel.com/pricing

### Netlify

- **Fits:** static sites and server-rendered frameworks through its functions.
- **Does not keep files.**
- **Free plan:** a monthly credit allowance with a hard stop: when it runs out, every site
  on the account shows "not available" until the next month.
- **Deploy:** connect a repository, drag a folder into the dashboard, or the Netlify CLI.
- **Watch for:** short time limits on functions; only the publish folder is deployed.
- **Start:** https://docs.netlify.com/start/get-started-guide/ · Plans: https://www.netlify.com/pricing/

### Cloudflare (Workers)

- **Fits:** static sites best of all; server-rendered frameworks through Workers, with
  official guides for the common ones. Cloudflare now points new projects to Workers rather
  than Pages.
- **Does not keep files.** Data goes to its own storage products or an outside database.
- **Free plan:** static files are free and unlimited; server code has a daily request
  allowance and a very small processing-time allowance per request.
- **Deploy:** `npm create cloudflare@latest`, then `npx wrangler deploy`, or connect a
  repository. Secrets: `npx wrangler secret put <NAME>` or the dashboard.
- **Watch for:** it is not a normal Node server; Express-style servers do not run as they
  are. A custom domain must be managed in Cloudflare.
- **Start:** https://developers.cloudflare.com/workers/get-started/guide/

### Firebase Hosting and App Hosting

- **Fits:** Firebase Hosting serves static sites and single-page apps, and suits a project
  already on Firebase. App Hosting runs Next.js and Angular with server rendering.
- **Free plan:** Hosting has a free monthly allowance, after which the site is switched off
  until the next month. App Hosting needs the pay-as-you-go plan.
- **Deploy:** `firebase init hosting`, then `firebase deploy --only hosting`. App Hosting
  connects a GitHub repository; secrets are set with `firebase apphosting:secrets:set`.
- **Start:** https://firebase.google.com/docs/hosting/quickstart · https://firebase.google.com/docs/app-hosting

### GitHub Pages

- **Fits:** static sites only. No server code, no secret settings.
- **Free plan:** for public repositories. GitHub's terms do not allow running an online
  business, a shop or a commercial service on it. Good for a portfolio, documentation or a
  project page.
- **Deploy:** repository Settings → Pages, from a branch or a GitHub Actions workflow.
- **Watch for:** a project site lives at `<owner>.github.io/<repo>`, so addresses inside the
  site must allow for that path. Turn on "Enforce HTTPS" after adding a custom domain.
- **Start:** https://docs.github.com/en/pages/quickstart ·
  Limits: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits

---

## Servers that stay on

The platform runs the project's server continuously. Better for Express, FastAPI, Django,
Laravel, WebSockets and background workers.

### Render

- **Fits:** web servers, background workers, scheduled jobs, Docker, static sites. PHP only
  through Docker.
- **Files:** erased on deploy unless a permanent disk is added, which is a paid feature and
  limits the service to one copy.
- **Free plan:** web servers go to sleep when idle and take about a minute to wake; the free
  database expires. Not suitable for a launch.
- **Deploy:** connect a repository; settings go in the service's Environment section. The
  server must listen on `0.0.0.0` and the port Render provides.
- **Start:** https://render.com/docs/your-first-deploy · Plans: https://render.com/pricing

### Railway

- **Fits:** any server from a repository or a Docker image, scheduled jobs, WebSockets.
- **Files:** a volume keeps files across deploys, one per service. It is attached only
  while the app runs, not during the build, and a service with a volume cannot run several
  copies. Railway can back volumes up on a schedule and restore them from its dashboard.
- **Free plan:** a short trial, then a very small allowance with sleeping services and no
  custom domain. The lowest paid plan is the realistic starting point.
- **Deploy:** connect a repository or run `railway up`; settings in the Variables tab;
  "Generate Domain" gives an address.
- **Start:** https://docs.railway.com/quick-start · Plans: https://railway.com/pricing

### Fly.io

- **Fits:** anything that runs in Docker; `fly launch` writes the Dockerfile for common stacks.
- **Files:** a volume keeps files, but lives on one machine and is not copied elsewhere, so
  backups are the owner's job.
- **Free plan:** a small monthly allowance with a card on file; going over it bills the month.
- **Deploy:** command line only: `fly launch`, `fly deploy`, `fly secrets set`.
- **Watch for:** machines stop when idle by default and take a couple of seconds to wake.
- **Start:** https://docs.fly.io/getting-started/launch · Plans: https://docs.fly.io/about/pricing

### DigitalOcean App Platform

- **Fits:** Node, Python, Go, Ruby, PHP or Docker apps, plus static sites.
- **Files:** erased on deploy, and volumes are not supported: data must live in a database.
- **Free plan:** a few static sites only. Servers are paid from the first day.
- **Deploy:** connect a repository; settings on the Environment page, with an "Encrypt" box
  for secrets.
- **Start:** https://docs.digitalocean.com/products/app-platform/getting-started/quickstart/

---

## A server of the owner's own

One machine that runs everything: the site, the database, scheduled jobs. The lowest monthly
cost and nothing is erased, but the owner becomes responsible for updates, backups, the
firewall and HTTPS. Recommend it only when the owner said they are comfortable with that.

- **DigitalOcean Droplet:** a plain virtual server.
  https://www.digitalocean.com/pricing/droplets
- **Hostinger VPS:** a virtual server with one-click templates for the tools below.
  https://www.hostinger.com/vps-hosting
- **Hostinger shared hosting:** suits static sites, PHP and WordPress. Node.js apps run only
  on its higher plans, the app folder is overwritten on every deploy, and Python needs a
  VPS. Introductory prices rise at renewal: check the renewal price.
  https://docs.hostinger.com/node.js/overview

**Make a server manageable** with a deploy panel, which gives a dashboard, push-to-deploy
and automatic HTTPS on the owner's own machine:

- **Coolify** (needs about 2 GB of memory): https://coolify.io/docs/get-started/installation
- **Dokploy** (about 2 GB): https://docs.dokploy.com/docs/core/installation
- **CapRover** (about 1 GB): https://caprover.com/docs/get-started.html

The smallest servers have too little memory for these panels; choose a size that meets the
panel's requirement.

The minimum on any server: log in with a key instead of a password, turn on the firewall
with only the web and login ports open, turn on automatic security updates, and schedule a
backup of the database to somewhere off the machine.

---

## Domain and HTTPS

1. **Buy the domain.** It is the owner's purchase, in the owner's name. The simplest route is
   to buy it where its DNS will be managed: from the host itself when the host sells domains
   (several do), or from a registrar such as Cloudflare. Compare the renewal price, not only
   the first year.
2. **Add the domain** in the host's dashboard. The host shows the DNS records to create.
3. **Create those records** where the domain's DNS is managed. Copy them exactly from the
   host: often an `A` record for the bare domain and a `CNAME` for `www`, but some hosts ask
   for a `CNAME` plus a `TXT` record, and then the bare domain only works with a DNS provider
   that supports CNAME flattening (Cloudflare does).
4. **Wait** for the change to spread; it can take from minutes to a day.
5. **HTTPS** is issued automatically by every host in this file once the records resolve.
   Turn on "force HTTPS" where the host offers the switch, and check the site with and
   without `www`.

Changing only these records leaves the domain's email untouched. Moving the whole domain to
another DNS provider means copying the email records (`MX`, `TXT`) first.

Putting the domain's DNS on **Cloudflare's free plan** adds caching and protection against
floods of traffic in front of any host. https://www.cloudflare.com/plans/free/

---

## Letting Claude deploy (official connectors)

These hosts publish an official MCP server or Claude Code plugin, so Claude can create
projects, set up deploys and read logs. Each one signs in through the owner's own browser.
Offer it only when the owner wants Claude to do the deploying, and check the linked page for
the current command first.

| Host | In Claude Code | Docs |
|---|---|---|
| Vercel | `claude mcp add --transport http vercel https://mcp.vercel.com` | https://vercel.com/docs/agent-resources/vercel-mcp |
| Netlify | `claude mcp add --transport http netlify https://mcp.netlify.com/mcp` | https://docs.netlify.com/build/build-with-ai/agent-setup-guides/set-up-claude-code-for-netlify/ |
| Cloudflare | `/plugin marketplace add cloudflare/skills` | https://developers.cloudflare.com/agents/model-context-protocol/mcp-servers-for-cloudflare/ |
| Firebase | `claude plugin marketplace add firebase/firebase-tools`, then `claude plugin install firebase@firebase` | https://firebase.google.com/docs/ai-assistance/mcp-server |
| Render | `/plugin install render@claude-plugins-official` | https://render.com/docs/mcp-server |
| Railway | `/plugin install railway@claude-plugins-official` | https://docs.railway.com/ai/claude-code-plugin |
| DigitalOcean | `claude mcp add --transport http digitalocean --scope user https://mcp.digitalocean.com/mcp` | https://docs.digitalocean.com/reference/mcp/configure-mcp/ |
| Hostinger | `/plugin install hostinger@claude-plugins-official` | https://docs.hostinger.com/hostinger-connector/overview |

A deploy connector can change and delete live things. Keep approving each action by hand,
and never let it act on a project other than the one being launched.

---

## Signing up and paying

Some providers do not serve every country or accept every card. DigitalOcean does not accept
virtual or prepaid cards; Railway accepts only credit cards; Hostinger and GitHub publish
lists of countries they cannot serve. Before the plan depends on a provider, have the owner
confirm they can open an account and pay there.
