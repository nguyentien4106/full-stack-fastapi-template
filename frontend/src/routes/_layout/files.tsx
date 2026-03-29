import { useSuspenseQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense, useEffect, useRef } from "react"

import { FilesService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import { columns } from "@/components/Files/columns"
import PendingItems from "@/components/Pending/PendingItems"

function getFilesQueryOptions(limit = 0) {
  return {
    queryFn: () => FilesService.listFiles({ skip: 0, limit }),
    queryKey: ["files"],
    refetchInterval: 3000, // Refetch every 5 seconds to get real-time updates
  }
}



export const Route = createFileRoute("/_layout/files")({
  component: Files,
  head: () => ({
    meta: [
      {
        title: "Files - FastAPI Template",
      },
    ],
  }),
})

function FilesTableContent() {
  const queryClient = useQueryClient()
  const { data: files } = useSuspenseQuery(getFilesQueryOptions())
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    const pollPendingFiles = async () => {
      const pendingFiles = files.data.filter(
        (f) => f.job_status !== "done" && f.job_status !== "failed",
      )

      if (pendingFiles.length === 0) {
        if (pollingRef.current) {
          clearInterval(pollingRef.current)
          pollingRef.current = null
        }
        return
      }

      await Promise.allSettled(
        pendingFiles.map(async (file) => {
          const updated = await FilesService.getFileStatus({ fileId: file.id })
          queryClient.setQueryData(["files"], (old: typeof files | undefined) => {
            if (!old) return old
            return {
              ...old,
              data: old.data.map((f) => (f.id === updated.id ? updated : f)),
            }
          })
        }),
      )
    }

    pollingRef.current = setInterval(pollPendingFiles, 3000)

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }
  }, [files.data, queryClient])

  if (files.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">You don't have any items yet</h3>
        <p className="text-muted-foreground">Add a new item to get started</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={files.data} />
}

function FilesTable() {
  return (
    <Suspense fallback={<PendingItems />}>
      <FilesTableContent />
    </Suspense>
  )
}

function Files() {
  return (
    <div className="flex flex-col gap-6">
      <FilesTable />
    </div>
  )
}
