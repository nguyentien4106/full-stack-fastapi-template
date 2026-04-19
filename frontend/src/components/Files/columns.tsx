import type { ColumnDef } from "@tanstack/react-table"
import dayjs from "dayjs"
import { DownloadIcon, Loader2, RefreshCcw } from "lucide-react"
import { type FilePublic, FilesService } from "@/client"
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
import { type DownloadFormat, useDownloadFile } from "@/hooks/useDownloadFile"
import { FilePreviewModal } from "./FilePreviewModal"

function DownloadMenu({ file }: { file: FilePublic }) {
  const { mutate: download, isPending } = useDownloadFile()

  const handleSelect = (format: DownloadFormat) => {
    download({ fileId: file.id, filename: file.filename, format })
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="w-8 h-8 p-0"
          title="Download"
          disabled={isPending}
        >
          {isPending ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <DownloadIcon className="w-4 h-4" />
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => handleSelect("xlsx")}>
          Excel (.xlsx)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleSelect("xlsx-acc-code")}>
          Analyze Account Code then Excel (.xlsx)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleSelect("csv")}>
          CSV (.csv)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleSelect("json")}>
          JSON (.json)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleSelect("html")}>
          HTML (.html)
        </DropdownMenuItem>
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
            <>
              <FilePreviewModal file={file} />
              <DownloadMenu file={file} />
            </>
          )}
        </div>
      )
    },
  },
]
