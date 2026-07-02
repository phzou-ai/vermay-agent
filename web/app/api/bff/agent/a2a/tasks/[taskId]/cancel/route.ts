import { type NextRequest } from "next/server"

import { buildA2ARpcTaskCancelEnvelope } from "@/lib/agent/a2a"
import { jsonRpcResultResponse, readJsonRpcResponse } from "@/lib/agent/bff-rpc"
import { buildAgentRootPath, proxyAgentRootJson } from "@/lib/agent/server"

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ taskId: string }> }
) {
  const { taskId } = await params
  const payload = await request.json().catch(() => ({}))
  const reason =
    payload && typeof payload === "object" && "reason" in payload
      ? payload.reason
      : undefined
  const upstreamPayload = buildA2ARpcTaskCancelEnvelope(
    taskId,
    typeof reason === "string" ? reason : undefined
  )
  const upstream = await proxyAgentRootJson(buildAgentRootPath("/rpc"), {
    method: "POST",
    body: JSON.stringify(upstreamPayload),
  })

  if (!upstream.ok) {
    return upstream
  }

  const body = await readJsonRpcResponse(upstream)
  return jsonRpcResultResponse(body, {
    invalidMessage: "Invalid A2A cancel response",
  })
}
