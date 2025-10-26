import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Simple VAD Demo',
  description: 'Real-time Voice Activity Detection using Silero VAD',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, padding: 0, backgroundColor: '#f5f5f5' }}>
        {children}
      </body>
    </html>
  )
}
