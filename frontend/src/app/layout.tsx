import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/providers/theme-provider'
import { Toaster } from '@/components/ui/sonner'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Risk Management Platform | Institutional-Grade Analytics',
  description: 'Professional risk management platform with VaR analysis, DeFi analytics, portfolio optimization, and advanced ML models. Built for institutional traders and quantitative analysts.',
  keywords: ['risk management', 'VaR', 'portfolio analytics', 'DeFi', 'quantitative finance', 'machine learning'],
  authors: [{ name: 'Risk Management Platform' }],
  creator: 'Risk Management Platform',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    title: 'Risk Management Platform',
    description: 'Institutional-Grade Risk Analytics',
    siteName: 'Risk Management Platform',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Risk Management Platform',
    description: 'Institutional-Grade Risk Analytics',
  },
  robots: {
    index: true,
    follow: true,
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
  },
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head />
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  )
}
