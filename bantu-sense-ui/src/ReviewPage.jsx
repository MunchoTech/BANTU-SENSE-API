import { useMemo, useState } from 'react'
import './ReviewPage.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'

async function readError(response) {
  try {
    const body = await response.json()
    return body.detail || body.message || body.error || 'The review service could not complete that request.'
  } catch {
    return 'The review service could not complete that request.'
  }
}

function ReviewPage() {
  const [accessCode, setAccessCode] = useState('')
  const [reviewerCode, setReviewerCode] = useState('')
  const [queue, setQueue] = useState(null)
  const [languageCheck, setLanguageCheck] = useState('')
  const [intentLabel, setIntentLabel] = useState('')
  const [naturalness, setNaturalness] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const completed = useMemo(() => new Set(queue?.completedSampleIds || []), [queue])
  const currentTask = queue?.tasks.find((task) => !completed.has(task.sampleId))
  const completedCount = completed.size
  const totalCount = queue?.tasks.length || 0

  const loadTasks = async (event) => {
    event.preventDefault()
    if (!accessCode.trim() || !reviewerCode.trim()) return
    setIsLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_BASE_URL}/api/review/tasks`, {
        headers: {
          'X-Review-Access-Code': accessCode.trim(),
          'X-Reviewer-Code': reviewerCode.trim(),
        },
      })
      if (!response.ok) throw new Error(await readError(response))
      setQueue(await response.json())
    } catch (requestError) {
      setError(requestError.message || 'Could not load review messages. Check your access code and try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const submitReview = async (event) => {
    event.preventDefault()
    if (!currentTask || !languageCheck || !intentLabel || !naturalness || isLoading) return
    setIsLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_BASE_URL}/api/review/submissions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Review-Access-Code': accessCode.trim(),
        },
        body: JSON.stringify({
          sampleId: currentTask.sampleId,
          reviewerCode: reviewerCode.trim(),
          languageCheck,
          intentLabel,
          naturalness,
          notes,
        }),
      })
      if (!response.ok) throw new Error(await readError(response))
      setQueue((previous) => ({
        ...previous,
        completedSampleIds: [...previous.completedSampleIds, currentTask.sampleId],
      }))
      setLanguageCheck('')
      setIntentLabel('')
      setNaturalness('')
      setNotes('')
    } catch (requestError) {
      setError(requestError.message || 'Your review could not be saved. Please try again.')
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
        <a className="review-home-link" href="/">Back to message analyzer</a>
      </header>

      <main className="review-main">
        <div className="review-eyebrow">COMMUNITY LANGUAGE REVIEW</div>
        <h1 className="review-title">Help us understand the message.</h1>
        <p className="review-intro">Read each message and share what it means to you as a Bemba or Nyanja speaker. There are no right answers to guess. We want your honest judgment.</p>

        {!queue ? (
          <section className="review-card">
            <h2>Start reviewing</h2>
            <p className="review-help">Enter the review access code and the reviewer code given to you by the project owner. Your name and email are not requested.</p>
            <form className="review-access-form" onSubmit={loadTasks}>
              <label htmlFor="access-code">Review access code</label>
              <input id="access-code" type="password" autoComplete="off" value={accessCode} onChange={(event) => setAccessCode(event.target.value)} required />
              <label htmlFor="reviewer-code">Your reviewer code</label>
              <input id="reviewer-code" type="text" autoComplete="off" value={reviewerCode} onChange={(event) => setReviewerCode(event.target.value)} minLength={2} maxLength={24} required />
              {error && <p className="review-error" role="alert">{error}</p>}
              <button className="review-primary-button" type="submit" disabled={isLoading || !accessCode.trim() || !reviewerCode.trim()}>
                {isLoading ? 'Loading messages…' : 'Start review'}
              </button>
            </form>
          </section>
        ) : currentTask ? (
          <section className="review-card" aria-labelledby="message-title">
            <div className="review-progress-row">
              <span>Message {completedCount + 1} of {totalCount}</span>
              <span>{completedCount} completed</span>
            </div>
            <div className="review-progress-track" role="progressbar" aria-valuenow={completedCount} aria-valuemin="0" aria-valuemax={totalCount}>
              <span style={{ width: `${totalCount ? (completedCount / totalCount) * 100 : 0}%` }} />
            </div>
            <div className="review-language">{currentTask.language}</div>
            <h2 id="message-title" className="review-message">{currentTask.phrase}</h2>
            <p className="review-sample-id">Message reference: {currentTask.sampleId}</p>

            <form className="review-answers" onSubmit={submitReview}>
              <fieldset>
                <legend>Is this message written in the language shown above?</legend>
                <RadioOption name="language-check" value="correct" label="Yes" selected={languageCheck} onChange={setLanguageCheck} />
                <RadioOption name="language-check" value="incorrect" label="No" selected={languageCheck} onChange={setLanguageCheck} />
                <RadioOption name="language-check" value="unsure" label="Not sure" selected={languageCheck} onChange={setLanguageCheck} />
              </fieldset>

              <fieldset>
                <legend>What is the main intent of this message?</legend>
                <RadioOption name="intent" value="medical" label="Medical or health" selected={intentLabel} onChange={setIntentLabel} />
                <RadioOption name="intent" value="legal" label="Legal or rights" selected={intentLabel} onChange={setIntentLabel} />
                <RadioOption name="intent" value="financial" label="Money or financial" selected={intentLabel} onChange={setIntentLabel} />
                <RadioOption name="intent" value="unclear" label="Unclear or another intent" selected={intentLabel} onChange={setIntentLabel} />
              </fieldset>

              <fieldset>
                <legend>Does the message sound natural in this language?</legend>
                <RadioOption name="naturalness" value="natural" label="Yes, it sounds natural" selected={naturalness} onChange={setNaturalness} />
                <RadioOption name="naturalness" value="awkward" label="No, it sounds awkward" selected={naturalness} onChange={setNaturalness} />
                <RadioOption name="naturalness" value="unsure" label="Not sure" selected={naturalness} onChange={setNaturalness} />
              </fieldset>

              <label className="review-notes-label" htmlFor="review-notes">Anything else we should know? <span>Optional</span></label>
              <textarea id="review-notes" value={notes} maxLength={1000} onChange={(event) => setNotes(event.target.value)} placeholder="For example, is more context needed to understand it?" />
              {error && <p className="review-error" role="alert">{error}</p>}
              <button className="review-primary-button" type="submit" disabled={isLoading || !languageCheck || !intentLabel || !naturalness}>
                {isLoading ? 'Saving…' : 'Save and continue'}
              </button>
            </form>
          </section>
        ) : (
          <section className="review-card review-finished" role="status">
            <div className="review-finished-mark" aria-hidden="true">✓</div>
            <h2>Thank you for helping.</h2>
            <p>You have reviewed all {totalCount} messages assigned to you. Your answers have been saved.</p>
            <a className="review-secondary-link" href="/">Return to Bantu-Sense</a>
          </section>
        )}

        <p className="review-privacy">Please do not add names, phone numbers, or other personal details in your notes. Your answers are saved for this research review. They will not change the model automatically. <a href="/review/results">Project owner: download answers</a></p>
      </main>
    </div>
  )
}

function RadioOption({ name, value, label, selected, onChange }) {
  return (
    <label className={`review-radio-option${selected === value ? ' selected' : ''}`}>
      <input type="radio" name={name} value={value} checked={selected === value} onChange={() => onChange(value)} />
      <span>{label}</span>
    </label>
  )
}

export default ReviewPage
