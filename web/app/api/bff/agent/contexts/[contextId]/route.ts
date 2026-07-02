import { type NextRequest } from "next/server"

import { buildAgentPath, proxyAgentJson } from "@/lib/agent/server"

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ contextId: string }> },
) {
  const { contextId } = await params

  return proxyAgentJson(buildAgentPath(`/contexts/${encodeURIComponent(contextId)}`))
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ contextId: string }> },
) {
  const { contextId } = await params

  return proxyAgentJson(
    buildAgentPath(`/contexts/${encodeURIComponent(contextId)}`, request.nextUrl.searchParams),
    { method: "DELETE" },
  )
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ contextId: string }> },
) {
  const { contextId } = await params

  return proxyAgentJson(
    buildAgentPath(`/contexts/${encodeURIComponent(contextId)}`),
    {
      method: "PATCH",
      body: JSON.stringify(await request.json()),
    },
  )
}
