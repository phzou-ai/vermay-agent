import { buildAgentRootPath, proxyAgentRootJson } from "@/lib/agent/server"

export async function GET() {
  return proxyAgentRootJson(buildAgentRootPath("/.well-known/agent-card.json"))
}
