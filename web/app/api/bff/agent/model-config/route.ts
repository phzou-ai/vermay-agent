import { buildAgentPath, proxyAgentJson } from "@/lib/agent/server"

export async function GET() {
  return proxyAgentJson(buildAgentPath("/model-config"))
}
