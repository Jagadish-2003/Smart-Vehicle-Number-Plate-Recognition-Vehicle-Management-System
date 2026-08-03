# Smart Vehicle Number Plate Recognition & Vehicle Management System

An end-to-end ANPR (Automatic Number Plate Recognition) application built
with a custom-trained YOLO11 license-plate detector, EasyOCR, and a
Streamlit UI, with SQLite persistence and Plotly analytics.

## Features

- **Image Detection** — upload an image, detect plates, view YOLO/OCR
  confidence, corrected plate text, validation result, and a full
  **vehicle report** (owner, challans, blacklist, authorized status).
- **Live Camera** — capture frames from your browser camera (works on
  desktop and mobile — the browser prompts for camera permission) and run
  detection in near-real-time, with a live results table, FPS tracking,
  vehicle report for the latest capture, and CSV export.
- **Video Detection** — upload a video, process it frame-by-frame (with
  configurable frame skipping), download an annotated output video, and
  view a vehicle report for every unique plate found.
- **Vehicle Database** — register vehicles (owner, brand/model, color,
  registration state, RC/insurance/PUC dates, authorized flag), issue and
  settle traffic challans, and manage a blacklist. Seeded with 6 demo
  vehicles so the app is testable immediately; any plate you look up that
  isn't registered gets a one-click "quick add" form right on the
  detection result.
- **Detection History** — search, filter, sort, delete, and export past
  detections.
- **Analytics** — KPIs and Plotly charts: daily/hourly trend, OCR &
  detection confidence distributions, top plates, valid vs invalid split.
- **Settings** — tune detection/OCR thresholds, manage the duplicate cache
  and database, and view storage/model status.

## Tech Stack

Frontend: Streamlit · Backend: Python · CV: OpenCV · Detection: Ultralytics
YOLO (custom license-plate model) · OCR: EasyOCR · DB: SQLite · Analysis:
Pandas/NumPy · Visualization: Plotly

## Project Structure

```
app.py                     Entry point — bootstraps config/model/OCR/DB/cache, launches UI
ai/                         Model loading, preprocessing, OCR engine, detector (+ TTA rescue pass), video processor
services/                   Business logic: detection, vehicle lookup, analytics, history, settings
database/                   SQLite persistence: detections, vehicles, challans, blacklist + analytics queries
config/                     JSON config + config manager + static settings
utils/                      Logger, duplicate cache, plate validation
components/                 Reusable UI: navbar, footer, metric cards, charts, vehicle report card
app_pages/                  One module per Streamlit page (home, dashboard, detection pages, vehicle_manager, history, analytics, settings)
models/weights/best.pt      Your custom-trained YOLO11 plate-detection weights
yolo11n.pt                  Base YOLO11n checkpoint (reference / fallback)
outputs/                    Saved cropped plates, annotated images, processed videos
logs/                       Application log file
```

## Setup

1. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Confirm your trained weights are in place**
   The app expects `models/weights/best.pt` (already included in this zip).
   If you retrain, drop the new `best.pt` in the same location, or update
   `config/app_config.json -> model.weights_path`.

3. **Run the app**
   ```bash
   streamlit run app.py
   ```
   The app opens at `http://localhost:8501`.

## Configuration

All tunable parameters live in `config/app_config.json` and can also be
edited live from the **Settings** page:

- `model.confidence_threshold` / `model.iou_threshold` — YOLO detection thresholds
- `ocr.min_confidence` — minimum OCR confidence to accept a reading
- `validation.min_plate_length` / `max_plate_length` — plate length bounds
- `video.frame_skip` — frames skipped between detection passes on video
- `cache.duplicate_window_seconds` — time window for suppressing duplicate saves

## Plate Validation

OCR text is cleaned (uppercase, symbols/spaces stripped), checked for
length and OCR confidence, then matched against Indian registration
formats: `AA00AA0000`, `AA00A0000`, `AA0AA0000`.

## Improving detection accuracy

`models/weights/best.pt` was trained on a small custom dataset, so recall
will vary on plates that differ a lot from the training images (unusual
angle, distance, lighting, motion blur). Two things are already built in
to help:

1. **Rescue pass** (`ai/vehicle_plate_detector.py`) — if the primary
   confidence threshold finds nothing, the app automatically retries once
   at a much lower threshold with Ultralytics' test-time augmentation
   (`augment=True`, multi-scale + flip inference merged). This trades a
   little speed for meaningfully better recall on a small-data model,
   without changing the weights.
2. **Best-of-two OCR** (`ai/ocr_engine.py`) — every crop is read both raw
   and after CLAHE + adaptive-threshold preprocessing, and whichever
   result has higher OCR confidence is kept.

If detections are still missed too often, the real fix is more training
data, not more inference-time tricks:

- Add more images to `dataset/` (different lighting, angles, distances,
  vehicle types, occlusion) and re-run your training script (Colab is
  fine on the free GPU tier for YOLO11n).
- Increase training epochs / image size, and enable YOLO's built-in
  augmentation (mosaic, HSV jitter, random flip) during training, not
  just inference.
- Lower `model.confidence_threshold` in Settings if you'd rather trade
  some false positives for fewer misses.
- Drop the newly trained `best.pt` into `models/weights/` (same filename)
  and restart — no code changes needed.

## Vehicle Management

- The **Vehicle Database** page manages three tables: `vehicles`
  (owner/brand/model/color/state/RC/insurance/PUC/authorized),
  `challans` (violation, amount, pending/paid), and `blacklist`
  (plate + reason). It's seeded with 6 demo vehicles so lookups work
  out of the box; register your own test plates there any time.
- Every detection page looks the recognized plate up against this
  database and shows a report card: owner, vehicle, pending challans,
  blacklist alert, and authorized/unauthorized status — matching the
  "Expected Output" section of the project brief. Fuzzy matching
  (`difflib`) tolerates a one-character OCR misread when looking up a
  plate.

## Notes

- First run downloads EasyOCR's language weights (`en`) — needs an internet
  connection once; cached afterward.
- `outputs/` and `logs/` are pre-created with `.gitkeep` files so the app
  runs immediately after cloning.
- No external database is required — everything runs locally on SQLite
  (`database/anpr.db`, created automatically). The app has no login —
  it opens straight to the dashboard.

## Roadmap (not yet implemented)

Live CCTV/IP camera monitoring, multi-object tracking across video frames
(DeepSORT/ByteTrack), automatic gate control, email/SMS alerts, and
integration with real RTO databases (see the project brief's Future
Enhancements — these are out of scope for a local demo app).
