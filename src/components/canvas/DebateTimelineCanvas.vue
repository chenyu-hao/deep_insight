<template>
  <div v-if="showPreview" class="w-full h-full bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl shadow-lg p-6">
    <div class="text-sm text-slate-500">辩论时间线预览</div>
  </div>
</template>

<script setup>
const props = defineProps({
  timeline: {
    type: Array,
    default: () => []
  },
  theme: {
    type: String,
    default: 'default'
  },
  showPreview: {
    type: Boolean,
    default: false
  }
})

// 智能提取核心观点（使用 summary 字段，完整显示）
const extractKeyPoint = (item) => {
  if (item.summary) {
    return item.summary
  }
  const text = item.insight || ''
  const firstSentence = text.match(/^[^。！？.!?]+[。！？.!?]/)
  if (firstSentence) {
    return firstSentence[0]
  }
  return text.substring(0, 30)
}

// 动态计算布局参数
const calculateLayout = (roundCount) => {
  if (roundCount <= 3) {
    return { 
      itemSpacing: 280,      // 🔧 调整这里：每个卡片之间的垂直间距
      cardHeight: 240,       // 🔧 调整这里：卡片高度
      contentFont: 26,
      titleFont: 32
    }
  } else if (roundCount <= 5) {
    return { 
      itemSpacing: 240,      // 🔧 调整这里：4-5轮时的间距
      cardHeight: 200,       // 🔧 调整这里：卡片高度
      contentFont: 24,
      titleFont: 30
    }
  } else if (roundCount <= 7) {
    return { 
      itemSpacing: 200,      // 🔧 调整这里：6-7轮时的间距
      cardHeight: 180,       // 🔧 调整这里：卡片高度
      contentFont: 22,
      titleFont: 28
    }
  } else {
    return { 
      itemSpacing: 170,      // 🔧 调整这里：8轮时的间距
      cardHeight: 160,       // 🔧 调整这里：卡片高度
      contentFont: 20,
      titleFont: 26
    }
  }
}

const generateImage = async () => {
  console.log('[DebateTimelineCanvas] 🎨 开始生成辩论时间线')
  console.log('[DebateTimelineCanvas] 📊 输入数据:', {
    roundCount: props.timeline.length,
    timeline: props.timeline.map(t => ({
      round: t.round,
      title: t.title,
      summaryLength: t.summary?.length || 0
    }))
  })
  
  const canvas = document.createElement('canvas')
  const WIDTH = 1080
  const HEIGHT = 1440
  canvas.width = WIDTH
  canvas.height = HEIGHT
  const ctx = canvas.getContext('2d')
  
  // 动态计算显示的轮数（最多8轮）
  const maxRounds = Math.min(props.timeline.length, 8)
  const timeline = props.timeline.slice(0, maxRounds)
  const layout = calculateLayout(timeline.length)
  
  // 1. 背景 - 浅灰色
  ctx.fillStyle = '#f5f5f5'
  ctx.fillRect(0, 0, WIDTH, HEIGHT)
  
  // 2. 顶部标题区域（与 InsightCanvas/KeyFindingsCanvas 一致）
  const headerY = 80
  const headerHeight = 120
  
  // 绘制图标背景圆
  ctx.fillStyle = '#e9d5ff'  // 紫色系背景
  ctx.beginPath()
  ctx.arc(120, headerY + headerHeight / 2, 50, 0, Math.PI * 2)
  ctx.fill()
  
  // 绘制 Emoji
  ctx.font = '60px "Apple Color Emoji", "Segoe UI Emoji", sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('🔀', 120, headerY + headerHeight / 2)
  
  // 标题文字
  ctx.fillStyle = '#1e293b'
  ctx.font = 'bold 72px "PingFang SC", "Microsoft YaHei", sans-serif'
  ctx.textAlign = 'left'
  ctx.textBaseline = 'middle'
  ctx.fillText('辩论演化过程', 200, headerY + headerHeight / 2)
  
  // 3. 布局计算 - 简化且正确的垂直居中算法
  // 
  // 画布布局：
  // [0-80]        顶部留白
  // [80-200]      标题区域 (headerY=80, headerHeight=120)
  // [200-260]     标题与时间线间距 (60px)
  // [260-1260]    时间线内容区域 (1000px 可用)
  // [1260-1340]   时间线与总结框间距 (80px，包含总结框)
  // [1340-1440]   底部水印区域 (100px)
  
  const PADDING_TOP = 60           // 标题下方间距
  const PADDING_BOTTOM = 60        // 总结框上方间距
  const SUMMARY_BOX_HEIGHT = 100   // 绿色总结框高度
  const WATERMARK_AREA = 80        // 底部水印区域
  
  // 可用于时间线的区域
  const contentAreaTop = headerY + headerHeight + PADDING_TOP
  const contentAreaBottom = HEIGHT - WATERMARK_AREA - SUMMARY_BOX_HEIGHT - PADDING_BOTTOM
  const availableHeight = contentAreaBottom - contentAreaTop
  
  // 计算时间线实际需要的高度
  // 时间线高度 = 第一个圆心到最后一个圆心的距离 + 卡片高度（因为卡片以圆心为中心）
  const timelineHeight = (timeline.length - 1) * layout.itemSpacing + layout.cardHeight
  
  // 计算起始Y（第一个圆心的位置），使时间线在可用区域内垂直居中
  const startY = contentAreaTop + (availableHeight - timelineHeight) / 2 + layout.cardHeight / 2
  
  console.log('[DebateTimelineCanvas] 📐 布局计算:', {
    contentAreaTop,
    contentAreaBottom,
    availableHeight,
    timelineHeight,
    startY,
    rounds: timeline.length
  })
  
  const circleX = 125          // 🔧 调整这里：左侧圆圈的X坐标（增大向右移动）
  const cardX = 200            // 🔧 调整这里：右侧卡片的X坐标
  const cardWidth = WIDTH - cardX - 80
  
  // 绘制每个时间点
  timeline.forEach((item, index) => {
    const itemY = startY + index * layout.itemSpacing
    
    // 虚线连接（在圆圈之间）
    if (index < timeline.length - 1) {
      ctx.strokeStyle = '#60a5fa'
      ctx.lineWidth = 3
      ctx.setLineDash([8, 8])
      ctx.beginPath()
      ctx.moveTo(circleX, itemY + 45)
      ctx.lineTo(circleX, itemY + layout.itemSpacing - 45)
      ctx.stroke()
      ctx.setLineDash([])
    }
    
    // 圆圈
    ctx.fillStyle = '#3b82f6'
    ctx.beginPath()
    ctx.arc(circleX, itemY, 45, 0, Math.PI * 2)
    ctx.fill()
    
    // 轮次文字
    ctx.fillStyle = '#ffffff'
    ctx.font = `bold 40px "PingFang SC", "Microsoft YaHei", sans-serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(`R${item.round}`, circleX, itemY)
    
    // 卡片
    const cardY = itemY - (layout.cardHeight / 2)  // 🔧 使用动态高度，卡片垂直居中对齐圆圈
    const cardHeight = layout.cardHeight           // 🔧 从 layout 获取动态高度
    const cardRadius = 12  // 🔧 调整这里：卡片整体圆角大小
    
    // 卡片背景
    ctx.fillStyle = '#ffffff'
    ctx.beginPath()
    ctx.roundRect(cardX, cardY, cardWidth, cardHeight, cardRadius)
    ctx.fill()
    
    // 左侧蓝色装饰条（只有左侧圆角）
    const barWidth = 8       // 🔧 调整这里：蓝色条的宽度
    const barRadius = 12     // 🔧 调整这里：蓝色条的圆角（应该和 cardRadius 一致）
    ctx.fillStyle = '#3b82f6'
    ctx.beginPath()
    // 使用 roundRect 的四角圆角参数：[左上, 右上, 右下, 左下]
    ctx.roundRect(cardX, cardY, barWidth, cardHeight, [barRadius, 0, 0, barRadius])
    ctx.fill()
    
    // 标题
    ctx.fillStyle = '#1e293b'
    ctx.font = `bold ${layout.titleFont}px "PingFang SC", "Microsoft YaHei", sans-serif`
    ctx.textAlign = 'left'
    ctx.textBaseline = 'top'
    const titleText = item.title.length > 18 ? item.title.substring(0, 18) + '...' : item.title
    ctx.fillText(titleText, cardX + 24, cardY + 20)
    
    // 内容
    ctx.fillStyle = '#64748b'
    ctx.font = `${layout.contentFont}px "PingFang SC", "Microsoft YaHei", sans-serif`
    const keyPoint = extractKeyPoint(item)
    const lines = wrapText(ctx, keyPoint, cardWidth - 48)
    
    lines.slice(0, 3).forEach((line, lineIndex) => {
      ctx.fillText(line, cardX + 24, cardY + 20 + layout.titleFont + 12 + lineIndex * (layout.contentFont + 8))
    })
  })
  
  // 4. 底部总结卡片（固定位置，在水印上方）
  const summaryY = HEIGHT - WATERMARK_AREA - SUMMARY_BOX_HEIGHT
  
  // 总结卡片背景
  ctx.fillStyle = '#d1fae5'
  ctx.beginPath()
  ctx.roundRect(80, summaryY, WIDTH - 160, SUMMARY_BOX_HEIGHT, 16)
  ctx.fill()
  
  // 勾选图标
  ctx.fillStyle = '#059669'
  ctx.font = '48px "Apple Color Emoji", "Segoe UI Emoji", sans-serif'
  ctx.textAlign = 'left'
  ctx.textBaseline = 'middle'
  ctx.fillText('✓', 120, summaryY + 50)
  
  // 总结文字
  ctx.fillStyle = '#065f46'
  ctx.font = 'bold 32px "PingFang SC", "Microsoft YaHei", sans-serif'
  const summaryText = props.timeline.length > maxRounds 
    ? `展示前 ${maxRounds} 轮，共 ${props.timeline.length} 轮辩论收敛`
    : `经过 ${timeline.length} 轮辩论，AI推理最终收敛`
  ctx.fillText(summaryText, 190, summaryY + 50)
  
  // 5. 底部水印
  ctx.fillStyle = '#94a3b8'
  ctx.font = '24px "PingFang SC", "Microsoft YaHei", sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText('@观潮GlobalInSight · AI舆情洞察', WIDTH / 2, HEIGHT - 40)
  
  const dataUrl = canvas.toDataURL('image/png')
  console.log('[DebateTimelineCanvas] ✅ 辩论时间线生成完成，大小:', dataUrl.length, 'bytes')
  return dataUrl
}

// 辅助函数：文本换行
const wrapText = (ctx, text, maxWidth) => {
  const chars = text.split('')
  const lines = []
  let currentLine = ''
  
  for (const char of chars) {
    const testLine = currentLine + char
    const metrics = ctx.measureText(testLine)
    
    if (metrics.width > maxWidth && currentLine.length > 0) {
      lines.push(currentLine)
      currentLine = char
    } else {
      currentLine = testLine
    }
  }
  if (currentLine) lines.push(currentLine)
  return lines
}

defineExpose({
  generateImage
})
</script>
