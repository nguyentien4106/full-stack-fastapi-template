import React from 'react'

const testimonials = [
  {
    name: 'Sarah Martinez',
    role: 'Business Manager',
    content: 'Easy to use, good service. Exactly what I needed for converting my documents.',
    rating: 5
  },
  {
    name: 'James Chen',
    role: 'Freelance Designer',
    content: 'Great experience, high quality service! The conversion was perfect and very fast.',
    rating: 5
  },
  {
    name: 'Emily Rodriguez',
    role: 'Data Analyst',
    content: 'Good Service, Very good customer service! They helped me when I had questions.',
    rating: 5
  }
]

export default function Testimonials() {
  return (
    <section className="py-20 sm:py-32 bg-background">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            What Users Are Saying
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Trusted by thousands of users worldwide
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className="rounded-lg border border-border bg-card p-8 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center gap-1 mb-4">
                {Array.from({ length: testimonial.rating }).map((_, i) => (
                  <span key={i} className="text-yellow-400">★</span>
                ))}
              </div>
              <p className="text-card-foreground mb-6 leading-relaxed">
                "{testimonial.content}"
              </p>
              <div>
                <p className="font-semibold text-card-foreground">
                  {testimonial.name}
                </p>
                <p className="text-sm text-muted-foreground">
                  {testimonial.role}
                </p>
              </div>
              <div className="mt-4 flex items-center gap-2 text-xs font-medium text-primary">
                ✓ Verified
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
