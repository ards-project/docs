# How to add ARD support to your agent

This guide is for developers building an AI **client** — an orchestrator, agent,
or harness — that should **discover agentic resources at runtime** instead of
having its tools hardcoded. With ARD, your client asks a discovery service
*"what is available for this task?"*, picks a resource, and connects to it over
that resource's own mechanism.

You want this when your agent needs capabilities — MCP servers, A2A agents,
Skills, APIs — that aren't wired in ahead of time, and you want that set to stay
current without re-shipping the client.

Already using a major chatbot? For Claude, ChatGPT, GitHub Copilot, Microsoft Copilot, and Gemini we provide ready-made connectors — see [Connect a chatbot](connect.md). You're welcome to build on or improve those. This guide is for when you have your own client and want to add ARD support directly.

## What a client does

1. Hold a list of discovery-service endpoints it is allowed to query.
2. Turn the user's task into a search and send it to those services.
3. Rank results and, optionally, federate across services.
4. Verify trust before using anything.
5. Connect to the chosen resource over its native mechanism and use it.

## Step 1 — Configure discovery endpoints

A client never invents where to look. Keep a configured list of discovery
services (registries / [Agent Finders](https://github.com/agentfinder)) it may query — public, vendor, or your
organization's internal one — and let the operator decide what is trusted. The
[connectors](https://github.com/ards-project/connectors) repo's `agent-finders.json`
is one example of this pattern.

## Step 2 — Search

Send the user's intent to a discovery service's `POST /search` endpoint. `text`
carries the natural-language need and `filter` narrows by structured fields, both
inside `query`; `federation` and `pageSize` are root-level:

```json
POST https://your-discovery-service/search

{
  "query": {
    "text": "book me a flight to Tokyo",
    "filter": { "type": ["application/mcp-server+json"] }
  },
  "federation": "referrals",
  "pageSize": 3
}
```

- **`query.text`** — required; the task in plain language.
- **`query.filter`** — optional structured constraints (`type`, `tags`,
  `capabilities`, `publisher`, `trustManifest.*`, …). Within a key, values are
  OR'd; across keys, AND'd.
- **`federation`** — `auto` (the service merges upstream results), `referrals`
  (the service returns other services for you to query yourself), or `none`.
- **`pageSize` / `pageToken`** — paging (default 10, max 100).

## Step 3 — Read the response

You get back ranked catalog entries — each carrying the schema and endpoint you
need — plus optional referrals:

```json
{
  "results": [
    {
      "identifier": "urn:air:acme.com:travel:concierge",
      "displayName": "Travel Concierge",
      "type": "application/mcp-server+json",
      "url": "https://api.acme.com/mcp/travel.json",
      "score": 95,
      "source": "https://registry.acme.com/api/v1/"
    }
  ],
  "referrals": [
    {
      "identifier": "urn:air:example.org:registry",
      "type": "application/ai-registry",
      "url": "https://finder.example.org/search"
    }
  ]
}
```

Note that `score` (0–100) is a semantic relevance ranking from the discovery
service. Your client **MUST NOT** read it as a trust, compliance, or safety
rating — do that independently (Step 4).

## Step 4 — Verify trust before using anything

Before connecting to or invoking a discovered resource, verify the publisher:

1. **Extract the domain** — parse the FQDN authority from the URN identifier
   (`urn:air:acme.com:travel:…` ➜ `acme.com`).
2. **Verify identity** — fetch the manifest and confirm the
   `trustManifest.identity` (e.g. a SPIFFE ID or `did:web`) is bound to that
   domain.
3. **Audit compliance** — check the `attestations` array (SOC2, HIPAA, GDPR, …).
4. **Verify the signature** — validate the detached JWS over the trust manifest
   to confirm the record wasn't altered in transit.

Trust is your decision (and the registry's). The specification only carries the
evidence; it never vouches for a resource on its own.

## Step 5 — Federate (optional)

With `federation: "referrals"`, the response lists other discovery services in
`referrals`. Follow the ones you trust by issuing the same search to their `url`
and merging the results yourself. `federation: "auto"` pushes that merge onto the
service; `none` keeps it local. You control the topology.

## Step 6 — Connect and use

Discovery tells you *which* resource fits and *where* to reach it; you then
connect over that resource's own mechanism:

- **`application/mcp-server+json`** — fetch the artifact (`url`) or read inline
  `data`, then speak MCP (JSON-RPC) to the server.
- **`application/a2a-agent-card+json`** — load the agent card and use A2A.
- **`application/ai-skill`** — install or load the skill.
- **A traditional API** — call it per its OpenAPI / REST description.

Load only the **selected** resource's schema into your model's context. That is
the point of discovery-first: the model sees the few tools that matter for the
task, not thousands.

## Minimal example

```bash
curl -s https://your-discovery-service/search \
  -H 'content-type: application/json' \
  -d '{"query":{"text":"summarize a PDF"},"pageSize":3}' \
  | jq '.results[] | {displayName, type, url, score}'
```

Pick a result, verify its `trustManifest`, fetch its `url`, and connect over the
resource's own mechanism.
