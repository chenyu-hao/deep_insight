/**
 * Radar Chart renderer – mirrors RadarChartCanvas.vue generateImage()
 *
 * Input: { labels: [str], datasets: [{ data: [number] }] }
 *
 * Chart.js is NOT available – we draw the radar with Canvas 2D API.
 */
import {
  WIDTH, HEIGHT, FONT_FAMILY,
  createCard, drawGradientBg, drawHeader, drawWatermark, toPng,
} from './base.js';

const PALETTE = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function renderRadarChart(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');

  const labels = (data && data.labels) || [];
  const values = (data && data.datasets && data.datasets[0] && data.datasets[0].data) || [];
  const maxVal = 100;

  // 1. Background
  drawGradientBg(ctx, '#ffffff', '#eff6ff');

  // 2. Header
  const headerBottom = drawHeader(ctx, {
    emoji: '📡', title: '平台覆盖分布', bgColor: '#dbeafe',
  });

  // 3. Radar chart (manual draw)
  const cx = WIDTH / 2;
  const cy = headerBottom + 60 + 400; // center Y for 800px chart
  const maxR = 340;
  const n = labels.length || 1;
  const rings = 5; // 0, 20, 40, 60, 80, 100

  // Helper: point on radar
  const pt = (idx, val) => {
    const angle = (Math.PI * 2 * idx) / n - Math.PI / 2;
    const r = (val / maxVal) * maxR;
    return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  };

  // Grid rings
  for (let ring = 1; ring <= rings; ring++) {
    const r = (ring / rings) * maxR;
    ctx.strokeStyle = 'rgba(0,0,0,0.1)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i <= n; i++) {
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
      const x = cx + r * Math.cos(angle);
      const y = cy + r * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();

    // Tick label
    const tickPt = pt(0, ring * 20);
    ctx.fillStyle = '#64748b';
    ctx.font = `20px ${FONT_FAMILY}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.fillText(`${ring * 20}`, tickPt.x, tickPt.y - 4);
  }

  // Axes
  for (let i = 0; i < n; i++) {
    const ep = pt(i, maxVal);
    ctx.strokeStyle = 'rgba(0,0,0,0.1)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(ep.x, ep.y);
    ctx.stroke();
  }

  // Data polygon
  ctx.beginPath();
  values.forEach((v, i) => {
    const p = pt(i, v);
    if (i === 0) ctx.moveTo(p.x, p.y); else ctx.lineTo(p.x, p.y);
  });
  ctx.closePath();
  ctx.fillStyle = 'rgba(59,130,246,0.2)';
  ctx.fill();
  ctx.strokeStyle = '#3b82f6';
  ctx.lineWidth = 3;
  ctx.stroke();

  // Data points
  values.forEach((v, i) => {
    const p = pt(i, v);
    ctx.beginPath(); ctx.arc(p.x, p.y, 6, 0, Math.PI * 2);
    ctx.fillStyle = '#3b82f6'; ctx.fill();
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; ctx.stroke();
  });

  // Axis labels
  labels.forEach((lbl, i) => {
    const edge = pt(i, maxVal + 30);
    ctx.fillStyle = '#1e293b';
    ctx.font = `bold 24px ${FONT_FAMILY}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(lbl, edge.x, edge.y);
  });

  // 4. Legend (3 cols)
  const legendY = cy + maxR + 80;
  const colW = WIDTH / 3;
  labels.forEach((lbl, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 80 + col * colW;
    const y = legendY + row * 80;

    ctx.fillStyle = PALETTE[i % PALETTE.length];
    ctx.beginPath(); ctx.arc(x, y, 12, 0, Math.PI * 2); ctx.fill();

    ctx.fillStyle = '#475569';
    ctx.font = `32px ${FONT_FAMILY}`;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(lbl, x + 25, y);

    ctx.fillStyle = '#1e293b';
    ctx.font = `bold 36px ${FONT_FAMILY}`;
    const nameW = ctx.measureText(lbl).width;
    ctx.fillText(String(values[i] || 0), x + 25 + nameW + 20, y);
  });

  // 5. Watermark
  drawWatermark(ctx, '* 数值基于各平台实际爬取内容数量归一化');

  return toPng(canvas);
}
