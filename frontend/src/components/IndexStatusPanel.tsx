import { useEffect, useState } from 'react'

import {
  getIndexStatus,
  runIndex,
} from '../services/adminApi'

import type { IndexStatus } from '../types/admin'


function formatDate(
  value?: string | null,
): string {
  if (!value) {
    return '-'
  }

  return new Date(value).toLocaleString(
    'ko-KR',
    {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    },
  )
}


function getStatusLabel(
  status?: string,
): string {
  switch (status) {
    case 'completed':
      return '정상'

    case 'running':
      return '인덱싱 중'

    case 'failed':
      return '실패'

    case 'never_run':
      return '실행 기록 없음'

    default:
      return status ?? '-'
  }
}


function getStatusClass(
  status?: string,
): string {
  switch (status) {
    case 'completed':
      return 'status-success'

    case 'running':
      return 'status-running'

    case 'failed':
      return 'status-failed'

    default:
      return 'status-default'
  }
}


function IndexStatusPanel() {
  const [status, setStatus] =
    useState<IndexStatus | null>(null)

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)


  const loadStatus = async () => {
    try {
      const data = await getIndexStatus()

      setStatus(data)
      setError(null)
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message)
      } else {
        setError(
          '인덱싱 상태를 불러오지 못했습니다.',
        )
      }
    }
  }


  const handleIndex = async () => {
    setLoading(true)
    setError(null)

    try {
      const result = await runIndex()

      setStatus(result)

      await loadStatus()

    } catch (error) {
      if (error instanceof Error) {
        setError(error.message)
      } else {
        setError(
          '인덱싱 실행 중 오류가 발생했습니다.',
        )
      }
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadStatus()
  }, [])


  return (
    <section className="index-panel">

      <div className="index-panel-header">
        <div>
          <div className="section-label">
            FILE INDEX
          </div>

          <h2>파일 인덱스</h2>

          <p className="index-description">
            검색 대상 폴더의 파일 정보를
            최신 상태로 갱신합니다.
          </p>
        </div>

        <button
          type="button"
          className="index-button"
          onClick={handleIndex}
          disabled={loading}
        >
          {loading
            ? '인덱싱 중...'
            : '파일 새로고침'}
        </button>
      </div>


      {error && (
        <div className="index-error">
          {error}
        </div>
      )}


      {status && (
        <>
          <div className="index-current-status">

            <span
              className={`status-badge ${getStatusClass(
                status.status,
              )}`}
            >
              {getStatusLabel(
                status.status,
              )}
            </span>

            <span className="index-last-updated">
              마지막 갱신:{' '}
              {formatDate(
                status.completed_at,
              )}
            </span>

          </div>


          <div className="index-status">

            <div>
              <span>확인 파일</span>
              <strong>
                {status.scanned_files ?? 0}
              </strong>
            </div>

            <div>
              <span>신규</span>
              <strong>
                {status.new_files ?? 0}
              </strong>
            </div>

            <div>
              <span>수정</span>
              <strong>
                {status.updated_files ?? 0}
              </strong>
            </div>

            <div>
              <span>비활성</span>
              <strong>
                {status.inactive_files ?? 0}
              </strong>
            </div>

            <div>
              <span>건너뜀</span>
              <strong>
                {status.skipped_files ?? 0}
              </strong>
            </div>

            <div>
              <span>오류</span>
              <strong>
                {status.error_count ?? 0}
              </strong>
            </div>

          </div>


          {status.error_message && (
            <div className="index-error-detail">
              {status.error_message}
            </div>
          )}
        </>
      )}

    </section>
  )
}


export default IndexStatusPanel