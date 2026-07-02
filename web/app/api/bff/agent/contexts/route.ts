import { type NextRequest } from "next/server"

import { buildAgentPath, proxyAgentJson } from "@/lib/agent/server"

export async function GET(request: NextRequest) {
  return proxyAgentJson(buildAgentPath("/contexts", request.nextUrl.searchParams))
}
