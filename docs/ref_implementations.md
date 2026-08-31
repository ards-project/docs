# Reference Implementations

## Hugging Face Discover Tool

The Hugging Face [Discover Tool](https://github.com/huggingface/hf-discover) provides search access to thousands of Skills, ML Applications, and MCP Servers — on Hugging Face - or any other ARD compliant service.

### Hugging Face CLI (`hf`)

`discover` is built into the [Hugging Face CLI](https://github.com/huggingface/huggingface_hub) (`hf`). To get started:

```bash
# Install the Hugging Face CLI tool:
uv tool install huggingface_hub

# Search for resources to train a model
hf discover search "Fine tune a language model"

# Find MCP Servers to generate an image
hf discover search "Generate an image" --json --kind mcp

# Search other registries
hf discover search "Purchase aeroplane tickets" --registry-url <catalog-url>

# Navigate a federated catalog from a website
hf discover navigate <web-url> "Research biomedical datasets"
```

### REST and MCP API Access

Query the Hugging Face catalog service directly via:

  - The REST API at: `https://huggingface-hf-discover.hf.space/search`
  - MCP at: `https://huggingface-hf-discover.hf.space/mcp`

## GitHub Agent Finder

GitHub's Agent Finder is a discovery service for agentic resources — Skills, tools, and MCP servers — reachable over HTTPS at `https://agentfinder.github.com/api/v1`.

### GitHub Copilot

GitHub Copilot can search it directly: add Agent Finder as a remote MCP tool (or as custom instructions), then ask Copilot to find a capability for your task and it returns ranked matches you choose to install. See [Connect GitHub Copilot](connect/github-copilot.md) for the full setup — it uses this same endpoint as its example.

### HTTP API

Call search directly at `POST https://agentfinder.github.com/api/v1/search`. The MCP endpoint is `https://agentfinder.github.com/api/v1/mcp`.

## Cisco AI Catalog

The [AGNTCY Agent Directory](https://dir.agntcy.org) reference implementation of ARD is deployed by the Cisco [AI Catalog](https://ai-catalog.outshift.io).
The catalog can be pulled from [`ai-catalog.outshift.io/.well-known/ard.json`](https://ai-catalog.outshift.io/.well-known/ard.json).
It supports secure verification through trust manifests, so clients can validate publisher identity and resource integrity before use.

### 1. Pull the catalog manifest

```bash
curl -sS https://ai-catalog.outshift.io/.well-known/ard.json | jq '.entries | length'
```

### 2. Discover A2A cards

```bash
curl -sS 'https://ai-catalog.outshift.io/v1/agents?filter=type%3Dapplication%2Fa2a-agent-card%2Bjson' \
	| jq -r '.results[] | "\(.displayName)\t\(.data.card_data.url // .identifier)"'
```

### 3. Search by card type and extract trust details

```bash
curl -sS 'https://ai-catalog.outshift.io/v1/agents?filter=type%3Dapplication%2Fmcp-server-card%2Bjson' \
	| jq -r '.results[] | {displayName, identity: .trustManifest.identity, identityType: .trustManifest.identityType, cardUrl: .data.card_data.url} | @json'
```

## Ora Directory

The [Ora Directory](https://ora.directory) is an ARD discovery service over products and services that agents use on behalf of users, run by [Ora](https://ora.ai). Ora scans each product for agent-readiness — static checks against its docs, llms.txt, registries, and public APIs, plus live agent runs that attempt to use it end to end — and serves the results over the ARD protocol, alongside the MCP servers, Skills, and OpenAPI specs detected on each product, plus payable x402/MPP HTTP endpoints with per-call pricing, indexed from the public Bazaar registry. Every product entry carries its agent-readiness scorecard as a signed trust attestation, so a client can weigh not only whether a resource matches the task, but whether it has been observed to work for agents.

Ora's publisher manifest at [`ora.ai/.well-known/ard.json`](https://ora.ai/.well-known/ard.json) describes Ora's own resources and advertises the registry: its `application/ai-registry+json` entry points at `https://ora.ai/api/ard`, which serves a self-describing descriptor listing the endpoints. The index itself is queried through those endpoints.

### Search and browse

The registry implements the full protocol surface — `POST /search`, `POST /explore`, and `GET /agents` with the spec's `filter` expressions and `orderBy` — and returns `referrals` to peer registries.

```bash
# Find products for a task
curl -sS -X POST https://ora.ai/api/ard/search \
  -H 'content-type: application/json' \
  -d '{"query":{"text":"send transactional email"},"pageSize":5}' \
  | jq -r '.results[] | "\(.displayName)\t\(.url)"'

# Browse just the MCP servers in the index
curl -sS -G https://ora.ai/api/ard/agents \
  --data-urlencode "filter=type = 'application/mcp-server-card+json'" \
  --data-urlencode "pageSize=5" \
  | jq -r '.items[].displayName'
```

### Verify a scorecard

Each result's `trustManifest.attestations[]` references the product's agent-readiness scorecard, signed as a detached Ed25519 JWS and verifiable against the JWKS at [`ora.ai/.well-known/jwks.json`](https://ora.ai/.well-known/jwks.json):

```bash
curl -sS https://ora.ai/api/ard/attestation/resend.com \
  | jq '{subject, score, grade, issuer}'
```

### MCP

Ora is also reachable as an MCP server at `https://ora.ai/api/mcp` (streamable HTTP); its `discover_products`, `get_score`, and `search_capabilities` tools query the same index.

## ANS Finder

The [ANS Finder](https://github.com/agentnameservice/ans) is the discovery service of the open-source **Agent Name Service (ANS)** reference implementation — a registration authority, transparency log, and offline verifier in Go, based on the ANS IETF draft. The Finder tails the registry's lifecycle event feed, projects every ANS-registered agent into a search index, and serves the ARD Registry REST interface: `POST /v1/search` and `POST /v1/explore` (ARDS v0.9). What sets it apart is verifiable registration: every catalog entry's `trustManifest.attestations[]` carries an `ANS-Registration` attestation whose URI resolves to a SCITT COSE receipt on the ANS Transparency Log, so a client can cryptographically verify an agent's registration — independently of the Finder — before invoking it. It validates against this project's [conformance suite](https://github.com/ards-project/ard-spec/tree/main/conformance) (registry mode).

ANS Finder is self-hosted: run the stack locally (or deploy your own) rather than querying a public endpoint.

### Run the demo stack

```bash
git clone https://github.com/agentnameservice/ans && cd ans
scripts/demo/start.sh    # builds + starts the registry :18080, transparency log :18081, finder :18082
scripts/demo/register.sh --v2 translator.example.com    # register an MCP agent and drive it to ACTIVE
```

The Finder polls the registry's event feed (every 2s in the demo) and indexes the agent; a Swagger UI serves the Finder's ARD contract at `http://localhost:18082/docs`.

### Search

```bash
curl -sS -X POST http://localhost:18082/v1/search \
  -H 'content-type: application/json' \
  -d '{"query":{"text":"translator"},"pageSize":5}' \
  | jq '.results[] | {identifier, displayName, url, score}'
```

### Verify an entry against the Transparency Log

Each result's `trustManifest.attestations[]` carries the SCITT receipt URI on the Transparency Log:

```bash
curl -sS -X POST http://localhost:18082/v1/search \
  -H 'content-type: application/json' \
  -d '{"query":{"text":"translator"},"pageSize":1}' \
  | jq -r '.results[0].trustManifest.attestations[0].uri'
```

### Check conformance

```bash
git clone https://github.com/ards-project/ard-spec
ard-spec/conformance/bin/conformance-test registry http://localhost:18082/v1
```

## MCP Gateway Registry

The [MCP Gateway Registry](https://github.com/agentic-community/mcp-gateway-registry) is an open-source (Apache-2.0), self-hostable implementation of ARD that covers both the Publisher and Registry roles, plus federation between registries. It indexes MCP servers, A2A agents, and skills, and serves them over the ARD contract. See [docs/ard.md](https://github.com/agentic-community/mcp-gateway-registry/blob/main/docs/ard.md) for the full description.

### Publisher: pull the catalog manifest

The Publisher role renders a conformant, anonymous `/.well-known/ai-catalog.json` from the registry's records, listing only public and enabled assets. Each entry carries a domain-anchored URN (`urn:air:<publisher>:<namespace>:<name>`), the IANA media type for its kind, and an `https` `trustManifest`.

Note that this implementation currently serves the pre-v0.91 `/.well-known/ai-catalog.json` path rather than `/.well-known/ard.json`; the examples below use the path a live instance answers on today, and `ard.json` support is pending upstream.

```bash
# Against a self-hosted instance
curl -sS https://your-registry.example.com/.well-known/ai-catalog.json \
  | jq '.specVersion, .host.displayName'
```

### Registry: search & browse

The Registry role exposes ARD's search/browse contract under `/api/ard`. Both endpoints are JWT-required and access-scoped: a caller only sees the assets it is authorized to access.

```bash
# Semantic search over the catalog
curl -sS -X POST https://your-registry.example.com/api/ard/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "content-type: application/json" \
  -d '{"query":{"text":"financial data tools","filter":{"type":["mcp_server"],"tags":["finance"]}},"pageSize":10}' \
  | jq -r '.results[] | "\(.displayName)\t\(.score)"'

# Browse all asset types (MCP servers + A2A agents + skills)
curl -sS -X GET "https://your-registry.example.com/api/ard/agents?orderBy=identifier" \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.items[].displayName'
```

Results are ARD `catalogEntry`s plus a `score` (integer 0–100) and `source`. Errors use the ARD `{errorCode, message}` envelope. Federation ingests other registries' `ai-catalog.json` catalogs into a unified local index, selectable per request via the `federation` parameter (`none` / `auto` / `referrals`).

## Nevermined

[Nevermined](https://nevermined.app) is an ARD publisher and the **payment layer** for agentic discovery. Most discovery answers *"what can do this task?"*; Nevermined also answers *"what will it cost, and how do I pay it?"* — every catalog entry names its payment protocol, per-call price, and settlement network, and its Router lets an agent actually **pay** for what it discovers (x402 and MPP, across chains, under a spend cap) without leaving the discovery flow.

Nevermined's publisher manifest at [`api.live.nevermined.app/.well-known/ard.json`](https://api.live.nevermined.app/.well-known/ard.json) is the curated Agent Services Catalog — external x402 / MPP / REST / A2A services, each entry pointing at its callable endpoint. Payment and discovery data ride in JSON-LD extension terms (`@context` + `nvm:catalog` for external services, `nvm:payment` for Nevermined-hosted plans), so a registry can index price, protocol, and network as filter dimensions rather than parsing free-form metadata. Every entry's `trustManifest.identity` is domain-anchored to the publisher.

### 1. Pull the catalog manifest

```bash
curl -sS https://api.live.nevermined.app/.well-known/ard.json | jq '.entries | length'
```

### 2. Discover services and their pay-per-call terms

```bash
curl -sS https://api.live.nevermined.app/.well-known/ard.json \
  | jq -r '.entries[]
      | [.displayName, .["nvm:catalog"].protocol, .["nvm:catalog"].priceLabel, .["nvm:catalog"].network]
      | @tsv'
```

Each entry's `nvm:catalog` carries the payment `protocol` (`x402` / `mpp`), the per-call `priceLabel`, the settlement `network`, the callable `targetUrl`, and per-endpoint pricing — everything an agent needs to decide whether and how to pay *before* it calls.

### 3. Read a Nevermined-hosted agent's pre-signable x402 terms

Nevermined-hosted agents are published per organization, where each paid plan exposes an x402 `accepts` block under `nvm:payment` that a client can pre-sign for the plan's own chain:

```bash
curl -sS https://api.live.nevermined.app/api/v1/organizations/<orgId>/ai-catalog.json \
  | jq '.entries[0]["nvm:payment"].plans[0].accepts[0]'
```

### 4. Verify publisher identity

```bash
curl -sS https://api.live.nevermined.app/.well-known/ard.json | jq '{host, trust: .entries[0].trustManifest}'
```

### Check conformance

```bash
git clone https://github.com/ards-project/ard-spec
pip install jsonschema
ard-spec/conformance/bin/conformance-test manifest https://api.live.nevermined.app/.well-known/ard.json
```
