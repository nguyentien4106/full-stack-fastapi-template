import { Link } from '@tanstack/react-router'
import { Appearance } from './Common/Appearance'
import { isLoggedIn } from '@/hooks/useAuth'
import { ArrowRight } from 'lucide-react'

export default function Header() {
  console.log("Header rendered, isLoggedIn:", isLoggedIn())
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link to='/home' className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
                {/** biome-ignore lint/a11y/noSvgWithoutTitle: <explanation> */}
                <svg className="h-5 w-5 text-primary-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-lg font-bold text-foreground">KeToanAuto</span>
            </Link>
            <nav className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Features
              </a>
              <a href="#how" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                How it works
              </a>
              <a href="#faq" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                FAQ
              </a>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <Appearance />
            
            {!isLoggedIn() ? (
              <>
                <Link to="/login" className="hidden sm:inline-flex text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                  Sign In
                </Link>
                <Link to="/signup" className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors">
                  Sign Up
                </Link>
              </>
            ) : (
              <Link to="/dashboard" className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors">
                <div className="flex items-center gap-2">
                  Dashboard
                  <ArrowRight className="w-4 h-4" />
                </div>
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
