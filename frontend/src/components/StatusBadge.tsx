import { CheckCircle2, Clock, AlertCircle, HardDrive } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface StatusBadgeProps {
  status: "pending" | "processing" | "completed" | "error"
  className?: string
}

const statusConfig = {
  pending: {
    icon: Clock,
    label: "Pending",
    variant: "outline" as const,
  },
  processing: {
    icon: HardDrive,
    label: "Processing",
    variant: "default" as const,
  },
  completed: {
    icon: CheckCircle2,
    label: "Completed",
    variant: "secondary" as const,
  },
  error: {
    icon: AlertCircle,
    label: "Error",
    variant: "destructive" as const,
  },
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status]
  const Icon = config.icon

  return (
    <Badge
      variant={config.variant}
      className={`inline-flex items-center gap-2 ${className}`}
    >
      <Icon
        className={`w-4 h-4 ${status === "processing" ? "animate-spin" : ""}`}
      />
      <span>{config.label}</span>
    </Badge>
  )
}
