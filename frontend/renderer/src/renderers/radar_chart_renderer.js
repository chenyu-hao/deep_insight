/**
 * Radar Chart renderer
 *
 * Input: { labels: [str], datasets: [{ data: [number] }] }
 */
import {
  WIDTH, FONT_FAMILY,
  createCard, drawStudioBackdrop, drawShowcaseHeader, drawGlassPanel,
  drawFloatingLabel, drawWatermark, withAlpha, toPng,
} from './base.js';

const ACCENT = '#0a84ff';
const PALETTE = ['#0a84ff', '#635bff', '#34c759', '#ff9f0a', '#ff453a', '#64d2ff'];

function normalizeInput(data) {
  const labelsRaw = Array.isArray(data && data.labels) ? data.labels : [];
  const labels = labelsRaw
    .map((item) => String(item || '').trim())
    .filter(Boolean)
    .slice(0, 6);

  const valuesRaw = (((data && data.datasets) || [])[0] || {}).data;
  const values = Array.isArray(valuesRaw)
    ? valuesRaw
      .map((v) => Number(v))
      .map((v) => (Number.isFinite(v) ? Math.max(0, Math.min(100, v)) : 0))
    : [];

  if (labels.length < 3 || values.length < labels.length) {
    return {
      labels: ['微博', '知乎', '抖音', 'B站', '小红书', 'Reddit'],
      values: [92, 76, 81, 69, 88, 64],
    };
  }

  return {
    labels,
    values: values.slice(0, labels.length),
  };
}

function drawMetricCard(ctx, x, y, label, value, accent) {
  drawGlassPanel(ctx, x, y, 198, 92, {
    radius: 24,
    accent,
    fillTop: 'rgba(255,255,255,0.88)',
    fillBottom: 'rgba(246,249,255,0.72)',
    shadow: 'rgba(15,23,42,0.03)',
    shadowBlur: 12,
    shadowY: 5,
  });

  ctx.fillStyle = 'rgba(100,116,139,0.9)';
  ctx.font = `560 21px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(label, x + 22, y + 34);

  ctx.fillStyle = '#0f172a';
  ctx.font = `700 38px ${FONT_FAMILY}`;
  ctx.fillText(String(value), x + 22, y + 74);
}

function drawPlatformCard(ctx, x, y, item) {
  drawGlassPanel(ctx, x, y, 286, 86, {
    radius: 24,
    accent: item.color,
    fillTop: 'rgba(255,255,255,0.88)',
    fillBottom: 'rgba(247,250,255,0.74)',
    shadow: 'rgba(15,23,42,0.035)',
    shadowBlur: 12,
    shadowY: 5,
  });

  ctx.fillStyle = item.color;
  ctx.beginPath();
  ctx.arc(x + 28, y + 43, 8, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = '#0f172a';
  ctx.font = `640 25px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(item.label, x + 46, y + 38);

  ctx.fillStyle = 'rgba(100,116,139,0.9)';
  ctx.font = `520 20px ${FONT_FAMILY}`;
  ctx.fillText('覆盖指数', x + 46, y + 64);

  ctx.fillStyle = '#0f172a';
  ctx.font = `700 32px ${FONT_FAMILY}`;
  ctx.textAlign = 'right';
  ctx.fillText(String(item.value), x + 250, y + 52);
}

function drawRadarGlyph(ctx, { x, y, size, accent }) {
  const cx = x + size / 2;
  const cy = y + size / 2;
  const radius = 32;
  const corners = [0, 1, 2].map((idx) => {
    const angle = (Math.PI * 2 * idx) / 3 - Math.PI / 2;
    return {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
    };
  });

  ctx.save();
  ctx.strokeStyle = withAlpha(accent, 0.22);
  ctx.lineWidth = 2;
  [0.45, 0.72, 1].forEach((ratio) => {
    ctx.beginPath();
    corners.forEach((corner, idx) => {
      const px = cx + (corner.x - cx) * ratio;
      const py = cy + (corner.y - cy) * ratio;
      if (idx === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    });
    ctx.closePath();
    ctx.stroke();
  });

  ctx.strokeStyle = accent;
  ctx.lineWidth = 3.2;
  ctx.beginPath();
  corners.forEach((corner, idx) => {
    if (idx === 0) ctx.moveTo(corner.x, corner.y);
    else ctx.lineTo(corner.x, corner.y);
  });
  ctx.closePath();
  ctx.stroke();

  corners.forEach((corner) => {
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(corner.x, corner.y, 4.8, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = accent;
    ctx.lineWidth = 2;
    ctx.stroke();
  });
  ctx.restore();
}

export default function renderRadarChart(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');

  const { labels, values } = normalizeInput(data);
  const n = labels.length;
  const maxVal = 100;
  const maxValue = Math.max(...values);
  const avgValue = Math.round(values.reduce((sum, value) => sum + value, 0) / values.length);

  drawStudioBackdrop(ctx, {
    start: '#f7f8fb',
    end: '#eceff5',
    primary: '#8fd0ff',
    secondary: '#98a2ff',
  });

  const headerBottom = drawShowcaseHeader(ctx, {
    title: '平台覆盖分布',
    kicker: 'Platform Landscape',
    accent: ACCENT,
    glow: '#d8ecff',
    iconRenderer: drawRadarGlyph,
  });

  const shellY = headerBottom + 34;
  const shellH = 1022;
  drawGlassPanel(ctx, 48, shellY, WIDTH - 96, shellH, {
    radius: 40,
    accent: '#d9ecff',
    fillTop: 'rgba(255,255,255,0.9)',
    fillBottom: 'rgba(243,247,255,0.74)',
    shadow: 'rgba(15,23,42,0.06)',
    shadowBlur: 26,
    shadowY: 10,
  });

  drawFloatingLabel(ctx, '平台结构', 88, shellY + 34, {
    accent: ACCENT,
    fillAlpha: 0.08,
    strokeAlpha: 0.14,
    height: 42,
  });

  const metricY = shellY + 34;
  drawMetricCard(ctx, WIDTH - 92 - 198 * 2 - 18, metricY, '平台数', n, '#8fd0ff');
  drawMetricCard(ctx, WIDTH - 92 - 198, metricY, '峰值覆盖', maxValue, '#d8ecff');

  const chartX = 88;
  const chartY = shellY + 112;
  const chartW = WIDTH - 176;
  const chartH = 560;
  drawGlassPanel(ctx, chartX, chartY, chartW, chartH, {
    radius: 32,
    accent: '#d8ecff',
    fillTop: 'rgba(252,254,255,0.9)',
    fillBottom: 'rgba(241,246,255,0.78)',
    shadow: 'rgba(15,23,42,0.03)',
    shadowBlur: 14,
    shadowY: 6,
  });

  const cx = WIDTH / 2;
  const cy = chartY + 300;
  const maxR = 248;
  const rings = 5;

  const point = (idx, value) => {
    const angle = (Math.PI * 2 * idx) / n - Math.PI / 2;
    const radius = (value / maxVal) * maxR;
    return {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
      angle,
    };
  };

  ctx.save();
  const focus = ctx.createRadialGradient(cx, cy, 40, cx, cy, 320);
  focus.addColorStop(0, 'rgba(10,132,255,0.12)');
  focus.addColorStop(1, 'rgba(10,132,255,0)');
  ctx.fillStyle = focus;
  ctx.beginPath();
  ctx.arc(cx, cy, 320, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  for (let ring = 1; ring <= rings; ring += 1) {
    const radius = (ring / rings) * maxR;
    ctx.strokeStyle = ring === rings ? 'rgba(148,163,184,0.22)' : 'rgba(148,163,184,0.14)';
    ctx.lineWidth = ring === rings ? 1.4 : 1;
    ctx.beginPath();
    for (let i = 0; i <= n; i += 1) {
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
      const x = cx + radius * Math.cos(angle);
      const y = cy + radius * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();

    ctx.fillStyle = 'rgba(100,116,139,0.72)';
    ctx.font = `500 18px ${FONT_FAMILY}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.fillText(`${ring * 20}`, cx, cy - radius - 6);
  }

  for (let i = 0; i < n; i += 1) {
    const edge = point(i, maxVal);
    ctx.strokeStyle = 'rgba(148,163,184,0.12)';
    ctx.lineWidth = 1.1;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(edge.x, edge.y);
    ctx.stroke();
  }

  const polygon = new Path2D();
  values.forEach((value, i) => {
    const p = point(i, value);
    if (i === 0) polygon.moveTo(p.x, p.y);
    else polygon.lineTo(p.x, p.y);
  });
  polygon.closePath();

  const fill = ctx.createRadialGradient(cx, cy, 50, cx, cy, maxR);
  fill.addColorStop(0, 'rgba(10,132,255,0.3)');
  fill.addColorStop(0.68, 'rgba(10,132,255,0.13)');
  fill.addColorStop(1, 'rgba(10,132,255,0.04)');
  ctx.fillStyle = fill;
  ctx.fill(polygon);

  const stroke = ctx.createLinearGradient(cx - maxR, cy - maxR, cx + maxR, cy + maxR);
  stroke.addColorStop(0, '#64d2ff');
  stroke.addColorStop(0.5, ACCENT);
  stroke.addColorStop(1, '#635bff');
  ctx.strokeStyle = stroke;
  ctx.lineWidth = 4;
  ctx.stroke(polygon);

  values.forEach((value, i) => {
    const p = point(i, value);
    const halo = ctx.createRadialGradient(p.x, p.y, 4, p.x, p.y, 22);
    halo.addColorStop(0, withAlpha(PALETTE[i % PALETTE.length], 0.28));
    halo.addColorStop(1, withAlpha(PALETTE[i % PALETTE.length], 0));
    ctx.fillStyle = halo;
    ctx.beginPath();
    ctx.arc(p.x, p.y, 22, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = PALETTE[i % PALETTE.length];
    ctx.beginPath();
    ctx.arc(p.x, p.y, 7, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2.5;
    ctx.stroke();
  });

  labels.forEach((label, i) => {
    const edge = point(i, maxVal + 13);
    const outer = maxR + 36;
    const labelX = cx + outer * Math.cos(edge.angle);
    const labelY = cy + outer * Math.sin(edge.angle);

    ctx.fillStyle = '#0f172a';
    ctx.font = `620 24px ${FONT_FAMILY}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, labelX, labelY - 10);

    ctx.fillStyle = 'rgba(100,116,139,0.86)';
    ctx.font = `560 18px ${FONT_FAMILY}`;
    ctx.fillText(String(values[i]), labelX, labelY + 16);
  });

  const statY = chartY + chartH + 26;
  drawMetricCard(ctx, 88, statY, '平均覆盖', avgValue, '#d8ecff');
  drawMetricCard(ctx, 88 + 216, statY, '最高平台', labels[values.indexOf(maxValue)] || '-', '#8fd0ff');

  const legendY = statY + 120;
  labels.forEach((label, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    drawPlatformCard(ctx, 88 + col * 302, legendY + row * 98, {
      label,
      value: values[i] || 0,
      color: PALETTE[i % PALETTE.length],
    });
  });

  drawWatermark(ctx, '* 数值基于各平台内容规模归一化');
  return toPng(canvas);
}
