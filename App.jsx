import { useState } from "react";
import FileUpload from "./components/FileUpload";
import Logo from "./components/Logo";
import ResultDisplay from "./components/ResultDisplay";
import { getReportUrl, uploadForAnalysis } from "./api";

const App = () => {
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await uploadForAnalysis({ file, text });
      setResult(data);
    } catch (uploadError) {
      setError(uploadError?.response?.data?.detail || "Failed to run analysis.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <Logo />
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8">
        <form onSubmit={handleSubmit} className="rounded-xl bg-white p-6 shadow">
          <h1 className="mb-5 text-2xl font-semibold text-slate-900">Research Content Analysis</h1>
          <FileUpload onFileChange={setFile} />
          {file && <p className="mt-2 text-sm text-slate-600">Selected: {file.name}</p>}
          <div className="my-5 text-center text-slate-500">OR</div>
          <textarea placeholder="Paste your research content here..." rows={8} className="w-full rounded-lg border border-slate-300 p-3 outline-none focus:border-blue-500" value={text} onChange={(e) => setText(e.target.value)} />
          {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
          <button type="submit" disabled={loading} className="mt-4 rounded-lg bg-slate-900 px-5 py-2 font-medium text-white hover:bg-slate-800 disabled:opacity-70">{loading ? "Analyzing..." : "Submit Analysis"}</button>
        </form>

        {result && (
          <>
            <ResultDisplay result={result} />
            <a href={getReportUrl(result.job_id)} className="mt-6 inline-block rounded-lg bg-blue-600 px-5 py-3 font-medium text-white hover:bg-blue-700">Download IEEE Report</a>
          </>
        )}
      </main>

      <footer className="mt-14 border-t bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-5">
          <Logo className="scale-75 origin-left" />
          <p className="text-sm text-slate-500">Academic integrity analysis platform</p>
        </div>
      </footer>
    </div>
  );
};

export default App;
