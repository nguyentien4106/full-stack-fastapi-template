import { useNavigate } from "@tanstack/react-router"
import type React from "react"
import { useRef, useState } from "react"
import { isLoggedIn } from "@/hooks/useAuth"

export default function Hero() {
  const [isDrag, setIsDrag] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  const requireAuth = (action: () => void) => {
    if (!isLoggedIn()) {
      navigate({ to: "/login" })
      return
    }
    action()
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDrag(true)
  }

  const handleDragLeave = () => {
    setIsDrag(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDrag(false)
    requireAuth(() => {
      navigate({ to: "/dashboard" })
    })
  }

  const handleClick = () => {
    requireAuth(() => {
      navigate({ to: "/dashboard" })
    })
  }

  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-primary/10 via-primary/5 to-background py-16 sm:py-24 lg:py-32">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-foreground sm:text-6xl lg:text-7xl text-balance">
            Convert Bank Statements to Excel
          </h1>
          <p className="mt-6 text-xl text-muted-foreground sm:text-2xl max-w-3xl mx-auto">
            Upload your PDF or image bank statements and get organized Excel
            files instantly
          </p>

          <div className="mt-16 w-full">
            {/** biome-ignore lint/a11y/noStaticElementInteractions: <explanation> */}
            {/** biome-ignore lint/a11y/useKeyWithClickEvents: <explanation> */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={handleClick}
              className={`cursor-pointer rounded-2xl border-2 border-dashed p-16 sm:p-20 text-center transition-all ${
                isDrag
                  ? "border-primary bg-primary/10 shadow-2xl scale-105"
                  : "border-primary/40 bg-primary/5 hover:bg-primary/8 hover:border-primary/60 shadow-lg hover:shadow-2xl"
              }`}
            >
              <div className="flex justify-center mb-6">
                {/** biome-ignore lint/a11y/noSvgWithoutTitle: <explanation> */}
                <svg
                  className="h-24 w-24 text-primary/80"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
              </div>
              <p className="text-2xl sm:text-3xl font-bold text-foreground">
                Drag and drop your bank statement
              </p>
              <p className="mt-4 text-lg text-muted-foreground">
                or click to browse
              </p>
              <p className="mt-3 text-sm text-muted-foreground">
                Supports PDF and images (JPG, PNG) up to 100 MB
              </p>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.jpg,.jpeg,.png,.gif,.bmp"
              className="hidden"
            />
          </div>

          <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-8">
            <div className="flex flex-col items-center gap-3">
              <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-primary/10 border border-primary/20">
                {/** biome-ignore lint/a11y/noSvgWithoutTitle: <explanation> */}
                <svg
                  className="h-8 w-8 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <h3 className="font-semibold text-foreground text-lg">
                Instant Conversion
              </h3>
              <p className="text-sm text-muted-foreground">
                PDFs & images to Excel
              </p>
            </div>
            <div className="flex flex-col items-center gap-3">
              <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-primary/10 border border-primary/20">
                {/** biome-ignore lint/a11y/noSvgWithoutTitle: <explanation> */}
                <svg
                  className="h-8 w-8 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
              </div>
              <h3 className="font-semibold text-foreground text-lg">
                Bank-Grade Security
              </h3>
              <p className="text-sm text-muted-foreground">
                Your data is encrypted
              </p>
            </div>
            <div className="flex flex-col items-center gap-3">
              <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-primary/10 border border-primary/20">
                {/** biome-ignore lint/a11y/noSvgWithoutTitle: <explanation> */}
                <svg
                  className="h-8 w-8 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h3 className="font-semibold text-foreground text-lg">
                100% Accurate
              </h3>
              <p className="text-sm text-muted-foreground">
                Preserves all data
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
