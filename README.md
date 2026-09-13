# SiteGuard AI

## Construction Site PPE Compliance Detection System

SiteGuard AI is a computer-vision-based PPE compliance detection system designed to assist construction-site safety monitoring.

The system analyzes construction-site images using a custom YOLO detection model and evaluates the presence of required Personal Protective Equipment (PPE), including helmets, gloves, safety vests, safety boots, and goggles.

The application provides structured compliance results with confidence scores, missing PPE identification, and an explicit uncertainty state when visual evidence is insufficient.

> **Purpose:** SiteGuard AI is an AI-assisted safety monitoring tool. It does not replace qualified safety personnel, site regulations, or mandatory human inspection procedures.

---

## Overview

Manual PPE inspection requires continuous human supervision and can be difficult to scale across large construction environments.

SiteGuard AI provides an automated image-based inspection workflow:

```text
Site Image
    |
    v
Image Upload
    |
    v
FastAPI Backend
    |
    v
YOLO PPE Detection
    |
    v
Detection Analysis
    |
    v
Compliance Evaluation
    |
    v
Structured JSON Result
    |
    v
Web Dashboard
```

The system is designed to make PPE inspection faster, more structured, and easier to interpret while maintaining an explicit uncertainty state for cases where visual evidence is insufficient.

---

## Key Features

### AI-Powered PPE Detection

Uses a custom YOLO-based computer vision model to analyze construction-site images and detect relevant PPE equipment.

### PPE Compliance Evaluation

Evaluates the required safety equipment:

- Helmet
- Gloves
- Safety Vest
- Safety Boots
- Goggles

### Overall Site Status

The system produces an overall compliance status:

| Status | Meaning |
|---|---|
| `COMPLIANT` | Required PPE was detected with sufficient confidence |
| `VIOLATION` | One or more required PPE items were identified as missing |
| `UNCERTAIN` | Available visual evidence is insufficient for a reliable decision |
| `NO PERSON` | No person was detected in the submitted image |

### Confidence Scores

Each PPE detection includes confidence information so results are not presented as an unexplained yes/no decision.

### Missing PPE Identification

When required PPE is missing, the system explicitly identifies which equipment was not detected.

### Uncertainty Handling

Low-confidence or visually ambiguous detections are separated from confirmed violations.

```text
Not detected != Definitely missing
```

Poor image quality, occlusion, distance, lighting, or camera angle can prevent reliable detection.

### Web Dashboard

The frontend provides:

- Construction-site image upload
- Image preview
- File information
- AI analysis trigger
- Loading state
- Overall compliance status
- Person detection result
- PPE status cards
- Confidence indicators
- Missing PPE alerts
- Uncertain detection alerts
- Reset functionality

---

## System Architecture

SiteGuard AI follows a frontend-backend-machine-learning architecture.

```text
+----------------------------------------------+
|                Web Dashboard                |
|                                              |
| React + Vite + CSS                           |
| Image Upload / Results / Visualization       |
+---------------------+------------------------+
                      |
                      | HTTP POST /analyze
                      v
+----------------------------------------------+
|              FastAPI Backend                |
|                                              |
| Request Validation                           |
| Image Handling                               |
| PPE Analysis                                 |
| JSON Response                                |
+---------------------+------------------------+
                      |
                      v
+----------------------------------------------+
|           PPE Analysis Pipeline              |
|                                              |
| Image -> YOLO Detection -> Interpretation    |
|                    |                         |
|                    v                         |
|           Compliance Evaluation              |
+---------------------+------------------------+
                      |
                      v
+----------------------------------------------+
|              V2 YOLO Model                  |
|                                              |
|              v2best.pt                      |
+----------------------------------------------+
```

---

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS
- HTML

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- Python Multipart

### Machine Learning

- PyTorch
- Ultralytics YOLO
- Torchvision
- Custom trained PPE detection model

### Supporting Libraries

- NumPy
- OpenCV
- Pillow
- Requests
- PyYAML

---

## Project Structure

```text
rapid_ml/
|
+-- backend/
|   |
|   +-- app/
|   |   +-- __init__.py
|   |   +-- main.py
|   |   +-- model_service.py
|   |   +-- ppe_analyzer.py
|   |   +-- reasoning.py
|   |   +-- schemas.py
|   |
|   +-- models/
|   |   +-- v2best.pt
|   |
|   +-- uploads/
|   +-- test_model.py
|   +-- requirements.txt
|   +-- .gitignore
|
+-- frontend/
|   |
|   +-- public/
|   |   +-- logo.png
|   |
|   +-- src/
|   |   +-- App.jsx
|   |   +-- App.css
|   |   +-- main.jsx
|   |
|   +-- index.html
|   +-- package.json
|
+-- .gitignore
+-- README.md
```

---

## How the System Works

### 1. Image Upload

The user uploads a construction-site image through the web dashboard.

Supported image formats:

```text
JPG
PNG
WEBP
```

The frontend validates the selected file and displays a preview before analysis.

### 2. API Request

When the user clicks **ANALYZE PPE**, the frontend sends the image to the FastAPI backend.

```http
POST /analyze
```

The image is transmitted using multipart form data.

### 3. YOLO Detection

The backend loads the custom V2 PPE detection model:

```text
backend/models/v2best.pt
```

The model processes the submitted image and produces detection results.

### 4. Detection Analysis

The PPE analysis layer interprets the model output and evaluates the required PPE categories.

Each PPE item can be classified as:

```text
present
missing
uncertain
```

### 5. Compliance Decision

The individual PPE results are combined to determine the overall site status.

Example:

```text
Helmet       -> PRESENT
Gloves       -> PRESENT
Safety Vest  -> PRESENT
Safety Boots -> MISSING
Goggles      -> PRESENT

Overall      -> VIOLATION
```

Another example:

```text
Helmet       -> PRESENT
Gloves       -> UNCERTAIN
Safety Vest  -> PRESENT
Safety Boots -> PRESENT
Goggles      -> PRESENT

Overall      -> UNCERTAIN
```

This prevents ambiguous detections from automatically being treated as confirmed violations.

---

## API

### Analyze Image

```http
POST /analyze
```

### Request

The endpoint accepts an image using multipart form data:

```text
file: <image>
```

### Example Response

```json
{
  "status": "violation",
  "person_detected": true,
  "ppe": {
    "helmet": {
      "status": "present",
      "positive_confidence": 0.96,
      "negative_confidence": 0.04
    },
    "gloves": {
      "status": "missing",
      "positive_confidence": 0.08,
      "negative_confidence": 0.92
    },
    "vest": {
      "status": "present",
      "positive_confidence": 0.94,
      "negative_confidence": 0.06
    },
    "boots": {
      "status": "present",
      "positive_confidence": 0.89,
      "negative_confidence": 0.11
    },
    "goggles": {
      "status": "uncertain",
      "positive_confidence": 0.48,
      "negative_confidence": 0.52
    }
  },
  "missing": ["gloves"],
  "uncertain": ["goggles"]
}
```

> The exact response structure and confidence values depend on the current backend implementation and model output.

---

## Running the Project Locally

### Prerequisites

Install:

- Python
- Node.js
- npm
- Git

A Python virtual environment is recommended for the backend.

### Backend Setup

```powershell
cd C:\Users\DELL\Documents\rapid_ml\backend
```

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the FastAPI server:

```powershell
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

### Frontend Setup

Open another terminal:

```powershell
cd C:\Users\DELL\Documents\rapid_ml\frontend
```

Install dependencies:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

Vite will display the local development URL, typically:

```text
http://localhost:5173
```

---

## Production Build

Create a production build:

```powershell
npm run build
```

Generated files:

```text
frontend/dist/
```

Preview the production build:

```powershell
npm run preview
```

---

## Model

The project uses a custom YOLO PPE detection model:

```text
backend/models/v2best.pt
```

The model is loaded by the PPE analysis service and used for image-based detection.

The V2 model is tracked using Git LFS because of its large file size.

---

## Detection States

### Present

The model has sufficient evidence to identify the PPE item as present.

```text
status = present
```

### Missing

The model determines that the PPE item is not detected with sufficient evidence.

```text
status = missing
```

### Uncertain

The model does not have enough reliable visual evidence to make a confident classification.

```text
status = uncertain
```

Uncertainty can occur because of:

- Occlusion
- Poor lighting
- Low image resolution
- Small object size
- Unusual camera angles
- Partial visibility
- Visual similarity between objects

---

## Why Uncertainty Matters

A safety system should avoid treating every low-confidence detection as a confirmed violation.

For example:

```text
Person is wearing a helmet
        |
Helmet is partially blocked
        |
Model confidence decreases
        |
System reports UNCERTAIN
```

Instead of incorrectly producing:

```text
VIOLATION
```

The system exposes the uncertainty so the result can be reviewed by a human.

---

## Frontend Workflow

```text
01 INPUT
   |
   +-- Select Site Image
   +-- Preview Image
   +-- Confirm Image
        |
        v
   ANALYZE PPE
        |
        v
02 OUTPUT
   |
   +-- Overall Site Status
   +-- Person Detection
   +-- PPE Status
   +-- Confidence
   +-- Missing PPE
   +-- Uncertain PPE
```

---

## Error Handling

The application handles common failures such as:

- Invalid file selection
- Unsupported image formats
- Missing image input
- Backend connection failure
- API errors
- Model inference errors
- Unavailable analysis results

The frontend displays user-facing error messages instead of silently failing.

---

## Development and Testing

The backend can be tested independently using sample construction-site images:

```powershell
python test_model.py
```

The frontend production build can be verified using:

```powershell
npm run build
```

A successful build should generate the `dist` directory without compilation errors.

---

## Security and Repository Hygiene

Sensitive and generated files should not be committed unnecessarily.

The project uses `.gitignore` rules for:

```text
venv/
__pycache__/
*.pyc
uploads/
runs/
.env
*.log
```

Environment variables and secrets should be stored outside source code.

The trained model is tracked separately using Git LFS.

---

## Performance Considerations

Inference performance depends on:

- CPU/GPU availability
- Image resolution
- Model architecture
- Number of detections
- Runtime environment

CPU inference is supported. GPU acceleration can improve inference performance when a compatible CUDA environment is available.

---

## Limitations

### Image-Based Detection

The current workflow analyzes submitted images rather than continuously monitoring live camera feeds.

### Visual Dependency

Detection quality depends heavily on input image quality.

### Occlusion

PPE that is completely or partially hidden may not be detected reliably.

### Camera Angle

Unusual camera perspectives can reduce detection accuracy.

### Model Limitations

The model can produce false positives and false negatives.

Therefore, results should be interpreted as decision-support information rather than absolute safety certification.

---

## Future Improvements

### Real-Time Camera Monitoring

```text
CCTV / IP Camera
       |
       v
Live Video Stream
       |
       v
Frame Sampling
       |
       v
YOLO Detection
       |
       v
PPE Compliance
       |
       v
Real-Time Alerts
```

### Multi-Person Tracking

Track individual workers across video frames and maintain PPE status per person.

### Safety Violation Alerts

Trigger alerts when repeated PPE violations are detected.

### Historical Analytics

Potential analytics include:

- Violation frequency
- PPE compliance trends
- Site-level statistics
- Worker-level history
- Time-based analysis

### Automated Reports

Generate safety inspection reports containing:

- Inspection timestamp
- Image
- Detected personnel
- PPE status
- Confidence scores
- Violations
- Uncertain detections

### Edge Deployment

Deploy the detection pipeline closer to cameras for reduced latency and lower network dependency.

---

## Design Principles

### 1. Practicality

The system focuses on a real operational safety problem rather than only demonstrating model inference.

### 2. Explainability

The dashboard exposes individual PPE states and confidence information instead of returning only a single classification.

### 3. Uncertainty Awareness

Ambiguous visual evidence is represented as uncertain rather than automatically converted into a safety violation.

### 4. Human-in-the-Loop Safety

AI detection is intended to support safety personnel, not replace professional judgment.

---

## Example User Flow

```text
User opens SiteGuard AI
        |
        v
Uploads construction-site image
        |
        v
Image preview displayed
        |
        v
Clicks "ANALYZE PPE"
        |
        v
Backend receives image
        |
        v
YOLO model performs detection
        |
        v
PPE analyzer evaluates detections
        |
        v
Compliance status calculated
        |
        v
Results returned as JSON
        |
        v
Dashboard displays:
        |
        +-- COMPLIANT
        +-- VIOLATION
        +-- UNCERTAIN
        +-- NO PERSON
```

---

## Project Status

**Current Version:** V2

**Detection Engine:** YOLO-based custom PPE detection

**Application Type:** Web-based AI safety monitoring system

**Current Input:** Construction-site images

**PPE Categories:**

```text
Helmet
Gloves
Safety Vest
Safety Boots
Goggles
```

**Analysis Output:**

```text
Overall Status
Person Detection
PPE Status
Confidence
Missing PPE
Uncertain PPE
```

---

## Responsible Use

SiteGuard AI should be used as an assistance and monitoring system.

AI predictions can be affected by image quality, environmental conditions, model limitations, and unseen scenarios. Safety-critical decisions should be verified by qualified personnel and follow applicable workplace safety regulations and procedures.

---

## License

This project is currently maintained as a hackathon / internship project.

If the project is distributed publicly, add an appropriate open-source or proprietary license.

---

## Acknowledgements

Built as an AI/ML engineering project focused on applying computer vision to real-world construction safety monitoring.

---

## Author

**SiteGuard AI**

Construction Safety Intelligence

**V2 Detection Engine**
