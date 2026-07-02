import { type NextRequest } from "next/server"

import { buildAgentPath, proxyAgentJson } from "@/lib/agent/server"

export async function GET(request: NextRequest) {
  return proxyAgentJson(
    buildAgentPath("/registered-agents", request.nextUrl.searchParams),
  )
}

export async function POST(request: NextRequest) {
  const payload = await request.json()
  return proxyAgentJson(buildAgentPath("/registered-agents"), {
    method: "POST",
    body: JSON.stringify(payload),
  })
}
