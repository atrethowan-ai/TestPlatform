
# Quiz Local Service (Unified Server)

## What is this?
A unified Python FastAPI backend for the kids_learning_system. It now:
- Serves the built quiz frontend UI
- Handles all API endpoints under `/api`
- Stores quiz attempts to disk
- Forms the foundation for a future LAN/local server

## Why does it exist?
- Enables running the entire platform with a single command
- No CORS or separate dev servers needed
- Lays the foundation for future local/LAN features (analysis, TTS, media, admin, etc.)
- Keeps the system local-first and privacy-friendly

## Endpoints

All API endpoints are now under `/api`:

### GET /api/health
Returns `{ "status": "ok" }` to confirm the service is running.

### POST /api/attempts
Accepts a JSON payload representing a quiz attempt. Writes the attempt to disk under `quiz_pipeline/work/attempts/<childId>/`.

Payload example:
```
{
  "attemptId": "abc123",
  "childId": "test-user",
  "quizId": "math_v1",
  "completedAt": "2026-03-12T10:00:00Z",
  "responses": { ... },
  "score": { ... },
  "metadata": { ... }
}
```

### GET /api/attempts/{child_id}
Lists all attempts for a given child. Returns filename, attemptId, quizId, completedAt for each.

## Static Frontend Serving

- The server serves the built quiz frontend from `apps/quiz_shell/dist/`.
- Open [http://127.0.0.1:8000](http://127.0.0.1:8000) to use the quiz UI.
- All frontend routes are handled (SPA catch-all).

## Where are files saved?
Attempts are saved under:
```
quiz_pipeline/work/attempts/<childId>/<completedAt>__<quizId>__<attemptId>.json
```


## How to run
1. Build the frontend:
   ```
   cd kids_learning_system/apps/quiz_shell
   npm install
   npm run build
   ```
2. Activate your Python environment
3. Install FastAPI and uvicorn if needed:
   ```
   pip install fastapi uvicorn pydantic
   ```
4. Run the service in LOCAL mode (default, only accessible from this computer):
   ```
   python -m quiz_pipeline.cli.main run-local-service
   ```
   or
   ```
   run_local_service.bat
   ```
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

5. Run the service in LAN mode (accessible from other devices on your local network):
   ```
   python -m quiz_pipeline.cli.main run-local-service --lan
   ```
   or
   ```
   run_local_service_lan.bat
   ```
   The server will print your LAN IP address. On another device (phone, tablet, laptop) connected to the same WiFi/network, open:
   ```
   http://<YOUR_LAN_IP>:8000
   ```

### Security Note

**This server is intended for LAN use only. Do NOT expose it to the internet via router port forwarding.**
LAN mode binds to all local interfaces and is discoverable by any device on your local network.

## How the TS app uses it
The TypeScript quiz runtime now POSTs attempt JSON to `/api/attempts` after quiz completion.

## Why this is the foundation
This unified server is the first step toward a richer, LAN-hosted system for local learning, analysis, and media generation. It is intentionally simple and file-based for now, but is designed to be extended.
