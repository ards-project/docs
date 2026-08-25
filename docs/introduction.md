# Agentic Resource Discovery Specification

AI clients are no longer limited to what the model knows. They can use external capabilities — tools, Skills, MCP servers, APIs, workflows, and other agents. We call these capabilities **[agentic resources](glossary.md#agentic-resource)**.

The number of agentic resources is already growing quickly. Some are public, some come from vendors, some are built inside companies; some are narrow tools for a single task, and others are agents or workflows that know how to get something done. That creates a simple problem: **how does an AI client know what is available?**

Today the answer is mostly manual. A user, developer, or IT admin has to find the agentic resource, judge whether it is useful and trustworthy, connect it to the client, and keep that wiring current. That works when there are a handful of well-known tools. It breaks down when every product, team, vendor, and organization is publishing agentic resources of its own.

The bottleneck is no longer invocation. It is **discovery**. A client cannot use a capability it does not know exists, a user cannot ask for an agentic resource they have never heard of, and an enterprise cannot expect every employee to know which internal tools, approved vendor services, and private workflows apply to each task.

This is the problem the **Agentic Resource Discovery Specification (ARD)** solves. ARD lets a client ask one question: *what agentic resource can help with this task?* The answer is a set of matching capabilities: what each one does, who provides it, where it lives, and how the client can reach it.

ARD only handles discovery. The client invokes the agentic resource it selects through that agentic resource's own mechanism — MCP, an API, an agent framework, a workflow system, or something else. ARD sits *before* invocation; it helps the client decide which capability to use. *What* to search over, *when* to search, and *what to do* with the results returned are all choices left to the designer of the system.

ARD is not a product. Any number of [discovery services](glossary.md#discovery-service) can implement it — **GitHub's [Agent Finder](https://github.com/agentfinder)**, **Hugging Face's [Discover](https://github.com/huggingface/hf-discover)**, and the self-hostable **[ANS Finder](https://github.com/agentnameservice/ans)** are three such services. The point is that an agentic resource published once should be discoverable by many clients, and a client should be able to find useful agentic resources well beyond the small set it already knows about.

To see how that works in practice, read **[How ARD works](how_ard_works.md)**.
