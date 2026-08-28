export type FileTypeFilter =
  | 'all'
  | 'pdf'
  | 'excel'
  | 'ppt'
  | 'word'

export interface SearchResult {
  id: number
  file_name: string
  extension: string | null
  full_path: string
  folder_path: string
  file_size: number | null
  modified_at: string | null
  score: number
}

export interface SearchResponse {
  query: string
  normalized_query: string

  keywords: string[]
  extensions: string[]

  year: number | null
  recent: boolean

  file_type: string | null

  total: number

  page: number
  page_size: number
  total_pages: number

  count: number

  response_time_ms: number

  results: SearchResult[]
}