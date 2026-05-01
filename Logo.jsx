const Logo = ({ className = "" }) => {
  return (
    <a href="/" className={`inline-flex items-center gap-2 ${className}`}>
      <svg width="48" height="48" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" className="drop-shadow-md">
        <defs>
          <linearGradient id="ghGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#0f172a" />
            <stop offset="100%" stopColor="#2563eb" />
          </linearGradient>
        </defs>
        <rect x="8" y="8" width="104" height="104" rx="26" fill="url(#ghGradient)" />
        <text x="50%" y="58%" dominantBaseline="middle" textAnchor="middle" fill="#e2e8f0" fontSize="46" fontWeight="700" fontFamily="Inter, Arial, sans-serif">GH</text>
      </svg>
      <span className="text-xl font-bold text-slate-800">GH Plagiarism Checker</span>
    </a>
  );
};

export default Logo;
