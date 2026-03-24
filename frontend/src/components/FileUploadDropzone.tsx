import { useState } from "react"
import { Upload, File, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface FileUploadDropzoneProps {
  onFileSelect?: (file: File) => void
  accept?: string
}

export function FileUploadDropzone({
  onFileSelect,
  accept = ".pdf,.csv,.txt",
}: FileUploadDropzoneProps) {
  const [isDragActive, setIsDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true)
    } else if (e.type === "dragleave") {
      setIsDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
    if (e.dataTransfer.files?.[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file: File) => {
    setSelectedFile(file)
    onFileSelect?.(file)
  }

  const handleClear = () => {
    setSelectedFile(null)
  }

  return (
    <Card
      className={`border-2 border-dashed transition-all ${
        isDragActive
          ? "border-primary bg-primary/5 scale-105"
          : "border-border hover:border-primary/50"
      }`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      {!selectedFile ? (
        <div className="p-12 flex flex-col items-center justify-center text-center">
          <div className="mb-4">
            <Upload className="w-12 h-12 text-primary/60 mx-auto" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Upload bank statement</h3>
          <p className="text-sm text-foreground/60 mb-6">
            Drag and drop your file here, or click to browse
          </p>
          <label className="cursor-pointer">
            <Button asChild>
              <span>Select File</span>
            </Button>
            <input
              type="file"
              accept={accept}
              onChange={handleChange}
              className="hidden"
            />
          </label>
          <p className="text-xs text-foreground/50 mt-2">
            Supported formats: PDF, CSV, TXT (Max 10MB)
          </p>
        </div>
      ) : (
        <div className="p-8 flex flex-col items-center justify-center">
          <div className="mb-4 p-3 rounded-full bg-accent/10">
            <File className="w-8 h-8 text-accent" />
          </div>
          <h4 className="text-sm font-semibold mb-1 text-center wrap-break-word max-w-xs">
            {selectedFile.name}
          </h4>
          <p className="text-xs text-foreground/60 mb-6">
            {(selectedFile.size / 1024).toFixed(2)} KB
          </p>
          <div className="flex gap-3">
            <Button variant="outline" size="sm" onClick={handleClear}>
              <X className="w-4 h-4 mr-1" />
              Clear
            </Button>
            <Button size="sm">Upload File</Button>
          </div>
        </div>
      )}
    </Card>
  )
}
