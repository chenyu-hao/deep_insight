/**
 * Trend Chart renderer
 *
 * Input: { stage, growth, curve: [numbers] }
 */
import {
  WIDTH, FONT_FAMILY,
  createCard, drawStudioBackdrop, drawShowcaseHeader, drawGlassPanel,
  drawFloatingLabel, drawWatermark, withAlpha, toPng,
} from './base.js';

const ACCENT = '#0a84ff';

function normalizeCurve(curve) {
  const values = Array.isArray(curve) ? curve : [];
  const safe = values
    .map((v) => Number(v))
    .filter((v) => Number.isFinite(v))
    .map((v) => Math.max(0, Math.min(100, v)));
  if (safe.length >= 2) return safe.slice(0, 10);
  return [48, 58, 68, 96, 95, 93, 92];
}

function stageColor(stage) {
  if (stage === '爆发期') return '#30d158';
  if (stage === '回落期') return '#ff9f0a';
  return ACCENT;
}

function stageDescription(stage) {
  if (stage === '爆发期') return '信号快速抬升';
  if (stage === '回落期') return '热度开始降温';
  return '仍在外扩传播';
}

function drawSmoothPath(ctx, points) {
  if (!points.length) return;
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (let i = 1; i < points.length - 1; i += 1) {
    const midX = (points[i].x + points[i + 1].x) / 2;
    const midY = (points[i].y + points[i + 1].y) / 2;
    ctx.quadraticCurveTo(points[i].x, points[i].y, midX, midY);
  }
  const last = points[points.length - 1];
  ctx.quadraticCurveTo(last.x, last.y, last.x, last.y);
}

function drawAreaPath(ctx, points, baseline) {
  if (!points.length) return;
  ctx.beginPath();
  ctx.moveTo(points[0].x, baseline);
  ctx.lineTo(points[0].x, points[0].y);
  for (let i = 1; i < points.length - 1; i += 1) {
    const midX = (points[i].x + points[i + 1].x) / 2;
    const midY = (points[i].y + points[i + 1].y) / 2;
    ctx.quadraticCurveTo(points[i].x, points[i].y, midX, midY);
  }
  const last = points[points.length - 1];
  ctx.quadraticCurveTo(last.x, last.y, last.x, last.y);
  ctx.lineTo(last.x, baseline);
  ctx.closePath();
}

function drawLegendChip(ctx, x, y, item) {
  drawGlassPanel(ctx, x, y, 286, 76, {
    radius: 24,
    accent: item.color,
    fillTop: 'rgba(255,255,255,0.88)',
    fillBottom: 'rgba(248,250,255,0.72)',
    shadow: 'rgba(15,23,42,0.035)',
    shadowBlur: 12,
    shadowY: 5,
  });

  ctx.fillStyle = item.color;
  ctx.beginPath();
  ctx.arc(x + 28, y + 38, 8, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = '#0f172a';
  ctx.font = `640 26px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(item.label, x + 46, y + 34);

  ctx.fillStyle = 'rgba(100,116,139,0.9)';
  ctx.font = `500 22px ${FONT_FAMILY}`;
  ctx.fillText(item.desc, x + 46, y + 60);
}

function drawTrendGlyph(ctx, { x, y, size, accent }) {
  const points = [
    { x: x + 22, y: y + size - 28 },
    { x: x + 42, y: y + size - 48 },
    { x: x + 58, y: y + size - 40 },
    { x: x + 82, y: y + 30 },
  ];

  ctx.save();
  ctx.strokeStyle = withAlpha(accent, 0.24);
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  ctx.moveTo(x + 18, y + 18);
  ctx.lineTo(x + 18, y + size - 18);
  ctx.lineTo(x + size - 18, y + size - 18);
  ctx.stroke();

  ctx.strokeStyle = accent;
  ctx.lineWidth = 4;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.beginPath();
  points.forEach((point, idx) => {
    if (idx === 0) ctx.moveTo(point.x, point.y);
    else ctx.lineTo(point.x, point.y);
  });
  ctx.stroke();

  points.forEach((point, idx) => {
    ctx.fillStyle = idx === points.length - 1 ? accent : '#ffffff';
    ctx.beginPath();
    ctx.arc(point.x, point.y, idx === points.length - 1 ? 6 : 4.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = accent;
    ctx.lineWidth = 2;
    ctx.stroke();
  });
  ctx.restore();
}

export default function renderTrendChart(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');

  const stage = (data && data.stage) || '扩散期';
  const growth = Number((data && data.growth) ?? 50);
  const curve = normalizeCurve(data && data.curve);
  const labels = curve.map((_, i) => `T${i + 1}`);
  const growthColor = growth > 100 ? '#30d158' : growth > 0 ? ACCENT : '#ff453a';
  const growthText = growth > 0 ? `+${growth}%` : `${growth}%`;
  const peak = Math.max(...curve);
  const peakIndex = curve.indexOf(peak);

  drawStudioBackdrop(ctx, {
    start: '#f7f8fb',
    end: '#eceff5',
    primary: '#8fd0ff',
    secondary: '#9eafff',
  });

  const headerBottom = drawShowcaseHeader(ctx, {
    title: '热度趋势分析',
    kicker: 'Trend Intelligence',
    accent: ACCENT,
    glow: '#d8ecff',
    iconRenderer: drawTrendGlyph,
  });

  const shellY = headerBottom + 34;
  const shellH = 1018;
  drawGlassPanel(ctx, 48, shellY, WIDTH - 96, shellH, {
    radius: 40,
    accent: '#d9ecff',
    fillTop: 'rgba(255,255,255,0.9)',
    fillBottom: 'rgba(243,247,255,0.74)',
    shadow: 'rgba(15, 23, 42, 0.06)',
    shadowBlur: 26,
    shadowY: 10,
  });

  drawFloatingLabel(ctx, '热度信号', 88, shellY + 34, {
    accent: ACCENT,
    fillAlpha: 0.08,
    strokeAlpha: 0.14,
    height: 42,
  });

  ctx.fillStyle = 'rgba(100,116,139,0.88)';
  ctx.font = `520 21px ${FONT_FAMILY}`;
  ctx.textAlign = 'right';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(`PEAK ${peak}`, WIDTH - 92, shellY + 68);

  const chartX = 86;
  const chartY = shellY + 106;
  const chartW = WIDTH - 172;
  const chartH = 560;
  drawGlassPanel(ctx, chartX, chartY, chartW, chartH, {
    radius: 32,
    accent: '#d6e9ff',
    fillTop: 'rgba(252,254,255,0.9)',
    fillBottom: 'rgba(240,246,255,0.78)',
    shadow: 'rgba(15,23,42,0.03)',
    shadowBlur: 14,
    shadowY: 6,
  });

  ctx.save();
  ctx.beginPath();
  ctx.roundRect(chartX, chartY, chartW, chartH, 32);
  ctx.clip();
  const chartGlow = ctx.createRadialGradient(chartX + chartW * 0.64, chartY + 80, 40, chartX + chartW * 0.64, chartY + 80, 360);
  chartGlow.addColorStop(0, withAlpha(ACCENT, 0.14));
  chartGlow.addColorStop(1, withAlpha(ACCENT, 0));
  ctx.fillStyle = chartGlow;
  ctx.fillRect(chartX, chartY, chartW, chartH);
  ctx.restore();

  const plotX = chartX + 56;
  const plotY = chartY + 76;
  const plotW = chartW - 96;
  const plotH = 400;
  const baseline = plotY + plotH;
  const stepX = plotW / (curve.length - 1);

  for (let pct = 0; pct <= 100; pct += 20) {
    const y = baseline - (pct / 100) * plotH;
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.18)';
    ctx.lineWidth = pct === 100 ? 1.4 : 1;
    ctx.beginPath();
    ctx.moveTo(plotX, y);
    ctx.lineTo(plotX + plotW, y);
    ctx.stroke();

    ctx.fillStyle = 'rgba(100,116,139,0.8)';
    ctx.font = `520 20px ${FONT_FAMILY}`;
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${pct}%`, plotX - 14, y);
  }

  const points = curve.map((value, i) => ({
    x: plotX + i * stepX,
    y: baseline - (value / 100) * plotH,
    value,
  }));

  labels.forEach((label, i) => {
    ctx.fillStyle = 'rgba(51,65,85,0.92)';
    ctx.font = `620 21px ${FONT_FAMILY}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText(label, plotX + i * stepX, baseline + 18);
  });

  drawAreaPath(ctx, points, baseline);
  const area = ctx.createLinearGradient(0, plotY, 0, baseline);
  area.addColorStop(0, 'rgba(10,132,255,0.24)');
  area.addColorStop(0.72, 'rgba(10,132,255,0.08)');
  area.addColorStop(1, 'rgba(10,132,255,0.02)');
  ctx.fillStyle = area;
  ctx.fill();

  drawSmoothPath(ctx, points);
  const stroke = ctx.createLinearGradient(plotX, plotY, plotX + plotW, baseline);
  stroke.addColorStop(0, '#55b5ff');
  stroke.addColorStop(0.42, ACCENT);
  stroke.addColorStop(1, '#246bff');
  ctx.strokeStyle = stroke;
  ctx.lineWidth = 5;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.stroke();

  points.forEach((point, i) => {
    if (i === peakIndex) {
      const halo = ctx.createRadialGradient(point.x, point.y, 10, point.x, point.y, 42);
      halo.addColorStop(0, 'rgba(10,132,255,0.24)');
      halo.addColorStop(1, 'rgba(10,132,255,0)');
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(point.x, point.y, 42, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(point.x, point.y, i === peakIndex ? 9 : 7, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = i === peakIndex ? '#246bff' : ACCENT;
    ctx.lineWidth = i === peakIndex ? 4 : 3;
    ctx.stroke();
  });

  const metricY = chartY + chartH + 30;
  const leftW = 454;
  const rightW = WIDTH - 96 - 56 - leftW - 28;

  drawGlassPanel(ctx, 88, metricY, leftW, 146, {
    radius: 30,
    accent: stageColor(stage),
    fillTop: 'rgba(255,255,255,0.88)',
    fillBottom: 'rgba(249,250,255,0.72)',
    shadow: 'rgba(15,23,42,0.04)',
    shadowBlur: 14,
    shadowY: 6,
  });

  ctx.fillStyle = stageColor(stage);
  ctx.beginPath();
  ctx.arc(126, metricY + 46, 10, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = 'rgba(100,116,139,0.9)';
  ctx.font = `560 24px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText('当前阶段', 148, metricY + 54);

  ctx.fillStyle = '#0f172a';
  ctx.font = `700 46px ${FONT_FAMILY}`;
  ctx.fillText(stage, 120, metricY + 110);

  ctx.fillStyle = 'rgba(100,116,139,0.92)';
  ctx.font = `500 24px ${FONT_FAMILY}`;
  ctx.fillText(stageDescription(stage), 282, metricY + 110);

  drawGlassPanel(ctx, 88 + leftW + 28, metricY, rightW, 146, {
    radius: 30,
    accent: ACCENT,
    fillTop: 'rgba(255,255,255,0.88)',
    fillBottom: 'rgba(245,249,255,0.72)',
    shadow: 'rgba(15,23,42,0.04)',
    shadowBlur: 14,
    shadowY: 6,
  });

  ctx.fillStyle = 'rgba(100,116,139,0.9)';
  ctx.font = `560 24px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.fillText('趋势增速', 88 + leftW + 60, metricY + 54);

  ctx.fillStyle = growthColor;
  ctx.font = `700 64px ${FONT_FAMILY}`;
  ctx.fillText(growthText, 88 + leftW + 60, metricY + 118);

  const legendY = metricY + 174;
  const stageItems = [
    { label: '爆发期', desc: '快速抬升', color: '#30d158' },
    { label: '扩散期', desc: '持续外扩', color: ACCENT },
    { label: '回落期', desc: '逐步降温', color: '#ff9f0a' },
  ];
  stageItems.forEach((item, i) => {
    drawLegendChip(ctx, 88 + i * 302, legendY, item);
  });

  drawWatermark(ctx, '* 基于语义分析与时序热度推演模型');
  return toPng(canvas);
}
