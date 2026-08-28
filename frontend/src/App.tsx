import {
  useState,
} from 'react'

import './App.css'

import IndexStatusPanel from './components/IndexStatusPanel'
import SearchBar from './components/SearchBar'
import SearchResultList from './components/SearchResultList'

import {
  searchFiles,
} from './services/searchApi'

import type {
  FileTypeFilter,
  SearchResponse,
} from './types/search'


const PAGE_SIZE = 5


function App() {
  const [
    data,
    setData,
  ] = useState<SearchResponse | null>(
    null
  )

  const [
    loading,
    setLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  )

  const [
    currentQuery,
    setCurrentQuery,
  ] = useState('')

  const [
    selectedFileType,
    setSelectedFileType,
  ] = useState<FileTypeFilter>(
    'all'
  )


  const executeSearch = async (
    query: string,
    page: number,
    fileType: FileTypeFilter,
  ) => {
    const trimmedQuery =
      query.trim()

    if (!trimmedQuery) {
      return
    }

    setLoading(true)
    setError(null)

    try {
      const result = await searchFiles({
        query: trimmedQuery,
        page,
        pageSize: PAGE_SIZE,
        fileType,
      })

      setData(
        result
      )

    } catch (searchError) {

      if (
        searchError
        instanceof Error
      ) {
        setError(
          searchError.message
        )

      } else {
        setError(
          '파일 검색 중 오류가 발생했습니다.'
        )
      }

    } finally {
      setLoading(false)
    }
  }


  const handleSearch = async (
    query: string,
  ) => {
    const trimmedQuery =
      query.trim()

    if (!trimmedQuery) {
      return
    }

    //
    // 새로운 검색어는
    // 전체 파일 / 1페이지부터 시작
    //
    setCurrentQuery(
      trimmedQuery
    )

    setSelectedFileType(
      'all'
    )

    await executeSearch(
      trimmedQuery,
      1,
      'all',
    )
  }


  const handleFileTypeChange = async (
    fileType: FileTypeFilter,
  ) => {
    if (!currentQuery) {
      return
    }

    //
    // 확장자 변경 시
    // 무조건 1페이지로 이동
    //
    setSelectedFileType(
      fileType
    )

    await executeSearch(
      currentQuery,
      1,
      fileType,
    )
  }


  const handlePageChange = async (
    page: number,
  ) => {
    if (!currentQuery) {
      return
    }

    await executeSearch(
      currentQuery,
      page,
      selectedFileType,
    )

    //
    // 페이지 이동 후
    // 검색 결과 상단을 보기 편하도록 이동
    //
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }


  return (
    <main className="app">

      <section className="hero">

        <div className="hero-badge">
          INTERNAL FILE SEARCH
        </div>

        <h1>
          사내 파일 검색
        </h1>

        <p>
          파일명과 폴더 정보를 기반으로
          필요한 자료를 빠르게 찾습니다.
        </p>

      </section>


      <SearchBar
        onSearch={handleSearch}
        loading={loading}
      />


      {error && (
        <div className="search-error">
          {error}
        </div>
      )}


      {loading && (
        <div className="search-loading">
          검색 중입니다...
        </div>
      )}


      {!loading && (
        <SearchResultList
          data={data}
          selectedFileType={
            selectedFileType
          }
          onFileTypeChange={
            handleFileTypeChange
          }
          onPageChange={
            handlePageChange
          }
        />
      )}


      <IndexStatusPanel />

    </main>
  )
}


export default App