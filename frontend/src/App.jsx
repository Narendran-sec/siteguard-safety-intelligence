import { useState } from "react";
import "./App.css";

const API_URL = "https://siteguard-safety-intelligence.onrender.com";

const PPE_ITEMS = [
  { key: "helmet", label: "Helmet", icon: "⛑" },
  { key: "gloves", label: "Gloves", icon: "🧤" },
  { key: "vest", label: "Safety Vest", icon: "🦺" },
  { key: "boots", label: "Safety Boots", icon: "🥾" },
  { key: "goggles", label: "Goggles", icon: "🥽" },
];

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setError("Please select a valid image file.");
      return;
    }

    setSelectedFile(file);
    setResult(null);
    setError("");

    const imageUrl = URL.createObjectURL(file);
    setPreview(imageUrl);
  };

  const analyzeImage = async () => {
    if (!selectedFile) {
      setError("Please select an image first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "PPE analysis failed.");
      }

      setResult(data);
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Unable to connect to the PPE detection server."
      );
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError("");
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case "compliant":
        return "COMPLIANT";
      case "violation":
        return "VIOLATION";
      case "uncertain":
        return "UNCERTAIN";
      case "no_person":
        return "NO PERSON";
      default:
        return status?.toUpperCase() || "UNKNOWN";
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case "compliant":
        return "compliant";
      case "violation":
        return "violation";
      case "uncertain":
        return "uncertain";
      case "no_person":
        return "no-person";
      default:
        return "";
    }
  };

  const getPPEClass = (status) => {
    if (status === "present") return "present";
    if (status === "missing") return "missing";
    return "ppe-uncertain";
  };

  const getOverallIcon = (status) => {
    switch (status) {
      case "compliant":
        return "✓";
      case "violation":
        return "!";
      case "uncertain":
        return "?";
      case "no_person":
        return "∅";
      default:
        return "•";
    }
  };

  return (
    <div className="app">

      {/* =====================================================
          TOP NAVBAR
      ===================================================== */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-mark">
            <img src="/logo.png" alt="SiteGuard AI" />
          </div>

          <div className="brand-text">
            <h1>SITEGUARD<span> AI</span></h1>
            <p>PPE COMPLIANCE INTELLIGENCE</p>
          </div>

        </div>

        <div className="system-indicator">
          <span className="live-dot"></span>
          <div>
            <strong>SYSTEM ONLINE</strong>
            <small>V2 DETECTION ENGINE</small>
          </div>
        </div>

      </header>


      {/* =====================================================
          MAIN
      ===================================================== */}

      <main className="dashboard">

        {/* HEADER */}

        <section className="dashboard-header">

          <div>
            <div className="eyebrow">
              <span></span>
              AI-POWERED SAFETY MONITORING
            </div>

            <h2>
              Construction Site
              <br />
              <span>PPE Compliance</span>
            </h2>

            <p>
              Upload a construction-site image and let the
              detection engine identify PPE compliance,
              missing equipment and uncertain detections.
            </p>
          </div>

          <div className="model-card">
            <span className="model-label">ACTIVE MODEL</span>
            <strong>V2 BEST</strong>
            <small>YOLO DETECTION ENGINE</small>
          </div>

        </section>


        {/* WORKSPACE */}

        <section className="workspace">

          {/* =================================================
              UPLOAD PANEL
          ================================================= */}

          <div className="panel upload-panel">

            <div className="panel-header">

              <div className="panel-number">
                01
              </div>

              <div>
                <span>INPUT</span>
                <h3>Site Image</h3>
              </div>

            </div>


            <label
              className={`upload-zone ${
                preview ? "has-preview" : ""
              }`}
            >

              {preview ? (

                <div className="preview-wrapper">

                  <img
                    src={preview}
                    alt="Construction site preview"
                  />

                  <div className="preview-overlay">
                    <span>IMAGE READY</span>
                  </div>

                </div>

              ) : (

                <div className="upload-placeholder">

                  <div className="upload-symbol">
                    ↑
                  </div>

                  <h4>
                    DROP SITE IMAGE
                  </h4>

                  <p>
                    Drag & drop or click to browse
                  </p>

                  <div className="format-tags">
                    <span>JPG</span>
                    <span>PNG</span>
                    <span>WEBP</span>
                  </div>

                </div>

              )}

              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleFileChange}
              />

            </label>


            {/* FILE INFO */}

            {selectedFile && (

              <div className="file-row">

                <div className="file-icon">
                  IMG
                </div>

                <div className="file-details">
                  <strong>{selectedFile.name}</strong>

                  <span>
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </div>

                <div className="file-ready">
                  READY
                </div>

              </div>

            )}


            {/* BUTTONS */}

            <div className="action-row">

              <button
                className="analyze-btn"
                onClick={analyzeImage}
                disabled={!selectedFile || loading}
              >

                {loading ? (
                  <>
                    <span className="button-spinner"></span>
                    ANALYZING
                  </>
                ) : (
                  <>
                    RUN PPE ANALYSIS
                    <span>→</span>
                  </>
                )}

              </button>


              {(selectedFile || result) && (

                <button
                  className="reset-btn"
                  onClick={reset}
                >
                  RESET
                </button>

              )}

            </div>


            {error && (

              <div className="error-message">
                <span>!</span>
                {error}
              </div>

            )}

          </div>


          {/* =================================================
              RESULTS PANEL
          ================================================= */}

          <div className="panel results-panel">

            <div className="panel-header">

              <div className="panel-number">
                02
              </div>

              <div>
                <span>OUTPUT</span>
                <h3>AI Analysis</h3>
              </div>

            </div>


            {/* EMPTY */}

            {!result && !loading && (

              <div className="empty-state">

                <div className="radar">
                  <div className="radar-line"></div>
                  <div className="radar-dot"></div>
                </div>

                <h4>AWAITING ANALYSIS</h4>

                <p>
                  Upload a site image to begin
                  PPE compliance detection.
                </p>

              </div>

            )}


            {/* LOADING */}

            {loading && (

              <div className="loading-state">

                <div className="loader-ring"></div>

                <h4>
                  ANALYZING SITE
                </h4>

                <p>
                  Detecting people and PPE equipment...
                </p>

                <div className="processing-bar">
                  <div></div>
                </div>

              </div>

            )}


            {/* RESULT */}

            {result && (

              <div className="result-content">

                {/* OVERALL STATUS */}

                <div
                  className={`overall-status ${getStatusClass(
                    result.status
                  )}`}
                >

                  <div className="status-icon">
                    {getOverallIcon(result.status)}
                  </div>

                  <div className="status-info">

                    <span>
                      OVERALL SITE STATUS
                    </span>

                    <h2>
                      {getStatusLabel(result.status)}
                    </h2>

                  </div>

                  <div className="status-side">
                    <small>PERSON DETECTED</small>

                    <strong>
                      {result.person_detected
                        ? "YES"
                        : "NO"}
                    </strong>
                  </div>

                </div>


                {/* PPE HEADER */}

                <div className="section-title">

                  <span>03</span>

                  <div>
                    <small>REQUIRED EQUIPMENT</small>
                    <h4>PPE Detection Results</h4>
                  </div>

                </div>


                {/* PPE GRID */}

                <div className="ppe-grid">

                  {PPE_ITEMS.map((item) => {

                    const data = result.ppe?.[item.key];

                    if (!data) return null;

                    const confidence = Math.max(
                      data.positive_confidence || 0,
                      data.negative_confidence || 0
                    );

                    return (

                      <div
                        className={`ppe-card ${getPPEClass(
                          data.status
                        )}`}
                        key={item.key}
                      >

                        <div className="ppe-top">

                          <div className="ppe-icon">
                            {item.icon}
                          </div>

                          <div className="ppe-name">
                            <strong>
                              {item.label}
                            </strong>

                            <span
                              className={`ppe-status ${getPPEClass(
                                data.status
                              )}`}
                            >
                              {data.status.toUpperCase()}
                            </span>
                          </div>

                        </div>


                        <div className="confidence-row">

                          <span>
                            CONFIDENCE
                          </span>

                          <strong>
                            {(confidence * 100).toFixed(1)}%
                          </strong>

                        </div>

                        <div className="confidence-track">

                          <div
                            className={`confidence-value ${getPPEClass(
                              data.status
                            )}`}
                            style={{
                              width: `${Math.min(
                                100,
                                confidence * 100
                              )}%`,
                            }}
                          />

                        </div>

                      </div>

                    );

                  })}

                </div>


                {/* ALERTS */}

                {result.missing?.length > 0 && (

                  <div className="result-alert missing">

                    <div className="alert-symbol">
                      !
                    </div>

                    <div>
                      <strong>MISSING PPE DETECTED</strong>

                      <p>
                        {result.missing
                          .map(
                            (item) =>
                              item.charAt(0).toUpperCase() +
                              item.slice(1)
                          )
                          .join(" • ")}
                      </p>
                    </div>

                  </div>

                )}


                {result.uncertain?.length > 0 && (

                  <div className="result-alert uncertain-alert">

                    <div className="alert-symbol">
                      ?
                    </div>

                    <div>
                      <strong>LIMITED VISUAL EVIDENCE</strong>

                      <p>
                        {result.uncertain
                          .map(
                            (item) =>
                              item.charAt(0).toUpperCase() +
                              item.slice(1)
                          )
                          .join(" • ")}
                      </p>
                    </div>

                  </div>

                )}


                {/* AI NOTE */}

                <div className="ai-note">

                  <span>AI NOTE</span>

                  <p>
                    Uncertain means the model did not
                    receive enough visual evidence to
                    confidently classify that PPE item.
                  </p>

                </div>

              </div>

            )}

          </div>

        </section>

      </main>


      {/* =====================================================
          FOOTER
      ===================================================== */}

      <footer>

        <div>
          <strong>SITEGUARD AI</strong>
          <span>CONSTRUCTION SAFETY INTELLIGENCE</span>
        </div>

        <div className="footer-status">
          <span className="live-dot"></span>
          V2 MODEL ACTIVE
        </div>

      </footer>

    </div>
  );
}

export default App;