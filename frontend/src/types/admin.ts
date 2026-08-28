export interface IndexStatus {
  index_run_id?: number
  status: string
  started_at?: string | null
  completed_at?: string | null
  scanned_files?: number
  new_files?: number
  updated_files?: number
  inactive_files?: number
  skipped_files?: number
  error_count?: number
  error_message?: string | null
  message?: string
}