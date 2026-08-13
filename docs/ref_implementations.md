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
The catalog can be pulled from [`ai-catalog.outshift.io/.well-known/ai-catalog.json`](https://ai-catalog.outshift.io/.well-known/ai-catalog.json).
It supports secure verification through trust manifests, so clients can validate publisher identity and resource integrity before use.

### 1. Pull the catalog manifest

```bash
curl -sS https://ai-catalog.outshift.io/.well-known/ai-catalog.json | jq '.specVersion, .host.displayName'
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

Ora's publisher manifest at [`ora.ai/.well-known/ai-catalog.json`](https://ora.ai/.well-known/ai-catalog.json) describes Ora's own resources and advertises the registry: its `application/ai-registry+json` entry points at `https://ora.ai/api/ard`, which serves a self-describing descriptor listing the endpoints. The index itself is queried through those endpoints.

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

## MCP Gateway Registry

The [MCP Gateway Registry](https://github.com/agentic-community/mcp-gateway-registry) is an open-source (Apache-2.0), self-hostable implementation of ARD that covers both the Publisher and Registry roles, plus federation between registries. It indexes MCP servers, A2A agents, and skills, and serves them over the ARD contract. See [docs/ard.md](https://github.com/agentic-community/mcp-gateway-registry/blob/main/docs/ard.md) for the full description.

### Publisher: pull the catalog manifest

The Publisher role renders a conformant, anonymous `/.well-known/ai-catalog.json` from the registry's records, listing only public and enabled assets. Each entry carries a domain-anchored URN (`urn:air:<publisher>:<namespace>:<name>`), the IANA media type for its kind, and an `https` `trustManifest`.

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
