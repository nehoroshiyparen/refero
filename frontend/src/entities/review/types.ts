export type ReviewStatus = 'APPROVED' | 'REJECTED' | 'REQUESTING_CHANGES'

export type ReviewAssignmentPayload = {
  id: string
  article_version_id: string
  reviewer_id: string
  created_at: string
}

export type ReviewAssignmentFullPayload = ReviewAssignmentPayload & {
  review_status: ReviewStatus | null
  review_completed_at: string | null
  article_id: string | null
  article_title: string | null
  version_number: number | null
  version_title: string | null
}

export type ReviewPayload = {
  id: string
  review_assignment_id: string
  status: ReviewStatus
  created_at: string | null
  completed_at: string | null
}

export type CommentPayload = {
  id: string
  article_version_id: string
  user_id: string
  user_name: string
  content: string
  created_at: string
}

export type CreateReviewData = {
  status: ReviewStatus
}
