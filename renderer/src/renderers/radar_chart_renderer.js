/**
 * Radar Chart renderer
 *
 * Input: { labels: [str], datasets: [{ data: [number] }] }
 */
import {
  WIDTH, FONT_FAMILY,
  createCard, drawAppleBackdrop, drawAmbientOrbs,
  drawHeader, drawPanel, drawSectionLabel, drawWatermark, toPng,
} from './base.js';

const ACCENT = '#0a84ff';
const PALETTE = ['#0a84ff', '#5e5ce6', '#30d158', '#ff9f0a', '#ff453a', '#64d2ff'];

function normalizeInput(data) {
  const labelsRaw = Array.isArray(data && data.labels) ? data.labels : [];
  const labels = labelsRaw
    .map((item) => String(item || '').trim())
    .filter(Boolean)
    .slice(0, 6);

  const valuesRaw = (((data && data.datasets) || [])[0] || {}).data;
  const values = Array.isArray(valuesRaw)
    ? valuesRaw.map((v) => Number(v)).map((v) => (Number.isFinite(v) ? Math.max(0, Math.min(100, v)) : 0))
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

export default function renderRadarChart(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');

  const { labels, values } = normalizeInput(data);
  const maxVal = 100;
  const n = labels.length;

  drawAppleBackdrop(ctx, {
    start: '#f8f9fc',
    end: '#edf1f7',
    topLight: '#ffffff',
    bottomTint: '#dbeafe',
    textureAlpha: 0.012,
  });
  drawAmbientOrbs(ctx, [
    { x: 210, y: 280, r: 240, color: '#dbeafe', alpha: 0.2 },
    { x: 920, y: 1120, r: 300, color: '#c7d2fe', alpha: 0.14 },
  ]);

  const headerBottom = drawHeader(ctx, {
    emoji: '📡',
    title: '平台覆盖分布',
    bgColor: '#dbeafe',
    textColor: '#0f172a',
  });

  const shellY = headerBottom + 44;
  drawPanel(ctx, 56, shellY, WIDTH - 112, 782, {
    radius: 34,
    fill: 'rgba(255,255,255,0.66)',
    stroke: 'rgba(255,255,255,0.88)',
    shadow: 'rgba(15, 23, 42, 0.06)',
    shadowBlur: 24,
    shadowY: 10,
  });
  drawSectionLabel(ctx, '平台结构', 100, shellY + 34, ACCENT);

  const cx = WIDTH / 2;
  const cy = shellY + 405;
  const maxR = 326;
  const rings = 5;

  const point = (idx, value) => {
    const angle = (Math.PI * 2 * idx) / n - Math.PI / 2;
    const radius = (value / maxVal) * maxR;
    return {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
    };
  };

  for (let ring = 1; ring <= rings; ring++) {
    const radius = (ring / rings) * maxR;
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.24)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    for (let i = 0; i <= n; i++) {
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
      const x = cx + radius * Math.cos(angle);
      const y = cy + radius * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();

    const tick = point(0, ring * 20);
    ctx.fillStyle = 'rgba(100,116,139,0.86)';
    ctx.font = `500 20px ${FONT_FAMILY}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.fillText(`${ring * 20}`, tick.x, tick.y - 4);
  }

  for (let i = 0; i < n; i++) {
    const edge = point(i, maxVal);
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.22)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(edge.x, edge.y);
    ctx.stroke();
  }

  const poly = new Path2D();
  values.forEach((value, i) => {
    const p = point(i, value);
    if (i === 0) poly.moveTo(p.x, p.y);
    else poly.lineTo(p.x, p.y);
  });
  poly.closePath();

  const area = ctx.createRadialGradient(cx, cy, 50, cx, cy, maxR);
  area.addColorStop(0, 'rgba(10,132,255,0.34)');
  area.addColorStop(1, 'rgba(10,132,255,0.06)');
  ctx.fillStyle = area;
  ctx.fill(poly);

  ctx.strokeStyle = ACCENT;
  ctx.lineWidth = 3;
  ctx.stroke(poly);

  values.forEach((value, i) => {
    const p = point(i, value);
    ctx.fillStyle = PALETTE[i % PALETTE.length];
    ctx.beginPath();
    ctx.arc(p.x, p.y, 7, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2.5;
    ctx.stroke();
  });

  labels.forEach((label, i) => {
    const edge = point(i, maxVal + 11);
    ctx.fillStyle = '#0f172a';
    ctx.font = `620 25px ${FONT_FAMILY}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, edge.x, edge.y);
  });

  const legendY = cy + maxR + 88;
  const colW = (WIDTH - 160) / 3;
  labels.forEach((label, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 84 + col * colW;
    const y = legendY + row * 84;

    ctx.fillStyle = PALETTE[i % PALETTE.length];
    ctx.beginPath();
    ctx.arc(x + 10, y - 8, 8, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#475569';
    ctx.font = `530 26px ${FONT_FAMILY}`;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    ctx.fillText(label, x + 24, y);

    const valueText = `${values[i] || 0}`;
    const nameW = ctx.measureText(label).width;
    ctx.fillStyle = '#0f172a';
    ctx.font = `700 31px ${FONT_FAMILY}`;
    ctx.fillText(valueText, x + 24 + nameW + 18, y);
  });

  drawWatermark(ctx, '* 数值基于各平台内容规模归一化');
  return toPng(canvas);
}
