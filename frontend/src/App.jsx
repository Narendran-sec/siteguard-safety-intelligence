import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

const PPE_CLASSES = [
  ["helmet", "Helmets"],
  ["no_helmet", "No Helmets"],
  ["vest", "Safety Vests"],
  ["no-safety vest", "No Vests"],
  ["goggles", "Goggles"],
  ["no_goggle", "No Goggles"],
  ["gloves", "Gloves"],
  ["no_gloves", "No Gloves"],
  ["boots", "Boots"],
  ["no_boots", "No Boots"],
];

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);
  const [reasonResult, setReasonResult] = useState(null);
  const [query, setQuery] = useState("");

  const [loading, setLoading] = useState(false);
  const [reasonLoading, setReasonLoading] = useState(false);

  const [error, setError] = useState("");
  const [dragging, setDragging] = useState(false);
  const [apiOnline, setApiOnline] = useState(false);

  const inputRef = useRef(null);

  useEffect(() => {
    checkHealth();
  }, []);

  async function checkHealth() {
    try {
      const response = await fetch(`${API_BASE}/health`);
      setApiOnline(response.ok);
    } catch {
      setApiOnline(false);
    }
  }

  function selectFile(selectedFile) {
    if (!selectedFile) return;

    if (!selectedFile.type.startsWith("image/")) {
      setError("Please select an image file.");
      return;
    }

    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));

    setResult(null);
    setReasonResult(null);
    setError("");
  }

  function handleFileInput(event) {
    selectFile(event.target.files?.[0]);
  }

  function handleDrop(event) {
    event.preventDefault();
    setDragging(false);

    selectFile(event.dataTransfer.files?.[0]);
  }

  async function analyzeImage() {
    if (!file) {
      setError("Upload a construction-site image first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setReasonResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/detect`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Detection failed.");
      }

      setResult(data);
    } catch (err) {
      setError(
        `${err.message} Make sure FastAPI is running at ${API_BASE}.`
      );
    } finally {
      setLoading(false);
    }
  }

  async function getSafetyReport() {
    if (!file) return;

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/safety-report`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Safety analysis failed.");
      }

      setResult((previous) => ({
        ...(previous || {}),
        safety: data,
      }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function askAI() {
    if (!file || !query.trim()) return;

    setReasonLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const url =
        `${API_BASE}/reason?query=` +
        encodeURIComponent(query.trim());

      const response = await fetch(url, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Reasoning request failed."
        );
      }

      setReasonResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setReasonLoading(false);
    }
  }

  function reset() {
    if (preview) {
      URL.revokeObjectURL(preview);
    }

    setFile(null);
    setPreview("");
    setResult(null);
    setReasonResult(null);
    setQuery("");
    setError("");

    if (inputRef.current) {
      inputRef.current.value = "";
    }
  }

  const detections = result?.detections || [];

  const counts = buildCounts(detections);

  const safety =
    result?.safety ||
    result?.evidence ||
    reasonResult?.evidence ||
    null;

  const status =
    result?.safety_status ||
    reasonResult?.safety_status ||
    safety?.status ||
    inferStatus(detections);

  const confidence =
    result?.confidence ||
    reasonResult?.confidence ||
    confidenceFromDetections(detections);

  return (
    <div className="app-shell">

      {/* ================= HEADER ================= */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-mark">
            S
          </div>

          <div>
            <div className="brand-name">
              SITEGUARD
            </div>

            <div className="brand-subtitle">
              AI SAFETY INTELLIGENCE
            </div>
          </div>

        </div>

        <div
          className={`api-status ${
            apiOnline ? "online" : "offline"
          }`}
        >
          <span className="status-dot" />

          {apiOnline
            ? "API ONLINE"
            : "API OFFLINE"}
        </div>

      </header>


      {/* ================= MAIN ================= */}

      <main>

        {/* HERO */}

        <section className="hero">

          <div className="eyebrow">
            <span />
            CONSTRUCTION SITE SAFETY
          </div>

          <h1>
            Detect PPE violations
            <br />

            <span>
              before they become incidents.
            </span>
          </h1>

          <p>
            RT-DETR powered visual inspection
            for construction-site safety intelligence.
          </p>

        </section>


        {/* ================= UPLOAD ================= */}

        {!file ? (

          <section
            className={`drop-zone ${
              dragging ? "dragging" : ""
            }`}
            onDragOver={(event) => {
              event.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() =>
              inputRef.current?.click()
            }
          >

            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              hidden
              onChange={handleFileInput}
            />

            <div className="upload-icon">
              ↑
            </div>

            <h2>
              Upload a site image
            </h2>

            <p>
              Drag & drop an image here,
              or click to browse
            </p>

            <span className="file-hint">
              JPG, PNG, WEBP
            </span>

          </section>

        ) : (

          <section className="workspace">

            <div className="workspace-header">

              <div>
                <span className="section-label">
                  INSPECTION IMAGE
                </span>

                <h2>
                  {file.name}
                </h2>
              </div>

              <button
                className="ghost-button"
                onClick={reset}
              >
                Change image
              </button>

            </div>

            <div className="preview-card">

              <img
                src={preview}
                alt="Construction site preview"
              />

            </div>

            <button
              className="primary-button analyze-button"
              onClick={analyzeImage}
              disabled={loading}
            >

              {loading ? (
                <>
                  <span className="spinner" />
                  ANALYZING...
                </>
              ) : (
                <>
                  ANALYZE SITE →
                </>
              )}

            </button>

          </section>

        )}


        {/* ERROR */}

        {error && (

          <div className="error-box">

            <strong>
              Request failed
            </strong>

            <span>
              {error}
            </span>

          </div>

        )}


        {/* ================= RESULTS ================= */}

        {result && (

          <section className="results-section">

            <div className="section-heading">

              <div>

                <span className="section-label">
                  ANALYSIS COMPLETE
                </span>

                <h2>
                  Safety intelligence
                </h2>

              </div>

              <span className="model-chip">
                {result.model || "RT-DETR"}
              </span>

            </div>


            {/* IMAGE + OVERVIEW */}

            <div className="result-grid">

              <DetectionPreview
                src={preview}
                detections={detections}
                width={result.image_width}
                height={result.image_height}
              />


              <div className="overview-card">

                <div
                  className={`safety-banner ${
                    statusClass(status)
                  }`}
                >

                  <div>

                    <span className="small-label">
                      SITE STATUS
                    </span>

                    <strong>
                      {formatStatus(status)}
                    </strong>

                  </div>

                  <div className="banner-symbol">

                    {status ===
                    "NO_DETECTED_VIOLATIONS"
                      ? "✓"
                      : "!"}

                  </div>

                </div>


                <div className="metric-grid">

                  <Metric
                    label="Objects"
                    value={
                      result.detection_count ??
                      detections.length
                    }
                  />

                  <Metric
                    label="Workers"
                    value={counts.person || 0}
                  />

                  <Metric
                    label="Violations"
                    value={violationCount(counts)}
                  />

                  <Metric
                    label="Confidence"
                    value={confidence}
                  />

                </div>


                <button
                  className="secondary-button"
                  onClick={getSafetyReport}
                  disabled={loading}
                >

                  {loading
                    ? "CHECKING..."
                    : "RUN SAFETY REPORT"}

                </button>

              </div>

            </div>


            {/* ================= PPE ================= */}

            <section className="detection-panel">

              <div className="section-heading compact">

                <div>

                  <span className="section-label">
                    DETECTED OBJECTS
                  </span>

                  <h3>
                    PPE inventory
                  </h3>

                </div>

                <span className="object-count">
                  {detections.length} detections
                </span>

              </div>


              <div className="ppe-grid">

                {PPE_CLASSES.map(
                  ([key, label]) => (

                    <div
                      className={`ppe-card ${
                        key.startsWith("no_") ||
                        key.startsWith("no-")
                          ? "negative"
                          : ""
                      }`}
                      key={key}
                    >

                      <span>
                        {label}
                      </span>

                      <strong>
                        {counts[key] || 0}
                      </strong>

                    </div>

                  )
                )}

              </div>

            </section>


            {/* ================= VIOLATIONS ================= */}

            {safety?.violations?.length > 0 && (

              <section className="violations-card">

                <span className="section-label">
                  ATTENTION REQUIRED
                </span>

                <h3>
                  Potential PPE violations
                </h3>

                <ul>

                  {safety.violations.map(
                    (item, index) => (

                      <li key={index}>

                        <span>
                          !
                        </span>

                        {item}

                      </li>

                    )
                  )}

                </ul>

              </section>

            )}


            {/* ================= REASONING ================= */}

            <section className="reasoning-card">

              <div className="reasoning-header">

                <div>

                  <span className="section-label">
                    SAFETY AI
                  </span>

                  <h3>
                    Ask about this image
                  </h3>

                </div>

                <span className="reasoning-tag">
                  RULE-BASED REASONING
                </span>

              </div>


              <div className="query-row">

                <input
                  value={query}
                  onChange={(event) =>
                    setQuery(event.target.value)
                  }
                  onKeyDown={(event) => {

                    if (
                      event.key === "Enter"
                    ) {
                      askAI();
                    }

                  }}
                  placeholder="e.g. Is everyone wearing a helmet?"
                />

                <button
                  className="primary-button ask-button"
                  onClick={askAI}
                  disabled={
                    reasonLoading ||
                    !query.trim()
                  }
                >

                  {reasonLoading
                    ? "THINKING..."
                    : "ASK AI →"}

                </button>

              </div>


              <div className="suggestions">

                {[
                  "How many workers are there?",
                  "Is anyone without a helmet?",
                  "Are there PPE violations?",
                ].map((item) => (

                  <button
                    key={item}
                    onClick={() =>
                      setQuery(item)
                    }
                  >
                    {item}
                  </button>

                ))}

              </div>


              {reasonResult && (

                <div className="answer-box">

                  <div className="answer-meta">

                    <span>
                      INTENT:{" "}
                      {reasonResult.intent}
                    </span>

                    <span>
                      CONFIDENCE:{" "}
                      {reasonResult.confidence}
                    </span>

                  </div>

                  <p>
                    {reasonResult.answer}
                  </p>

                </div>

              )}

            </section>

          </section>

        )}


        {/* ================= CAPABILITIES ================= */}

        <section className="capabilities">

          <div>

            <span className="cap-number">
              01
            </span>

            <strong>
              Visual detection
            </strong>

            <p>
              Locate workers, PPE and
              visible safety violations.
            </p>

          </div>


          <div>

            <span className="cap-number">
              02
            </span>

            <strong>
              Safety reasoning
            </strong>

            <p>
              Convert detections into
              explainable safety decisions.
            </p>

          </div>


          <div>

            <span className="cap-number">
              03
            </span>

            <strong>
              Confidence aware
            </strong>

            <p>
              Separate detected evidence
              from unsupported conclusions.
            </p>

          </div>

        </section>

      </main>


      {/* ================= FOOTER ================= */}

      <footer>

        <span>
          SITEGUARD AI
        </span>

        <span>
          CONSTRUCTION PPE SAFETY INTELLIGENCE
        </span>

        <span>
          RT-DETR + FASTAPI
        </span>

      </footer>

    </div>
  );
}


/* =========================================================
   DETECTION PREVIEW
========================================================= */

function DetectionPreview({
  src,
  detections,
  width,
  height,
}) {
  return (

    <div className="image-result-card">

      <div className="image-frame">

        <img
          src={src}
          alt="Analyzed construction site"
        />

        {width &&
          height &&
          detections.map(
            (detection, index) => (

              <BoundingBox
                key={`${detection.class_id}-${index}`}
                detection={detection}
                imageWidth={width}
                imageHeight={height}
              />

            )
          )}

      </div>


      <div className="image-caption">

        <span>
          DETECTION OVERLAY
        </span>

        <span>
          {detections.length} objects located
        </span>

      </div>

    </div>

  );
}


/* =========================================================
   BOUNDING BOX
========================================================= */

function BoundingBox({
  detection,
  imageWidth,
  imageHeight,
}) {
  const {
    x1,
    y1,
    x2,
    y2,
  } = detection.bbox;

  const style = {
    left:
      `${(x1 / imageWidth) * 100}%`,

    top:
      `${(y1 / imageHeight) * 100}%`,

    width:
      `${((x2 - x1) / imageWidth) * 100}%`,

    height:
      `${((y2 - y1) / imageHeight) * 100}%`,
  };

  const className =
    detection.class_name
      .toLowerCase();

  const negative =
    className.startsWith("no_") ||
    className.startsWith("no-");

  return (

    <div
      className={`bbox ${
        negative ? "bbox-negative" : ""
      }`}
      style={style}
    >

      <span>

        {detection.class_name}{" "}
        {Math.round(
          detection.confidence * 100
        )}
        %

      </span>

    </div>

  );
}


/* =========================================================
   METRIC
========================================================= */

function Metric({
  label,
  value,
}) {
  return (

    <div className="metric">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>

  );
}


/* =========================================================
   COUNTING
========================================================= */

function buildCounts(detections) {

  return detections.reduce(
    (acc, item) => {

      const key =
        item.class_name.toLowerCase();

      acc[key] =
        (acc[key] || 0) + 1;

      return acc;

    },
    {}
  );

}


/* =========================================================
   VIOLATIONS
========================================================= */

function violationCount(counts) {

  return (
    (counts.no_helmet || 0) +
    (counts["no-safety vest"] || 0) +
    (counts.no_goggle || 0) +
    (counts.no_gloves || 0) +
    (counts.no_boots || 0)
  );

}


/* =========================================================
   STATUS
========================================================= */

function inferStatus(detections) {

  const counts =
    buildCounts(detections);

  if (!detections.length) {
    return "INSUFFICIENT_INFORMATION";
  }

  return violationCount(counts) > 0
    ? "ATTENTION_REQUIRED"
    : "NO_DETECTED_VIOLATIONS";

}


function statusClass(status) {

  if (
    status ===
    "NO_DETECTED_VIOLATIONS"
  ) {
    return "safe";
  }

  if (
    status ===
    "INSUFFICIENT_INFORMATION"
  ) {
    return "unknown";
  }

  return "warning";

}


function formatStatus(status) {

  return {
    ATTENTION_REQUIRED:
      "ATTENTION REQUIRED",

    NO_DETECTED_VIOLATIONS:
      "NO DETECTED VIOLATIONS",

    INSUFFICIENT_INFORMATION:
      "INSUFFICIENT INFORMATION",

  }[status] ||
    status ||
    "UNKNOWN";

}


/* =========================================================
   CONFIDENCE
========================================================= */

function confidenceFromDetections(
  detections
) {

  if (!detections.length) {
    return "LOW";
  }

  const average =
    detections.reduce(
      (sum, item) =>
        sum + item.confidence,
      0
    ) / detections.length;

  if (average >= 0.8) {
    return "HIGH";
  }

  if (average >= 0.6) {
    return "MEDIUM";
  }

  return "LOW";

}


export default App;