import SearchResultCard from './SearchResultCard'

import type {
  FileTypeFilter,
  SearchResponse,
} from '../types/search'


interface SearchResultListProps {
  data: SearchResponse | null

  selectedFileType: FileTypeFilter

  onFileTypeChange: (
    fileType: FileTypeFilter
  ) => void

  onPageChange: (
    page: number
  ) => void
}


const FILE_TYPE_FILTERS: {
  value: FileTypeFilter
  label: string
}[] = [
  {
    value: 'all',
    label: '전체',
  },
  {
    value: 'pdf',
    label: 'PDF',
  },
  {
    value: 'excel',
    label: 'Excel',
  },
  {
    value: 'ppt',
    label: 'PPT',
  },
  {
    value: 'word',
    label: 'Word',
  },
]


function getVisiblePages(
  currentPage: number,
  totalPages: number,
): number[] {
  if (totalPages <= 10) {
    return Array.from(
      {
        length: totalPages,
      },
      (_, index) => index + 1,
    )
  }

  let startPage =
    currentPage - 4

  let endPage =
    currentPage + 5

  if (startPage < 1) {
    startPage = 1
    endPage = 10
  }

  if (endPage > totalPages) {
    endPage = totalPages
    startPage = totalPages - 9
  }

  return Array.from(
    {
      length:
        endPage - startPage + 1,
    },
    (_, index) =>
      startPage + index,
  )
}


export default function SearchResultList({
  data,
  selectedFileType,
  onFileTypeChange,
  onPageChange,
}: SearchResultListProps) {

  if (!data) {
    return null
  }

  const visiblePages =
    getVisiblePages(
      data.page,
      data.total_pages,
    )

  return (
    <section className="search-results">

      <div className="results-toolbar">

        <div className="results-summary">
          <div className="results-count">
            관련 파일{' '}
            <strong>
              {data.total}
            </strong>
            건
          </div>

          <div className="response-time">
            응답시간 {data.response_time_ms}ms
          </div>
        </div>

        <div
          className="file-type-filters"
          aria-label="파일 형식 필터"
        >
          {FILE_TYPE_FILTERS.map(
            (filter) => (
              <button
                key={filter.value}
                type="button"
                className={
                  selectedFileType
                    === filter.value
                    ? 'file-type-button active'
                    : 'file-type-button'
                }
                onClick={() =>
                  onFileTypeChange(
                    filter.value
                  )
                }
              >
                {filter.label}
              </button>
            )
          )}
        </div>

      </div>


      {data.total === 0 ? (

        <div className="empty-result">
          검색 결과가 없습니다.
        </div>

      ) : (

        <>
          <div className="result-list">
            {data.results.map(
              (result) => (
                <SearchResultCard
                  key={result.id}
                  result={result}
                />
              )
            )}
          </div>


          {data.total_pages > 1 && (

            <nav
              className="pagination"
              aria-label="검색 결과 페이지"
            >

              <button
                type="button"
                className="pagination-nav"
                disabled={
                  data.page <= 1
                }
                onClick={() =>
                  onPageChange(
                    data.page - 1
                  )
                }
              >
                이전
              </button>


              <div className="pagination-pages">

                {visiblePages.map(
                  (pageNumber) => (
                    <button
                      key={pageNumber}
                      type="button"
                      className={
                        data.page
                          === pageNumber
                          ? 'pagination-page active'
                          : 'pagination-page'
                      }
                      onClick={() =>
                        onPageChange(
                          pageNumber
                        )
                      }
                    >
                      {pageNumber}
                    </button>
                  )
                )}

              </div>


              <button
                type="button"
                className="pagination-nav"
                disabled={
                  data.page
                  >= data.total_pages
                }
                onClick={() =>
                  onPageChange(
                    data.page + 1
                  )
                }
              >
                다음
              </button>

            </nav>

          )}

        </>
      )}

    </section>
  )
}