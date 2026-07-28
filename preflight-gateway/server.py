#!/usr/bin/env python3
"""Preflight MCP Gateway — a gated MCP server for the "Filed, Sent, Relied On" demo.

Exposes consequential legal actions (email / share / sign) as MCP tools. Before any
of them "executes," the gateway runs the action through ICME Preflight's real solver
(POST /v1/checkIt) and BLOCKS on anything that isn't an explicit SAT (fail-closed).
Every decision returns a real receipt (check_id) that verifies keyless via verifyProof.

Runs two ways from one file:
  Claude Code (local, your machine):   python server.py
      → stdio transport, no hosting, no public URL. Point .mcp.json at it (see README).
  Cowork (recognizable surface):       python server.py --http --port 8787
      → streamable-HTTP; expose with `ngrok http 8787` (or cloudflared) and add the
        public https URL as a Cowork custom connector (Settings → Connectors).

Env:
  ICME_API_KEY    (required)   funded sk-smt-... key
  ICME_POLICY_ID  (default: e396f8d8-... — the compiled demo policy)
  FIRM_DOMAIN     (default: firm.example)

Note: for a truly airtight gate the gated tools must be the ONLY send/share/sign path
available to the agent (don't also expose the plugin's raw connectors). See README.
"""
import sys

from mcp.server.fastmcp import FastMCP

import gate  # pure logic, no MCP dependency (testable on its own)

mcp = FastMCP("preflight-gateway")


@mcp.tool()
def email_document(document_name: str, recipient_email: str, privileged: bool = False) -> str:
    """Email a document to a recipient (the "sent" action). Gated by Preflight: blocks
    if a privileged document is emailed outside the firm domain."""
    action, human = gate.action_email(document_name, recipient_email, privileged)
    return gate.gate(action, human)


@mcp.tool()
def share_to_drive(document_name: str, destination: str, privileged: bool = False) -> str:
    """Share a document to an external drive/folder (the "relied-on" action). Gated by
    Preflight: blocks sharing a privileged document to an external recipient."""
    action, human = gate.action_share(document_name, destination, privileged)
    return gate.gate(action, human)


@mcp.tool()
def send_for_signature(document_name: str, approved_by_authorized_reviewer: bool = False,
                       privileged: bool = False) -> str:
    """Execute a signature via DocuSign (the "filed" action). Gated by Preflight: blocks
    executing an agreement that was not approved by an authorized reviewer."""
    action, human = gate.action_signature(document_name, approved_by_authorized_reviewer, privileged)
    return gate.gate(action, human)


@mcp.tool()
def read_document(document_name: str) -> str:
    """Read/summarize a local document (benign). A pure read touches no rule variable, so
    Preflight's relevance screen permits it without a paid check — the checkpoint costs
    nothing when the agent is harmless."""
    return (f"PERMITTED — read/summarize {document_name}. Local read touches no rule variable; "
            f"Preflight's relevance screen lets it through with no check.")


if __name__ == "__main__":
    if "--http" in sys.argv:
        port = 8787
        if "--port" in sys.argv:
            port = int(sys.argv[sys.argv.index("--port") + 1])
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = port
        sys.stderr.write(f"[preflight-gateway] streamable-HTTP on 0.0.0.0:{port} "
                         f"— tunnel with `ngrok http {port}` and add the https URL as a Cowork connector\n")
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
