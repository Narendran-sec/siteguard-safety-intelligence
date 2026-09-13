# SiteGuard AI

### Construction Site PPE Compliance Detection System

SiteGuard AI is a computer-vision-based PPE compliance system designed to assist construction-site safety monitoring.

The system analyzes construction-site images using a custom YOLO detection model and evaluates the presence of required Personal Protective Equipment (PPE), including helmets, gloves, safety vests, safety boots, and goggles.

The application provides structured compliance results with confidence scores, missing PPE identification, and an explicit uncertainty state when visual evidence is insufficient.

---

## Overview

Manual PPE inspection requires continuous human supervision and does not scale efficiently across large construction environments.

SiteGuard AI addresses this by providing an automated image-based inspection workflow:

```text
Site Image
    │
    ▼
Image Upload
    │
    ▼
FastAPI Backend
    │
    ▼
YOLO PPE Detection
    │
    ▼
Detection Analysis
    │
    ▼
Compliance Evaluation
    │
    ▼
Structured JSON Result
    │
    ▼
Web Dashboard