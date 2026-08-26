# Interoperability

ARD is designed as a **superset** of existing agent and tool discovery approaches. It is not a replacement for other registries; rather, it acts as a federated overlay that unites them.

*   **Universal envelope**: Anything can get an AI Catalog "card" — an MCP server, a Skill, an ACP agent, an A2A agent, a traditional REST API, or whatever comes next.
*   **Federated indexing**: Once a card is published, it can be indexed by any ARD discovery service. You don't have to choose between registries; a discovery service can consume all of them, or you can curate your own subset.

---

## How does ARD relate to registries and tool catalogs?

The ecosystem already has many **curated collections of agentic resources**: registries for MCP servers and A2A agents, plugin directories like [Open Plugins](https://open-plugins.com/), and platform tool catalogs from some partners. Each is a **centralized directory** — resources are submitted to it, it owns the canonical list, and clients query that one list. They're useful, but each is an island, with its own onboarding, governance, and reach.

ARD inverts the relationship. Instead of publishing *into* each collection, a publisher describes a resource once on its own domain (`yourdomain.com/.well-known/ard.json`), and any discovery service can index it organically — no central gatekeeper, no per-collection re-registration. Discovery becomes a property of the open web, the way search engines crawl sites, rather than a list owned by one operator.

These collections don't disappear in this model — they become **ARD discovery services**. A registry, plugin directory, or tool catalog can index ARD entries from across the web, apply its own curation and trust policy, and expose the result; clients choose which to query, and they compose. So "ARD vs. a registry" is the wrong axis: ARD is the specification that lets *many* curated collections — public, vendor, and internal — index the same published resource without anyone having to choose just one.

---

## Is ARD a replacement for MCP or OpenAPI?

**No.** ARD is a **discovery protocol (an envelope)**, not an execution mechanism. It wraps existing execution standards (like MCP, A2A, and OpenAPI) using standard and proposed IANA media types so clients can find agentic resources dynamically. Once discovered, the client connects to and invokes the agentic resource using its native mechanism (e.g., JSON-RPC for MCP).

---

## How is ARD different from built-in tool search in AI clients?

They're closely related. At one level, a client's built-in tool search is itself an implementation of agentic resource discovery — scoped to the tools that client already has. It chooses among a known, client-managed set, which works well within that boundary.

ARD describes the same idea more generally, and decouples discovery from any single client. The capabilities a task might need can come from many places — internal systems, vendor services, public catalogs, Skills, MCP servers, APIs, workflows, or agents — and ARD lets a client or organization discover which of them should be available in the first place, rather than that universe being fixed by the client implementation.

The two compose naturally. An ARD discovery service can produce a policy-filtered toolbox that a client's built-in tool search then ranks over, or a client can query the discovery service dynamically at task time. Because discovery is decoupled, ranking and filtering can also draw on signals a single client usually can't see on its own: policy, permissions, provenance, trust, usage history, success rates, cost, latency, region, compliance requirements, and deprecation state.

Decoupling discovery from the client is what makes this useful in practice:

- **Enterprise control** — an organization can decide which resources are approved, and which are *preferred* for a given task, and apply policy, permissions, and compliance rules once, centrally, instead of configuring every client by hand.
- **Federation** — discovery services compose. A company can run its own service that merges internal resources with selected vendor and public sources and expose it as a single endpoint, while still controlling what is included.
- **Portability** — because the discovery layer is separate, the same resources can be found and used across different AI clients and harnesses, rather than being locked to one client's tool universe.
- **Independent evolution** — resources can be added, updated, or deprecated without changing the client; a newly published capability becomes discoverable the moment a service indexes it.

In short: built-in tool search selects among known tools; ARD is the layer that decides which tools should be known — and a client's tool search is one natural way to consume it.

---

## What about the ACP Agent Registry

The list of ACP agents in [ACP's Agent Registry](https://agentclientprotocol.com/get-started/registry) is already structurally close to an ARD manifest. ACP registries can export their directory manifests as standard `ard.json` feeds, enabling instant web-scale discovery for editor-context agents — without those agents having to be re-registered anywhere.
