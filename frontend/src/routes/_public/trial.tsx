import { createFileRoute, Link } from "@tanstack/react-router"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { BankTypeSelect } from "@/components/BankTypeSelect"
import { FileUploadDropzone } from "@/components/FileUploadDropzone"
import { FileHistoryTable } from "@/components/FileHistoryTable"
import { mockFileHistory } from "@/lib/mock-data"
import { ArrowRight } from "lucide-react"

export const Route = createFileRoute("/_public/trial")({
  component: Trial,
  head: () => ({
    meta: [{ title: "Trial - KeToanAuto" }],
  }),
})

function Trial() {
  const [selectedBank, setSelectedBank] = useState<string>("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
  }

  const handleConvert = async () => {
    if (!selectedFile || !selectedBank) return
    setIsProcessing(true)
    await new Promise((resolve) => setTimeout(resolve, 2000))
    setIsProcessing(false)
    setSelectedFile(null)
    setSelectedBank("")
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="mb-12">
        <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
        <p className="text-foreground/60">
          Upload and convert your bank statements to Excel
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        {/* Upload Section */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="p-8">
            <h2 className="text-2xl font-bold mb-6">Convert Your Statement</h2>
            <div className="space-y-6">
              <BankTypeSelect
                value={selectedBank}
                onValueChange={setSelectedBank}
              />
              <div>
                <label
                  htmlFor="file-upload"
                  className="text-sm font-medium block mb-3"
                >
                  Upload Statement
                </label>
                <FileUploadDropzone onFileSelect={handleFileSelect} />
              </div>
              <Button
                onClick={handleConvert}
                disabled={!selectedFile || !selectedBank || isProcessing}
                className="w-full gap-2"
                size="lg"
              >
                {isProcessing ? (
                  <>Processing...</>
                ) : (
                  <>
                    Convert to Excel <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </Button>
              <div className="bg-primary/5 rounded-lg p-4 border border-primary/10 text-sm text-foreground/70">
                <p className="font-medium mb-2 text-primary">💡 Pro Tip:</p>
                <p>
                  Upload multiple statements to process them together. Our system
                  will automatically organize all transactions chronologically.
                </p>
              </div>
            </div>
          </Card>

          {/* Recent Conversions */}
          <div>
            <h2 className="text-2xl font-bold mb-6">Recent Conversions</h2>
            <Card className="overflow-hidden">
              <FileHistoryTable files={mockFileHistory} />
            </Card>
          </div>
        </div>

        {/* Sidebar Stats */}
        <div className="space-y-6">
          <Card className="p-6 bg-primary/5 border-primary/10">
            <div className="text-center">
              <p className="text-4xl font-bold text-primary mb-2">12</p>
              <p className="text-sm text-foreground/70 mb-4">
                Files Processed This Month
              </p>
              <div className="w-full bg-primary/20 rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{ width: "60%" }}
                />
              </div>
              <p className="text-xs text-foreground/60 mt-2">
                60% of monthly quota
              </p>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="font-semibold mb-4">Quick Stats</h3>
            <div className="space-y-4 text-sm">
              <div className="flex justify-between">
                <span className="text-foreground/60">Total Files</span>
                <span className="font-semibold">48</span>
              </div>
              <div className="border-t border-border pt-4 flex justify-between">
                <span className="text-foreground/60">Total Transactions</span>
                <span className="font-semibold">2,847</span>
              </div>
              <div className="border-t border-border pt-4 flex justify-between">
                <span className="text-foreground/60">Storage Used</span>
                <span className="font-semibold">245 MB</span>
              </div>
            </div>
          </Card>

          <Card className="p-6 border-primary/30 bg-primary/5">
            <h3 className="font-semibold mb-3">Upgrade to Pro</h3>
            <p className="text-sm text-foreground/70 mb-4">
              Get unlimited conversions and advanced features
            </p>
            <Link to="/pricing">
              <Button className="w-full">Upgrade Plan</Button>
            </Link>
          </Card>
        </div>
      </div>
    </div>
  )
}
