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
  PREFLIGHT_OFF   (demo A/B)   if set, the checkpoint is bypassed AND all Preflight
                               wording is removed from the tool descriptions/responses,
                               so the connector reads as a plain, unguarded email tool
                               (the "no checkpoint" side of the side-by-side). Rename the
                               connector neutrally (e.g. "Email Tool") to match.

Note: for a truly airtight gate the gated tools must be the ONLY send/share/sign path
available to the agent (don't also expose the plugin's raw connectors). See README.
"""
import os
import sys

try:
    from mcp.server.mcpserver import MCPServer as _Server   # mcp >= 2.0
except ImportError:                                          # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

import gate  # pure logic, no MCP dependency (testable on its own)

# When the checkpoint is bypassed, the server presents itself as a neutral email tool
# with no Preflight branding anywhere Claude can read it (server name, tool descriptions,
# responses). This keeps the "no checkpoint" take honest and un-branded.
OFF = bool(os.environ.get("PREFLIGHT_OFF"))

mcp = _Server("email-tools" if OFF else "preflight-gateway")


def _doc(neutral: str, branded: str) -> str:
    # Always present neutral descriptions. The agent should hit the checkpoint like any
    # enforced-egress control (send/file/sign), not read "this tool has a gate" in the
    # description and start negotiating the privileged flag. The gate still runs
    # server-side (unless PREFLIGHT_OFF); the tool RESPONSE tells the truth (blocked +
    # receipt). This matches how a real deployment works and keeps takes clean.
    return neutral


def email_document(document_name: str, recipient_email: str, privileged: bool = False) -> str:
    action, human = gate.action_email(document_name, recipient_email, privileged)
    return gate.gate(action, human)
email_document.__doc__ = _doc(
    "Email a document to a recipient.",
    "Email a document to a recipient (the \"sent\" action). Gated by Preflight: blocks "
    "if a privileged document is emailed outside the firm domain.")
email_document = mcp.tool()(email_document)


def share_to_drive(document_name: str, destination: str, privileged: bool = False) -> str:
    action, human = gate.action_share(document_name, destination, privileged)
    return gate.gate(action, human)
share_to_drive.__doc__ = _doc(
    "Share a document to a drive or folder.",
    "Share a document to an external drive/folder (the \"relied-on\" action). Gated by "
    "Preflight: blocks sharing a privileged document to an external recipient.")
share_to_drive = mcp.tool()(share_to_drive)


def send_for_signature(document_name: str, approved_by_authorized_reviewer: bool = False,
                       privileged: bool = False) -> str:
    action, human = gate.action_signature(document_name, approved_by_authorized_reviewer, privileged)
    return gate.gate(action, human)
send_for_signature.__doc__ = _doc(
    "Send a document for signature.",
    "Execute a signature via DocuSign (the \"filed\" action). Gated by Preflight: blocks "
    "executing an agreement that was not approved by an authorized reviewer.")
send_for_signature = mcp.tool()(send_for_signature)


def read_document(document_name: str) -> str:
    if OFF:
        return f"Done. Read and summarized {document_name}."
    return (f"PERMITTED — read/summarize {document_name}. Local read touches no rule variable; "
            f"Preflight's relevance screen lets it through with no check.")
read_document.__doc__ = _doc(
    "Read or summarize a local document.",
    "Read/summarize a local document (benign). A pure read touches no rule variable, so "
    "Preflight's relevance screen permits it without a paid check — the checkpoint costs "
    "nothing when the agent is harmless.")
read_document = mcp.tool()(read_document)


if __name__ == "__main__":
    if "--http" in sys.argv:
        port = 8787
        if "--port" in sys.argv:
            port = int(sys.argv[sys.argv.index("--port") + 1])
        mode = "no-checkpoint (email-tools)" if OFF else "Preflight gate"
        sys.stderr.write(f"[{'email-tools' if OFF else 'preflight-gateway'}] streamable-HTTP on "
                         f"0.0.0.0:{port} — mode: {mode}\n")
        try:
            # mcp >= 2.0: host/port are run() kwargs
            mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
        except TypeError:
            # mcp 1.x (FastMCP): host/port via settings
            mcp.settings.host = "0.0.0.0"
            mcp.settings.port = port
            mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
