import { type NextRequest } from "next/server"

import { buildA2ARpcTaskGetEnvelope } from "@/lib/agent/a2a"
import { jsonRpcResultResponse, readJsonRpcResponse } from "@/lib/agent/bff-rpc"
import { buildAgentRootPath, proxyAgentRootJson } from "@/lib/agent/server"

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ taskId: string }> }
) {
  const { taskId } = await params
  const upstream = await proxyAgentRootJson(buildAgentRootPath("/rpc"), {
    method: "POST",
    body: JSON.stringify(buildA2ARpcTaskGetEnvelope(taskId)),
  })

  if (!upstream.ok) {
    return upstream
  }

  const body = await readJsonRpcResponse(upstream)
  return jsonRpcResultResponse(body, {
    invalidMessage: "Invalid A2A task response",
  })
}
