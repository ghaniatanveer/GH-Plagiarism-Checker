const Gauge = ({ label, value, color }) => {
  const radius = 50;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <svg width="140" height="140" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r={radius} stroke="#e2e8f0" strokeWidth="10" fill="none" />
        <circle cx="60" cy="60" r={radius} stroke={color} strokeWidth="10" fill="none" strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={offset} transform="rotate(-90 60 60)" />
        <text x="50%" y="52%" dominantBaseline="middle" textAnchor="middle" className="fill-slate-800 text-sm font-bold">{value.toFixed(2)}%</text>
      </svg>
      <p className="mt-2 font-medium text-slate-700">{label}</p>
    </div>
  );
};

const ResultDisplay = ({ result }) => {
  return (
    <section className="mt-8 rounded-xl bg-white p-6 shadow">
      <h2 className="mb-6 text-2xl font-semibold text-slate-800">Analysis Results</h2>
      <div className="flex flex-col justify-center gap-8 md:flex-row">
        <Gauge label="Plagiarism" value={result.plagiarism_percentage} color="#ef4444" />
        <Gauge label="Humanized" value={result.humanized_percentage} color="#22c55e" />
        <Gauge label="AI Detected" value={result.ai_generated_percentage} color="#f59e0b" />
      </div>
      <div className="mt-6">
        <h3 className="mb-2 text-lg font-semibold">Top Similar Sources</h3>
        <ul className="space-y-1 text-slate-700">
          {result.top_sources.map((source) => (
            <li key={source.filename}>
              <div className="font-medium">{source.title || source.filename}</div>
              <div className="text-sm">{(source.source_type || "Source")} - {source.similarity.toFixed(2)}%</div>
              {source.url ? <a href={source.url} target="_blank" rel="noreferrer" className="text-sm text-blue-600 hover:underline">{source.url}</a> : null}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
};

export default ResultDisplay;
