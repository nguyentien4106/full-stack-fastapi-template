import { useMutation, useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { CheckCircle, Wallet } from "lucide-react"
import { Suspense, useState } from "react"

import { type TopupPackage, TopupService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/topup")({
  component: TopupPage,
  head: () => ({
    meta: [{ title: "Top Up - FastAPI Template" }],
  }),
})

function formatVND(amount: number): string {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(amount)
}

function PackageGrid({
  selected,
  onSelect,
}: {
  selected: TopupPackage | null
  onSelect: (pkg: TopupPackage) => void
}) {
  const { data } = useSuspenseQuery({
    queryKey: ["topupPackages"],
    queryFn: () => TopupService.getTopupPackages(),
  })

  const packages = data.packages ?? []

  return (
    <div className="grid grid-cols-3 sm:grid-cols-3 lg:grid-cols-3 gap-3">
      {packages.map((pkg) => {
        const isSelected = selected?.id === pkg.id
        return (
          <button
            key={pkg.id}
            type="button"
            onClick={() => onSelect(pkg)}
            className={`relative rounded-xl border-2 p-4 text-center transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
              isSelected
                ? "border-primary bg-primary/10 shadow-md"
                : "border-border hover:border-primary/50 hover:bg-muted/50"
            }`}
          >
            {isSelected && (
              <CheckCircle className="absolute top-2 right-2 h-4 w-4 text-primary" />
            )}
            <p className="text-base font-semibold">{formatVND(pkg.amount)}</p>
          </button>
        )
      })}
    </div>
  )
}

function PackageGridSkeleton() {
  return (
    <div className="grid grid-cols-3 gap-3">
      {Array.from({ length: 9 }).map((_, i) => (
        // biome-ignore lint/suspicious/noArrayIndexKey: static skeleton list
        <Skeleton key={i} className="h-16 rounded-xl" />
      ))}
    </div>
  )
}

function QRCodeDisplay({ url }: { url: string }) {
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(url)}`
  return (
    <div className="flex flex-col items-center gap-4 mt-4">
      <img
        src={qrUrl}
        alt="VNPAY QR Code"
        className="rounded-xl border shadow-sm"
        width={220}
        height={220}
      />
      <p className="text-sm text-muted-foreground text-center max-w-xs">
        Scan this QR code with your VNPAY-supported banking app to complete the
        payment.
      </p>
      <Button variant="outline" size="sm" asChild>
        <a href={url} target="_blank" rel="noopener noreferrer">
          Open payment page
        </a>
      </Button>
    </div>
  )
}

function TopupContent() {
  const [selected, setSelected] = useState<TopupPackage | null>(null)
  const [paymentUrl, setPaymentUrl] = useState<string | null>(null)
  const { showSuccessToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: (amount: number) =>
      TopupService.createTopupPayment({ requestBody: { amount } }),
    onSuccess: (data) => {
      setPaymentUrl(data.payment_url)
      console.log("Payment URL:", data.payment_url)
      showSuccessToast("QR code generated! Scan to pay.")
    },
    onError: handleError,
  })

  const handleGenerate = () => {
    if (!selected) return
    setPaymentUrl(null)
    mutation.mutate(selected.amount)
  }

  const handleSelectPackage = (pkg: TopupPackage) => {
    setSelected(pkg)
    setPaymentUrl(null)
  }

  return (
    <div className="max-w-lg mx-auto space-y-6">
      {/* Package selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Wallet className="h-5 w-5 text-primary" />
            Select a top-up package
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Suspense fallback={<PackageGridSkeleton />}>
            <PackageGrid selected={selected} onSelect={handleSelectPackage} />
          </Suspense>

          {selected && (
            <div className="flex items-center justify-between rounded-lg bg-muted/50 px-4 py-2">
              <span className="text-sm text-muted-foreground">Selected</span>
              <Badge variant="secondary" className="text-sm font-semibold">
                {formatVND(selected.amount)}
              </Badge>
            </div>
          )}

          <Button
            className="w-full"
            disabled={!selected || mutation.isPending}
            onClick={handleGenerate}
          >
            {mutation.isPending ? "Generating…" : "Generate QR Code"}
          </Button>
        </CardContent>
      </Card>

      {/* QR Code result */}
      {paymentUrl && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Scan to pay</CardTitle>
          </CardHeader>
          <CardContent>
            <QRCodeDisplay url={paymentUrl} />
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function TopupPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Top Up</h1>
        <p className="text-muted-foreground">
          Add balance to your account via VNPAY
        </p>
      </div>
      <TopupContent />
    </div>
  )
}
