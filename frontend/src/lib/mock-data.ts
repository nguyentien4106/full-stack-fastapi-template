export interface FileHistoryItem {
  id: string
  filename: string
  uploadDate: string
  size: string
  status: "pending" | "processing" | "completed" | "error"
  bankType: string
}

export interface PricingTier {
  name: string
  price: string
  description: string
  features: string[]
  cta: string
  highlighted?: boolean
}

export const mockFileHistory: FileHistoryItem[] = [
  {
    id: "1",
    filename: "Vietcombank_Statement_May_2024.pdf",
    uploadDate: "2024-05-15",
    size: "2.4 MB",
    status: "completed" as const,
    bankType: "Vietcombank",
  },
  {
    id: "2",
    filename: "Techcombank_April_Statement.pdf",
    uploadDate: "2024-04-28",
    size: "1.8 MB",
    status: "completed" as const,
    bankType: "Techcombank",
  },
  {
    id: "3",
    filename: "ACB_Statement_June.pdf",
    uploadDate: "2024-06-10",
    size: "3.1 MB",
    status: "processing" as const,
    bankType: "ACB",
  },
  {
    id: "4",
    filename: "BIDV_May_Statement.pdf",
    uploadDate: "2024-05-20",
    size: "2.7 MB",
    status: "completed" as const,
    bankType: "BIDV",
  },
]

export const pricingTiers: PricingTier[] = [
  {
    name: "Starter",
    price: "Free",
    description: "Perfect for individuals getting started",
    features: [
      "5 files per month",
      "Basic format conversion",
      "Email support",
      "Up to 2 MB file size",
    ],
    cta: "Get Started",
  },
  {
    name: "Professional",
    price: "99,000",
    description: "For active accountants and small firms",
    features: [
      "Unlimited files",
      "Advanced formatting",
      "Transaction categorization",
      "Priority support",
      "API access",
      "Custom templates",
    ],
    cta: "Start Free Trial",
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For large accounting firms",
    features: [
      "Everything in Professional",
      "Dedicated account manager",
      "Custom integration",
      "Team management",
      "Advanced analytics",
      "99.9% SLA",
    ],
    cta: "Contact Sales",
  },
]
