import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col items-center">
      {/* Hero Section */}
      <section className="w-full max-w-5xl px-6 py-20 text-center">
        <h1 className="text-5xl font-bold text-slate-900 mb-6">
          Learn Guitar with Your{" "}
          <span className="text-primary-600">AI Coach</span>
        </h1>
        <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
          Get real-time feedback on your guitar practice. Our AI analyzes your 
          playing and guides you through personalized exercises designed for beginners.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/practice"
            className="px-8 py-4 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors"
          >
            Start Practicing
          </Link>
          <Link
            href="/dashboard"
            className="px-8 py-4 bg-white text-primary-600 border-2 border-primary-600 rounded-lg font-semibold hover:bg-primary-50 transition-colors"
          >
            View Dashboard
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="w-full max-w-5xl px-6 py-16 bg-white">
        <h2 className="text-3xl font-bold text-slate-900 text-center mb-12">
          How It Works
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            title="🎸 Practice Sessions"
            description="Follow guided practice routines designed for your skill level with real-time feedback."
          />
          <FeatureCard
            title="📊 Track Progress"
            description="Monitor your improvement over time with detailed analytics and practice history."
          />
          <FeatureCard
            title="🎯 Personalized Coaching"
            description="Get AI-powered tips and corrections tailored to your unique learning journey."
          />
        </div>
      </section>

      {/* Getting Started Section */}
      <section className="w-full max-w-5xl px-6 py-16 bg-primary-50">
        <h2 className="text-3xl font-bold text-slate-900 text-center mb-8">
          Ready to Start?
        </h2>
        <p className="text-lg text-slate-600 text-center mb-8 max-w-2xl mx-auto">
          All you need is your guitar and a microphone. No expensive equipment required.
          Our AI works with your device&apos;s built-in microphone to analyze your playing.
        </p>
        <div className="flex justify-center">
          <Link
            href="/practice"
            className="px-8 py-4 bg-guitar-amber text-white rounded-lg font-semibold hover:bg-orange-600 transition-colors"
          >
            Begin Your Journey
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="w-full py-8 text-center text-slate-500">
        <p>Built with ❤️ for guitar learners everywhere</p>
      </footer>
    </div>
  );
}

function FeatureCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="p-6 bg-slate-50 rounded-xl hover:shadow-lg transition-shadow">
      <h3 className="text-xl font-semibold text-slate-900 mb-3">{title}</h3>
      <p className="text-slate-600">{description}</p>
    </div>
  );
}