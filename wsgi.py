socketio.run(
    app,
    host='0.0.0.0',
    port=port,
    allow_unsafe_werkzeug=True  # 新增这行
)