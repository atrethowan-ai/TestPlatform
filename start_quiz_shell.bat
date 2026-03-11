@echo off
REM Start Vite dev server for quiz_shell and open browser to quiz app
cd kids_learning_system
start "Vite Dev Server" cmd /k npm run --workspace apps/quiz_shell dev
REM Wait a moment for server to start
ping 127.0.0.1 -n 3 > nul
start http://localhost:5173/
