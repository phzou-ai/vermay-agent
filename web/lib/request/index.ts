type RequestMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE"

type RequestOptions = {
  body?: unknown
  headers?: HeadersInit
  signal?: AbortSignal
}

export class RequestError extends Error {
  status: number
  details?: unknown

  constructor(message: string, status: number, details?: unknown) {
    super(message)
    this.name = "RequestError"
    this.status = status
    this.details = details
  }
}

function extractErrorMessage(details: unknown, fallback: string) {
  if (details && typeof details === "object") {
    if ("msg" in details && typeof details.msg === "string" && details.msg.trim()) {
      return details.msg
    }

    if (
      "message" in details &&
      typeof details.message === "string" &&
      details.message.trim()
    ) {
      return details.message
    }

    if ("title" in details && typeof details.title === "string" && details.title.trim()) {
      return details.title
    }
  }

  return fallback
}

export function getRequestErrorMessage(error: unknown, fallback = "Request failed") {
  if (error instanceof RequestError) {
    return error.message || fallback
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return fallback
}

async function requestJson<T>(
  method: RequestMethod,
  url: string,
  { body, headers, signal }: RequestOptions = {}
): Promise<T> {
  const response = await fetch(url, {
    method,
    headers: {
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      ...headers
    },
    body: body === undefined ? undefined : JSON.stringify(body),
    signal
  })

  if (!response.ok) {
    const fallbackMessage = `Request failed (${response.status})`
    let details: unknown

    try {
      details = await response.clone().json()
    } catch {
      try {
        const text = await response.text()
        details = text ? { message: text } : undefined
      } catch {
        details = undefined
      }
    }

    throw new RequestError(
      extractErrorMessage(details, fallbackMessage),
      response.status,
      details
    )
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

const requestGet = async <T = any>(
  url: string,
  options?: Omit<RequestOptions, "body">
) => requestJson<T>("GET", url, options)

const requestDelete = async <T = any>(
  url: string,
  options?: Omit<RequestOptions, "body">
) => requestJson<T>("DELETE", url, options)

const requestPost = async <T = any>(
  url: string,
  params: unknown,
  options?: Omit<RequestOptions, "body">
) => requestJson<T>("POST", url, { ...options, body: params })

const requestPut = async <T = any>(
  url: string,
  params: unknown,
  options?: Omit<RequestOptions, "body">
) => requestJson<T>("PUT", url, { ...options, body: params })

const requestPatch = async <T = any>(
  url: string,
  params: unknown,
  options?: Omit<RequestOptions, "body">
) => requestJson<T>("PATCH", url, { ...options, body: params })

export { requestDelete, requestGet, requestPatch, requestPost, requestPut }
