"""MkDocs build hook: publish the ARD base context at /context/v1.

§4.1 of the specification says term IRIs come from a base context served at
`https://agenticresourcediscovery.org/context/v1`, and that a conformant consumer applies it as
the JSON-LD `expandContext`. That URL has to resolve, or the one normative reference an entry
makes to this site is a 404.

The context lives only in ards-project/ard-spec (spec/schemas/ard.context.jsonld), the same way
the specification text does. This hook fetches it at build time and publishes it verbatim, so the
site never holds a second copy that can drift from the canonical one.

Two paths are published for the same bytes:

    /context/v1        the URL the specification names
    /context/v1.jsonld the same document with a `.jsonld` extension

The alias exists because of how static hosting assigns Content-Type. GitHub Pages derives it from
the file extension and offers no way to set headers, so the extensionless path is served as
`application/octet-stream`. The JSON-LD 1.1 API requires a remote context to arrive as
`application/ld+json`, `application/json`, or a `+json` media type, and a strict processor rejects
anything else — so `/context/v1` resolves and reads correctly, but a strict consumer that
dereferences it may still refuse it. The `.jsonld` alias gives those consumers a URL that works
today; making the bare path correct needs either a host that can set headers, or a spec that names
the suffixed URL. Both are decisions for the spec, not for this build.

Unlike the specification hook, a fetch failure here publishes NOTHING. A placeholder page is a
reasonable fallback for prose a human is reading; an unparseable or partial document served at a
context URL is worse than a 404, because a consumer would apply it and expand every term wrongly.
"""
import json
import urllib.error
import urllib.request

from mkdocs.structure.files import File

SRC = ("https://raw.githubusercontent.com/ards-project/ard-spec/main/"
       "spec/schemas/ard.context.jsonld")
DEST = "context/v1"
DEST_SUFFIXED = "context/v1.jsonld"
TIMEOUT = 20


def _fetch() -> str | None:
    """The canonical context, or None if it cannot be had intact.

    The document is parsed before being published: a truncated or HTML error body that happened to
    arrive with a 200 would otherwise be served as the context.
    """
    try:
        with urllib.request.urlopen(SRC, timeout=TIMEOUT) as r:
            raw = r.read().decode("utf-8")
    except (urllib.error.URLError, OSError, UnicodeDecodeError):
        return None
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(doc, dict) or "@context" not in doc:
        return None
    return raw


def on_files(files, config):
    raw = _fetch()
    if raw is None:
        # Leave the URL 404ing rather than publish something a consumer would trust.
        print("WARNING - context_from_canonical: could not fetch the ARD base context from "
              f"{SRC}; /context/v1 will not be published for this build.")
        return files
    for dest in (DEST, DEST_SUFFIXED):
        files.append(File.generated(config, dest, content=raw))
    return files
