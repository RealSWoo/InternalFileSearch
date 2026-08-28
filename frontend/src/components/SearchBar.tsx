import { useState } from 'react'

interface SearchBarProps {
  onSearch: (query: string) => void
  loading: boolean
}

const EXAMPLE_QUERIES = [
  '스타필드 제안서',
  '미니쉬 PDF',
  '스타필드 엑셀',
]

function SearchBar({
  onSearch,
  loading,
}: SearchBarProps) {
  const [query, setQuery] = useState('')

  const submitQuery = (value: string) => {
    const trimmedQuery = value.trim()

    if (!trimmedQuery) {
      return
    }

    setQuery(trimmedQuery)
    onSearch(trimmedQuery)
  }

  const handleSubmit = (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()
    submitQuery(query)
  }

  return (
    <>
      <form
        className="search-bar"
        onSubmit={handleSubmit}
      >
        <input
          type="text"
          value={query}
          onChange={(event) =>
            setQuery(event.target.value)
          }
          placeholder="예: 스타필드 제안서 찾아줘"
          maxLength={200}
          disabled={loading}
          autoFocus
        />

        {query && !loading && (
          <button
            type="button"
            className="clear-button"
            onClick={() => setQuery('')}
            aria-label="검색어 지우기"
          >
            ×
          </button>
        )}

        <button
          className="search-button"
          type="submit"
          disabled={
            loading || !query.trim()
          }
        >
          {loading ? '검색 중...' : '검색'}
        </button>
      </form>

      <div className="example-chips">
        <span>빠른 검색</span>

        {EXAMPLE_QUERIES.map((example) => (
          <button
            type="button"
            key={example}
            onClick={() =>
              submitQuery(example)
            }
            disabled={loading}
          >
            {example}
          </button>
        ))}
      </div>
    </>
  )
}

export default SearchBar