import { FileText, Download, Eye } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { StatusBadge } from "./StatusBadge"
import { Empty } from "@/components/ui/empty"
import type { FileHistoryItem } from "@/lib/mock-data"

interface FileHistoryTableProps {
  files: FileHistoryItem[]
}

export function FileHistoryTable({ files }: FileHistoryTableProps) {
  if (files.length === 0) {
    return (
      <Empty>
        <FileText className="w-12 h-12 text-muted-foreground mb-2" />
        <p className="font-medium">No files uploaded yet</p>
        <p className="text-sm text-muted-foreground">
          Start by uploading a bank statement to get started
        </p>
      </Empty>
    )
  }

  return (
    <div className="rounded-lg border border-border overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Filename</TableHead>
            <TableHead>Bank</TableHead>
            <TableHead>Size</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Date</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {files.map((file) => (
            <TableRow key={file.id}>
              <TableCell>
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-primary/60" />
                  <span className="truncate font-medium">{file.filename}</span>
                </div>
              </TableCell>
              <TableCell className="text-foreground/70">{file.bankType}</TableCell>
              <TableCell className="text-foreground/70">{file.size}</TableCell>
              <TableCell>
                <StatusBadge status={file.status} />
              </TableCell>
              <TableCell className="text-foreground/70">
                {file.uploadDate}
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-2">
                  {file.status === "completed" && (
                    <>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="w-8 h-8 p-0"
                        title="View"
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="w-8 h-8 p-0"
                        title="Download"
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                    </>
                  )}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
