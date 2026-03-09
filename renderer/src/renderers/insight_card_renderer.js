/**
 * Insight Card renderer – mirrors InsightCanvas.vue generateImage()
 *
 * Input: { conclusion, coverage: { platforms, debateRounds, growth, controversy } }
 */
import {
  WIDTH, HEIGHT, FONT_FAMILY, EMOJI_FONT,
  createCard, drawGradientBg, drawHeader, drawWatermark, wrapText, toPng,
} from './base.js';

function formatControversy(c) {
  if (typeof c === 'number') return `${c.toFixed(1)}/10`;
  return c || '未知';
}

function getControversyColor(c) {
  if (typeof c === 'number') return c > 7 ? '#ef4444' : c > 4 ? '#f97316' : '#10b981';
  return c === '高' ? '#ef4444' : c === '中' ? '#f97316' : '#10b981';
}

export default function renderInsightCard(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');

  const conclusion = (data && data.conclusion) || '暂无洞察';
  const coverage = (data && data.coverage) || {};

  // 1. Background
  drawGradientBg(ctx, '#ffffff', '#eff6ff');

  // 2. Header
  const headerBottom = drawHeader(ctx, {
    emoji: '💡', title: '核心洞察', bgColor: '#dbeafe',
  });

  // 3. Conclusion text
  const conclusionY = headerBottom + 60;
  const maxW = WIDTH - 160;
  ctx.fillStyle = '#475569';
  ctx.font = `48px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
  const lines = wrapText(ctx, conclusion, maxW);
  const lineH = 72;
  lines.forEach((line, i) => ctx.fillText(line, 80, conclusionY + i * lineH));

  // 4. Data overview
  const dataY = conclusionY + lines.length * lineH + 80;
  const dataH = 280;

  ctx.fillStyle = '#f8fafc';
  ctx.fillRect(80, dataY, WIDTH - 160, dataH);

  ctx.fillStyle = '#64748b';
  ctx.font = `bold 40px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.fillText('数据概览', 120, dataY + 60);

  const gridY = dataY + 120;
  const gridW = (WIDTH - 160) / 2;
  const items = [
    { label: '话题覆盖', value: `${coverage.platforms || 0}个平台`, color: '#3b82f6' },
    { label: '辩论轮次', value: `${coverage.debateRounds || 0}轮推演`, color: '#a855f7' },
    { label: '生命周期', value: coverage.growth || '未知', color: '#10b981' },
    { label: '争议程度', value: formatControversy(coverage.controversy), color: getControversyColor(coverage.controversy) },
  ];
  items.forEach((item, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 120 + col * gridW;
    const y = gridY + row * 80;
    ctx.fillStyle = '#94a3b8';
    ctx.font = `32px ${FONT_FAMILY}`;
    ctx.textAlign = 'left';
    ctx.fillText(item.label, x, y);
    ctx.fillStyle = item.color;
    ctx.font = `bold 52px ${FONT_FAMILY}`;
    ctx.fillText(item.value, x, y + 50);
  });

  // 5. Watermark
  drawWatermark(ctx, '* 核心洞察由 Multi-Agent 协作分析生成');

  return toPng(canvas);
}
