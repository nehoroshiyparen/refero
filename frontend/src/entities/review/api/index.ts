import { request } from '@/shared/api/client'
import type { ReviewAssignmentFullPayload, ReviewPayload, CommentPayload, ReviewStatus } from '../types'

export function getReviewAssignments() {
  return request<ReviewAssignmentFullPayload[]>('/api/reviews/assignments')
}

export function getReviewAssignment(assignmentId: string) {
  return request<ReviewAssignmentFullPayload | null>(`/api/reviews/assignments/${assignmentId}`)
}

export function getVersionAssignment(articleId: string, versionId: string) {
  return request<ReviewAssignmentFullPayload | null>(`/api/articles/${articleId}/versions/${versionId}/assignment`)
}

export function getReviewByAssignment(assignmentId: string) {
  return request<ReviewPayload | null>(`/api/reviews/assignments/${assignmentId}/review`)
}

export function submitReview(assignmentId: string, status: ReviewStatus) {
  return request<ReviewPayload>(`/api/reviews/assignments/${assignmentId}/review`, {
    method: 'POST',
    body: JSON.stringify({ review_assignment_id: assignmentId, status }),
  })
}

export function getComments(versionId: string) {
  return request<CommentPayload[]>(`/api/reviews/versions/${versionId}/comments`)
}

export function addComment(versionId: string, content: string) {
  return request<CommentPayload>(`/api/reviews/versions/${versionId}/comments`, {
    method: 'POST',
    body: JSON.stringify({ article_version_id: versionId, content }),
  })
}
