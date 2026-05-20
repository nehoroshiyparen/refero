export type ArticleStatus = 'DRAFT' | 'PENDING_APPROVAL' | 'REVIEW' | 'PUBLISHED' | 'REJECTED'

export type AuthorBrief = {
  author_id: string
  name: string
  email: string
  joined_at?: string | null
}

export type ApprovalStatus = 'PENDING' | 'APPROVED' | 'REJECTED'

export type ApprovalBrief = {
  id: string
  approver_id: string
  approver_name: string
  status: ApprovalStatus
  comment?: string | null
  approved_at?: string | null
}

export type JournalBrief = {
  id: string
  name: string
}

export type CitationBrief = {
  id: string
  to_article_id?: string | null
  doi?: string | null
  raw_reference?: string | null
  match_status: string
  created_at?: string | null
}

export type ArticlePayload = {
  id: string
  current_version_id?: string | null
  title: string
  abstract?: string | null
  keywords: string[]
  language: string
  status: ArticleStatus
  version_number: number
  is_visible: boolean
  view_count: number
  download_count: number
  doi?: string | null
  pdf_path: string
  journal_id?: string | null
  creator_id?: string | null
  updated_by_user_id?: string | null
  published_at?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export type ArticleFullPayload = ArticlePayload & {
  authors: AuthorBrief[]
  journal?: JournalBrief | null
  citations: CitationBrief[]
}

export type ArticleFilters = {
  query?: string
  status?: ArticleStatus
  journal_id?: string
  author_id?: string
  language?: string
  keywords?: string[]
  limit?: number
  offset?: number
}

export type CreateArticleData = {
  title: string
  abstract?: string
  keywords?: string[]
  language?: string
  pdf_path: string
  journal_id?: string
}

export type ArticleVersionPayload = {
  id: string
  version_number: number
  title: string
  abstract?: string | null
  keywords: string[]
  language: string
  pdf_path: string
  status: ArticleStatus
  updated_by_user_id?: string | null
  published_at?: string | null
  created_at: string
  updated_at?: string | null
}

export type UpdateArticleData = {
  title?: string
  abstract?: string | null
  keywords?: string[]
  language?: string
  pdf_path?: string
  journal_id?: string | null
}
