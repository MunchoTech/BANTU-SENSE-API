import { useState } from 'react'
import './ReviewPage.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'

function ReviewResultsPage() {
  const [adminCode, setAdminCode] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [isError, setIsError] = useState(false)

  const downloadResults = async (event) => {
    event.preventDefault()
    if (!adminCode.trim() || isLoading) return
    setIsLoading(true)
    setMessage('')
    setIsError(false)
    try {
      const response = await fetch(`${API_BASE_URL}/api/review/results.csv`, {
        headers: { 'X-Review-Admin-Code': adminCode.trim() },
      })
      if (!response.ok) {
        let errorMessage = 'Could not download review answers.'
        try {
          const body = await response.json()
          errorMessage = body.detail || body.message || body.error || errorMessage
        } catch { /* Keep the simple fallback message. */ }
        throw new Error(errorMessage)
      }
      const file = await response.blob()
      const url = URL.createObjectURL(file)
      const link = document.createElement('a')
      link.href = url
      link.download = 'review-responses.csv'
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
      setMessage('Your review responses were downloaded.')
    } catch (error) {
      setIsError(true)
      setMessage(error.message || 'Could not reach the review service.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="review-shell">
      <header className="review-topbar">
        <a className="review-brand" href="/" aria-label="Bantu-Sense home">
          <span className="review-brand-mark">b.</span>
          <span>Bantu<span className="review-brand-light">Sense</span></span>
        </a>
        <a className="review-home-link" href="/review">Back to community review</a>
      </header>
      <main className="review-main">
        <div className="review-eyebrow">PROJECT OWNER</div>
        <h1 className="review-title">Download review answers.</h1>
        <p className="review-intro">Use the private owner code to download the answers reviewers have submitted. This file does not contain the model answer key.</p>
        <section className="review-card">
          <form className="review-access-form" onSubmit={downloadResults}>
            <label htmlFor="admin-code">Owner download code</label>
            <input id="admin-code" type="password" autoComplete="off" value={adminCode} onChange={(event) => setAdminCode(event.target.value)} required />
            {message && <p className={isError ? 'review-error' : 'review-success'} role="status">{message}</p>}
            <button className="review-primary-button" type="submit" disabled={isLoading || !adminCode.trim()}>
              {isLoading ? 'Preparing download…' : 'Download answers as CSV'}
            </button>
          </form>
        </section>
      </main>
    </div>
  )
}

export default ReviewResultsPage
