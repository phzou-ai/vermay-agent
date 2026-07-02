import { NextResponse } from "next/server"

const DEFAULT_VERMAY_AGENT_API_BASE = "http://127.0.0.1:8000"

function vermayAgentBaseUrl() {
  return (
    process.env.VERMAY_AGENT_API_BASE?.replace(/\/$/, "") ||
    process.env.MINI_AGENT_API_BASE?.replace(/\/$/, "") ||
    DEFAULT_VERMAY_AGENT_API_BASE
  )
}

function buildVermayAgentUrl(path: string) {
  return `${vermayAgentBaseUrl()}${path}`
}

function normalizeJsonRpcErrorCode(data: unknown) {
  if (!data || typeof data !== "object") return null
  if ("localCode" in data && typeof data.localCode === "string") {
    return data.localCode
  }
  const errorInfo = "errorInfo" in data ? data.errorInfo : null
  if (errorInfo && typeof errorInfo === "object" && "reason" in errorInfo) {
    return typeof errorInfo.reason === "string" ? errorInfo.reason : null
  }
  return null
}

function normalizeErrorPayload(status: number, payload: unknown) {
  if (payload && typeof payload === "object") {
    const detail = "detail" in payload ? payload.detail : null
    if (typeof detail === "string") {
      return { status, message: detail }
    }
    if (detail && typeof detail === "object") {
      const message = "message" in detail ? detail.message : null
      const code = "code" in detail ? detail.code : null
      if (typeof message === "string") {
        return {
          status,
          message,
          ...(typeof code === "string" ? { code } : {}),
        }
      }
    }

    const error = "error" in payload ? payload.error : null
    if (error && typeof error === "object") {
      const message = "message" in error ? error.message : null
      const data = "data" in error ? error.data : null
      const code = normalizeJsonRpcErrorCode(data)
      if (typeof message === "string") {
        return {
          status,
          message,
          ...(typeof code === "string" ? { code } : {}),
        }
      }
    }

    if ("message" in payload && typeof payload.message === "string") {
      return { status, message: payload.message }
    }
  }

  return { status, message: `Vermay Agent request failed (${status})` }
}

export function buildAgentPath(path: string, searchParams?: URLSearchParams) {
  const query = searchParams?.toString()
  return `/api${path}${query ? `?${query}` : ""}`
}

export function buildAgentRootPath(path: string, searchParams?: URLSearchParams) {
  const query = searchParams?.toString()
  return `${path}${query ? `?${query}` : ""}`
}

export async function proxyAgentJson(path: string, init?: RequestInit) {
  try {
    const response = await fetch(buildVermayAgentUrl(path), {
      ...init,
      cache: "no-store",
      headers: {
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...(init?.headers ?? {}),
      },
    })
    const text = await response.text()
    let payload: unknown = null

    if (text) {
      try {
        payload = JSON.parse(text)
      } catch {
        payload = { message: text }
      }
    }

    if (!response.ok) {
      return NextResponse.json(normalizeErrorPayload(response.status, payload), {
        status: response.status,
      })
    }

    if (response.status === 204) {
      return new Response(null, { status: 204 })
    }

    return NextResponse.json(payload)
  } catch (error) {
    return NextResponse.json(
      {
        status: 502,
        message:
          error instanceof Error
            ? error.message
            : "Vermay Agent API is unreachable",
      },
      { status: 502 },
    )
  }
}

export function proxyAgentRootJson(path: string, init?: RequestInit) {
  return proxyAgentJson(path, init)
}

export async function proxyAgentStream(path: string, init?: RequestInit) {
  try {
    const response = await fetch(buildVermayAgentUrl(path), {
      ...init,
      cache: "no-store",
      headers: {
        Accept: "text/event-stream",
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...(init?.headers ?? {}),
      },
    })

    if (!response.ok || !response.body) {
      let payload: unknown = null
      try {
        payload = await response.json()
      } catch {
        payload = null
      }

      return NextResponse.json(normalizeErrorPayload(response.status, payload), {
        status: response.status,
      })
    }

    return new Response(response.body, {
      status: response.status,
      headers: {
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
        "Content-Type": "text/event-stream",
        "X-Accel-Buffering": "no",
      },
    })
  } catch (error) {
    return NextResponse.json(
      {
        status: 502,
        message:
          error instanceof Error
            ? error.message
            : "Vermay Agent event stream is unreachable",
      },
      { status: 502 },
    )
  }
}

export function proxyAgentRootStream(path: string, init?: RequestInit) {
  return proxyAgentStream(path, init)
}
