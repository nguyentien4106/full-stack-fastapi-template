import { createFileRoute, Link } from "@tanstack/react-router"
import { ArrowRight, Check, Clock, FileText, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

export const Route = createFileRoute("/_layout/")({
  component: Home,
  head: () => ({
    meta: [{ title: "Trial - KeToanAuto" }],
  }),
})

function Home() {
  const features = [
    {
      icon: Zap,
      title: "Lightning Fast",
      description:
        "Convert your bank statements to Excel in seconds, not minutes",
    },
    {
      icon: Lock,
      title: "Secure & Private",
      description:
        "Your data is encrypted and deleted immediately after conversion",
    },
    {
      icon: Clock,
      title: "Batch Processing",
      description: "Upload multiple files and process them simultaneously",
    },
    {
      icon: FileText,
      title: "Auto-Detection",
      description:
        "Automatically detects and formats data from any bank statement",
    },
  ]

  const benefits = [
    "Supports all major Vietnamese banks",
    "Customizable Excel templates",
    "Transaction categorization",
    "Monthly reconciliation reports",
    "API integration available",
    "Dedicated support",
  ]

  return (
    <>
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
        <div className="text-center space-y-8">
          <div className="inline-block px-4 py-2 bg-primary/10 rounded-full border border-primary/20">
            <p className="text-sm font-medium text-primary">
              🚀 New feature: Batch processing for unlimited files
            </p>
          </div>

          <h1 className="text-5xl sm:text-6xl font-bold text-foreground text-balance">
            Convert Bank Statements to Excel in Seconds
          </h1>

          <p className="text-xl text-foreground/60 max-w-2xl mx-auto text-pretty">
            Stop wasting time manually copying bank transactions. BankToExcel
            converts your statements to perfectly formatted Excel files
            instantly. Built for accountants in Vietnam.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/dashboard">
              <Button className="gap-2">
                Get Started <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <Button variant="outline">Watch Demo</Button>
          </div>

          <div className="pt-8 border-t border-border">
            <p className="text-sm text-foreground/60 mb-6">
              Trusted by accountants and finance teams
            </p>
            <div className="flex items-center justify-center gap-8 flex-wrap">
              {["Vietcombank", "Techcombank", "BIDV", "VietinBank", "ACB"].map(
                (bank) => (
                  <div
                    key={bank}
                    className="text-sm font-medium text-foreground/50 px-3 py-1 bg-muted rounded"
                  >
                    {bank}
                  </div>
                ),
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-muted/30 py-20 sm:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4 text-balance">
              Why choose BankToExcel?
            </h2>
            <p className="text-lg text-foreground/60 max-w-2xl mx-auto">
              Designed specifically for Vietnamese accountants and finance
              professionals
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature) => {
              return (
                <Card key={feature.title} className="p-6">
                  {/* <Icon className="w-10 h-10 text-primary mb-4" /> */}
                  <h3 className="text-lg font-semibold mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-foreground/60">{feature.description}</p>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-6 text-balance">
              Everything you need for efficient accounting
            </h2>
            <p className="text-lg text-foreground/60 mb-8">
              From individual freelancers to large accounting firms, BankToExcel
              provides all the tools you need to streamline your workflow.
            </p>
            <ul className="space-y-4">
              {benefits.map((benefit) => (
                <li key={benefit} className="flex items-start gap-3">
                  <Check className="w-6 h-6 text-accent shrink-0 mt-0.5" />
                  <span className="text-foreground/70">{benefit}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-primary/5 rounded-lg p-8 border border-primary/10">
            <div className="space-y-6">
              <div className="bg-background rounded-lg p-4 border border-border">
                <p className="text-sm font-mono text-foreground/60">
                  Original PDF Statement
                </p>
                <div className="mt-3 space-y-2">
                  <p className="text-xs text-foreground/50">
                    Vietcombank Statement - May 2024
                  </p>
                  <p className="text-xs text-foreground/50">Account: ***4567</p>
                  <p className="text-xs text-foreground/50">
                    Opening Balance: 50,000,000 VND
                  </p>
                </div>
              </div>
              <div className="flex justify-center">
                <ArrowRight className="w-6 h-6 text-primary rotate-90" />
              </div>
              <div className="bg-background rounded-lg p-4 border border-border">
                <p className="text-sm font-mono text-foreground/60">
                  Converted Excel File
                </p>
                <div className="mt-3 space-y-2">
                  <p className="text-xs text-foreground/50">
                    📊 transactions.xlsx
                  </p>
                  <p className="text-xs text-foreground/50">
                    ✓ Formatted columns
                  </p>
                  <p className="text-xs text-foreground/50">
                    ✓ Categorized entries
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-primary/5 border-t border-b border-primary/10 py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <p className="text-4xl sm:text-5xl font-bold text-primary mb-2">
                500+
              </p>
              <p className="text-foreground/60">Files Converted Daily</p>
            </div>
            <div className="text-center">
              <p className="text-4xl sm:text-5xl font-bold text-primary mb-2">
                98%
              </p>
              <p className="text-foreground/60">Customer Satisfaction</p>
            </div>
            <div className="text-center">
              <p className="text-4xl sm:text-5xl font-bold text-primary mb-2">
                &lt;5s
              </p>
              <p className="text-foreground/60">Average Processing Time</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
        <div className="bg-primary/5 rounded-lg p-12 sm:p-16 border border-primary/10 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4 text-balance">
            Ready to simplify your accounting?
          </h2>
          <p className="text-lg text-foreground/60 mb-8 max-w-2xl mx-auto">
            Join hundreds of accountants and finance teams saving hours every
            week
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/dashboard">
              <Button className="gap-2">
                Start for Free <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            {/* <Link to="/pricing">
              <Button variant="outline">View Pricing</Button>
            </Link> */}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-muted/30 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-sm text-foreground/60">
                <li>
                  <Link to="/" className="hover:text-foreground">
                    Features
                  </Link>
                </li>
                {/* <li>
                  <Link to="/pricing" className="hover:text-foreground">
                    Pricing
                  </Link>
                </li> */}
                <li>
                  <Link to="/" className="hover:text-foreground">
                    Security
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-foreground/60">
                <li>
                  <Link to="/" className="hover:text-foreground">
                    About
                  </Link>
                </li>
                <li>
                  <Link to="/" className="hover:text-foreground">
                    Blog
                  </Link>
                </li>
                <li>
                  <Link to="/" className="hover:text-foreground">
                    Contact
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-sm text-foreground/60">
                <li>
                  <Link to="/" className="hover:text-foreground">
                    Privacy
                  </Link>
                </li>
                <li>
                  <Link to="/" className="hover:text-foreground">
                    Terms
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-sm text-foreground/60">
                <li>
                  <Link to="/" className="hover:text-foreground">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link to="/" className="hover:text-foreground">
                    Status
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-border pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-foreground/60">
              &copy; 2024 BankToExcel. All rights reserved.
            </p>
            <p className="text-sm text-foreground/60">
              Made for accountants in Vietnam 🇻🇳
            </p>
          </div>
        </div>
      </footer>
    </>
  )
}
