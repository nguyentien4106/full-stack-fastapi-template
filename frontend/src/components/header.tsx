import { Link } from '@tanstack/react-router'
import { Appearance } from './Common/Appearance'
import { isLoggedIn } from '@/hooks/useAuth'
import { ArrowRight } from 'lucide-react'
import { Logo } from './Common/Logo'

export default function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">

          {/* Left — Logo */}
          <Link to='/home' className="flex items-center shrink-0">
            <Logo variant="full" className="h-24" asLink={false} />
          </Link>

          {/* Centre — Nav links */}
          <nav className="hidden md:flex items-center gap-8 absolute left-1/2 -translate-x-1/2">
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

          {/* Right — Actions */}
          <div className="flex items-center gap-4 shrink-0">
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
