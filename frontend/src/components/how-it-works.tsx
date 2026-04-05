const steps = [
  {
    number: "1",
    title: "Upload Your Bank Statement",
    description:
      "Drag and drop your PDF or image bank statement. Supports JPG, PNG, and PDF formats.",
  },
  {
    number: "2",
    title: "We Extract the Data",
    description:
      "Our AI-powered system analyzes and extracts all transaction details automatically in seconds.",
  },
  {
    number: "3",
    title: "Download as Excel",
    description:
      "Your bank statement is now organized in an Excel file, ready for analysis and archiving.",
  },
]

export default function HowItWorks() {
  return (
    <section id="how" className="py-20 sm:py-32 bg-secondary">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            How KeToanAuto Works
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Three simple steps to organize your bank statements
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-16 left-1/2 w-full h-0.5 bg-gradient-to-r from-primary/50 to-transparent" />
              )}
              <div className="relative z-10 rounded-lg border border-border bg-background p-8">
                <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-primary text-primary-foreground font-bold text-lg mb-6 mx-auto">
                  {step.number}
                </div>
                <h3 className="text-lg font-semibold text-foreground text-center mb-3">
                  {step.title}
                </h3>
                <p className="text-center text-muted-foreground">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-16 rounded-lg bg-primary/5 border border-primary/20 p-8 text-center">
          <p className="text-foreground font-semibold">
            Convert your first bank statement for free. Unlock unlimited
            conversions with KeToanAuto Pro.
          </p>
        </div>
      </div>
    </section>
  )
}
