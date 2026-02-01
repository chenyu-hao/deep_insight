# 启动脚本说明

本目录包含 GlobalInSight 项目的各个服务启动脚本。

## 📁 文件结构

```
scripts/
├── README.md                    # 本文件
├── start-xhs-mcp.sh            # 小红书 MCP 服务 (macOS/Linux)
├── start-xhs-mcp.bat           # 小红书 MCP 服务 (Windows)
├── start-opinion-mcp.sh        # Opinion MCP 服务 (macOS/Linux)
├── start-opinion-mcp.bat       # Opinion MCP 服务 (Windows)
├── start-backend.sh            # 后端 API 服务 (macOS/Linux)
├── start-backend.bat           # 后端 API 服务 (Windows)
├── start-frontend.sh           # 前端开发服务器 (macOS/Linux)
└── start-frontend.bat          # 前端开发服务器 (Windows)
```

## 🚀 使用方法

### 推荐方式：使用主启动脚本

**macOS/Linux:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

主启动脚本会自动：
- 检查环境依赖
- 安装必要的包
- 在新窗口中启动所有服务

### 手动启动单个服务

如果需要单独启动某个服务：

**macOS/Linux:**
```bash
./scripts/start-xhs-mcp.sh      # 小红书 MCP
./scripts/start-backend.sh      # 后端 API
./scripts/start-frontend.sh     # 前端
./scripts/start-opinion-mcp.sh  # Opinion MCP (可选)
```

**Windows:**
```cmd
scripts\start-xhs-mcp.bat      # 小红书 MCP
scripts\start-backend.bat      # 后端 API
scripts\start-frontend.bat     # 前端
scripts\start-opinion-mcp.bat  # Opinion MCP (可选)
```

## 📋 服务说明

### 1. 小红书 MCP 服务 (端口 18060)
- 提供小红书内容发布功能
- 首次使用需要扫码登录
- 验证: `curl http://localhost:18060/mcp`

### 2. 后端 API 服务 (端口 8000)
- FastAPI 后端服务
- API 文档: http://localhost:8000/docs
- 需要配置 `.env` 文件中的 API Keys

### 3. 前端开发服务器 (端口 5173)
- Vue 3 + Vite 开发服务器
- 访问: http://localhost:5173
- 支持热重载

### 4. Opinion MCP 服务 (端口 18061) - 可选
- 用于 ClawdBot 集成
- 健康检查: http://localhost:18061/health
- 详见 README.md 中的 ClawdBot 配置说明

## ⚠️ 注意事项

1. **首次运行**: 请使用主启动脚本，它会自动完成环境配置
2. **依赖检查**: 手动启动前确保已安装所有依赖
3. **端口占用**: 确保相应端口未被占用
4. **停止服务**: 在终端/命令行窗口中按 `Ctrl+C`

## 🔧 故障排除

### 脚本无法执行 (macOS/Linux)
```bash
chmod +x scripts/*.sh
```

### 端口被占用
**macOS/Linux:**
```bash
lsof -i :8000  # 查看端口占用
kill -9 <PID>  # 关闭进程
```

**Windows:**
```cmd
netstat -ano | findstr :8000  # 查看端口占用
taskkill /F /PID <PID>        # 关闭进程
```

### 虚拟环境问题 (Windows)
如果遇到执行策略错误，以管理员身份运行 PowerShell：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📚 更多信息

- [快速启动指南 (macOS)](../QUICK_START.md)
- [快速启动指南 (Windows)](../QUICK_START_WINDOWS.md)
- [完整 README](../README.md)
