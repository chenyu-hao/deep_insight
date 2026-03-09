/**
 * Trend Chart renderer
 *
 * Input: { stage, growth, curve: [numbers] }
 */
import {
  WIDTH, FONT_FAMILY,
  createCard, drawAppleBackdrop, drawAmbientOrbs,
  drawHeader, drawPanel, drawSectionLabel, drawWatermark, toPng,
} from './base.js';

const ACCENT = '#0a84ff';

function normalizeCurve(curve) {
  const values = Array.isArray(curve) ? curve : [];
  const safe = values
    .map((v) => Number(v))
    .filter((v) => Number.isFinite(v))
    .map((v) => Math.max(0, Math.min(100, v)));
  if (safe.length >= 2) return safe.slice(0, 10);
  return [40, 55, 70, 80, 90, 95, 92];
}

function stageColor(stage) {
  if (stage === '爆发期') return '#30d158';
  if (stage === '回落期') return '#ff9f0a';
  return ACCENT;
}

export default function renderTrendChart(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');

  const stage = (data && data.stage) || '扩散期';
  const growth = Number((data && data.growth) ?? 50);
  const curve = normalizeCurve(data && data.curve);
  const labels = curve.map((_, i) => `T${i + 1}`);

  drawAppleBackdrop(ctx, {
    start: '#f8f9fc',
    end: '#edf1f7',
    topLight: '#ffffff',
    bottomTint: '#dbeafe',
    textureAlpha: 0.012,
  });
  drawAmbientOrbs(ctx, [
    { x: 220, y: 260, r: 240, color: '#dbeafe', alpha: 0.2 },
    { x: 910, y: 1180, r: 320, color: '#c7d2fe', alpha: 0.14 },
  ]);

  const headerBottom = drawHeader(ctx, {
    emoji: '📈',
    title: '热度趋势分析',
    bgColor: '#dbeafe',
    textColor: '#0f172a',
  });

  const shellY = headerBottom + 44;
  drawPanel(ctx, 56, shellY, WIDTH - 112, 738, {
    radius: 34,
    fill: 'rgba(255,255,255,0.66)',
    stroke: 'rgba(255,255,255,0.88)',
    shadow: 'rgba(15, 23, 42, 0.06)',
    shadowBlur: 24,
    shadowY: 10,
  });
  drawSectionLabel(ctx, '热度曲线', 100, shellY + 34, ACCENT);

  const chartX = 120;
  const chartY = shellY + 118;
  const chartW = 840;
  const chartH = 520;
  const stepX = chartW / (curve.length - 1);

  ctx.strokeStyle = 'rgba(148, 163, 184, 0.24)';
  ctx.lineWidth = 1.5;
  for (let pct = 0; pct <= 100; pct += 20) {
    const y = chartY + chartH - (pct / 100) * chartH;
    ctx.beginPath();
    ctx.moveTo(chartX, y);
    ctx.lineTo(chartX + chartW, y);
    ctx.stroke();

    ctx.fillStyle = 'rgba(100,116,139,0.9)';
    ctx.font = `520 23px ${FONT_FAMILY}`;
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${pct}%`, chartX - 12, y);
  }

  labels.forEach((label, i) => {
    const x = chartX + i * stepX;
    ctx.fillStyle = '#334155';
    ctx.font = `620 23px ${FONT_FAMILY}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText(label, x, chartY + chartH + 14);
  });

  const areaGradient = ctx.createLinearGradient(0, chartY, 0, chartY + chartH);
  areaGradient.addColorStop(0, 'rgba(10,132,255,0.28)');
  areaGradient.addColorStop(1, 'rgba(10,132,255,0.03)');

  ctx.beginPath();
  curve.forEach((value, i) => {
    const x = chartX + i * stepX;
    const y = chartY + chartH - (value / 100) * chartH;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.lineTo(chartX + (curve.length - 1) * stepX, chartY + chartH);
  ctx.lineTo(chartX, chartY + chartH);
  ctx.closePath();
  ctx.fillStyle = areaGradient;
  ctx.fill();

  ctx.beginPath();
  curve.forEach((value, i) => {
    const x = chartX + i * stepX;
    const y = chartY + chartH - (value / 100) * chartH;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = ACCENT;
  ctx.lineWidth = 4;
  ctx.stroke();

  curve.forEach((value, i) => {
    const x = chartX + i * stepX;
    const y = chartY + chartH - (value / 100) * chartH;
    ctx.beginPath();
    ctx.arc(x, y, 7, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff';
    ctx.fill();
    ctx.strokeStyle = ACCENT;
    ctx.lineWidth = 3;
    ctx.stroke();
  });

  const stageY = shellY + 768;
  drawPanel(ctx, 80, stageY, WIDTH - 160, 124, {
    radius: 24,
    fill: 'rgba(255,255,255,0.6)',
    stroke: 'rgba(255,255,255,0.86)',
    shadow: 'rgba(15, 23, 42, 0.04)',
    shadowBlur: 14,
    shadowY: 6,
  });

  const currentColor = stageColor(stage);
  ctx.fillStyle = currentColor;
  ctx.beginPath();
  ctx.arc(132, stageY + 62, 13, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = '#475569';
  ctx.font = `560 34px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText('当前阶段', 160, stageY + 44);

  ctx.fillStyle = '#0f172a';
  ctx.font = `700 44px ${FONT_FAMILY}`;
  ctx.fillText(stage, 160, stageY + 84);

  const growthLabel = Number.isFinite(growth) ? growth : 0;
  const growthColor = growthLabel > 100 ? '#30d158' : growthLabel > 0 ? ACCENT : '#ff453a';
  const growthText = growthLabel > 0 ? `+${growthLabel}%` : `${growthLabel}%`;

  ctx.fillStyle = '#64748b';
  ctx.font = `560 32px ${FONT_FAMILY}`;
  ctx.textAlign = 'right';
  ctx.fillText('增速', WIDTH - 250, stageY + 48);

  ctx.fillStyle = growthColor;
  ctx.font = `700 46px ${FONT_FAMILY}`;
  ctx.fillText(growthText, WIDTH - 116, stageY + 86);

  const legendY = stageY + 152;
  const stageItems = [
    { label: '爆发期', desc: '快速上升', color: '#30d158' },
    { label: '扩散期', desc: '持续增长', color: ACCENT },
    { label: '回落期', desc: '热度降温', color: '#ff9f0a' },
  ];
  const colWidth = (WIDTH - 160) / 3;
  stageItems.forEach((item, i) => {
    const x = 82 + i * colWidth;
    ctx.fillStyle = item.color;
    ctx.beginPath();
    ctx.arc(x + 10, legendY + 8, 8, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#334155';
    ctx.font = `620 29px ${FONT_FAMILY}`;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    ctx.fillText(item.label, x + 26, legendY + 16);

    ctx.fillStyle = '#64748b';
    ctx.font = `500 24px ${FONT_FAMILY}`;
    ctx.fillText(item.desc, x + 26, legendY + 52);
  });

  drawWatermark(ctx, '* 基于语义分析与时序热度推演模型');

  return toPng(canvas);
}
