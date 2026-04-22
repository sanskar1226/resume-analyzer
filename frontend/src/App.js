import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [job, setJob] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const uploadFile = async () => {
    if (!file) {
      alert("Upload resume first");
      return;
    }

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job", job);

    try {
      const res = await axios.post(
        "http://127.0.0.1:5000/analyze",
        formData
      );

      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Error");
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <div className="card">
        <h1>Resume Analyzer 🚀</h1>

        <input type="file" onChange={(e) => setFile(e.target.files[0])} />

        <textarea
          placeholder="Paste Job Description"
          value={job}
          onChange={(e) => setJob(e.target.value)}
        />

        <button onClick={uploadFile}>
          {loading ? "Analyzing..." : "Analyze Resume"}
        </button>

        {loading && <div className="loader"></div>}

        {result && (
          <div className="result">
            <div
              className="circle"
              style={{ "--value": result.score }}
            >
              {result.score}%
            </div>

            <p><b>Matched:</b> {result.matched.join(", ")}</p>
            <p><b>Missing:</b> {result.missing.join(", ")}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;