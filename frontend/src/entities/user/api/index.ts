import { request } from '@/shared/api/client'
import type { UserBrief, UserFilters, UserProfile } from '../types'

export function getUsers(filters: UserFilters = {}) {
  const params = new URLSearchParams()
  if (filters.query) params.set('query', filters.query)
  if (filters.role_name) params.set('role_name', filters.role_name)
  if (filters.limit) params.set('limit', String(filters.limit))
  if (filters.offset) params.set('offset', String(filters.offset))
  const qs = params.toString()
  return request<UserBrief[]>(`/api/users${qs ? `?${qs}` : ''}`)
}

export function getUser(id: string) {
  return request<UserProfile>(`/api/users/${id}`)
}
