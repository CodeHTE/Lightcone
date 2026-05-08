---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100a8047d5c0ebf22aeb813b45ccc1c387bd30a9628cb710a6f07d75dc6bfdd631a022100d110513d8ad951043fb2cfef5b829337fcfa926bcdbe6b4fbca7618f7bc97de1
    ReservedCode2: 3045022100d370233c891ecc546d3cf6cdd0a348e490cfe35564536106d5ed78efcb371f1702202318b425cf2c5d35f3ff4e0fc4a18b1260386324abda811fa6f124b8aba774ca
---

# Collaborative Canvas - Real-time Collaboration Board

A real-time collaborative canvas application built with Flask and Socket.IO, allowing multiple users to work together on a shared whiteboard.

## Features

- **Real-time Collaboration**: Multiple users can edit the canvas simultaneously
- **User Presence**: See who else is online and their cursor positions
- **Card System**: Create, move, resize, and edit cards
- **Connection Lines**: Draw connections between cards
- **Media Support**: Paste URLs to embed images or videos (B站, 抖音, etc.)
- **Auto-sync**: Changes are automatically synced to all connected users
- **Export/Import**: Save and load canvas state as JSON

## Deployment to Render

### Option 1: Using render.yaml (Recommended)

1. Push this project to GitHub
2. Create a new Web Service on [Render](https://render.com)
3. Connect your GitHub repository
4. Use the following settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python wsgi.py`
   - **Environment Variables**: Add `SECRET_KEY` with a random value

### Option 2: Manual Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables:
   ```bash
   export SECRET_KEY="your-secret-key"
   export PORT=5000
   ```
4. Run: `python wsgi.py`

## Local Development

```bash
cd collaborative-canvas
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000/canvas` in your browser.

## Tech Stack

- **Backend**: Flask + Flask-SocketIO
- **Database**: SQLite (file-based, for simplicity)
- **Frontend**: Vanilla JavaScript + Socket.IO client
- **Real-time**: WebSocket via Socket.IO
- **Deployment**: Render (supports WebSocket natively)

## WebSocket Support

This application uses WebSocket for real-time communication. Render's free tier supports WebSocket connections, so no additional configuration is needed.

## Notes

- The SQLite database (`canvas_data.db`) is created automatically on first run
- For production with high traffic, consider migrating to PostgreSQL
- The current implementation uses polling + WebSocket for connection stability