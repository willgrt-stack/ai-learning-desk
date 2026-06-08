#!/bin/bash
# AI学习桌 - 一键启动后端服务
cd "$(dirname "$0")/backend"
echo "🚀 启动 AI学习桌 后端服务..."
nohup python3 main.py > /tmp/ai_learning_server.log 2>&1 &
PID=$!
sleep 2
echo "✅ 服务已启动，PID: $PID"
echo "   访问地址: http://localhost:8765"
echo "   API 文档: http://localhost:8765/docs"
echo ""
echo "   要停止服务，运行: kill $PID"
