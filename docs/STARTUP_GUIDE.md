# GlobalInSight 启动指南总览

本文档提供 GlobalInSight 项目在不同操作系统上的启动方式说明。

## 📋 快速导航

- **macOS 用户** → [QUICK_START.md](QUICK_START.md)
- **Windows 用户** → [QUICK_START_WINDOWS.md](QUICK_START_WINDOWS.md)
- **脚本说明** → [scripts/README.md](scripts/README.md)

## 🚀 一键启动

### macOS
```bash
# 方法 1: 双击启动
# 在 Finder 中双击 start.command 文件

# 方法 2: 终端启动
./start.sh
```

### Windows
```cmd
# 方法 1: 双击启动
# 在文件资源管理器中双击 start.bat 文件

# 方法 2: 命令行启动
start.bat
```

## 📁 启动文件结构

```
GlobalInSight/
├── start.sh                    # macOS/Linux 主启动脚本
├── start.command               # macOS 双击启动入口
├── start.bat                   # Windows 主启动脚本
├── QUICK_START.md             # macOS 快速启动指南
├── QUICK_START_WINDOWS.md     # Windows 快速启动指南
├── STARTUP_GUIDE.md           # 本文件
└── scripts/                   # 各服务启动脚本
    ├── README.md              # 脚本说明文档
    ├── start-xhs-mcp.sh       # 小红书 MCP (macOS)
    ├── start-xhs-mcp.bat      # 小红书 MCP (Windows)
    ├── start-opinion-mcp.sh   # Opinion MCP (macOS)
    ├── start-opinion-mcp.bat  # Opinion MCP (Windows)
    ├── start-backend.sh       # 后端服务 (macOS)
    ├── start-backend.bat      # 后端服务 (Windows)
    ├── start-frontend.sh      # 前端服务 (macOS)
    └── start-frontend.bat     # 前端服务 (Windows)
```

## 🎯 启动流程

主启动脚本会自动完成以下步骤：

1. ✅ **环境检查**
   - Python 3.9+ 
   - Node.js 16+

2. ✅ **依赖安装**
   - Python 虚拟环境
   - Python 包 (requirements.txt)
   - Node.js 包 (package.json)
   - Playwright 浏览器

3. ✅ **服务配置**
   - 环境变量 (.env)
   - 小红书 MCP 下载
   - 小红书登录（可选）

4. ✅ **服务启动**
   - 小红书 MCP (端口 18060)
   - 后端 API (端口 8000)
   - 前端开发服务器 (端口 5173)
   - Opinion MCP (端口 18061, 可选)

## 🔧 环境要求

### 必需
- **Python**: 3.9+ (推荐 3.10 或 3.11)
- **Node.js**: 16+ (推荐 18+)

### 可选
- **Git**: 用于克隆和更新代码
- **curl**: 用于下载 MCP 服务（Windows 10+ 自带）

## 📝 首次使用配置

### 1. 配置 API Keys

启动后访问 http://localhost:5173，进入"设置"页面：

- 添加至少一个 LLM 提供商的 API Key
- 支持：Moonshot、DeepSeek、Doubao、Gemini、Zhipu
- 配置火山引擎密钥（用于图片生成）

**注意**: 也可以直接编辑 `.env` 文件配置。

### 2. 登录小红书（可选）

如果需要使用小红书发布功能：

**macOS:**
```bash
cd external/XHS-MCP/xiaohongshu-mcp-darwin-arm64  # M1/M2/M3
# 或
cd external/XHS-MCP/xiaohongshu-mcp-darwin-amd64  # Intel

./xiaohongshu-login-darwin-arm64  # 或 darwin-amd64
```

**Windows:**
```cmd
cd external\XHS-MCP\xiaohongshu-mcp-windows-amd64
xiaohongshu-login-windows-amd64.exe
```

## 🛠️ 手动启动服务

如果需要单独启动某个服务，参见 [scripts/README.md](scripts/README.md)。

## ❓ 常见问题

### Q: 如何停止所有服务？
A: 在每个终端/命令行窗口中按 `Ctrl+C`，或直接关闭窗口。

### Q: 端口被占用怎么办？
A: 
**macOS/Linux:**
```bash
lsof -i :8000      # 查看端口占用
kill -9 <PID>      # 关闭进程
```

**Windows:**
```cmd
netstat -ano | findstr :8000  # 查看端口占用
taskkill /F /PID <PID>        # 关闭进程
```

### Q: 依赖安装失败？
A: 
1. 确保网络连接正常
2. 清理缓存后重新运行：

**macOS/Linux:**
```bash
rm -rf .venv node_modules
./start.sh
```

**Windows:**
```cmd
rmdir /s /q .venv
rmdir /s /q node_modules
start.bat
```

### Q: 脚本无法执行 (macOS)?
A: 
```bash
# 添加执行权限
chmod +x start.sh start.command
chmod +x scripts/*.sh
```

### Q: Windows 执行策略错误？
A: 以管理员身份运行 PowerShell：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🎯 启动后的下一步

1. 访问 http://localhost:5173
2. 进入"设置"页面配置 API Keys
3. 测试小红书 MCP 连接
4. 在"首页"输入议题开始分析
5. 查看"热榜页"浏览热点数据
6. 在"数据页"查看可视化分析

## 📚 相关文档

- [完整 README](../README.md)
- [小红书 MCP 设置指南](XHS_SETUP.md)
- [API 使用文档](../frontend/src/API_USAGE.md)
- [项目文档](project/)
- [系统架构](project/)

## 🆘 获取帮助

如果遇到问题：

1. 查看终端/命令行窗口的日志输出
2. 检查 [常见问题](#-常见问题) 部分
3. 查阅对应平台的快速启动指南
4. 查看项目 Issues 或提交新 Issue

---

**提示**: 建议首次使用时仔细阅读对应平台的快速启动指南，了解详细的配置和使用说明。
