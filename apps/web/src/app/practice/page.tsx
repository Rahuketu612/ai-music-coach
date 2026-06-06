export default function PracticePage() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">Practice Session</h1>
        <p className="text-xl text-slate-600">
          Ready to improve your guitar skills? Select a practice mode below.
        </p>
      </div>

      {/* Practice Modes Grid */}
      <div className="grid md:grid-cols-2 gap-6 mb-12">
        <PracticeModeCard
          title="Chord Practice"
          description="Learn and practice basic guitar chords with real-time feedback."
          icon="🎵"
          comingSoon={false}
        />
        <PracticeModeCard
          title="Scale Training"
          description="Master essential scales with guided exercises and progression tracking."
          icon="🎹"
          comingSoon={false}
        />
        <PracticeModeCard
          title="Song Practice"
          description="Learn popular songs step by step with automatic chord detection."
          icon="🎸"
          comingSoon={true}
        />
        <PracticeModeCard
          title="Free Play"
          description="Open practice mode with AI coaching and tips."
          icon="✨"
          comingSoon={true}
        />
      </div>

      {/* Getting Started Guide */}
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
        <h2 className="text-2xl font-bold text-slate-900 mb-4">Getting Started</h2>
        <ol className="space-y-4 text-slate-600">
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-semibold">
              1
            </span>
            <span>Choose a practice mode from the options above</span>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-semibold">
              2
            </span>
            <span>Allow microphone access when prompted</span>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-semibold">
              3
            </span>
            <span>Play your guitar and receive real-time feedback</span>
          </li>
          <li className="flex gap-4">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-semibold">
              4
            </span>
            <span>Review your progress in the Dashboard</span>
          </li>
        </ol>
      </div>

      {/* Notice */}
      <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-lg">
        <p className="text-amber-800 text-sm">
          <strong>Note:</strong> Audio analysis features are coming soon. 
          Stay tuned for updates!
        </p>
      </div>
    </div>
  );
}

function PracticeModeCard({
  title,
  description,
  icon,
  comingSoon,
}: {
  title: string;
  description: string;
  icon: string;
  comingSoon: boolean;
}) {
  return (
    <div className={`p-6 rounded-xl border-2 transition-all ${
      comingSoon 
        ? "bg-slate-50 border-slate-200 opacity-75" 
        : "bg-white border-primary-200 hover:border-primary-400 hover:shadow-md"
    }`}>
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-slate-600 mb-4">{description}</p>
      {comingSoon ? (
        <span className="inline-block px-3 py-1 bg-slate-200 text-slate-600 text-sm rounded-full">
          Coming Soon
        </span>
      ) : (
        <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
          Start Practice
        </button>
      )}
    </div>
  );
}