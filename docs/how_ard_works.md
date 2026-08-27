# How ARD works

ARD in five steps — from describing a resource to using it from a chatbot.

## 1. Describe each resource

Agentic resources come in many forms — tools, Skills, MCP servers, APIs, workflows, and agents. The **[ARD entry](glossary.md#ard-entry)** gives you one extensible way to describe any of them: what it does, who provides it, where it lives, and how a client reaches it.

## 2. Discovery is the hard part

A collection of agentic resources can get large fast — public ones, vendor ones, internal ones. An agent can't feed thousands of schemas into its context window, and a person can't be expected to know which one fits a given task. The job ARD addresses is finding the **right** resource for the task at hand.

## 3. Build a collection

You assemble a collection of agentic resources. It can be **wide open** (anything published on the web), **tightly curated** (an approved, governed set), or anything in between — and you rank it however you like. ARD doesn't dictate what goes into a collection or how a service builds it. The same flexibility applies to *when* you search — at build time, choosing which tools to wire into an agent, or at run time, looking one up mid-task. In practice most enterprises will want the restricted case: discovery scoped to a governed, approved set rather than the open web.

## 4. Put an ARD interface over the collection

ARD defines the search interface a client uses to find the right resource in that collection:

| Endpoint | What it does |
| --- | --- |
| `POST /search` | Find resources by task — *"what can help me do X?"* (required) |
| `POST /explore` | Browse and filter the collection (optional) |
| `GET /agents` | List the collection's entries (optional) |

Any collection exposed through this interface is a **[discovery service](glossary.md#discovery-service)** — an Agent Finder. ARD standardizes how resources are *described* and *searched*; it leaves ranking, hosting, and business model open.

## 5. Reach it from a chatbot

A client — Claude, ChatGPT, Copilot, or Gemini — reaches an Agent Finder through a **Skill** or a **remote MCP connector**. Ask it to find a capability for a task; it searches, presents the matches, and you decide what to install. See **[Connect a chatbot](connect.md)**.
