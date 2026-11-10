<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg?v=2">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg?v=2">
  <img src="assets/banner-dark.svg?v=2" alt="Indra Prasetya, Senior Software Engineer, backend and platform engineering">
</picture>

# Indra Prasetya

### Senior Software Engineer | Backend and Platform Engineering

<p align="right"><img src="https://komarev.com/ghpvc/?username=indraoverflow&style=flat-square&color=gray" alt="profile views"></p>

I am a software engineer working on backend and platform systems. I have been
building software professionally since 2012, most of it in enterprise
environments: data migrations at telecommunications scale, database-heavy
services, and the delivery and monitoring work that keeps them running.

Day to day I work in Go, TypeScript and Python on PostgreSQL. At
[Qansa Solusi Indonesia](https://www.qansa.id) I build systems for clients and
maintain our open-source tooling. The rest of my time goes to developer tools
that remove a measurable cost, which is how
[agentdiet](https://github.com/qansaid/agentdiet) started.

[LinkedIn](https://www.linkedin.com/in/indraoverflow/) |
[GitHub](https://github.com/indraoverflow) |
[qansa.id](https://www.qansa.id) |
[agentdiet.qansa.web.id](https://agentdiet.qansa.web.id)

---

## Engineering profile

- **Enterprise backend.** Service and data layers for systems where a wrong
  number matters, including customer data migration work for Telkomsel, one of
  Indonesia's largest telecommunications operators.
- **Databases and data movement.** PostgreSQL schema design, migrations,
  reconciliation, and the batch jobs around them.
- **Platform and delivery.** Containerised deployment with Docker and Compose,
  NGINX routing and caching, GitHub Actions pipelines, and release automation.
- **Observability.** Metrics, logs and alerting with Prometheus, Loki, Promtail
  and Grafana, including broker health checks that alert when a Kafka cluster
  degrades.
- **Open source.** Maintaining [qansaid](https://github.com/qansaid), where
  agentdiet and Qansa's tooling live, plus merged fixes to third-party projects
  listed below.

---

## Expertise

**Core.** Go, TypeScript and Node.js, Python, SQL and PostgreSQL, Bash.

**Platform and operations.** Docker and Compose, NGINX, GitHub Actions, Linux,
Git, Kafka with TLS and SASL-SCRAM, Prometheus, Loki, Grafana.

**Working knowledge.** Java and Spring Boot, from reviewed and tested changes
to a Spring Boot ERP codebase (pull requests in review upstream).

**Currently exploring.** Kubernetes, infrastructure as code, distributed
systems patterns, and tooling for AI coding agents.

---

## Flagship projects

### [agentdiet](https://github.com/qansaid/agentdiet)

Every AI coding agent loads its instruction files before it reads your request:
`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `copilot-instructions.md`. Those files
are paid for on every call, and most repositories never measure them.

agentdiet is a single static Go binary that measures that cost, keeps always-on
context separate from on-demand material, detects verbatim and near-duplicate
guidance, and fails CI when the always-on figure grows. On a simulated
repository it measured 6,770 always-on tokens at grade C and 711 at grade A, an
89.5 percent reduction. No account, no API key, no network call.

Stack: Go, GitHub Actions, Next.js product site. MIT licensed.
[source](https://github.com/qansaid/agentdiet) |
[site](https://agentdiet.qansa.web.id) |
`go install github.com/qansaid/agentdiet@latest`

### [gha-bill](https://github.com/indraoverflow/gha-bill)

CI bills arrive after the cost is committed. gha-bill reads the workflow files
already in a repository and reports cost per workflow, per month, before the
invoice exists.

The interesting part is modelling what GitHub actually charges: per-job minute
rounding, operating system multipliers, and matrix expansion, computed from
triggers and schedules with no API token. Python CLI with a test suite, and a
CI workflow that runs it.

Stack: Python, GitHub Actions, CodeQL.

### [kafka-security-ssl-sasl](https://github.com/indraoverflow/kafka-security-ssl-sasl) and [kafka-monitoring](https://github.com/indraoverflow/kafka-monitoring)

Operating a Kafka cluster is two problems: proving a broker is healthy, and
seeing what it is doing. These two repositories cover both.

The first is a health checker for brokers behind TLS and SASL-SCRAM, built on
`kafka-broker-api-versions`, with retries and webhook alerts when a broker
fails. The second is a Compose stack that collects metrics and logs with
Prometheus, Loki and Promtail and visualises them in Grafana.

Stack: Bash, Kafka, Prometheus, Loki, Grafana, Docker Compose.

### [consistency-nginx](https://github.com/indraoverflow/consistency-nginx)

A cache cluster only works when the same key lands on the same node, or the hit
rate collapses. This project builds a working demonstration: an NGINX router
using consistent hashing in front of two cache nodes and a backend, with a
script that proves routing is stable across requests.

Stack: NGINX, Docker Compose, Makefile, Shell.

### [backend-wis-mulai-hidup](https://github.com/indraoverflow/backend-wis-mulai-hidup)

Backend for a wedding invitation platform, and the project where most of my
Node.js and PostgreSQL production patterns were exercised end to end:
authentication, media handling, transactional email, and schema migrations.

Stack: Node.js, Express, TypeScript, Prisma, PostgreSQL, JWT, Nodemailer.

---

## Open source contributions

Merged pull requests into repositories I do not own.

Most of it so far is in an open-source bug-bounty toolkit: four merged fixes to
its installer, its HackerOne MCP integration and its documentation, each one
made after reproducing the failure.

<!-- CONTRIBUTIONS:START -->
- **[awarexone/Agentic-Bug-Hunter](https://github.com/awarexone/Agentic-Bug-Hunter)**: fix(install): resolve split repo layout, anchor to script dir, fail loud ([#161](https://github.com/awarexone/Agentic-Bug-Hunter/pull/161), merged 2026-09-28)
- **[awarexone/Agentic-Bug-Hunter](https://github.com/awarexone/Agentic-Bug-Hunter)**: fix(hackerone-mcp): update Team GraphQL query for removed H1 fields ([#164](https://github.com/awarexone/Agentic-Bug-Hunter/pull/164), merged 2026-09-28)
- **[awarexone/Agentic-Bug-Hunter](https://github.com/awarexone/Agentic-Bug-Hunter)**: fix(docs): correct install_tools.sh path, add doc-path regression test ([#163](https://github.com/awarexone/Agentic-Bug-Hunter/pull/163), merged 2026-09-28)
- **[awarexone/Agentic-Bug-Hunter](https://github.com/awarexone/Agentic-Bug-Hunter)**: fix(tools): point _dep_hint fallback at a path that exists ([#162](https://github.com/awarexone/Agentic-Bug-Hunter/pull/162), merged 2026-09-28)
<!-- CONTRIBUTIONS:END -->

Also credited: [garrytan/gstack#4085](https://github.com/garrytan/gstack/pull/4085),
merged 2026-11-06, where my work appears as a `Co-authored-by` trailer on commit
[5e2964d](https://github.com/garrytan/gstack/commit/5e2964d). The pull request
belongs to the maintainer, so it does not appear in the generated list.

---

## Engineering practice

- **Measure the cost before optimising it.** Token budgets, CI spend and broker
  health all start as numbers nobody looked at.
- **Keep failures visible.** Services that report staleness, truncation and
  partial results are easier to operate than services that only report success.
- **Automate the repeatable part.** Migrations, releases and health checks
  should behave the same at 03:00 as they do on a laptop.
- **Write the documentation with the change.** A tool nobody can install is not
  shipped, which is why each repository above carries run and verify steps.
- **Prefer the smallest design that survives production.** Fewer moving parts
  means fewer things to get paged about.

---

## Current focus

- Kubernetes and infrastructure as code, moving from Compose-based deployment
  toward declarative platforms.
- Tooling for AI coding agents, starting with context cost in agentdiet.
- Observability at the level of individual services, not only host metrics.
- Distributed systems patterns, currently consistent hashing and cache routing.

---

## Activity

<a href="https://github.com/indraoverflow">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://streak-stats.demolab.com?user=indraoverflow&theme=dark&hide_border=true&short_numbers=true">
    <source media="(prefers-color-scheme: light)" srcset="https://streak-stats.demolab.com?user=indraoverflow&theme=default&hide_border=true&short_numbers=true">
    <img src="https://streak-stats.demolab.com?user=indraoverflow&theme=dark&hide_border=true&short_numbers=true" alt="GitHub streak: total contributions, current streak and longest streak">
  </picture>
</a>

---

## Contact

- LinkedIn: [indraoverflow](https://www.linkedin.com/in/indraoverflow/)
- GitHub: [@indraoverflow](https://github.com/indraoverflow)
- Company: [Qansa Solusi Indonesia](https://www.qansa.id)
- Product: [agentdiet.qansa.web.id](https://agentdiet.qansa.web.id)

Open to remote backend and platform engineering work.
