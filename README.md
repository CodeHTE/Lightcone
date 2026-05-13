---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3044022078c193b598f56ecb0bbd24e9c42a622d067361aa568bacb6a5b46b4945d55a1d0220611af417dd7fdd1e917da8e294fbce70282e7fec29d473b87103dac54bbdfdf8
    ReservedCode2: 3045022100c9e745cac3d28c3e50bdf455f324fddaaf10a83addcc9a95950f043d4743c5e802206baca5ef770d6e0f3ac9e45b398f7301664b482fb086500c959551cdacc05105
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