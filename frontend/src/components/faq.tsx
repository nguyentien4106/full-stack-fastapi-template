"use client"

import * as Accordion from "@radix-ui/react-accordion"

const faqs = [
  {
    question: "What is KeToanAuto?",
    answer:
      "KeToanAuto is an all-in-one online PDF/Images converter that lets you transform PDF/Images files into various formats, including Excel (XLSX). No installation or technical skills required.",
  },
  {
    question: "Is KeToanAuto safe to use?",
    answer:
      "Yes, absolutely. We use advanced encryption to ensure your sensitive data stays secure throughout the entire process. Your privacy is our priority.",
  },
  {
    question: "Is KeToanAuto available as a subscription or one-time purchase?",
    answer:
      "Your first file is always free to convert. After that, we offer flexible subscription plans to meet your needs.",
  },
  // {
  //   question: "How to edit PDF files using KeToanAuto?",
  //   answer:
  //     "KeToanAuto provides intuitive editing tools. Simply upload your PDF, use our editor to make changes, and download your modified file.",
  // },
  {
    question: "What file types does KeToanAuto support?",
    answer:
      "KeToanAuto supports conversion to and from PDF, Excel, Word, PowerPoint, and many other popular document formats.",
  },
  {
    question: "What should I do if I encounter problems?",
    answer:
      "Our friendly support team is here to help. Contact us directly through the support form, and we&apos;ll get back to you quickly with a solution.",
  },
]

export default function FAQ() {
  return (
    <section id="faq" className="py-20 sm:py-32 bg-secondary">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            Frequently Asked Questions
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Find answers to common questions
          </p>
        </div>

        <Accordion.Root type="single" collapsible className="space-y-4">
          {faqs.map((faq, index) => (
            <Accordion.Item
              key={faq.question}
              value={`item-${index}`}
              className="rounded-lg border border-border bg-background overflow-hidden"
            >
              <Accordion.Header>
                <Accordion.Trigger className="flex w-full items-center justify-between px-6 py-4 text-left font-semibold text-foreground hover:text-primary transition-colors [&[data-state=open]>svg]:rotate-180">
                  <span>{faq.question}</span>
                  <svg
                    className="h-5 w-5 transition-transform duration-200"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <title>Toggle answer</title>
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 14l-7 7m0 0l-7-7m7 7V3"
                    />
                  </svg>
                </Accordion.Trigger>
              </Accordion.Header>
              <Accordion.Content className="px-6 pb-4 pt-0 text-muted-foreground leading-relaxed">
                {faq.answer}
              </Accordion.Content>
            </Accordion.Item>
          ))}
        </Accordion.Root>
      </div>
    </section>
  )
}
