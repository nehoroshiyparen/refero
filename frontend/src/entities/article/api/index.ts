import { request } from '@/shared/api/client'
import type { ArticlePayload, ArticleFullPayload, ArticleFilters, ArticleVersionPayload, ApprovalBrief, CreateArticleData, UpdateArticleData } from '../types'

function buildQuery(filters: ArticleFilters): string {
  const params = new URLSearchParams()
  if (filters.query) params.set('query', filters.query)
  if (filters.status) params.set('status', filters.status)
  if (filters.journal_id) params.set('journal_id', filters.journal_id)
  if (filters.author_id) params.set('author_id', filters.author_id)
  if (filters.language) params.set('language', filters.language)
  if (filters.keywords?.length) params.set('keywords', filters.keywords.join(','))
  if (filters.limit) params.set('limit', String(filters.limit))
  if (filters.offset) params.set('offset', String(filters.offset))
  const qs = params.toString()
  return qs ? `/api/articles?${qs}` : '/api/articles'
}

export function getArticles(filters: ArticleFilters = {}) {
  return request<ArticlePayload[]>(buildQuery(filters))
}

export function getArticle(id: string) {
  return request<ArticleFullPayload>(`/api/articles/${id}`)
}

export function createArticle(data: CreateArticleData) {
  return request<ArticleFullPayload>('/api/articles', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function updateArticle(id: string, data: UpdateArticleData, versionId?: string) {
  const params = versionId ? `?version_id=${versionId}` : ''
  return request<ArticleFullPayload>(`/api/articles/${id}${params}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export function getArticleVersions(articleId: string) {
  return request<ArticleVersionPayload[]>(`/api/articles/${articleId}/versions`)
}

export function getArticleVersionById(articleId: string, versionId: string) {
  return request<ArticleVersionPayload>(`/api/articles/${articleId}/versions/${versionId}`)
}

export function createArticleVersion(articleId: string) {
  return request<ArticleVersionPayload>(`/api/articles/${articleId}/versions`, {
    method: 'POST',
  })
}

export function deleteArticleVersion(articleId: string, versionId: string) {
  return request<void>(`/api/articles/${articleId}/versions/${versionId}`, {
    method: 'DELETE',
  })
}

export function setCurrentVersion(articleId: string, versionId: string) {
  return request<ArticleFullPayload>(`/api/articles/${articleId}/versions/${versionId}/set-current`, {
    method: 'PUT',
  })
}

export function submitForApproval(articleId: string) {
  return request<{ message: string }>(`/api/articles/${articleId}/submit-for-approval`, {
    method: 'POST',
  })
}

export function registerView(articleId: string) {
  return request<{ view_count: number }>(`/api/articles/${articleId}/view`, {
    method: 'POST',
  })
}

export function addAuthor(articleId: string, authorId: string) {
  return request<{ message: string }>(`/api/articles/${articleId}/authors`, {
    method: 'POST',
    body: JSON.stringify({ author_id: authorId }),
  })
}

export function removeAuthor(articleId: string, authorId: string) {
  return request<{ message: string }>(`/api/articles/${articleId}/authors/${authorId}`, {
    method: 'DELETE',
  })
}

export function getVersionApprovals(articleId: string, versionId: string) {
  return request<ApprovalBrief[]>(`/api/articles/${articleId}/versions/${versionId}/approvals`)
}

export function approveVersion(articleId: string, versionId: string, approved: boolean) {
  return request<{ message: string }>(`/api/articles/${articleId}/versions/${versionId}/approve?approved=${approved}`, {
    method: 'POST',
  })
}

export function hideArticle(articleId: string) {
  return request<ArticlePayload>(`/api/articles/${articleId}/hide`, {
    method: 'POST',
  })
}

export function showArticle(articleId: string) {
  return request<ArticlePayload>(`/api/articles/${articleId}/show`, {
    method: 'POST',
  })
}
