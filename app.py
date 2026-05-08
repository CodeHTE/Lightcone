import sqlite3
import os
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'collaborative-canvas-secret-key-2024')

# Configure Socket.IO for production
socketio = SocketIO(
    app,
    async_mode='threading',
    cors_allowed_origins='*',
    ping_timeout=60,
    ping_interval=25
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'canvas_data.db')

# Active users tracking
active_users = {}  # {sid: {user_id, username, color}}

# ---------- 数据库初始化 ----------
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id TEXT PRIMARY KEY,
            x REAL,
            y REAL,
            width REAL,
            height REAL,
            content TEXT,
            last_modified TEXT,
            last_editor TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            id TEXT PRIMARY KEY,
            fromCardId TEXT,
            fromSide TEXT,
            toCardId TEXT,
            toSide TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 启动时初始化表
init_db()

# ---------- 数据加载与持久化 ----------
def load_cards():
    conn = get_db()
    rows = conn.execute('SELECT * FROM cards').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def load_connections():
    conn = get_db()
    rows = conn.execute('SELECT * FROM connections').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_card(card):
    conn = get_db()
    conn.execute('''
        INSERT OR REPLACE INTO cards (id, x, y, width, height, content, last_modified, last_editor)
        VALUES (?,?,?,?,?,?,?,?)
    ''', (card['id'], card['x'], card['y'], card['width'], card['height'],
          card['content'], card['last_modified'], card.get('last_editor', 'unknown')))
    conn.commit()
    conn.close()

def delete_card_from_db(card_id):
    conn = get_db()
    conn.execute('DELETE FROM cards WHERE id = ?', (card_id,))
    conn.execute('DELETE FROM connections WHERE fromCardId = ? OR toCardId = ?', (card_id, card_id))
    conn.commit()
    conn.close()

def save_connection(conn_data):
    conn = get_db()
    conn.execute('''
        INSERT OR REPLACE INTO connections (id, fromCardId, fromSide, toCardId, toSide)
        VALUES (?,?,?,?,?)
    ''', (conn_data['id'], conn_data['fromCardId'], conn_data['fromSide'],
          conn_data['toCardId'], conn_data['toSide']))
    conn.commit()
    conn.close()

def delete_connection_from_db(conn_id):
    conn = get_db()
    conn.execute('DELETE FROM connections WHERE id = ?', (conn_id,))
    conn.commit()
    conn.close()

# ---------- 路由 ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/canvas')
def canvas():
    return render_template('canvas.html')

@app.route('/canvas.html')
def canvas_html():
    return render_template('canvas.html')

# ---------- SocketIO 事件 ----------
@socketio.on('connect')
def handle_connect():
    print(f'客户端连接: {request.sid if "request" in dir() else "unknown"}')

@socketio.on('join_canvas')
def handle_join_canvas(data):
    """用户加入画布"""
    user_id = data.get('user_id', f'user-{request.sid}')
    username = data.get('username', f'用户{user_id[:6]}')
    color = data.get('color', '#4a6fa5')

    active_users[request.sid] = {
        'user_id': user_id,
        'username': username,
        'color': color,
        'cursor': {'x': 0, 'y': 0}
    }

    # 广播用户加入
    emit('user_joined', {
        'user_id': user_id,
        'username': username,
        'color': color,
        'active_users': list(active_users.values())
    }, broadcast=True)

    # 发送当前画布数据
    cards = load_cards()
    connections = load_connections()
    emit('canvas_data', {
        'cards': cards,
        'connections': connections,
        'active_users': list(active_users.values())
    })

@socketio.on('cursor_move')
def handle_cursor_move(data):
    """实时光标位置同步"""
    if request.sid in active_users:
        active_users[request.sid]['cursor'] = {
            'x': data.get('x', 0),
            'y': data.get('y', 0)
        }
        # 广播光标位置给其他用户
        emit('cursor_update', {
            'user_id': active_users[request.sid]['user_id'],
            'username': active_users[request.sid]['username'],
            'color': active_users[request.sid]['color'],
            'x': data.get('x', 0),
            'y': data.get('y', 0)
        }, broadcast=True, include_self=False)

@socketio.on('card_update')
def handle_card_update(data):
    """实时卡片更新（无冲突检测，轻量同步）"""
    card = data.get('card')
    if not card:
        return

    # 立即保存到数据库
    save_card(card)

    # 广播给其他用户
    emit('card_updated', {
        'card': card,
        'editor': active_users.get(request.sid, {}).get('user_id', 'unknown')
    }, broadcast=True, include_self=False)

@socketio.on('card_created')
def handle_card_created(data):
    """新卡片创建"""
    card = data.get('card')
    if card:
        save_card(card)
        emit('card_created', {
            'card': card,
            'creator': active_users.get(request.sid, {}).get('user_id', 'unknown')
        }, broadcast=True, include_self=False)

@socketio.on('card_deleted')
def handle_card_deleted(data):
    """卡片删除"""
    card_id = data.get('card_id')
    if card_id:
        delete_card_from_db(card_id)
        emit('card_deleted', {
            'card_id': card_id,
            'deleted_by': active_users.get(request.sid, {}).get('user_id', 'unknown')
        }, broadcast=True, include_self=False)

@socketio.on('connection_created')
def handle_connection_created(data):
    """连线创建"""
    conn_data = data.get('connection')
    if conn_data:
        save_connection(conn_data)
        emit('connection_created', {
            'connection': conn_data
        }, broadcast=True, include_self=False)

@socketio.on('connection_deleted')
def handle_connection_deleted(data):
    """连线删除"""
    conn_id = data.get('connection_id')
    if conn_id:
        delete_connection_from_db(conn_id)
        emit('connection_deleted', {
            'connection_id': conn_id
        }, broadcast=True, include_self=False)

@socketio.on('disconnect')
def handle_disconnect():
    """用户断开连接"""
    if request.sid in active_users:
        user_info = active_users[request.sid]
        del active_users[request.sid]

        emit('user_left', {
            'user_id': user_info['user_id'],
            'username': user_info['username'],
            'active_users': list(active_users.values())
        }, broadcast=True)

@socketio.on('sync_request')
def handle_sync_request():
    """手动同步请求"""
    cards = load_cards()
    connections = load_connections()
    emit('sync_response', {
        'cards': cards,
        'connections': connections,
        'active_users': list(active_users.values())
    })

@socketio.on('load_canvas')
def handle_load_canvas():
    """兼容旧客户端"""
    cards = load_cards()
    connections = load_connections()
    emit('canvas_data', {
        'cards': cards,
        'connections': connections,
        'active_users': list(active_users.values())
    })

@socketio.on('sync_changes')
def handle_sync_changes(data):
    """兼容旧客户端的同步方式"""
    user_id = data.get('user_id', 'unknown')
    client_cards = data.get('cards', [])
    client_connections = data.get('connections', [])
    conflicts = []
    now_utc = datetime.now(timezone.utc)

    # 处理卡片
    for client_card in client_cards:
        card_id = client_card['id']
        existing = None
        conn = get_db()
        row = conn.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
        if row:
            existing = dict(row)
        conn.close()

        if existing is None:
            # 新卡片
            new_card = {
                'id': card_id,
                'x': client_card.get('x', 0),
                'y': client_card.get('y', 0),
                'width': client_card.get('width', 300),
                'height': client_card.get('height', 200),
                'content': client_card.get('content', ''),
                'last_modified': now_utc.isoformat(),
                'last_editor': user_id
            }
            save_card(new_card)
        else:
            # 更新
            existing['x'] = client_card.get('x', existing.get('x', 0))
            existing['y'] = client_card.get('y', existing.get('y', 0))
            existing['width'] = client_card.get('width', existing.get('width', 300))
            existing['height'] = client_card.get('height', existing.get('height', 200))
            existing['content'] = client_card.get('content', existing.get('content', ''))
            existing['last_modified'] = now_utc.isoformat()
            existing['last_editor'] = user_id
            save_card(existing)

    # 同步连线
    conn = get_db()
    conn.execute('DELETE FROM connections')
    conn.commit()
    conn.close()
    for cn in client_connections:
        save_connection(cn)

    cards = load_cards()
    connections = load_connections()
    emit('sync_result', {
        'success': True,
        'conflicts': conflicts,
        'cards': cards,
        'connections': connections
    })

# 需要导入 request
from flask import request

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)