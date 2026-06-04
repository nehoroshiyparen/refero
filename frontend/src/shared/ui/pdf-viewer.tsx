import { useState, useEffect, useRef } from 'react'
import { getAccessToken } from '@/shared/api/client'

interface PdfViewerProps {
  pdfUrl: string
  height?: string
}

export function PdfViewer({ pdfUrl, height = '1000px' }: PdfViewerProps) {
  const [loadError, setLoadError] = useState(false)
  const [checking, setChecking] = useState(true)
  const iframeRef = useRef<HTMLIFrameElement>(null)

  useEffect(() => {
    if (!pdfUrl) return

    setLoadError(false)
    setChecking(true)

    const controller = new AbortController()
    const token = getAccessToken()

    const sep = pdfUrl.includes('?') ? '&' : '?'
    const checkUrl = `${pdfUrl}${sep}inline=1${token ? `&token=${token}` : ''}`

    fetch(checkUrl, { signal: controller.signal })
      .then(async (res) => {
        if (!res.ok) setLoadError(true)
        if (!res.body) return
        const reader = res.body.getReader()
        await reader.cancel()
      })
      .catch(() => setLoadError(true))
      .finally(() => setChecking(false))

    return () => controller.abort()
  }, [pdfUrl])

  if (!pdfUrl) return null

  const token = getAccessToken()
  const sep = pdfUrl.includes('?') ? '&' : '?'
  const viewerUrl = `${pdfUrl}${sep}inline=1${token ? `&token=${token}` : ''}#toolbar=0`

  return (
    <div className="rounded-lg border overflow-hidden bg-muted/20">
      {checking && (
        <div
          className="flex items-center justify-center text-muted-foreground"
          style={{ height }}
        >
          Загрузка...
        </div>
      )}
      {loadError && (
        <div
          className="flex items-center justify-center text-muted-foreground"
          style={{ height }}
        >
          Статья не загружена
        </div>
      )}
      {!checking && !loadError && (
        <iframe
          ref={iframeRef}
          src={viewerUrl}
          className="w-full"
          style={{ height, border: 'none' }}
          title="PDF preview"
        />
      )}
    </div>
  )
}
