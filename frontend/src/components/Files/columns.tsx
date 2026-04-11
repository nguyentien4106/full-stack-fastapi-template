import type { ColumnDef } from "@tanstack/react-table"
import dayjs from "dayjs"
import { DownloadIcon, Loader2, RefreshCcw } from "lucide-react"
import { useState } from "react"
import { FaFileExcel } from "react-icons/fa6"
import { type FilePublic, FilesService } from "@/client"
import { OpenAPI } from "@/client/core/OpenAPI"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import { DateTimeFormat } from "@/utils"
import { StatusBadge } from "../StatusBadge"

async function downloadExcel(fileId: string, filename: string) {
  const token =
    typeof OpenAPI.TOKEN === "function"
      ? await OpenAPI.TOKEN({} as never)
      : OpenAPI.TOKEN

  const base = OpenAPI.BASE || ""
  const response = await fetch(`${base}/api/v1/files/${fileId}/download`, {
    method: "POST",
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })

  if (!response.ok) {
    throw new Error(`Download failed: ${response.statusText}`)
  }

  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  const safeName = filename.replace(/\.[^.]+$/, "")
  a.href = url
  a.download = `${safeName}_tables.xlsx`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

function DownloadMenu({ file }: { file: FilePublic }) {
  const [loading, setLoading] = useState(false)

  const handleSelect = async (format: string) => {
    if (format === "excel") {
      setLoading(true)
      try {
        await downloadExcel(file.id, file.filename)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
      return
    }

    // TODO: implement CSV/DOCX generation server-side or client-side conversion
    console.warn(`Download format '${format}' not supported yet for file ${file.id}`)
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="w-8 h-8 p-0"
          title="Download"
          disabled={loading}
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <DownloadIcon className="w-4 h-4" />}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => void handleSelect("excel")}>Excel (.xlsx)</DropdownMenuItem>
        <DropdownMenuItem onClick={() => void handleSelect("csv")}>
          CSV (.csv) — not supported
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => void handleSelect("docx")}>DOCX (.docx) — not supported</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}



export const columns: ColumnDef<FilePublic>[] = [
  {
    accessorKey: "filename",
    header: "File Name",
    cell: ({ row }) => (
      <span className="font-medium">{row.original.filename}</span>
    ),
  },
  {
    accessorKey: "content_type",
    header: "Content Type",
    cell: ({ row }) => {
      const contentType = row.original.content_type
      return (
        <span
          className={cn(
            "max-w-xs truncate block text-muted-foreground",
            !contentType && "italic",
          )}
        >
          {contentType || "No content type provided"}
        </span>
      )
    },
  },
  {
    id: "state",
    header: "State",
    cell: ({ row }) => {
      const state = row.original.job_status as
        | "pending"
        | "running"
        | "done"
        | "failed"
        | undefined

      return <StatusBadge status={state || "pending"} />
    },
  },
  {
    id: "created_at",
    header: "Uploaded At",
    cell: ({ row }) => {
      const file = row.original
      return (
        <div className="flex justify-between text-muted-foreground">
          {file.created_at
            ? dayjs(file.created_at).format(DateTimeFormat)
            : "Unknown"}
        </div>
      )
    },
  },
  {
    id: "actions",
    header: "Actions",
    cell: ({ row }) => {
      const file = row.original
      return (
        <div className="flex justify-end gap-2">
          {(file.job_status === "running" || file.job_status === "pending") && (
            <Button
              variant="ghost"
              size="sm"
              className="w-8 h-8 p-0"
              title="View"
              onClick={() => {
                FilesService.getFileStatus({ fileId: file.id })
              }}
            >
              <RefreshCcw className="w-4 h-4 text-green-300" />
            </Button>
          )}
          {file.job_status === "done" && (
            <DownloadMenu file={file} />
          )}
        </div>
      )
    },
  },
]
