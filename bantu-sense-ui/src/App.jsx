import { useState } from 'react'
import './App.css'

const examples = [
  'Mwana wanga akudwala kwambiri, ndithandizeni.',
  'Nifuna kutsegula account ya banki.',
]

function App() {
  const [inputText, setInputText] = useState('')
  const [result, setResult] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [donateForReview, setDonateForReview] = useState(false)

  const handleAnalyze = async (event) => {
    event.preventDefault()
    if (!inputText.trim() || isAnalyzing) return

    setIsAnalyzing(true)
    setResult(null)

    try {
      const response = await fetch('http://localhost:8080/api/inquiries/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ originalText: inputText.trim(), donateForReview }),
      })

      if (!response.ok) throw new Error('The analysis service could not complete this request.')

      const contentType = response.headers.get('content-type') || ''
      const data = contentType.includes('application/json') ? await response.json() : null
      setResult(data ? {
        intent: data.detectedIntent || 'PENDING_ANALYSIS',
        confidence: data.confidenceScore,
        urgency: data.urgencyLevel,
        reviewSubmitted: data.reviewSubmitted,
        message: data.detectedIntent === 'PENDING_ANALYSIS'
          ? 'Your message was received and is waiting for analysis.'
          : data.analysisMessage || 'Your message has been analyzed.',
      } : {
        intent: 'PENDING_ANALYSIS',
        message: 'Your message was received and is waiting for analysis.',
      })
    } catch (error) {
      setResult({ error: error.message || 'Unable to reach the Bantu-Sense service.' })
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#home" aria-label="Bantu-Sense home">
          <span className="brand-mark" aria-hidden="true">b.</span>
          <span>Bantu<span className="brand-light">Sense</span></span>
        </a>
        <div className="topbar-note"><span className="status-dot" /> Language support for people first</div>
      </header>

      <main id="home" className="main-content">
        <section className="intro">
          <div className="eyebrow"><span /> BUILT FOR LOCAL CONTEXT</div>
          <h1>Every message<br />deserves to be <em>understood.</em></h1>
          <p className="intro-copy">Share a message in Nyanja or Bemba. Bantu-Sense helps surface its intent and urgency with local language in mind.</p>
          <div className="language-row" aria-label="Supported languages">
            <span className="language-pill"><span className="language-dot" /> Nyanja</span>
            <span className="language-pill"><span className="language-dot" /> Bemba</span>
            <span className="language-caption">More languages are on the way</span>
          </div>
        </section>

        <section className="analyzer-card" aria-labelledby="analyzer-title">
          <div className="card-heading">
            <div>
              <div className="card-kicker">MESSAGE ANALYZER</div>
              <h2 id="analyzer-title">What would you like us to understand?</h2>
            </div>
            <div className="spark-icon" aria-hidden="true">✳</div>
          </div>

          <form onSubmit={handleAnalyze}>
            <label className="sr-only" htmlFor="message">Your message in Nyanja or Bemba</label>
            <textarea
              id="message"
              value={inputText}
              onChange={(event) => setInputText(event.target.value)}
              placeholder="Type or paste a message in Nyanja or Bemba…"
              maxLength={2000}
            />
            <div className="form-meta"><span>Review contribution is optional.</span><span>{inputText.length} / 2,000</span></div>
            <label className="review-consent">
              <input
                type="checkbox"
                checked={donateForReview}
                onChange={(event) => setDonateForReview(event.target.checked)}
              />
              <span>
                If analysis is uncertain, allow this message to be saved for human review and model improvement.
                <small>Optional. Unchecked by default. Your inquiry may still be stored by the service to return its result.</small>
              </span>
            </label>
            <div className="form-actions">
              <span className="action-hint">Try an example below, or write your own.</span>
              <button type="submit" disabled={!inputText.trim() || isAnalyzing}>
                {isAnalyzing ? 'Analyzing…' : 'Analyze message'} <span aria-hidden="true">↗</span>
              </button>
            </div>
          </form>

          <div className="examples">
            <span className="examples-label">EXAMPLE MESSAGES</span>
            <div className="example-list">
              {examples.map((example) => (
                <button className="example-chip" key={example} onClick={() => setInputText(example)} type="button">{example}<span aria-hidden="true">↗</span></button>
              ))}
            </div>
          </div>

          {result && (
            <div className={`result-panel${result.error ? ' result-error' : ''}`} role="status" aria-live="polite">
              {result.error ? <>
                <div className="result-label">SERVICE UNAVAILABLE</div>
                <p>{result.error}</p>
                <span className="result-note">Check that the Bantu-Sense services are running, then try again.</span>
              </> : <>
                <div className="result-label">ANALYSIS RESULT</div>
                <div className="result-intent">{result.intent?.replaceAll('_', ' ')}</div>
                {result.message && <p>{result.message}</p>}
                {result.intent === 'UNCERTAIN' && (
                  <span className="result-note">
                    {result.reviewSubmitted
                      ? 'Review contribution submitted with your consent.'
                      : 'This message was not submitted to the review dataset.'}
                  </span>
                )}
                <div className="result-details">
                  {result.confidence != null && <span><b>Confidence</b>{result.confidence}%</span>}
                  {result.urgency && <span><b>Urgency</b>{result.urgency}</span>}
                </div>
              </>}
            </div>
          )}
        </section>

        <p className="footnote"><span>✳</span> Designed to listen to language, context, and the person behind every message.</p>
      </main>

      <footer className="page-footer"><span>© 2026 Bantu-Sense</span><span>Made with care in Zambia <span className="flag">●</span></span></footer>
    </div>
  )
}

export default App
