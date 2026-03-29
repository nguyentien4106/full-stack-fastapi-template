import { createFileRoute, Link } from "@tanstack/react-router"
import { Check } from "lucide-react"
import { PricingCard } from "@/components/PricingCard"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { pricingTiers } from "@/lib/mock-data"

export const Route = createFileRoute("/_public/pricing")({
  component: Pricing,
  head: () => ({
    meta: [{ title: "Pricing - BankToExcel" }],
  }),
})

function Pricing() {
  const features = [
    {
      category: "File Processing",
      items: [
        {
          name: "Files per month",
          starter: "5",
          professional: "Unlimited",
          enterprise: "Unlimited",
        },
        {
          name: "File size limit",
          starter: "2 MB",
          professional: "50 MB",
          enterprise: "Unlimited",
        },
        {
          name: "Processing speed",
          starter: "Standard",
          professional: "Fast",
          enterprise: "Priority",
        },
      ],
    },
    {
      category: "Features",
      items: [
        {
          name: "Basic conversion",
          starter: true,
          professional: true,
          enterprise: true,
        },
        {
          name: "Advanced formatting",
          starter: false,
          professional: true,
          enterprise: true,
        },
        {
          name: "Transaction categorization",
          starter: false,
          professional: true,
          enterprise: true,
        },
        {
          name: "Custom templates",
          starter: false,
          professional: true,
          enterprise: true,
        },
        {
          name: "API access",
          starter: false,
          professional: true,
          enterprise: true,
        },
        {
          name: "Batch processing",
          starter: false,
          professional: true,
          enterprise: true,
        },
      ],
    },
    {
      category: "Support",
      items: [
        {
          name: "Email support",
          starter: true,
          professional: true,
          enterprise: true,
        },
        {
          name: "Priority support",
          starter: false,
          professional: true,
          enterprise: true,
        },
        {
          name: "Dedicated account manager",
          starter: false,
          professional: false,
          enterprise: true,
        },
        {
          name: "Phone support",
          starter: false,
          professional: false,
          enterprise: true,
        },
      ],
    },
  ]

  const faqs = [
    {
      question: "Can I change my plan anytime?",
      answer:
        "Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.",
    },
    {
      question: "Do you offer a refund policy?",
      answer:
        "We offer a 30-day money-back guarantee if you're not satisfied with our service.",
    },
    {
      question: "What banks do you support?",
      answer:
        "We support all major Vietnamese banks including Vietcombank, Techcombank, BIDV, VietinBank, ACB, and more.",
    },
    {
      question: "Is my data secure?",
      answer:
        "Yes, all data is encrypted in transit and at rest. We delete files immediately after conversion.",
    },
    {
      question: "Do you offer enterprise plans?",
      answer:
        "Yes, we have custom enterprise plans for large organizations. Contact our sales team for details.",
    },
    {
      question: "Can I use the API?",
      answer:
        "API access is included with Professional and Enterprise plans. See our documentation for more details.",
    },
  ]

  return (
    <>
      {/* Pricing Header */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
        <div className="text-center space-y-6 mb-16">
          <h1 className="text-5xl sm:text-6xl font-bold text-foreground text-balance">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-foreground/60 max-w-2xl mx-auto">
            Choose the plan that's right for you. No hidden fees, cancel
            anytime.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {pricingTiers.map((tier) => (
            <PricingCard key={tier.name} tier={tier} />
          ))}
        </div>

        {/* Monthly / Annual Toggle */}
        <div className="flex items-center justify-center gap-4 mb-16">
          <span className="text-foreground/60">Monthly</span>
          <button
            type="button"
            className="relative inline-flex h-8 w-14 items-center rounded-full bg-primary/20 cursor-pointer"
          >
            <span className="inline-block h-6 w-6 transform rounded-full bg-primary ml-1 transition-transform" />
          </button>
          <span className="text-foreground/60">Annual</span>
          <span className="ml-2 px-3 py-1 bg-accent/20 text-accent text-sm rounded-full font-medium">
            Save 20%
          </span>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="border-t border-border bg-muted/30 py-20 sm:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold mb-12 text-center">
            Detailed Comparison
          </h2>
          <div className="space-y-8">
            {features.map((section) => (
              <div
                key={section.category}
                className="bg-primary/5 border border-primary/10 rounded-lg p-6"
              >
                <h3 className="font-bold text-primary mb-4">
                  {section.category}
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="sr-only">
                      <tr>
                        <th>Feature</th>
                        <th>Starter</th>
                        <th>Professional</th>
                        <th>Enterprise</th>
                      </tr>
                    </thead>
                    <tbody>
                      {section.items.map((item) => (
                        <tr
                          key={item.name}
                          className="border-t border-primary/5 first:border-t-0"
                        >
                          <td className="py-3 text-foreground/70 font-medium">
                            {item.name}
                          </td>
                          <td className="py-3 text-center">
                            {typeof item.starter === "boolean" ? (
                              item.starter ? (
                                <Check className="w-5 h-5 text-accent mx-auto" />
                              ) : (
                                <span className="text-foreground/30">—</span>
                              )
                            ) : (
                              item.starter
                            )}
                          </td>
                          <td className="py-3 text-center">
                            {typeof item.professional === "boolean" ? (
                              item.professional ? (
                                <Check className="w-5 h-5 text-accent mx-auto" />
                              ) : (
                                <span className="text-foreground/30">—</span>
                              )
                            ) : (
                              item.professional
                            )}
                          </td>
                          <td className="py-3 text-center">
                            {typeof item.enterprise === "boolean" ? (
                              item.enterprise ? (
                                <Check className="w-5 h-5 text-accent mx-auto" />
                              ) : (
                                <span className="text-foreground/30">—</span>
                              )
                            ) : (
                              item.enterprise
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-foreground/60">
            Can't find the answer you're looking for? Contact our support team.
          </p>
        </div>
        <div className="space-y-4">
          {faqs.map((faq) => (
            <Card key={faq.question} className="p-6">
              <details className="group cursor-pointer">
                <summary className="flex items-center justify-between font-semibold text-foreground hover:text-primary transition-colors">
                  <span>{faq.question}</span>
                  <span className="text-lg group-open:rotate-180 transition-transform">
                    ▼
                  </span>
                </summary>
                <p className="mt-4 text-foreground/70 text-sm leading-relaxed">
                  {faq.answer}
                </p>
              </details>
            </Card>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-primary/5 rounded-lg p-12 sm:p-16 border border-primary/10 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4 text-balance">
            Ready to get started?
          </h2>
          <p className="text-lg text-foreground/60 mb-8">
            Start with our free plan, no credit card required
          </p>
          <Link to="/dashboard">
            <Button size="lg">Get Started Free</Button>
          </Link>
        </div>
      </section>
    </>
  )
}
