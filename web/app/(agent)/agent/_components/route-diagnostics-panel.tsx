"use client"

import { Search } from "lucide-react"

import type { AgentDelegation, AgentRouteDecision } from "@/lib/agent/types"

export function RouteDiagnosticsPanel({
  routeDecisions,
  delegations,
}: {
  routeDecisions: AgentRouteDecision[]
  delegations: AgentDelegation[]
}) {
  const latestDecision = routeDecisions[routeDecisions.length - 1]
  const latestDelegation = delegations[delegations.length - 1]
  const latestSource = latestDecision
    ? routeDecisionSource(latestDecision)
    : "unknown"
  const latestConfidence = latestDecision
    ? routeDecisionConfidence(latestDecision)
    : null

  return (
    <div className="min-w-0 border-b border-[#E7E5E8] p-5">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Search className="h-4 w-4 text-[#54465C]" />
          <h2 className="m-0 text-[14px] font-semibold leading-5">
            Route diagnostics
          </h2>
        </div>
        <span className="rounded-full bg-[#F1F5F9] px-2 py-1 text-[11px] font-medium text-[#64748B]">
          {routeDecisions.length}
        </span>
      </div>

      {latestDecision ? (
        <div className="rounded-[6px] border border-[#E7E5E8] bg-white px-3 py-2">
          <div className="flex items-center justify-between gap-2">
            <p className="m-0 truncate text-[13px] font-semibold leading-5 text-[#1F0013]">
              {routeKindLabel(latestDecision.kind)}
            </p>
            <div className="flex min-w-0 shrink-0 items-center gap-1">
              <span className="rounded-full bg-[#EEF4FF] px-2 py-0.5 text-[11px] font-medium text-[#1E3A8A]">
                {latestSource}
              </span>
              {latestConfidence && (
                <span className="rounded-full bg-[#F1F5F9] px-2 py-0.5 text-[11px] font-medium text-[#64748B]">
                  {latestConfidence}
                </span>
              )}
            </div>
          </div>
          <p className="m-0 mt-1 line-clamp-2 text-[12px] leading-5 text-[#64748B]">
            {latestDecision.reason}
          </p>
          {typeof latestDecision.metadata?.fallbackReason === "string" && (
            <p className="m-0 mt-1 truncate text-[11px] leading-4 text-[#8B5CF6]">
              fallback: {latestDecision.metadata.fallbackReason}
            </p>
          )}
          {latestDecision.target_agent_id && (
            <p className="m-0 mt-1 truncate text-[11px] leading-4 text-[#64748B]">
              target: {latestDecision.target_agent_id}
            </p>
          )}
        </div>
      ) : (
        <div className="rounded-[4px] border border-dashed border-[#CBD5E1] px-3 py-5 text-center text-[12px] leading-5 text-[#64748B]">
          Route decisions will appear after a message is sent.
        </div>
      )}

      {latestDelegation && (
        <div className="mt-2 rounded-[6px] border border-[#E7E5E8] bg-[#F8FAFC] px-3 py-2">
          <div className="flex items-center justify-between gap-2">
            <p className="m-0 truncate text-[12px] font-semibold leading-5 text-[#1F0013]">
              {latestDelegation.remote_agent_id}
            </p>
            <span className="shrink-0 rounded-full bg-white px-2 py-0.5 text-[11px] font-medium text-[#64748B]">
              {latestDelegation.status}
            </span>
          </div>
          <p className="m-0 mt-1 truncate text-[11px] leading-4 text-[#64748B]">
            remote task:{" "}
            {latestDelegation.remote_task_id ||
              latestDelegation.remote_message_id ||
              "message"}
          </p>
        </div>
      )}
    </div>
  )
}

function routeKindLabel(kind: AgentRouteDecision["kind"]) {
  if (kind === "local_message") return "Direct answer"
  if (kind === "local_task") return "Local task"
  if (kind === "remote_agent") return "Child agent"
  return kind
}

function routeDecisionSource(decision: AgentRouteDecision) {
  const source = decision.metadata?.source
  return typeof source === "string" && source ? source : "unknown"
}

function routeDecisionConfidence(decision: AgentRouteDecision) {
  return typeof decision.confidence === "number"
    ? `${Math.round(decision.confidence * 100)}%`
    : null
}
