import React from 'react'

const features = [
  {
    icon: '📄',
    title: 'Multiple File Types',
    description: 'Convert bank statements from PDF and image formats. Supports JPG, PNG, and PDF uploads.'
  },
  {
    icon: '🔒',
    title: 'Bank-Grade Security',
    description: 'Your financial data is encrypted and never stored on our servers. Complete privacy guaranteed.'
  },
  {
    icon: '⚡',
    title: 'Instant Conversion',
    description: 'Process your bank statements in seconds. Get organized Excel files ready to use immediately.'
  },
  {
    icon: '✅',
    title: 'Accurate Data Extraction',
    description: 'Preserves all transaction details, amounts, and dates with 99.9% accuracy. No data loss.'
  },
  {
    icon: '📊',
    title: 'Ready for Analysis',
    description: 'Converted Excel files are fully formatted and compatible with all spreadsheet applications.'
  },
  {
    icon: '🚀',
    title: 'Zero Setup Required',
    description: 'No installation, no registration required. Start converting your bank statements instantly.'
  }
]

export default function Features() {
  return (
    <section id="features" className="py-20 sm:py-32 bg-background">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            Why Choose KeToanAuto
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            The smartest way to organize your bank statements
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="rounded-lg border border-border bg-card p-8 hover:border-primary/50 hover:shadow-lg transition-all"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-lg font-semibold text-card-foreground mb-2">
                {feature.title}
              </h3>
              <p className="text-muted-foreground">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
