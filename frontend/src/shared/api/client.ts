import { API_BASE_URL } from '../config'

let accessToken: string | null = null
let refreshPromise: Promise<string | null> | null = null

const STORAGE_KEY = 'access_token'

export function setAccessToken(token: string | null) {
  accessToken = token
  if (token) {
    localStorage.setItem(STORAGE_KEY, token)
  } else {
    localStorage.removeItem(STORAGE_KEY)
  }
}

export function getAccessToken() {
  return accessToken
}

export function withAuth(url: string): string {
  const token = accessToken
  if (!token) return url
  const sep = url.includes('?') ? '&' : '?'
  return `${url}${sep}token=${token}`
}

export function loadAccessToken(): string | null {
  const token = localStorage.getItem(STORAGE_KEY)
  if (token) setAccessToken(token)
  return token
}

async function refreshAccessToken(): Promise<string | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
    })
    if (!res.ok) return null
    const body = await res.json()
    const token: string = body.data?.access_token
    if (token) setAccessToken(token)
    return token
  } catch {
    return null
  }
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: unknown,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export async function request<T>(
  path: string,
  options?: RequestInit & { retry?: boolean },
): Promise<T> {
  const { retry = true, ...fetchOptions } = options ?? {}

  const headers: Record<string, string> = {
    ...(fetchOptions.headers as Record<string, string>),
    'Cache-Control': 'no-cache',
  }
  if (!(fetchOptions.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...fetchOptions,
    headers,
    credentials: 'include',
  })

  if (res.status === 204) return undefined as T

  if (res.status === 401 && retry) {
    refreshPromise ??= refreshAccessToken()
    const newToken = await refreshPromise
    refreshPromise = null

    if (newToken) {
      return request(path, { ...options, retry: false })
    }
    setAccessToken(null)
    throw new ApiError(401, 'UNAUTHORIZED', 'Session expired')
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    const message = body.error
      ?? (Array.isArray(body.detail) ? body.detail.map((d: any) => d.msg).join('; ') : null)
      ?? body.detail
      ?? res.statusText
    throw new ApiError(
      res.status,
      body.code ?? 'UNKNOWN',
      message,
      body.details ?? body.detail,
    )
  }

  const body = await res.json()
  if ('data' in body) return body.data as T
  return body as T
}
