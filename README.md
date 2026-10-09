# SecureVision

SecureVision is a local Flask application for image, video, and browser-camera weapon detection. It uses the existing YOLO checkpoint at `models\best.pt` and persists detection events, details, and evidence metadata through SQLAlchemy. SQLite is the default; a MySQL URL can be supplied through `DATABASE_URL`.

## Run on Windows

Open a VS Code terminal in the project directory and run:

```powershell
.\venv\Scripts\Activate.ps1
python app.py
```

Then browse to **http://127.0.0.1:5000**. Stop the development server with **Ctrl+C**.

If the virtual environment or dependencies are not present yet:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The app initializes missing database tables at startup. Do not delete `app.db` to troubleshoot; doing so removes saved event records. With the default configuration the database is `E:\SecureVision\app.db`. The startup log records the resolved SQLite database path. Override it with `DATABASE_URL` in a local `.env` file if needed. Never place real credentials in source control.

Event wall-clock timestamps are created as timezone-aware UTC datetimes in Python. SQLite and MySQL may return these values without timezone metadata, so API timestamps mark stored values as UTC (`Z`); the Dashboard, Event History, and Evidence Gallery convert them to `Asia/Kolkata` only for display. `detection_detail.timestamp_seconds` is a nullable video-relative offset, not an event timestamp; it is expected to be empty for image and camera detections. The parent event's `detected_at` is the authoritative wall-clock time.

The configured model path defaults to `models\best.pt`; set `MODEL_PATH` to use another existing checkpoint. If the model is missing or invalid, pages remain available but inference endpoints report the model failure instead of fabricating results.

## Workflows

- **Image detection:** upload JPG, JPEG, PNG, or WEBP. A successful inference, including a valid inference with no detections, is recorded as an event. Detected boxes and an annotated image are linked where produced.
- **Video detection:** upload MP4, AVI, MOV, MKV, or WEBM within the configured request-size limit. Processing runs in a background thread in this local single-process development setup. OpenCV creates a uniquely named annotated MP4 using its `mp4v` encoder and validates the finalized file. If local FFmpeg with `libx264` is available, the application creates and validates a browser-compatible H.264 copy; otherwise the MP4 remains available as a download and the result clearly reports that browser playback is unavailable. Event and detection results remain accessible if conversion cannot be performed.
- **Live camera:** select **Enable camera**, grant permission, then select **Start detection**. Frame processing only runs while explicitly enabled. **Pause detection** stops frame submissions but leaves the preview open; **Stop camera** stops the media tracks and requests cleanup of the session's temporal-verification state.
- **Event History, Dashboard, Evidence Gallery:** these pages fetch persisted records and evidence from the configured backend/database; refreshing a successful detection updates the views.

### Browser camera requirements

Camera access requires an explicit browser permission. Browsers generally permit `getUserMedia()` only on a secure origin; `http://localhost` and `http://127.0.0.1` are treated as secure local origins. Use one of those addresses rather than opening the site through a LAN IP over plain HTTP. If access was denied, change the site's camera permission in browser settings and reload.

## Configuration

Copy `.env.example` to `.env` for local overrides. Relevant settings include `DATABASE_URL`, `MODEL_PATH`, `MODEL_DEVICE`, `DEFAULT_CONFIDENCE_THRESHOLD`, and `MAX_UPLOAD_SIZE_MB`. Keep `.env` private.

SQLite is the default. For MySQL, provide a complete SQLAlchemy connection string as `DATABASE_URL` and install/configure the matching DB driver. The application applies only additive startup schema updates for its video frame metadata columns; it does not reset or delete existing records.

## API overview

- `GET /api/health`
- `POST /api/detect/image`
- `POST /api/detect/video`
- `GET /api/detect/video/<job_id>/status`
- `GET /api/detect/video/<job_id>/result`
- `POST /api/detect/video/<job_id>/cancel`
- `POST /api/camera/frame`
- `DELETE /api/camera/session/<session_id>`
- `GET /api/events` and `GET /api/events/<event_id>`
- `GET /api/dashboard/summary` and `GET /api/dashboard/trends`
- `GET /api/evidence` and `GET /api/evidence/<evidence_id>/download`

API responses use `success`, `message`, `data`, and `error` fields. A video result is available only after output validation and the event/evidence transaction commits.

## Tests

Activate the project's virtual environment and run:

```powershell
.\venv\Scripts\Activate.ps1
python -m pytest -q
```

Workflow tests use temporary SQLite databases and mock model inference where appropriate. The real-checkpoint regression test is separate and requires the configured checkpoint and bundled test image. The video integration test uses OpenCV's MP4V encoder/decoder; it skips only when that codec is unavailable.

## Troubleshooting

- **Model unavailable:** verify that `models\best.pt` exists or set `MODEL_PATH`. Inspect `/api/health` and the VS Code terminal.
- **Video playback unavailable:** the annotated MP4V output can still be downloaded. Install a local FFmpeg build that includes `libx264` and restart the application to enable optional browser-compatible H.264 conversion. Video status and diagnostic messages are available at `/api/detect/video/<job_id>/status`.
- **No camera preview:** use localhost/127.0.0.1 or HTTPS, allow browser camera permission, and ensure no other application has exclusive access to the device.
- **Events are not visible:** check the startup log for the SQLite path; open Event History to refresh from that database. Do not inspect a different `app.db` file and do not delete the configured database.
- **Upload rejected:** the server enforces `MAX_UPLOAD_SIZE_MB`, file extension checks, and actual image/video decodability.

The in-process video job registry and camera temporal state are intended for local development. A multi-worker or multi-host deployment needs shared job/session storage and a managed worker queue.
