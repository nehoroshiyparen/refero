import { request } from '@/shared/api/client'
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  UserProfile,
  CreateAuthorProfileData,
  CreateReviewerProfileData,
} from '../types'

export function login(data: LoginRequest) {
  return request<AuthResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function register(data: RegisterRequest) {
  return request<AuthResponse>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function logout() {
  return request<void>('/api/auth/logout', { method: 'POST' })
}

export function getMe() {
  return request<UserProfile>('/api/users/me')
}

export function createAuthorProfile(userId: string, data: CreateAuthorProfileData) {
  return request<UserProfile>(`/api/users/${userId}/author-profile`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function createReviewerProfile(userId: string, data: CreateReviewerProfileData) {
  return request<UserProfile>(`/api/users/${userId}/reviewer-profile`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}
