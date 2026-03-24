import { createFileRoute, Outlet } from "@tanstack/react-router"
import { Navbar } from "@/components/Navbar"

export const Route = createFileRoute("/_public")({
  component: PublicLayout,
})

function PublicLayout() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <Outlet />
    </div>
  )
}
