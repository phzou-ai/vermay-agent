import { type NextRequest } from "next/server"

import { buildA2ARpcMessageStreamEnvelope } from "@/lib/agent/a2a"
import { buildAgentRootPath, proxyAgentRootStream } from "@/lib/agent/server"
import type { AgentA2AMessagePayload } from "@/lib/agent/types"

export async function POST(request: NextRequest) {
  const payload = (await request.json()) as AgentA2AMessagePayload
  const upstreamPayload = buildA2ARpcMessageStreamEnvelope(payload)

  return proxyAgentRootStream(buildAgentRootPath("/rpc"), {
    method: "POST",
    body: JSON.stringify(upstreamPayload),
  })
}
