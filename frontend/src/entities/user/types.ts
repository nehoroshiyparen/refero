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
