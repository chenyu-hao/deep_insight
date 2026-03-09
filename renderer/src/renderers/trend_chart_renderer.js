/**
 * Trend Chart renderer – mirrors TrendChartCanvas.vue generateImage()
 *
 * Input: { stage, growth, curve: [7 numbers] }
 *
 * NOTE: Chart.js is NOT available in the Playwright context. We draw the
 * line-chart directly with Canvas 2D API so the renderer stays dependency-free.
 */
import {
  WIDTH, HEIGHT, FONT_FAMILY, EMOJI_FONT,
  createCard, drawHeader, drawWatermark, toPng,
} from './base.js';

export default function renderTrendChart(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');
  const stage = (data && data.stage) || '扩散期';
  const growth = (data && data.growth) ?? 50;
  const curve = (data && data.curve) || [40, 55, 70, 80, 90, 95, 92];

  // 1. White background
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

  // 2. Header
  const headerBottom = drawHeader(ctx, {
    emoji: '📈', title: '热度趋势分析', bgColor: '#dcfce7',
  });

  // 3. Draw line chart manually (replaces Chart.js)
  const chartX = 90;
  const chartY = headerBottom + 80;
  const chartW = 900;
  const chartH = 600;
  const labels = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];

  // Y-axis grid
  ctx.strokeStyle = 'rgba(0,0,0,0.1)';
  ctx.lineWidth = 2;
  for (let pct = 0; pct <= 100; pct += 20) {
    const y = chartY + chartH - (pct / 100) * chartH;
    ctx.beginPath();
    ctx.moveTo(chartX, y);
    ctx.lineTo(chartX + chartW, y);
    ctx.stroke();
    // label
    ctx.fillStyle = '#64748b';
    ctx.font = `24px ${FONT_FAMILY}`;
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${pct}%`, chartX - 10, y);
  }

  // X labels
  const stepX = chartW / (labels.length - 1);
  labels.forEach((lbl, i) => {
    const x = chartX + i * stepX;
    ctx.fillStyle = '#1e293b';
    ctx.font = `bold 24px ${FONT_FAMILY}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText(lbl, x, chartY + chartH + 12);
  });

  // Fill area
  ctx.beginPath();
  curve.forEach((v, i) => {
    const x = chartX + i * stepX;
    const y = chartY + chartH - (v / 100) * chartH;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.lineTo(chartX + (curve.length - 1) * stepX, chartY + chartH);
  ctx.lineTo(chartX, chartY + chartH);
  ctx.closePath();
  ctx.fillStyle = 'rgba(59,130,246,0.1)';
  ctx.fill();

  // Line
  ctx.beginPath();
  curve.forEach((v, i) => {
    const x = chartX + i * stepX;
    const y = chartY + chartH - (v / 100) * chartH;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = '#3b82f6';
  ctx.lineWidth = 4;
  ctx.stroke();

  // Points
  curve.forEach((v, i) => {
    const x = chartX + i * stepX;
    const y = chartY + chartH - (v / 100) * chartH;
    ctx.beginPath(); ctx.arc(x, y, 8, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff'; ctx.fill();
    ctx.strokeStyle = '#3b82f6'; ctx.lineWidth = 4; ctx.stroke();
    ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fillStyle = '#3b82f6'; ctx.fill();
  });

  // 4. Stage labels
  const stageY = chartY + chartH + 80;
  const stageW = WIDTH / 3;
  const stages = [
    { label: '爆发期', desc: '快速上升', color: '#10b981' },
    { label: '扩散期', desc: '持续增长', color: '#3b82f6' },
    { label: '回落期', desc: '逐渐降温', color: '#f97316' },
  ];
  stages.forEach((s, i) => {
    const x = 80 + i * stageW;
    ctx.fillStyle = s.color;
    ctx.font = `bold 40px ${FONT_FAMILY}`;
    ctx.textAlign = 'left';
    ctx.fillText(s.label, x, stageY);
    ctx.fillStyle = '#64748b';
    ctx.font = `32px ${FONT_FAMILY}`;
    ctx.fillText(s.desc, x, stageY + 50);
  });

  // 5. Status card
  const statusY = stageY + 140;
  ctx.fillStyle = '#f8fafc';
  ctx.fillRect(80, statusY, WIDTH - 160, 140);

  const stageColor = stage === '爆发期' ? '#10b981' : stage === '扩散期' ? '#3b82f6' : '#f97316';
  ctx.fillStyle = stageColor;
  ctx.beginPath(); ctx.arc(140, statusY + 70, 15, 0, Math.PI * 2); ctx.fill();

  ctx.fillStyle = '#475569';
  ctx.font = `36px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.fillText('当前阶段：', 180, statusY + 50);
  ctx.fillStyle = '#1e293b';
  ctx.font = `bold 40px ${FONT_FAMILY}`;
  ctx.fillText(stage, 180, statusY + 100);

  const growthColor = growth > 100 ? '#10b981' : growth > 0 ? '#3b82f6' : '#ef4444';
  ctx.fillStyle = '#475569';
  ctx.font = `36px ${FONT_FAMILY}`;
  ctx.textAlign = 'right';
  ctx.fillText('增速：', WIDTH - 280, statusY + 75);
  ctx.fillStyle = growthColor;
  ctx.font = `bold 44px ${FONT_FAMILY}`;
  ctx.fillText(growth > 0 ? `+${growth}%` : `${growth}%`, WIDTH - 100, statusY + 75);

  // 6. Watermark
  drawWatermark(ctx, '* 基于语义分析的热度推演模型');

  return toPng(canvas);
}
