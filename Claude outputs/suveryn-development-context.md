# Sūveryn — Development Context Handoff

Give this document to a new chat, a developer or Claude Code before starting implementation work on sūveryn. It covers everything decided so far that affects engineering: what is built, the architecture, the schemas, the house rules, and the decisions still open. Business and brand context (positioning, pricing, competitors) lives in a separate Strategic Plan; this document covers what is needed to build.

**Last updated: 12 October 2026.** The first slices of `suveryn-core` are built and running on a development pod (§12). The detailed, always-current engineering record is [`suveryn-core/docs/architecture.md`](https://github.com/suveryn/suveryn-core/blob/main/docs/architecture.md): what exists, the data flow, where confidential data lives, invariants, decisions with their evidence, and known limitations. When this document and that one disagree, that one wins.

---

## 1. What Sūveryn is, in one line

Private AI for organisations whose work can't leave the premises. It is on-premise, open source where it touches client data, air-gap capable, and sold through certified partners. The first market is Belgian notarial offices.

## 2. Repository architecture — live

GitHub org: **github.com/suveryn** (domain-verified against suveryn.com).

| Repo | License | Contents | State |
|---|---|---|---|
| `suveryn-core` | AGPL-3.0-or-later | Engine, chat, RAG, API gateway, chat UI; later the MCP host, official connectors and playbooks; the models manifest | Built (§12) |
| `suveryn-appliance` | Apache-2.0 | OS image, hardening and first-boot provisioning, including the runtime services core depends on but doesn't bundle (PostgreSQL/pgvector, Keycloak, llama-server) | Keycloak theme, production realm and the PDF reader sandbox are built; the OS image is not |
| `suveryn-connector-sdk` | Apache-2.0 | Contract, template and test harness for third-party connector and playbook authors | Empty |
| `suveryn-connectors-registry` | Apache-2.0, no real code | Index only: slug, UUID, version, licence, maintainer and signing-key fingerprint of every connector | Empty |
| `suveryn-brand` | Logo: all rights reserved plus `TRADEMARK_POLICY.md`. Design tokens: **MIT**. Fonts: each under its own SIL OFL. Guidelines: CC BY 4.0 | Logo, wordmark, colour tokens, fonts, brand guidelines | Live |
| `suveryn-docs` | Text: CC BY 4.0. **Benchmark scripts: Apache-2.0** | Install, admin and developer guides, architecture overview, benchmark reports (`benchmarks/`) | October 2026 benchmark published |
| `suveryn-website` | — | The public site | Live; fonts self-hosted (no Google Fonts), strict CSP and security headers |
| `suveryn-tracker` | — | Issues for all repos (labels `area: core`, `area: appliance`, …) | In use (§11) |

**Licensing notes:**
- **Design tokens are MIT** (`tokens.css` is copied into the AGPL core), so they can be reused without AGPL obligations.
- **NVIDIA's proprietary CUDA libraries**, installed with PyTorch, may ship in the appliance image; this was reviewed and accepted.
- **GeForce cards are for on-premise office use only.** NVIDIA's GeForce driver licence forbids datacenter deployment, so a hosted or datacenter installation needs a datacenter-class GPU.

**Not pre-created on purpose:** individual third-party connector and playbook repos (`suveryn-connector-<name>`). They are spun out one at a time, only once someone outside the core team wants to maintain one (n8n's pattern).

**Connector/playbook licensing is not a blanket rule.** Community connectors are typically AGPL alongside the core. Premium connectors sūveryn builds and sells can stay AGPL too and be monetised through certification and maintenance (Red Hat logic), not a closed licence.

## 3. Tech stack — DECIDED and built

| Layer | Choice |
|---|---|
| Backend | Python ≥ 3.12, **FastAPI** + uvicorn, a **uv workspace** (`packages/engine`, `chat`, `rag`, `api-gateway`) |
| Frontend | **React 19 + TypeScript + Vite**, tests with Vitest. It lives at `packages/chat-ui`, not `apps/web`, under the same AGPL boundary as the backend. It builds to static files served on the same origin as the API |
| Model serving | llama.cpp `llama-server` in router mode (several installed models, `--models-max 1` on a 24 GB card) |
| Store | PostgreSQL 16 + pgvector (HNSW) |
| Documents | OCRmyPDF/Tesseract (`ocr_fast`), Docling for layout, bge-m3 embeddings (multilingual) |
| Sign-in | Keycloak 26.8 (OIDC), validated with PyJWT (RS256 only) |
| Icons | Lucide |
| Office files | `docx` and `write-excel-file` in the browser (MIT), loaded on first use |

Why Python: the benchmark validated the whole document pipeline with Python-native tooling, so there is no glue layer. A Node backend and a split backend were rejected.

## 4. Hardware/pipeline benchmark — COMPLETE (October 2026)

Full report: [`suveryn-docs/benchmarks/2026-10-hardware-benchmark.md`](https://github.com/suveryn/suveryn-docs/blob/main/benchmarks/2026-10-hardware-benchmark.md).

**Headline results:**
- **Hardware is viable.** One RTX 4090 (24 GB) is fast enough for interactive use:
  - an 8-page born-digital deed goes from extraction to summary to Q&A in under 30 seconds;
  - a 60-page document gets a one-shot summary in 47–58 seconds.
- **NVIDIA, not AMD.** Everything was built and tuned against CUDA; there is no validated ROCm path.
- **Qwen3.8-27B is the default model.** It made fewer legal errors on real Belgian deeds. **Mistral Small 3.2 24B** is the faster alternative (20–40%), selectable per conversation.
- **`ocr_fast`** is 3.7–8× faster than Docling calling Tesseract per page. It works like this: skip pages that already have text, run OCRmyPDF in parallel, then let Docling read the text layer.

**Hardware profiles (validated):**

| Profile | GPU | CPU | RAM | Disk | Handles |
|---|---|---|---|---|---|
| Development pod | RTX 4090, 24 GB (tested) | 8 vCPU+ | 32 GB (64 GB to test prompt caching) | 60 GB+ | — |
| On-prem Standard (up to ~10 people) | 24 GB, RTX 4090 class, workstation card for 24/7 use | 8 cores (16 gave only 1.3×) | 64 GB | 2 TB NVMe | Documents up to ~60 pages in one pass; 4 concurrent askers |
| On-prem Heavy | 48 GB (**estimate, not tested**) | 16 cores | 128 GB | 2–4 TB NVMe | 60+ page documents, several summaries at once; both models loaded (`--models-max 2`) |

**Findings that shaped the architecture (status now):**
- **Prompt cache and logs are personal data.**
  - Logs: the audit log records kinds, ids and pages only, never text.
  - Prompt cache: llama-server's cache still holds document text unencrypted. **Open** (§11).
- **Heavy jobs are queued, never concurrent.** Ingestion runs as one worker with a queue, now capped per user (§5.6). Summaries-at-upload are not built yet.
- **Numbers can't be trusted without a source.** Built: the model never does arithmetic, and every figure is checked (§5.4).
- **Two OCR issues: a dropped last line, and a garbled cadastral reference.**
  - Covered by the regression harness on a fictional scanned deed (§5.4).
  - Still to validate on more real deeds.
- **Prompt order:** document text first, question last, for the prompt cache. Intermediate files never go to `/tmp`; they stay in a private 0700 work folder.

**Learned since the benchmark (2026-10-11):**
- **GPU memory is tight on 24 GB.** With Mistral loaded (19.6 GB) plus the gateway and the PDF reader, Docling ran out of GPU memory on 11 of 12 pages.
  - Fixed: a page that fails layout is read again on the CPU. Pages still unread put the document in `needs_review`.
  - A larger card, or a fixed GPU budget per service, is the real answer.
- **Reader start-up cost.** A fresh PDF reader process takes about 10 s (model loading). This matters for the per-owner isolation in §5.6.

**Still untested:** 48/32 GB cards; more than 4 concurrent users; AMD; more real scans (handwriting, stamps, rotated pages, Dutch as well as Belgian deeds); the claimed page-length distribution.

## 5. Product architecture

**Two editions:**
- **Sūveryn Open:** free, self-hosted, AGPL, no user limit.
- **Sūveryn Enterprise:** certified builds, premium connectors, multi-node support, SLAs, sold through certified partners.

**Two network modes, both must work:** Connected (outgoing traffic limited to approved destinations by the appliance's own firewall, or allow all) and Air-gapped (including offline updates). Outbound-blocked was dropped in October 2026: Connected with approved destinations covers it. The code respects this throughout:
- models load offline only (`suveryn-fetch-models` fills the cache at set-up);
- FastAPI's `/docs` is off (it loads CDN scripts);
- the UI bundles its fonts and libraries.

**Models:** Qwen3.8-27B default, Mistral Small 3.2 24B alternative; nothing model-specific in code.
- Weights are **never in git.** `suveryn-core/models/manifest.json` holds metadata only (source, sha256, size, licence, min RAM), and the bytes are checksum-verified on the appliance.
- People choose the model per conversation. A switch unloads the current model once running answers finish: about 5 s with the file cached, 26–32 s from a network volume.

**`suveryn-core` layout (actual):**
```
suveryn-core/
├── packages/
│   ├── engine/        # llama-server client; request/answer/citation/calculation schema; guard.py (control tokens,
│   │                  #   AI-addressed text); audit logger; token counts
│   ├── chat/          # grounded answers: passages → numbered excerpts → answer citing [n]; calc.py (server-side
│   │                  #   arithmetic); support.py (each citation checked against its own passage)
│   ├── rag/           # extraction (ocr_fast + Docling, isolated reader process), integrity checks, chunking,
│   │                  #   bge-m3 embeddings, pgvector store, hybrid retrieval, document service (upload queue)
│   ├── api-gateway/   # FastAPI: /v1/chat, /v1/documents, /v1/conversations, /v1/usage, /v1/admin/usage, /health,
│   │                  #   /auth/* (OIDC backend-for-frontend), rate limits; keycloak/ (development realm)
│   ├── chat-ui/       # React/TS chat UI, en/nl/fr, brand assets pinned from suveryn-brand (brand-lock.json)
│   ├── mcp-host/      # placeholder (README only)
│   ├── connectors/    # placeholder (README only)
│   └── playbooks/     # placeholder: schema/ only
├── models/            # manifest.json, scripts/, llama-server presets example
└── docs/architecture.md
```

### 5.1 Legal knowledge & template library — access pattern (not yet implemented)

Surfaced by competitor research (NOT/AI, §10). It adds two capabilities: **legislation and case-law access**, and a **clause/template library**.

**Proposed pattern (unchanged):**
- **Connected:** a live connector to a short, curated list of sources, registered as `type: legal-source` in the registry.
- **Air-gapped:** a signed, periodically refreshed bundle (the same manifest + checksum pattern as model weights).

**The licensing question blocks any engineering work.**
- Official legislation (Moniteur Belge/Justel) is plausibly redistributable, but needs a legal check.
- Commercial providers (Strada Lex, Jura, Jurisquare, Interacta) likely allow at most a customer-side mirror of the customer's own subscription.
- Where neither works, the capability is plainly unavailable when air-gapped.

Related, and buildable without that review: **tracker #22**, Word documents from the office's *own* templates, filled from its documents (§11).

### 5.2 Authentication — BUILT

**How sign-in works:**
- **Backend-for-frontend.** The gateway is a confidential OIDC client (authorization code + PKCE S256, state and nonce checked). It keeps the tokens and gives the browser only an HttpOnly session cookie: `__Host-` prefix, SameSite=Lax, Secure on https.
- **Sign-in state in an AES-GCM cookie** (10-minute lifetime, one use), so a sign-in flood can't fill server memory.
- **CSRF protection:** state-changing requests need an exact `Origin` match.
- **Every `/v1` route requires a session.** Only `/health`, `/auth/*` and `/openapi.json` are public. `/health` returns states only: no addresses or error texts.
- **Identity methods:**
  - Keycloak's own users only: **local accounts as the baseline**;
  - **LDAP/AD federation and TOTP are options an admin enables, not mandatory in code or realm**, so local accounts always work on their own. All three were checked against Keycloak 26.8;
  - social and online IdPs are ruled out (they fail air-gapped).
- **Administrators** have the realm role `suveryn-admin`.
- **Sign-out** ends the gateway session and the Keycloak session. It asks first whether to keep saved conversations.

**In suveryn-appliance:**
- **A branded Keycloak theme** for login, account console and e-mails, in en/nl/fr.
- **A production realm built from the development realm** by `build_realm.py`. It changes:
  - `sslRequired: all`;
  - sign-in and admin events kept **180 days** (decided 2026-10-11);
  - exact redirect URLs, no wildcards;
  - a new client secret per build.

**Belgian eID smart-card login** remains a differentiator to design toward. Offline revocation checking is open (§11).

### 5.3 Token usage tracking — BUILT (tracker #7)

- **Captured in one place:** every model call passes through the engine, which records it. The counts come from llama-server (`prompt_tokens`, `completion_tokens`, `total_tokens`) with a `kind` tag. No content is stored.
- **Storage:** one table of raw rows, aggregated live, with no rollup tiers.
- **End user:** a counter of today's own tokens in the sidebar, and a usage page with a range picker.
- **Administrator:** a usage page per user and for the office, with a **notional cloud cost** at admin-editable rates (per million input/output tokens, USD/EUR/GBP, 0 to 10,000).
- **Informational only:** it never throttles anyone.

### 5.4 Model harness / guardrails — BUILT (tracker #21, #11, #12)

1. **Document content is data, never instructions.**
   - **Control tokens:** `guard.neutralise` breaks chat-template sequences (`<|im_start|>`, `[INST]`, `[SYSTEM_PROMPT]`, …) with a zero-width space in *every* message sent to the model, including excerpts, file names, history and a client's own system message.
   - **Text addressed to an AI** ("ignore all previous instructions", Dutch and French variants, role headers) is detected (`instruction_like`):
     - flagged per page at ingestion (`instruction_like_text`);
     - reported in the answer (`instruction_like_sources`);
     - logged as an audit event.
   - **The grounded prompt** states that excerpts are data, and repeats it right before the question. Mistral followed an injection without that reminder.
2. **Regression harness** (`packages/rag/tests/test_answers_e2e.py`). Every model update runs the real pipeline on a **fictional trap deed** in three forms: born-digital, scanned, and with injected instructions. Cases with real deeds can be added from a private folder on the GPU machine only. It checks:
   - the citation requirement;
   - answer quality;
   - both OCR issues;
   - injection resistance;
   - server-side arithmetic.

   It writes a JSON report per model with no document text, and it compares models.
3. **Suspicious-pattern logging:** the `suveryn.audit` logger records kinds, ids and pages, never text.
4. **No model arithmetic.** The model writes `[[calc: …]]` with figures copied from the excerpts. The server computes exactly in `packages/chat/calc.py`, a recursive-descent parser over Decimal with no `eval`:
   - it refuses mixed or ambiguous number styles;
   - it checks each figure against the cited passages;
   - the UI marks the result as calculated by sūveryn.

   This is *in-process, not via `mcp-host`*. Moving the calculator behind the MCP host is an option once that exists; it was discussed, not decided.
5. **Figures and citations checked:**
   - a figure that is in no passage and is not a calculation's result is flagged ("unverified");
   - each citation is checked against its own passage (`support.py`): figures, dates, years and names in the cited claim must be there, and a name another passage spells differently is flagged.

   These checks work by rule, not by meaning. A second, meaning-based pass is an option (§11).

### 5.5 Documents: ingestion, integrity, retrieval — BUILT

**Ingestion:**
- **`ocr_fast` with refinements:**
  - OCR every page with fewer than 50 characters of text (not `skip_text`);
  - also OCR born-digital pages whose images cover at least 10% of the page, so a pasted-in scan is read;
  - signed PDFs and forms are OCR'd on a flattened private copy.
- **Integrity checks:**
  - completeness: body text the chunker skipped is kept;
  - header/footer rule: furniture is dropped only if it really repeats;
  - **text-layer recovery** for words the layout model dropped;
  - **page coverage** at 95%: below it, the document goes to `needs_review`;
  - `layout_failed` pages put the document in `needs_review`.
- **Text repair:**
  - characters read in the wrong encoding are put right per document, with evidence required: Mac Roman read as Windows-1252 (e.g. "ŽŽn" → "één", Ò…Ó → “…”) and UTF-8 read as Windows-1252;
  - PDFium's line-break hyphen (U+FFFE) becomes a hyphen;
  - **OCR noise** (an upside-down figure read as letters) is left out.
- **Re-upload:** de-duplication is per owner by SHA-256. A copy that was read poorly (in review, over half recovered text, misread characters or recovered noise) is **read again in place, keeping its id**, so saved conversations still point to it.

**Retrieval:**
- 384-token chunks with page provenance;
- **hybrid retrieval** (vector + full-text, RRF);
- small documents (up to 48,000 characters) are given whole, in reading order; larger ones as their best passages up to the same budget.

**Sources in the UI:** a source card marks the sentence a claim rests on, and the figures, dates and names in it. It scrolls to the first mark, per clicked marker.
- This works by word and number overlap in the browser. It is known to be incomplete: paraphrase, another language, numbers in words, abbreviations.
- **Tracker #25** moves it to the server, matched by meaning (bge-m3), with a regression set.

### 5.6 Security posture — BUILT (security review and code review, October 2026)

**The PDF reader (tracker #15)**
- **Isolation:** uploaded PDFs are parsed in a **separate process** whose environment has no secrets. Only validated JSON comes back, never pickle. There are no core dumps, and the reader is killed on a crash or a time-out (30 minutes per document).
- **Sandbox, in suveryn-appliance:** `suveryn-reader-sandbox` runs the reader as its own user, without network, under seccomp, set as `SUVERYN_EXTRACT_WRAPPER`.
  - Without a wrapper the gateway **refuses to read documents** unless `SUVERYN_EXTRACT_UNSANDBOXED=1` (development only).
  - **An appliance must set the wrapper before updating to this core version.**
- **A fresh reader per owner:** a reader taken over by one user's PDF never sees another user's document.
- **Private waiting uploads:** they stay in the gateway's 0600 folder, and only the document being read is in the reader's inbox.
- **Non-dumpable gateway** (`PR_SET_DUMPABLE 0`): a same-user process can't read its `/proc` environment or memory.

**Limits**
- **Rate limits** on the API and on sign-in (tracker #14).
- **Upload queue:** at most 20 waiting documents per user and 200 in all; at most 2,000 pages per PDF; 100 MB per upload.

**Data**
- **Ownership:** every document, job, conversation and usage row belongs to its user. Someone else's looks exactly like a missing one, and de-duplication is per owner (tracker #3).
- **Deleting a document** takes its passages, headings and file name out of every saved conversation. The UI offers to delete those conversations too (tracker #12).

### 5.7 Chat UI — BUILT

- **Grounded chat** with citation markers, source cards and a source list. Citations can be copied and downloaded.
- **Notices:** unverified figures, calculation notes, citation issues, and passages containing text addressed to an AI.
- **Languages:** **en/nl/fr** (tracker #8). Server errors are shown in the interface's language.
- **Saved conversations** per user (tracker #5, #9). Up to the last 40 messages are sent as history; a conversation over 500 turns can't be saved.
- **Model choice** per conversation (tracker #4). A waiting indicator in brand squares shows real pipeline status: searching, loading model, reading, writing (tracker #6).
- **Tables** in answers. An answer exports to **Word**, a table to **Excel**: cells as values, never formulas, with a sources sheet.
- **Layout:** only the conversation scrolls (tracker #23). Light theme, brand-pinned assets.

### 5.8 Appliance first-boot setup screen (not yet implemented)

Surfaced as a real gap: "first-boot provisioning" was described as an automated process (§2, §5.2, §5.6) without ever specifying how a human actually supplies the inputs it needs. Lives in `suveryn-appliance`, not `suveryn-core`.

**Audience (decided):** a user with basic networking/computer literacy — not a total novice requiring a certified partner on-site, and not assuming deep technical skill either. This sits between "anyone can do it" and "only a partner can do it."

**Form:** a web-based setup screen, reached via the appliance's own IP address on first boot, before the rest of the stack is fully configured — the same pattern as consumer/SOHO network appliances (pfSense, TrueNAS, a home router's setup page at its default IP), which already informed the bare-metal (not VM) decision for the image itself.

**Flow (designed October 2026, design canvas "Sūveryn — First-Boot Setup Screen"):**
1. **Console installer** (bare metal, from the USB stick): language and keyboard; hardware check (GPU, memory, TPM 2.0; Secure Boot is not required); target disk, erased and encrypted (#34); model bundles from the stick's `SUVERYN-BUNDLES` partition, signature-checked (#36); network: name (mDNS `.local`) and DHCP, or a fixed address after 30 s without DHCP; summary; install, which also creates the **appliance identity** (UUID and key pair, §8); disk recovery key shown once.
2. **Console banner** after boot: name, address, certificate fingerprint, appliance ID, and the support-agreement status.
3. **Web setup** at `https://<name>.local`: network access (Connected, with approved destinations or allow all; or Air-gapped); first administrator (NIST password rules); certificate (self-signed or own); **support agreement** (appliance ID and fingerprint, register by QR code in the portal, upload the manifest, or skip: administrators are reminded for 14 days, then everyone sees a banner until a valid manifest is uploaded); data and backups (#31, #33); review; provisioning; outgoing-traffic check.

**Security model, stated explicitly rather than left implicit:** during the brief first-boot window, whoever can reach the appliance's local network interface can access this screen — the same trust model pfSense/TrueNAS/a home router use. This is acceptable because the window is short-lived and the flow concludes by setting real admin credentials; it is not acceptable to leave the setup screen reachable indefinitely after initial configuration completes, and the implementation must close it off once setup is done, not just assume nobody will reconnect to it later.

**Branding:** follows the exact same brand rules as the Keycloak theme (§9) — light theme (product, not marketing), the design system's tokens via the same `brand-lock.json` pinning pattern already used in `chat-ui`, UK English / formal Dutch "u"/"uw", no clichés, no em dashes. Copy should use the Sūveryn brand-voice tone profile (§5.4) once that mechanism exists, rather than being hand-written independently of it.

**Stack, to avoid introducing a third toolchain:** React/TS, consistent with `chat-ui` (§3), served by a minimal local backend that can actually write config files and trigger the provisioning script — this can't depend on Keycloak for its own authentication, since setting up Keycloak is one of the things it does.

## 6. Playbook manifest schema (v2.0.0)

A playbook is a persona, the connectors it requires (with scopes), an explicit step graph (not array order), an output format and a mandatory audit config.

**Steps:**
- `entry`: the id of the first step.
- Each step has `next` (the default), or `branches: [{when, next}]` with a `"default"` catch-all.
- `type: "checkpoint"` steps use `on_approve`, `on_reject` and `max_retries`.
- `requires_human: true` is set per step, not globally.

**Rules:**
- The `audit` block is **mandatory**.
- `license_tier` gates which playbooks a customer is entitled to.
- Branch `when` conditions use a restricted expression language (JSONLogic or CEL style), **never `eval()`**.

Not built yet: `packages/playbooks/schema/` holds the schema only. Tracker #24 proposes declarative tone profiles for `persona`, with a sūveryn brand-voice default.

## 7. Connector manifest schema

Every connector, official or third-party, declares an id (slug + UUID), a version, required scopes and a licence. The registry indexes these, and the licensing system checks them. Not built yet.

## 8. Licensing and support — what engineering needs to build

**Locked October 2026** (tracker #35). Replaces all earlier licensing designs. Nothing here is built yet. Only the size of the renewal discount is still open.

### The model in plain terms

1. **Open source:** builds from the repos are free under the AGPL, including open-source connectors and playbooks. No support.
2. **Official appliance image:** built by Sūveryn Labs from stable, tested releases and installed on the customer's own hardware (Sūveryn Labs doesn't supply hardware).
3. **Software assurance and support:** paid per appliance, at least one year, per user with a minimum of 10. A user is an enabled named account; disabled accounts don't count.
4. **Identity:** at installation the appliance creates its own UUID and key pair. The setup screen and the admin dashboard show a QR code and copyable text (UUID plus key fingerprint) to register the appliance in the portal, so nothing has to leave the building as a file.
5. **Manifest:** issued by the portal for that one appliance (UUID and key fingerprint inside, signed by Sūveryn Labs). It holds the number of users, the certified connectors and playbooks, the yearly expiry date and the next quarterly check-in date. The admin uploads it on the appliance. The manifest is optional during setup: without a valid manifest the appliance works normally. For the first 14 days only administrators see a reminder; from day 15 everyone who signs in sees a banner that it runs without a support agreement (no updates, model bundles or support), until a valid manifest is uploaded.
6. **Quarterly check-in:** the appliance shows its usage as a QR code: the weighted average of enabled accounts over the quarter (the average of daily counts), signed with its key. The admin scans it with a phone camera; no app is needed, the portal opens in the browser. A file export is the fallback. The portal compares the number with the contract and invoices a pro-rated top-up if it's higher; there is no overage tolerance. A new manifest only comes back in when something changes (more users, renewal). If a check-in is missed, the interface shows warnings until it's done. Nothing stops.
7. **Yearly expiry:** the admin is warned one month before. After expiry the appliance keeps running with a permanent banner, but without software assurance (no updates, model bundles or certified connectors) and without support. Renewal within 30 days of expiry continues the contract from the original expiry date, at a renewal discount. After 30 days the customer starts over: a new contract at list price.
8. **Support requests:** need a fresh check-in from the appliance (QR code or file), carrying a single-use code from the support request in the portal.
9. **Connectors and playbooks:** certified ones are listed in the manifest by id and fingerprint. Others get a warning, never a block. The office's own playbooks never trigger a warning. Third-party connectors are reviewed by Sūveryn Labs and supported by their creator.
10. **Portal and support roles:** both the customer and the partner can register appliances, request manifests and see check-ins. First-line support is in principle the partner; Sūveryn Labs is second line.
**Visible to everyone (decided):** every deviation from the manifest shows a warning to all users, not only to the admin: no valid manifest after 14 days, more enabled named accounts than the contract, uncertified connectors or third-party playbooks in use, a missed quarterly check-in, and an expired agreement. The office's own playbooks never trigger a warning. Nothing is ever blocked.
11. **Hardware replacement mid-contract:** the contract moves to the new appliance (new UUID); the old UUID is retired.
12. **Tampering:** support is void for a modified installation, until an official release is installed. Protection is light: a read-only, verified system image, reported as "system intact: yes or no" in each check-in, plus a contract clause with an audit right.

### After expiry and renewal

- Everything keeps working for everyone. A permanent banner shows that software assurance and support have ended.
- No updates, model bundles or newly certified connectors are accepted; support requests are refused.
- **Renewal within 30 days of expiry:** the contract continues from the original expiry date (no free gap), at a renewal discount. Sūveryn Labs pays the discount, so the partner's margin is the same for a loyal customer as for a new one.
- **After 30 days:** start over with a new contract at list price, from the day it is signed. No back-payment for the gap, whether the appliance was used or not. The same appliance gets a new manifest; no reinstall.
- Rationale (compared with GitLab, JetBrains, Microsoft): back-dating per customer or per device is neither fair nor enforceable. The one-year minimum and the value of updates (security, models, legal knowledge) are what keep customers renewing.
- Purely a portal and contract rule: the appliance needs no proof about the lapsed period.

### Technical design (for developers)

1. **Installation identity:** UUID v4 and an Ed25519 key pair created at first boot. The private key is stored on the encrypted disk (#34), sealed in the TPM where available. Hardware replacement means a new identity; the portal moves the contract to it.
2. **Registration:** QR code encoding a portal URL with UUID and public key (well under 200 characters). The same data is shown as text. Connected appliances may register directly.
   **Check-in QR:** portal URL whose fragment (`#…`, never sent to web-server logs) carries a compact, signed usage record: UUID, period, daily counts, weighted average, version, "system intact", optional support code. If it doesn't fit a readable QR code, the admin dashboard offers the file instead.
3. **Manifest:** signed by the Sūveryn Labs licence key, verified with the public key built into the image. Holds UUID, key fingerprint, customer, contract number, users, certified connector and playbook ids with fingerprints, `valid_until` (yearly), `checkin_due` (quarterly), issue timestamp. The appliance only accepts a manifest whose UUID and fingerprint are its own. A copied manifest shows up in the portal as two keys for one UUID.
4. **Usage record (QR or file):** UUID, version, period, daily counts of enabled named accounts and their weighted average, active connectors and playbooks, "system intact" status, optional support code, timestamp, signature with the installation key. Counts only: no names, emails or content. The admin sees the contents before the QR code or file is shown.
5. **Clock:** expiry depends on the appliance clock. The appliance stores the latest time it has seen and flags a backwards jump.
6. **Warnings, all shown to every signed-in user as a banner (admins also get details and the fix in the dashboard):** no valid manifest from day 15 after installation (days 0 to 14: admin-only notice); enabled named accounts above the manifest's number (checked daily); uncertified connectors or third-party playbooks active; missed check-in from `checkin_due`; expiry (admin warning from 30 days before `valid_until`, then a permanent banner). Because nothing has to come back in after a check-in, the admin clears that warning by confirming the portal showed it as received; the portal remains the source of truth. Update and bundle installers refuse packages released after `valid_until`.
7. **System image:** read-only and verified (dm-verity); writable partitions `noexec`. No Secure Boot requirement, because the hardware isn't Sūveryn's.
8. **Keys, separate per purpose:** licence manifests, model and update bundles (#36). Rotation by shipping the next key in advance; revocation lists travel in bundles.

### Still open

- **Renewal discount:** a modest fixed percentage (e.g. 10 to 15%) or a price lock. Sūveryn Labs pays it either way. JetBrains dropped its rising continuity discount (20%, then 40%) for new business customers in 2025. A commercial decision; nothing to build differs.

## 9. Brand, design system and house style

**Design system:** https://claude.ai/artifact/5JFW41LpWFEWWFauNwGGCS. The chat UI copies the mark, fonts and `tokens.json` from suveryn-brand at a pinned commit (`brand-lock.json`), and a test fails on drift.

**Not to relitigate:**
- **Lucide** (MIT) for all UI icons.
- **Two themes genuinely differ:** dark is the brand and marketing identity; light is the product UI.
- **Never white text on the accent orange or teal;** use the `on-accent` token. Every text colour passes 4.5:1, measured from OKLCH lightness.
- **No assistant message bubble.** Only the user's turn gets one.
- **Attachments** sit on the user's message as attachment chips, never on the assistant's reply.
- **IBM Plex Mono** is for the wordmark only.

**House style for all copy (UI, docs, commits, PRs):**
- **UK English.**
- **Dutch is formal:** *u/uw*, never *je/jij/jouw*. A test enforces it in the UI.
- **The product name is lower case, "sūveryn",** except at the start of a sentence or when naming the company ("Sūveryn"). A test enforces it in the UI.
- **Errors have no separate red, amber or green.** An error is the accent ink **#C42F00** on the icon, plus an icon and a message. Figures to check get a wavy accent-ink underline, on screen and in Word.

## 10. Reference links

- GitHub org: https://github.com/suveryn
- Issue tracker: https://github.com/suveryn/suveryn-tracker/issues
- Engineering record: https://github.com/suveryn/suveryn-core/blob/main/docs/architecture.md
- Hardware/pipeline benchmark: https://github.com/suveryn/suveryn-docs/blob/main/benchmarks/2026-10-hardware-benchmark.md
- Design system: https://claude.ai/artifact/5JFW41LpWFEWWFauNwGGCS
- Strategic Plan: ask the project owner
- Competitor reference: NOT/AI (https://www.not-ai.be)

## 11. Open decisions and work, prioritised

**Decisions (yours):**
1. **Licensing and support: locked** (§8, tracker #35). Only the renewal discount (fixed percentage or price lock) is open. Bundle signing: tracker #36.
2. **Retention and encryption of llama-server's prompt cache.** It holds document text unencrypted in GPU memory and RAM, and is shared across users (a possible timing side channel). This sits with **encryption at rest:** deleted documents stay recoverable until VACUUM, and crypto-shredding would fix that.
3. **Air-gapped model distribution:** decided for the default model: a signed bundle on a separate exFAT partition of the installer USB (tracker #36). Still open: a customer-side mirror for later models.
4. **CI/CD and signing-key storage** (HSM or secrets manager).
5. **Legal review** of bundling legislation, and of commercial providers' mirroring terms (§5.1).
6. **Offline CRL/OCSP for Belgian eID** (§5.2).
7. **A runtime network-mode flag:** a provisioning-time value any component can read. It surfaced from the login page's "runs entirely on this premises" badge, which may only show when genuinely air-gapped.
8. **Sharing model: tracker #10, a "dossier" (case/matter)** for sharing documents and conversations between colleagues. Today everything belongs to its uploader only, with no roles.
9. **Meaning-based answer checking.** A second model pass that judges whether a cited passage supports a claim's meaning, not just its facts. Is it worth the extra seconds per answer?

**Work (tracker):**
- **#25:** source marking on the server, by meaning, with a regression set (also fixes "art. 3" cutting a sentence).
- **#26:** show ingestion warnings in the document list (text addressed to an AI, restored text). Needs a design choice.
- **#22:** Word documents from the office's own templates, filled from its documents.
- **#24:** tone profiles for playbook `persona`.
- **Appliance:** OS image, provisioning, the reverse proxy (TLS, security headers, static UI), and making sure `SUVERYN_EXTRACT_WRAPPER` is set.
- **OCR validation** on more real deeds: dropped last line, cadastral references, stamps in small images (under 10% of a page, not OCR'd today).
- **Scale limits to revisit when needed:**
  - sessions, rate limits and upload jobs live in the gateway's memory, per process;
  - revocation takes effect at the next token refresh (≤ 5 minutes); Keycloak back-channel logout would make it immediate;
  - the whole-document budget is counted in characters, not tokens.

**Resolved, for reference:**
- Language split and **stack:** FastAPI, uv, React/TS/Vite (§3).
- **GPU vendor:** NVIDIA. **Default model:** Qwen3.8-27B (§4).
- **Development and Standard hardware profiles** (§4).
- **Authentication:** BFF OIDC; local accounts as the baseline, LDAP and TOTP optional; no social IdPs; production realm with 180-day events (§5.2).
- **Token usage tracking** (§5.3).
- **Model harness:** injection handling, regression harness, audit events, server-side arithmetic, per-citation checks (§5.4).
- **PDF reader isolation and sandbox** (§5.6).
- **Licences:** core AGPL-3.0-or-later; design tokens MIT; benchmark scripts Apache-2.0; CUDA libraries in the image accepted; GeForce for on-premise only (§2).

## 12. Development environment (for whoever picks this up)

- **GPU machine:** a RunPod pod with an RTX 4090. Its persistent `/workspace/suveryn-dev` holds the models, scripts, Keycloak and PostgreSQL.
  - The pod is **stopped**, not deleted, when idle. Start it in RunPod; the bootstrap starts PostgreSQL, the model and Keycloak.
  - `start-gateway.sh` starts the gateway. The pod runs without a reader sandbox (`SUVERYN_EXTRACT_UNSANDBOXED=1` in its env file).
  - The chat UI runs locally (`npm run dev` in `packages/chat-ui`), reaching the pod's gateway (port 8000) and Keycloak (8180) over an SSH tunnel.
- **Deploy:** from `main` only, after merge.
- **Test data:**
  - fictional documents in the repository (e.g. `trap_deed.py`);
  - real documents only with the owner's permission, on the GPU machine, in a private 0700 folder, deleted after use; never in git;
  - never print document content or credentials in logs, chats or PRs.
- **Workflow:** one branch and PR per change. Merge only when the owner says so, and check a branch is fully merged before deleting it. Don't touch repository settings, secrets or CI/CD.
