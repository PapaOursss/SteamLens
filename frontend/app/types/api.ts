export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface HealthStatus {
  status: 'ok' | 'error'
  database?: string
  time?: string
}

export interface ApiError {
  detail?: string
  message?: string
  status?: number
}
