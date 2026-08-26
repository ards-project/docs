# Frequently Asked Questions (FAQ)

## Is ARD only for run-time, open-ended discovery?

**No** — and this is the most common misconception. ARD is a discovery *protocol*; it deliberately does **not** dictate **when** discovery happens or **what** it searches over.

- **When — build time *or* run time.** Discovery can happen at build time (a developer or pipeline choosing which tools to wire into an agent) or at run time (an agent looking up a capability mid-task). The request is identical.
- **What — curated *or* open.** The corpus can be a curated, closed set — an enterprise's approved tools, a single vendor's catalog, an explicit registry — or an open, web-scale index. In fact, **most enterprises will want to restrict the searched catalog to an approved, governed set of tools**, not the open web — and ARD serves that case just as directly. The discovery service decides what it indexes and serves; ARD is the same protocol over any of them.

Some partners' first ARD integrations are build-time discovery against a curated tool catalog — exactly as valid an ARD use as open-ended run-time discovery across the public web.

The whole point is **one open way to ask "what is available for this task?"** You ask the same way regardless of *when* you ask or *what* you ask against, and the discovery service answers from whatever corpus it curates. ARD is neither run-time-only nor open-ended-only.

---

## How does discovery reduce context window usage?

Traditional tool selection requires stuffing every available schema into the system prompt. ARD moves this calculation outside the LLM into a dedicated discovery service (`POST /search`). The orchestrator queries the service with natural language, and it returns only the top two or three most relevant schemas to inject into the prompt. You still spend tokens on those few — discovery doesn't eliminate context cost, it shrinks it from thousands of candidate tools down to a handful.

---

## Do I need to register my agentic resources on a central directory?

**No.** You have absolute publishing sovereignty. You host `ard.json` on your own domain (`yourdomain.com/.well-known/ard.json`) to advertise your agentic resources. Any compliant discovery service can find and index your endpoint organically, without requiring permission.

---

## Where does trust come from in ARD?

**From the curation of the registry, not from the protocol.** ARD does not make any agentic resource trustworthy — it gives publishers a way to *assert* verifiable identity and provenance, and clients a way to *verify* it. The actual trust decision lives in two places the specification does not own: the **registry that curates what it indexes and serves**, and the **client that checks the signals before invoking**. ARD's job is to communicate trust, not to confer it.

---

## What trust signals can ARD communicate?

The specification's role here is narrow and deliberate: it gives a publisher a **mechanism to assert verifiable claims**, and a registry or client a **standard way to check them**. ARD itself verifies nothing and vouches for no one. An entry can carry:

- **Domain-anchored identity** — a mechanism to declare a publisher domain in the entry's URN (`urn:air:acme.com:...`), so identity is rooted in DNS rather than a self-asserted label and can be checked by whoever consumes the entry.
- **Verified publishers** — a mechanism for a publisher to *demonstrate* they are who they claim: a `trustManifest.identity` (e.g. `did:web`, SPIFFE, or an Agent Name Service (ANS) identity) that a registry or client cryptographically verifies against the publisher's domain. The protocol carries the claim; the registry or client performs the verification.
- **Signed metadata** — a mechanism to attach a detached JWS `signature` over the trust manifest, so a client can confirm the record was not altered in transit or by an intermediary.
- **Provenance** — a mechanism to declare lineage (`derivedFrom`, `publishedFrom`) that records where a resource came from.
- **Attestations** — a mechanism to reference verifiable compliance artifacts (SOC2, HIPAA, GDPR, …) so they can be fetched and checked.

In every case ARD *enables the communication* of a trust signal. Whether the signal checks out, and what weight to give it, is the registry's and the client's decision — not the protocol's.

---

## How does ARD relate to the Agent Name Service (ANS)?

They are complementary. ARD focuses on task-based discovery — given a job, which agentic resource fits and where to reach it — across many kinds of resource. The Agent Name Service (ANS) focuses on secure naming and identity: a DNS-inspired directory where an agent's name resolves to a PKI-verified (X.509) identity. The two reinforce each other — discovery is only useful if you can trust the identity behind a result.

ARD is built to carry that identity rather than reinvent it. A catalog entry's `trustManifest.identity` is an open field: alongside `did:web` and SPIFFE, it can reference an ANS identity, so a registry or client can resolve and verify the publisher through ANS before invoking. ARD communicates the claim; ANS is one of the mechanisms a consumer uses to verify it.

In short: find the resource with ARD, and trust the name behind it with ANS.

---

## What makes a registry trustworthy?

A registry is a **trust boundary defined by its curation policy** — what it chooses to index, whom it verifies, and what it refuses to serve. A curated registry vouches for what it returns; an enterprise registry serves only internally approved resources; a vendor registry exposes one ecosystem. Clients decide which registries to query, and registries compose, so an organization can merge its own curated answer set with an upstream one. The protocol carries the evidence; the registry supplies the judgment.

---

## Does ARD verify that a tool or agent is safe?

**No — and it does not claim to.** Safety is not a property a discovery protocol can compute. What ARD does is let the relevant facts travel so others can judge. It enables a publisher to **communicate a verifiable identity** (a domain-anchored URN), to **show they are a verified publisher** (a `trustManifest.identity` such as `did:web` or SPIFFE that a registry or client checks against their domain), to ship **signed metadata** (a detached JWS signature proving the record is unaltered), and to declare **provenance** for where the resource came from. The safety call is then made by the **registry that curated the result** and the **client that verifies these signals** before invoking — not by the protocol. The relevance `score` returned by a search is *relevance only* and **MUST NOT** be read as a trust, compliance, or safety rating.

---

## Could ARD make it easier for agents to discover malicious tools?

Discovery is only as permissive as the registry you ask. Because **whoever runs the registry controls the answer set**, a curated or enterprise registry returns only resources it has vetted — a bad actor cannot inject an entry into a registry that did not choose to index it.

ARD also makes impersonation harder than the status quo, on several concrete fronts:

- **Identity** is anchored to a publisher's domain (`urn:air:google.com:...`), not a self-asserted label.
- **Verified publishers**: a registry MUST verify that a manifest is actually hosted on — or cryptographically bound (via `did:web`/SPIFFE) to — the domain it claims, so a manifest on `untrusted.com` cannot pose as `urn:air:google.com:...`.
- **Signed metadata** lets a client confirm a record was not altered in transit, and **provenance** lets it trace where a resource came from.

Compared with today's ad hoc wiring — copy-pasted endpoints with no identity or provenance — ARD raises the floor by giving every result a verifiable origin. It does not, on its own, decide what is safe; it **communicates the identity, verification, and provenance signals** that let curated registries and clients refuse what is not.

---

## How can I give feedback?

ARD is being developed in the open, and feedback is welcome. The best way to suggest changes, report a problem, or ask a question about the specification is to **open an issue on GitHub**: [github.com/ards-project/docs/issues](https://github.com/ards-project/docs/issues).
