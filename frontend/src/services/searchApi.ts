import type {
  FileTypeFilter,
  SearchResponse,
} from '../types/search'


const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL


interface SearchFilesOptions {
  query: string
  page?: number
  pageSize?: number
  fileType?: FileTypeFilter
}


export async function searchFiles({
  query,
  page = 1,
  pageSize = 5,
  fileType = 'all',
}: SearchFilesOptions): Promise<SearchResponse> {
  const params =
    new URLSearchParams()

  params.set(
    'q',
    query,
  )

  params.set(
    'page',
    String(page),
  )

  params.set(
    'page_size',
    String(pageSize),
  )

  if (fileType !== 'all') {
    params.set(
      'file_type',
      fileType,
    )
  }

  const response = await fetch(
    `${API_BASE_URL}/api/search?${params.toString()}`,
  )

  if (!response.ok) {
    let message =
      '파일 검색 중 오류가 발생했습니다.'

    try {
      const body = await response.json()

      if (body.detail) {
        message = body.detail
      }
    } catch {
      // JSON 응답이 아니면
      // 기본 오류 메시지를 사용한다.
    }

    throw new Error(
      message,
    )
  }

  return response.json()
}