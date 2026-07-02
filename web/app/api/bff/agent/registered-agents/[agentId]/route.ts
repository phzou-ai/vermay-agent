import { type NextRequest } from "next/server"

import { buildAgentPath, proxyAgentJson } from "@/lib/agent/server"

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ agentId: string }> },
) {
  const { agentId } = await params
  return proxyAgentJson(
    buildAgentPath(`/registered-agents/${encodeURIComponent(agentId)}`),
  )
}

export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ agentId: string }> },
) {
  const { agentId } = await params
  return proxyAgentJson(
    buildAgentPath(`/registered-agents/${encodeURIComponent(agentId)}`),
    { method: "DELETE" },
  )
}
