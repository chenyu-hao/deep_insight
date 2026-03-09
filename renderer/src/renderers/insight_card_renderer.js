/**
 * Insight Card renderer – mirrors InsightCanvas.vue generateImage()
 *
 * Input: { conclusion, coverage: { platforms, debateRounds, growth, controversy } }
 */
import {
  WIDTH, FONT_FAMILY,
  createCard, drawAppleBackdrop, drawAmbientOrbs,
  drawHeader, drawPanel, drawSectionLabel, drawStatChip, drawWatermark,
  wrapText, clampLines, withAlpha, toPng,
} from './base.js';

function formatControversy(c) {
  if (typeof c === 'number') return `${c.toFixed(1)}/10`;
  return c || '未知';
}

function getControversyColor(c) {
  if (typeof c === 'number') return c > 7 ? '#ff453a' : c > 4 ? '#ff9f0a' : '#30d158';
  return c === '高' ? '#ff453a' : c === '中' ? '#ff9f0a' : '#30d158';
}

export default function renderInsightCard(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');

  const conclusion = (data && data.conclusion) || '暂无洞察';
  const coverage = (data && data.coverage) || {};

  drawAppleBackdrop(ctx, {
    start: '#f8f9fc',
    end: '#edf1f7',
    topLight: '#ffffff',
    bottomTint: '#dbeafe',
    textureAlpha: 0.013,
  });
  drawAmbientOrbs(ctx, [
    { x: 190, y: 220, r: 240, color: '#c7d2fe', alpha: 0.2 },
    { x: 940, y: 1220, r: 320, color: '#bfdbfe', alpha: 0.16 },
  ]);

  const headerBottom = drawHeader(ctx, {
    emoji: '💡',
    title: '核心洞察',
    bgColor: '#dbeafe',
    textColor: '#0f172a',
  });

  const heroY = headerBottom + 42;
  const heroH = 442;
  drawPanel(ctx, 70, heroY, WIDTH - 140, heroH, {
    radius: 36,
    fill: 'rgba(255,255,255,0.67)',
    stroke: 'rgba(255,255,255,0.88)',
    shadow: 'rgba(15, 23, 42, 0.07)',
    shadowBlur: 24,
    shadowY: 10,
  });
  drawSectionLabel(ctx, '核心判断', 112, heroY + 42, '#0a84ff');

  const maxW = WIDTH - 244;
  ctx.fillStyle = '#0f172a';
  ctx.font = `620 54px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
  const lines = clampLines(wrapText(ctx, conclusion, maxW), 4);
  const lineH = 80;
  lines.forEach((line, i) => {
    ctx.fillText(line, 112, heroY + 142 + i * lineH);
  });

  ctx.strokeStyle = 'rgba(148, 163, 184, 0.2)';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(112, heroY + heroH - 88);
  ctx.lineTo(WIDTH - 112, heroY + heroH - 88);
  ctx.stroke();
  ctx.fillStyle = 'rgba(71, 85, 105, 0.84)';
  ctx.font = `500 25px ${FONT_FAMILY}`;
  ctx.fillText('从多平台样本与辩论推演中提炼的关键结论', 112, heroY + heroH - 42);

  const dataY = heroY + heroH + 40;
  drawSectionLabel(ctx, '分析维度', 82, dataY + 16, '#0a84ff');

  const gridY = dataY + 72;
  const gridW = (WIDTH - 190) / 2;
  const chipW = gridW - 22;
  const chipH = 164;
  drawPanel(ctx, 60, dataY + 2, WIDTH - 120, 420, {
    radius: 32,
    fill: withAlpha('#ffffff', 0.28),
    stroke: withAlpha('#ffffff', 0.5),
    shadow: 'rgba(15, 23, 42, 0)',
    shadowBlur: 0,
    shadowY: 0,
    lineWidth: 1,
  });

  const items = [
    { label: '话题覆盖', value: `${coverage.platforms || 0}个平台`, color: '#0a84ff' },
    { label: '辩论轮次', value: `${coverage.debateRounds || 0}轮推演`, color: '#5e5ce6' },
    { label: '生命周期', value: coverage.growth || '未知', color: '#30d158' },
    { label: '争议程度', value: formatControversy(coverage.controversy), color: getControversyColor(coverage.controversy) },
  ];
  items.forEach((item, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 82 + col * gridW;
    const y = gridY + row * (chipH + 24);
    drawStatChip(ctx, {
      x,
      y,
      w: chipW,
      h: chipH,
      label: item.label,
      value: item.value,
      accent: item.color,
      valueColor: item.color,
    });
  });

  drawWatermark(ctx, '* 核心洞察由 Multi-Agent 协作分析生成');

  return toPng(canvas);
}
