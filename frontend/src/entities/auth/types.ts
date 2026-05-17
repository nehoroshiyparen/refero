export type RoleName = 'GUEST' | 'AUTHOR' | 'REVIEWER' | 'ADMIN'

export type UserProfile = {
  id: string
  username: string
  email: string
  full_name: string
  avatar_url?: string
  is_active: boolean
  role_name: RoleName
  created_at: string
  updated_at: string
  author_profile?: {
    organization?: string
    position?: string
    degree?: string
    orcid?: string
    bio?: string
  } | null
  reviewer_profile?: {
    specialization?: string
    degree?: string
  } | null
}

export type LoginRequest = {
  username?: string
  email?: string
  password: string
}

export type RegisterRequest = {
  username: string
  email: string
  full_name: string
  password: string
}

export type AuthResponse = {
  access_token: string
}

export type CreateAuthorProfileData = {
  orcid: string
  organization?: string
  position?: string
  degree?: string
  bio?: string
}

export type CreateReviewerProfileData = {
  specialization: string
  degree?: string
}
