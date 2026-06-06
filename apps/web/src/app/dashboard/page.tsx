export default function DashboardPage() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">Your Dashboard</h1>
        <p className="text-xl text-slate-600">
          Track your guitar learning journey and see your progress over time.
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid md:grid-cols-4 gap-6 mb-12">
        <StatCard label="Practice Sessions" value="0" sublabel="This week" />
        <StatCard label="Total Practice Time" value="0h" sublabel="This week" />
        <StatCard label="Chords Learned" value="0" sublabel="Keep going!" />
        <StatCard label="Current Streak" value="0 days" sublabel="Start today!" />
      </div>

      {/* Practice History */}
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 mb-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Recent Practice</h2>
        <div className="text-center py-12 text-slate-500">
          <p className="text-lg mb-2">No practice sessions yet</p>
          <p className="text-sm">
            Complete your first practice session to see your history here.
          </p>
        </div>
      </div>

      {/* Progress Chart Placeholder */}
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 mb-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Weekly Progress</h2>
        <div className="h-64 flex items-center justify-center text-slate-400">
          <div className="text-center">
            <p className="text-6xl mb-4">📈</p>
            <p>Progress charts coming soon</p>
          </div>
        </div>
      </div>

      {/* Achievements */}
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Achievements</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <AchievementBadge title="First Steps" description="Complete your first practice" locked />
          <AchievementBadge title="Consistent" description="Practice 3 days in a row" locked />
          <AchievementBadge title="Chord Master" description="Learn 5 basic chords" locked />
          <AchievementBadge title="Dedicated" description="Practice for 10 hours total" locked />
        </div>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  sublabel,
}: {
  label: string;
  value: string;
  sublabel: string;
}) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
      <p className="text-sm text-slate-500 mb-1">{label}</p>
      <p className="text-3xl font-bold text-slate-900">{value}</p>
      <p className="text-sm text-slate-400">{sublabel}</p>
    </div>
  );
}

function AchievementBadge({
  title,
  description,
  locked,
}: {
  title: string;
  description: string;
  locked: boolean;
}) {
  return (
    <div className={`p-4 rounded-lg text-center ${
      locked ? "bg-slate-100" : "bg-primary-50 border-2 border-primary-200"
    }`}>
      <div className={`text-4xl mb-2 ${locked ? "grayscale opacity-50" : ""}`}>
        {locked ? "🔒" : "🏆"}
      </div>
      <h3 className={`font-semibold ${locked ? "text-slate-400" : "text-slate-900"}`}>
        {title}
      </h3>
      <p className={`text-sm ${locked ? "text-slate-400" : "text-slate-600"}`}>
        {description}
      </p>
    </div>
  );
}