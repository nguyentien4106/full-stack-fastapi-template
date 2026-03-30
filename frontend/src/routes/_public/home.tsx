/** biome-ignore-all lint/a11y/noStaticElementInteractions: <explanation> */
import { createFileRoute } from "@tanstack/react-router"
import { useRef, useState } from "react"
import Header from "@/components/header"
import Hero from "@/components/hero"
import Features from "@/components/features"
import HowItWorks from "@/components/how-it-works"
import Testimonials from "@/components/testimonials"
import FAQ from "@/components/faq"
import Footer from "@/components/footer"
import * as Dialog from '@radix-ui/react-dialog'
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_public/home")({
  component: Home,
  head: () => ({
    meta: [{ title: "BankToExcel - Convert Bank Statements to Excel" }],
  }),
})
function Home() {
  const [isOpen, setIsOpen] = useState(false)
  const [fileName, setFileName] = useState<string | null>(null)
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <Hero onOpenDialog={() => setIsOpen(true)} />
      <Features />
      <HowItWorks />
      <Testimonials />
      <FAQ />
      <Footer />

      <Dialog.Root open={isOpen} onOpenChange={setIsOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-50 bg-black/50" />
          <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg bg-card p-8 shadow-xl">
            <Dialog.Title className="text-2xl font-bold text-card-foreground">
              Upload Bank Statement
            </Dialog.Title>
            <Dialog.Description className="mt-2 text-sm text-muted-foreground">
              Upload a PDF or image of your bank statement to convert to Excel (up to 100 MB)
            </Dialog.Description>

            <FileUploadZone onFileSelect={(name) => setFileName(name)} />

            {fileName && (
              <div className="mt-6 space-y-4">
                <div className="rounded-lg bg-secondary p-4">
                  <p className="text-sm font-medium text-card-foreground">
                    Selected file: <span className="text-primary">{fileName}</span>
                  </p>
                </div>
                {/** biome-ignore lint/a11y/useButtonType: <explanation> */}
                <button className="w-full rounded-lg bg-primary px-4 py-2 font-semibold text-primary-foreground hover:bg-primary/90 transition-colors">
                  Convert to Excel
                </button>
              </div>
            )}

            <Dialog.Close asChild>
              {/** biome-ignore lint/a11y/useButtonType: <explanation> */}
              <button
                className="absolute right-4 top-4 text-muted-foreground hover:text-foreground transition-colors"
                aria-label="Close"
              >
                {/** biome-ignore lint/a11y/noSvgWithoutTitle: <explanation> */}
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </Dialog.Close>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  )
}

function FileUploadZone({ onFileSelect }: { onFileSelect: (name: string) => void }) {
  const [isDrag, setIsDrag] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

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
    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      const isValidType = file.type === 'application/pdf' || file.type.startsWith('image/')
      if (isValidType) {
        onFileSelect(file.name)
      }
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      onFileSelect(files[0].name)
    }
  }

  return (
    <div className="mt-6">
      {/** biome-ignore lint/a11y/useKeyWithClickEvents: <explanation> */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-all ${
          isDrag
            ? 'border-primary bg-secondary'
            : 'border-border bg-muted hover:bg-secondary'
        }`}
      >
        {/** biome-ignore lint/a11y/noSvgWithoutTitle: <explanation> */}
        <svg className="mx-auto h-12 w-12 text-primary/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        <p className="mt-4 text-sm font-medium text-foreground">
          Drag and drop your bank statement here
        </p>
        <p className="mt-1 text-xs text-muted-foreground">
          PDF or image (JPG, PNG)
        </p>
        <p className="mt-2 text-xs text-muted-foreground">
          Size up to 100 MB
        </p>
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.jpg,.jpeg,.png,.gif,.bmp"
        onChange={handleFileSelect}
        className="hidden"
      />
    </div>
  )
}
