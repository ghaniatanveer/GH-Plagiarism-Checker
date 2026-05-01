import { useRef } from "react";

const FileUpload = ({ onFileChange }) => {
  const inputRef = useRef(null);
  return (
    <div className="rounded-xl border-2 border-dashed border-slate-300 bg-white p-6 text-center">
      <p className="mb-3 text-slate-600">Upload PDF, DOCX, or TXT</p>
      <button type="button" onClick={() => inputRef.current?.click()} className="rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700">
        Select File
      </button>
      <input ref={inputRef} type="file" className="hidden" accept=".pdf,.docx,.txt" onChange={(e) => onFileChange(e.target.files?.[0] || null)} />
    </div>
  );
};

export default FileUpload;
