# How to publish

Exposing your agentic resources (MCP servers, Skills, ACP agents, APIs) to ARD discovery services is a simple three-step procedure.

This guide is about publishing on the public internet so that public discovery services can crawl and index your resources. Publishing makes you discoverable — it does not guarantee that any particular ARD-implementing service will find or index you; each service decides for itself what it includes. Inside an enterprise, agentic resources are often collected through other workflows entirely — an internal registry, a curated inventory, or a vendor feed — rather than open web crawling, so check how your organization gathers them.

---

## Step 1: Create the manifest (`ard.json`)

Create a static `ard.json` manifest listing your agentic resources. Below is a copy-pasteable template:

```json
{
  "entries": [
    {
      "identifier": "urn:air:acme.com:server:weather",
      "displayName": "Acme Weather Telemetry Server",
      "type": "application/mcp-server+json",
      "url": "https://api.acme.com/mcp/weather.json",
      "capabilities": ["WeatherTool", "ForecastTool"],
      "description": "An enterprise weather MCP server providing live telemetry.",
      "representativeQueries": [
        "what is the current wind speed in Chicago",
        "get the 5-day forecast for Seattle"
      ]
    }
  ]
}
```

*   **`identifier`**: Naming must follow the domain-anchored URN standard: `urn:air:<your-domain>:<namespace>:<agent-name>`.
*   **`representativeQueries`**: Provide **2–5 natural language queries** to enable high-fidelity semantic vector search.

---

## Step 2: Host the manifest

Upload the manifest to your domain:
```text
https://<your-domain>/.well-known/ard.json
```

Ensure your web server serves it with:

*   **HTTPS**: Secure connection only.
*   **Content-Type**: `application/json`
*   **CORS header**: `Access-Control-Allow-Origin: *` (crucial for crawlers to fetch it).

---

## Step 3: Set up DNS discovery (optional)

If you cannot host at the standard `.well-known` path, publish a DNS `TXT` record pointing directly to your raw JSON location (e.g., S3 or GitHub Pages):

| Name / Host | Type | Value |
| :--- | :--- | :--- |
| `_catalog._agents.yourdomain.com` | `TXT` | `"url=https://custom-bucket.s3.amazonaws.com/ard.json"` |

For dynamic discovery services (`POST /search`), publish an `SRV` record:

| Name / Service | Type | Port | Target |
| :--- | :--- | :--- | :--- |
| `_search._agents.yourdomain.com` | `SRV` | `443` | `search.yourdomain.com` |
