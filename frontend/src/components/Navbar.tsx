import { Link, useRouterState } from "@tanstack/react-router"
import { FileText } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Appearance } from "./Common/Appearance"

const navItems = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/pricing", label: "Pricing" },
]

export function Navbar() {
  const { location } = useRouterState()
  const pathname = location.pathname

  return (
    <nav className="border-b border-border bg-background/95 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link
            to="/"
            className="flex items-center gap-2 font-bold text-lg text-primary hover:opacity-80 transition-opacity"
          >
            <FileText className="w-6 h-6" />
            <span>KeToanAuto</span>
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <Link key={item.href} to={item.href as "/"}>
                <Button
                  variant={pathname === item.href ? "default" : "ghost"}
                  className="text-sm"
                >
                  {item.label}
                </Button>
              </Link>
            ))}
          </div>
          <div className="md flex items-center gap-4">
            <Appearance />
            <Link to="/login" className="btn btn-outline btn-sm">
              Login
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
