import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

export const uploadForAnalysis = async ({ file, text }) => {
  const formData = new FormData();
  if (file) formData.append("file", file);
  if (text) formData.append("text", text);
  const response = await api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const getReportUrl = (jobId) => `${api.defaults.baseURL}/download-report/${jobId}`;
