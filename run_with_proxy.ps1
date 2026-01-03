#!/usr/bin/env powershell
"""
带代理启动后端服务
"""

# 设置代理环境变量
$env:HTTP_PROXY = "http://127.0.0.1:7897"
$env:HTTPS_PROXY = "http://127.0.0.1:7897"

Write-Host "已设置代理: 127.0.0.1:7897" -ForegroundColor Green
Write-Host "启动后端服务..." -ForegroundColor Cyan

# 启动后端
python -m app.main
