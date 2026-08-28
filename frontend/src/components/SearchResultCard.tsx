import { useState } from 'react'

import type { SearchResult } from '../types/search'


interface SearchResultCardProps {
  result: SearchResult
}


function formatFileSize(
  bytes: number | null,
): string {
  if (bytes === null) {
    return '-'
  }

  if (bytes < 1024) {
    return `${bytes} B`
  }

  const kilobytes = bytes / 1024

  if (kilobytes < 1024) {
    return `${kilobytes.toFixed(1)} KB`
  }

  const megabytes = kilobytes / 1024

  if (megabytes < 1024) {
    return `${megabytes.toFixed(1)} MB`
  }

  const gigabytes = megabytes / 1024

  return `${gigabytes.toFixed(1)} GB`
}


function formatDate(
  value: string | null,
): string {
  if (!value) {
    return '-'
  }

  const date = new Date(value)

  return date.toLocaleString(
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


function SearchResultCard({
  result,
}: SearchResultCardProps) {
  const [copied, setCopied] =
    useState(false)

  const [copyError, setCopyError] =
    useState(false)


  const copyPath = async () => {
    try {
      await navigator.clipboard.writeText(
        result.full_path,
      )

      setCopied(true)
      setCopyError(false)

      window.setTimeout(() => {
        setCopied(false)
      }, 1500)

    } catch {
      setCopied(false)
      setCopyError(true)

      window.setTimeout(() => {
        setCopyError(false)
      }, 2000)
    }
  }


  return (
    <article className="result-card">

      <div className="result-header">

        <span className="extension-badge">
          {result.extension?.toUpperCase() ??
            'FILE'}
        </span>

        <button
          className={
            copied
              ? 'copy-button copied'
              : copyError
                ? 'copy-button copy-error'
                : 'copy-button'
          }
          type="button"
          onClick={copyPath}
        >
          {copied
            ? '복사 완료'
            : copyError
              ? '복사 실패'
              : '경로 복사'}
        </button>

      </div>


      <h2>
        {result.file_name}
      </h2>


      <p
        className="file-path"
        title={result.full_path}
      >
        {result.full_path}
      </p>


      <div className="result-meta">

        <span>
          수정일: {formatDate(result.modified_at)}
        </span>

        <span>
          크기: {formatFileSize(result.file_size)}
        </span>

      </div>

    </article>
  )
}


export default SearchResultCard