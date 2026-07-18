/**
 * CourseForge AI — 404 Not Found Page
 *
 * Shown for any unmatched route.
 * Designed per Section 4.16 of the UI/UX Design Specification.
 */

import { useNavigate } from 'react-router-dom'
import styles from './NotFoundPage.module.css'

export default function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <main className={styles.container} aria-labelledby="not-found-title">
      {/* Background ambient glow */}
      <div className={styles.glow} aria-hidden="true" />

      <div className={styles.content}>
        {/* Large 404 number */}
        <span className={styles.code} aria-hidden="true">404</span>

        <h1 id="not-found-title" className={styles.title}>
          This page doesn&apos;t exist
        </h1>

        <p className={styles.description}>
          The page you&apos;re looking for may have been moved or deleted.
        </p>

        <div className={styles.actions}>
          <button
            id="not-found-back"
            className={styles.btnGhost}
            onClick={() => navigate(-1)}
            type="button"
          >
            ← Go back
          </button>

          <button
            id="not-found-home"
            className={styles.btnPrimary}
            onClick={() => navigate('/dashboard')}
            type="button"
          >
            Dashboard →
          </button>
        </div>
      </div>
    </main>
  )
}
