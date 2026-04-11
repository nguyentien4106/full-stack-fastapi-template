import type { ColumnDef } from "@tanstack/react-table"
import dayjs from "dayjs"
import { DownloadIcon, Loader2, RefreshCcw } from "lucide-react"
import { useState } from "react"
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

async function downloadFile(fileId: string, filename: string, type: string) {
  const token =
    typeof OpenAPI.TOKEN === "function"
      ? await OpenAPI.TOKEN({} as never)
      : OpenAPI.TOKEN

  const base = OpenAPI.BASE || ""
  const response = await fetch(`${base}/api/v1/files/${fileId}/download?type=${type}`, {
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
  a.download = `${safeName}_tables.${type}`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

async function downloadNewVersion(fileId: string, filename: string) {
  const token =
    typeof OpenAPI.TOKEN === "function"
      ? await OpenAPI.TOKEN({} as never)
      : OpenAPI.TOKEN

  const base = OpenAPI.BASE || ""
  const response = await fetch(`${base}/api/v1/files/${fileId}/download/new`, {
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
  a.download = `${safeName}_tables_new.xlsx`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

function DownloadMenu({ file }: { file: FilePublic }) {
  const [loading, setLoading] = useState(false)

  const handleSelect = async (format: string) => {
    setLoading(true)
    try {
      await downloadFile(file.id, file.filename, format)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
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
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <DownloadIcon className="w-4 h-4" />
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => void handleSelect("xlsx")}>
          Excel (.xlsx)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => void handleSelect("csv")}>
          CSV (.csv)
        </DropdownMenuItem>

        <DropdownMenuItem onClick={() => void handleSelect("json")}>
          JSON (.json)
        </DropdownMenuItem>

        <DropdownMenuItem onClick={() => void handleSelect("html")}>
          HTML (.html)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => void handleSelect("docx")}>
          DOCX (.docx) — not supported
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

function DownloadNewButton({ file }: { file: FilePublic }) {
  const [loading, setLoading] = useState(false)

  const handleClick = async () => {
    setLoading(true)
    try {
      await downloadNewVersion(file.id, file.filename)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Button
      variant="ghost"
      size="sm"
      className="w-8 h-8 p-0"
      title="Download (new)"
      onClick={() => void handleClick()}
      disabled={loading}
    >
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        <DownloadIcon className="w-4 h-4 text-blue-400" />
      )}
    </Button>
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
            <>
              <DownloadNewButton file={file} />
              <DownloadMenu file={file} />
            </>
          )}
        </div>
      )
    },
  },
]
