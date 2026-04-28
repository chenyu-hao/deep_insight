#!/bin/bash

# 卡片渲染服务启动脚本

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  卡片渲染服务 (Express + Playwright)${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

cd renderer/ || {
    echo -e "${RED}错误: renderer/ 目录不存在${NC}"
    exit 1
}

# 安装依赖（如 node_modules 不存在）
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}安装 npm 依赖...${NC}"
    npm install
    echo ""
fi

# 始终确保 Playwright Chromium 存在（覆盖缓存被清的场景）
echo -e "${YELLOW}检查 Playwright Chromium...${NC}"
npx playwright install chromium 2>&1 | grep -v "^$"
echo ""

# 每次启动都重新 build，防止代码更新后跑旧 dist
echo -e "${YELLOW}构建渲染包...${NC}"
npm run build
echo ""

echo -e "${GREEN}启动渲染服务 (端口 3001)...${NC}"
if [ -z "${TITLE_CARD_STYLE}" ]; then
    export TITLE_CARD_STYLE=apple
fi
echo "Title 卡样式: ${TITLE_CARD_STYLE}"
echo ""
exec node server.js
