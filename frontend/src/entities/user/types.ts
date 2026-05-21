export type UserBrief = {
  id: string
  username: string
  email: string
  full_name: string
  avatar_url?: string | null
}

export type UserFilters = {
  query?: string
  role_name?: string
  limit?: number
  offset?: number
}

export type AuthorProfile = {
  organization?: string | null
  position?: string | null
  degree?: string | null
  orcid?: string | null
  bio?: string | null
}

export type ReviewerProfile = {
  specialization?: string | null
  degree?: string | null
}

export type UserProfile = {
  id: string
  username: string
  email: string
  full_name: string
  avatar_url?: string | null
  roles: string[]
  author_profile?: AuthorProfile | null
  reviewer_profile?: ReviewerProfile | null
  created_at?: string | null
  updated_at?: string | null
}
