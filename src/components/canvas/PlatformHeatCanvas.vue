<template>
  <div v-if="showPreview" class="w-full h-full bg-white rounded-xl shadow-lg p-6">
    <div class="text-sm text-slate-500">平台热度预览</div>
  </div>
</template>

<script setup>
const props = defineProps({
  platforms: {
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

const generateImage = async () => {
  const canvas = document.createElement('canvas')
  const WIDTH = 1080
  const HEIGHT = 1440
  canvas.width = WIDTH
  canvas.height = HEIGHT
  const ctx = canvas.getContext('2d')
  
  // 1. 背景
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, WIDTH, HEIGHT)
  
  // 2. 顶部标题区域
  const headerY = 80
  const headerHeight = 120
  
  // 绘制柱状图图标背景圆
  ctx.fillStyle = '#dbeafe'
  ctx.beginPath()
  ctx.arc(120, headerY + headerHeight / 2, 50, 0, Math.PI * 2)
  ctx.fill()
  
  // 绘制柱状图 Emoji
  ctx.font = '60px "Apple Color Emoji", "Segoe UI Emoji", sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('📊', 120, headerY + headerHeight / 2)
  
  // 标题文字
  ctx.fillStyle = '#1e293b'
  ctx.font = 'bold 72px "PingFang SC", "Microsoft YaHei", sans-serif'
  ctx.textAlign = 'left'
  ctx.textBaseline = 'middle'
  ctx.fillText('平台热度分布', 200, headerY + headerHeight / 2)
  
  // 3. 平台列表
  const listStartY = headerY + headerHeight + 80
  const platforms = props.platforms.slice(0, 7) // 最多7个平台
  const itemHeight = 140
  const barMaxWidth = WIDTH - 280
  const barHeight = 40
  
  // 颜色列表
  const colors = [
    '#3b82f6', // blue
    '#10b981', // green
    '#a855f7', // purple
    '#f97316', // orange
    '#ec4899', // pink
    '#6366f1', // indigo
    '#ef4444'  // red
  ]
  
  platforms.forEach((platform, index) => {
    const itemY = listStartY + index * itemHeight
    const color = colors[index % colors.length]
    
    // 平台名称
    ctx.fillStyle = '#475569'
    ctx.font = 'bold 48px "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.textAlign = 'left'
    ctx.textBaseline = 'top'
    ctx.fillText(platform.name, 80, itemY)
    
    // 热度数值
    ctx.fillStyle = '#94a3b8'
    ctx.font = '36px "PingFang SC", "Microsoft YaHei", sans-serif'
    ctx.textAlign = 'right'
    ctx.fillText(String(platform.value), WIDTH - 80, itemY)
    
    // 进度条背景
    const barY = itemY + 70
    ctx.fillStyle = '#f1f5f9'
    ctx.fillRect(80, barY, barMaxWidth, barHeight)
    
    // 进度条
    const barWidth = barMaxWidth * (platform.percentage / 100)
    ctx.fillStyle = color
    ctx.fillRect(80, barY, barWidth, barHeight)
  })
  
  // 4. 总结信息
  const summaryY = listStartY + platforms.length * itemHeight + 60
  const totalPlatforms = platforms.length
  const avgHeat = platforms.reduce((sum, p) => sum + p.value, 0) / totalPlatforms
  
  ctx.fillStyle = '#f8fafc'
  ctx.fillRect(80, summaryY, WIDTH - 160, 120)
  
  ctx.fillStyle = '#64748b'
  ctx.font = '36px "PingFang SC", "Microsoft YaHei", sans-serif'
  ctx.textAlign = 'left'
  ctx.fillText(`覆盖 ${totalPlatforms} 个平台`, 120, summaryY + 40)
  ctx.fillText(`平均热度 ${avgHeat.toFixed(1)}`, 120, summaryY + 85)
  
  // 5. 底部水印
  ctx.fillStyle = '#cbd5e1'
  ctx.font = '28px "PingFang SC", "Microsoft YaHei", sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText('@观潮GlobalInSight · AI舆情洞察', WIDTH / 2, HEIGHT - 60)
  
  return canvas.toDataURL('image/png')
}

defineExpose({
  generateImage
})
</script>
