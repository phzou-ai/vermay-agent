import { type NextRequest } from "next/server"

import { buildAgentPath, proxyAgentJson } from "@/lib/agent/server"

export async function POST(
  _request: NextRequest,
  { params }: { params: Promise<{ agentId: string }> },
) {
  const { agentId } = await params
  return proxyAgentJson(
    buildAgentPath(`/registered-agents/${encodeURIComponent(agentId)}/refresh-card`),
    { method: "POST" },
  )
}
