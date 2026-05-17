import { request } from '@/shared/api/client'
import type { JournalPayload } from '../types'

export function getJournals() {
  return request<JournalPayload[]>('/api/journals')
}
