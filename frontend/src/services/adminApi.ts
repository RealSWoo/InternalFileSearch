import type { IndexStatus } from '../types/admin'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL


export async function getIndexStatus(): Promise<IndexStatus> {
  const response = await fetch(
    `${API_BASE_URL}/api/admin/index/status`,
  )

  if (!response.ok) {
    throw new Error(
      '인덱싱 상태를 불러오지 못했습니다.',
    )
  }

  return response.json()
}


export async function runIndex(): Promise<IndexStatus> {
  const response = await fetch(
    `${API_BASE_URL}/api/admin/index`,
    {
      method: 'POST',
    },
  )

  if (!response.ok) {
    let message =
      '인덱싱 실행 중 오류가 발생했습니다.'

    try {
      const data = await response.json()

      if (data.detail) {
        message = data.detail
      }
    } catch {
      // 기본 메시지 사용
    }

    throw new Error(message)
  }

  return response.json()
}