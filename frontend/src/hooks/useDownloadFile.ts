import { useMutation } from "@tanstack/react-query"
import { OpenAPI } from "@/client/core/OpenAPI"
import useCustomToast from "./useCustomToast"
import { ApiError } from "@/client"

async function fetchDownload(url: string): Promise<Blob> {
  const token =
    typeof OpenAPI.TOKEN === "function"
      ? await OpenAPI.TOKEN({} as never)
      : OpenAPI.TOKEN

  const response = await fetch(url, {
    method: "POST",
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })
  console.log('response', response)
  if (!response.ok) {
    throw new Error(`Download failed: ${response.statusText}`)
  }

  return response.blob()
}

function triggerBlobDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export type DownloadFormat = "xlsx" | "xlsx-acc-code" | "csv" | "json" | "html"

export interface DownloadFileParams {
  fileId: string
  filename: string
  format: DownloadFormat
}

export function useDownloadFile() {
  const { showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: async ({ fileId, filename, format }: DownloadFileParams) => {
      const base = OpenAPI.BASE || ""
      const safeName = filename.replace(/\.[^.]+$/, "")

      if (format === "xlsx-acc-code") {
        const blob = await fetchDownload(
          `${base}/api/v1/files/${fileId}/download/new`,
        )
        triggerBlobDownload(blob, `${safeName}_tables_with_acc_codes.xlsx`)
      } else {
        const blob = await fetchDownload(
          `${base}/api/v1/files/${fileId}/download?type=${format}`,
        )
        triggerBlobDownload(blob, `${safeName}_tables.${format}`)
      }
    },
    onError: (err: ApiError) => {
        console.log("Download error:", err)
      showErrorToast(err instanceof Error ? err.message : "Download failed")
    },
  })
}
