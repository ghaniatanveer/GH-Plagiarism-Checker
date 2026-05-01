# 🔍 GH Plagiarism Checker

**AI‑powered full‑stack web application that detects plagiarism and AI‑generated text in research documents, and generates IEEE‑format reports.**

![GitHub repo size](https://img.shields.io/github/repo-size/GitwithHaseeb/GH-Plagiarism-Checker)
![GitHub stars](https://img.shields.io/github/stars/GitwithHaseeb/GH-Plagiarism-Checker?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/GitwithHaseeb/GH-Plagiarism-Checker)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![React](https://img.shields.io/badge/react-18-61dafb)

---

## 📌 Table of Contents

- [Features](#-features)
- [Demo Screenshots](#-demo-screenshots)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [How It Works (AI/ML)](#-how-it-works-aiml)
- [Future Improvements](#-future-improvements)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## ✨ Features

- 📄 **Multi‑format input** – Direct text, PDF, DOCX, or TXT files.
- 🔎 **Plagiarism detection** – Semantic similarity using `sentence-transformers` against a local corpus of research abstracts.
- 🧠 **Humanized text detection** – Fine‑tuned RoBERTa model (`roberta-base-openai-detector`) estimates probability of human vs. AI writing.
- 📊 **Clear visual results** – Plagiarism % and humanized % displayed with animated gauges.
- 📑 **IEEE‑style report** – Downloads a professional Word document with methodology, results, and top matching sources.
- 🎨 **Modern UI** – Built with React + Tailwind CSS, fully responsive.
- ⚡ **Fast backend** – FastAPI with async support, ready for deployment.

---

## 🖼️ Demo Screenshots

> *Add your actual screenshots here*

| Upload page | Results page |
|-------------|--------------|
| ![Upload](https://via.placeholder.com/400x250?text=Upload+Interface) | ![Results](https://via.placeholder.com/400x250?text=Results+with+Gauges) |

**Sample IEEE Report preview**  
![Report](https://via.placeholder.com/600x300?text=IEEE+Report+Preview)

---

## 🧰 Tech Stack

| Layer       | Technology                                                                 |
|-------------|----------------------------------------------------------------------------|
| Frontend    | React 18, Vite, Tailwind CSS, Axios, React Router DOM                     |
| Backend     | FastAPI, Uvicorn, Python 3.10+                                            |
| AI/ML       | sentence‑transformers (all‑MiniLM‑L6‑v2), 🤗 Transformers (RoBERTa)       |
| File parsing| PyPDF2, python‑docx                                                        |
| Report gen  | python‑docx (IEEE style layout)                                            |
| Version control | Git + GitHub                                                          |

---

## 📁 Project Structure
GH-Plagiarism-Checker/
├── backend/
│ ├── app/
│ │ ├── init.py
│ │ ├── main.py # FastAPI app, endpoints
│ │ ├── models.py # Pydantic schemas
│ │ ├── plagiarism_detector.py # Similarity & corpus handling
│ │ ├── human_detector.py # Human/AI classifier
│ │ ├── text_extractor.py # PDF/DOCX/TXT reader
│ │ ├── report_generator.py # IEEE Word export
│ │ └── utils.py # Helper functions
│ ├── corpus/ # Source documents (research abstracts)
│ │ └── *.txt
│ ├── requirements.txt
│ └── precompute_embeddings.py # One‑time script to embed corpus
├── frontend/
│ ├── src/
│ │ ├── components/
│ │ │ ├── Logo.jsx # "GH" brand logo (SVG)
│ │ │ ├── FileUpload.jsx
│ │ │ ├── ResultDisplay.jsx
│ │ │ └── Gauge.jsx # Animated percentage circles
│ │ ├── App.jsx
│ │ ├── api.js # Axios calls to backend
│ │ ├── main.jsx
│ │ └── index.css
│ ├── package.json
│ ├── tailwind.config.js
│ └── vite.config.js
├── .gitignore
├── LICENSE
└── README.md

---

## ⚙️ Installation & Setup

### Prerequisites
- **Node.js** 18+ and **npm**
- **Python** 3.10+
- **Git**

### Clone the repository
```bash
git clone https://github.com/GitwithHaseeb/GH-Plagiarism-Checker.git
cd GH-Plagiarism-Checker
Backend setup
cd backend
python -m venv venv
# Activate virtual environment:
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
python precompute_embeddings.py   # Builds corpus embeddings (may take a few minutes)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Backend runs at http://localhost:8000
Frontend setup
cd frontend
npm install
npm run dev
Frontend runs at http://localhost:5173
Usage
Open your browser at http://localhost:5173

Upload a file (PDF/DOCX/TXT) or paste text into the text area.

Click “Submit Analysis”.

View the Plagiarism % and Humanized % results.

Click “Download IEEE Report” to get a professional Word document.

The report includes the analysis methodology, top similar sources, and references.
How It Works (AI/ML)
Plagiarism Detection
Corpus: A collection of research abstracts stored in backend/corpus/.

Embeddings: Each abstract is converted into a 384‑dimension vector using the all-MiniLM-L6-v2 sentence‑transformer model.

Similarity: User‑submitted text is embedded and compared against all corpus embeddings using cosine similarity.

Percentage: The highest similarity (or average of top‑3) is mapped to a percentage (clamped 0‑100).

Humanized Text Detection
Model: roberta-base-openai-detector (fine‑tuned RoBERTa) from Hugging Face.

Output: Probability that the text is AI‑generated.

Humanized % = (1 - AI_probability) × 100.

IEEE Report Generation
Library: python-docx

Sections: Title, Abstract, Methodology, Results, Discussion (with top sources), References.

Format: Times New Roman, 10‑12pt, headings in bold – follows IEEE conference style.

🚀 Future Improvements
Add support for .doc, .rtf, and .odt files.

Integrate external APIs (Crossref, Google Search) for live plagiarism checking.

User authentication & analysis history dashboard.

Deploy with Docker + CI/CD (GitHub Actions) to cloud (AWS/GCP/Azure).

Add support for batch file uploads.

👥 Contributing
Contributions are welcome! Please follow these steps:

Fork the repository.

Create a new branch: git checkout -b feature/your-feature-name

Commit your changes: git commit -m 'Add some feature'

Push to the branch: git push origin feature/your-feature-name

Open a Pull Request.

📄 License
Distributed under the MIT License. See LICENSE for more information.

📬 Contact
Muhammad Haseeb

GitHub: @GitwithHaseeb

LinkedIn: Muhammad Haseeb (update with your actual URL)

Email: haseebch8130@gmail.com

Project Link: https://github.com/GitwithHaseeb/GH-Plagiarism-Checker

⭐ Show Your Support
If this project helped you or inspired you, please give it a ⭐ on GitHub and share it with fellow researchers and developers!

