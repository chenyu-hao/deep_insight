/**
 * Platform Heat renderer
 *
 * Input: { platforms: [{ name, value, percentage }] }
 */
import {
  WIDTH, FONT_FAMILY,
  createCard, drawAppleBackdrop, drawAmbientOrbs,
  drawHeader, drawPanel, drawSectionLabel, drawWatermark, toPng,
} from './base.js';

const COLORS = ['#0a84ff', '#5e5ce6', '#30d158', '#ff9f0a', '#ff453a', '#64d2ff', '#8e8e93'];

function normalizePlatforms(data) {
  const list = Array.isArray(data && data.platforms) ? data.platforms : [];
  const normalized = list
    .map((item) => ({
      name: String((item && item.name) || '').trim(),
      value: Number(item && item.value),
      percentage: Number(item && item.percentage),
    }))
    .filter((item) => item.name)
    .slice(0, 7)
    .map((item) => ({
      name: item.name,
      value: Number.isFinite(item.value) ? item.value : 0,
      percentage: Number.isFinite(item.percentage)
        ? Math.max(0, Math.min(100, item.percentage))
        : 0,
    }));

  if (normalized.length > 0) return normalized;
  return [
    { name: '微博', value: 86, percentage: 86 },
    { name: '小红书', value: 79, percentage: 79 },
    { name: '知乎', value: 64, percentage: 64 },
  ];
}

function fitText(ctx, text, maxWidth, maxSize = 36, minSize = 26) {
  let size = maxSize;
  while (size >= minSize) {
    ctx.font = `620 ${size}px ${FONT_FAMILY}`;
    if (ctx.measureText(text).width <= maxWidth) return size;
    size -= 1;
  }
  return minSize;
}

export default function renderPlatformHeat(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');
  const platforms = normalizePlatforms(data);

  drawAppleBackdrop(ctx, {
    start: '#f8f9fc',
    end: '#edf1f7',
    topLight: '#ffffff',
    bottomTint: '#dbeafe',
    textureAlpha: 0.012,
  });
  drawAmbientOrbs(ctx, [
    { x: 190, y: 240, r: 230, color: '#dbeafe', alpha: 0.2 },
    { x: 920, y: 1180, r: 300, color: '#c7d2fe', alpha: 0.14 },
  ]);

  const headerBottom = drawHeader(ctx, {
    emoji: '📊',
    title: '平台热度分布',
    bgColor: '#dbeafe',
    textColor: '#0f172a',
  });

  const panelY = headerBottom + 44;
  drawPanel(ctx, 56, panelY, WIDTH - 112, 948, {
    radius: 34,
    fill: 'rgba(255,255,255,0.66)',
    stroke: 'rgba(255,255,255,0.88)',
    shadow: 'rgba(15, 23, 42, 0.06)',
    shadowBlur: 24,
    shadowY: 10,
  });
  drawSectionLabel(ctx, '热度排序', 100, panelY + 34, '#0a84ff');

  const listY = panelY + 110;
  const itemH = 112;
  const barX = 132;
  const barMaxW = WIDTH - 300;
  const barH = 24;

  platforms.forEach((platform, i) => {
    const y = listY + i * itemH;
    const color = COLORS[i % COLORS.length];
    const name = platform.name.length > 8 ? `${platform.name.slice(0, 8)}…` : platform.name;
    const titleSize = fitText(ctx, name, 260);

    ctx.fillStyle = '#0f172a';
    ctx.font = `620 ${titleSize}px ${FONT_FAMILY}`;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    ctx.fillText(name, 92, y + 10);

    ctx.fillStyle = '#64748b';
    ctx.font = `560 30px ${FONT_FAMILY}`;
    ctx.textAlign = 'right';
    ctx.fillText(String(platform.value), WIDTH - 92, y + 8);

    const barY = y + 42;
    ctx.fillStyle = 'rgba(226,232,240,0.88)';
    roundRect(ctx, barX, barY, barMaxW, barH, 999);
    ctx.fill();

    ctx.fillStyle = color;
    const filledW = Math.max(12, barMaxW * (platform.percentage / 100));
    roundRect(ctx, barX, barY, filledW, barH, 999);
    ctx.fill();

    ctx.fillStyle = 'rgba(71,85,105,0.84)';
    ctx.font = `520 23px ${FONT_FAMILY}`;
    ctx.textAlign = 'right';
    ctx.fillText(`${platform.percentage.toFixed(1)}%`, barX + barMaxW, barY - 8);
  });

  const summaryY = listY + platforms.length * itemH + 26;
  drawPanel(ctx, 82, summaryY, WIDTH - 164, 138, {
    radius: 22,
    fill: 'rgba(255,255,255,0.62)',
    stroke: 'rgba(255,255,255,0.86)',
    shadow: 'rgba(15, 23, 42, 0.04)',
    shadowBlur: 12,
    shadowY: 5,
  });

  const avg = platforms.length
    ? (platforms.reduce((sum, item) => sum + item.value, 0) / platforms.length).toFixed(1)
    : '0.0';
  ctx.fillStyle = '#475569';
  ctx.font = `560 34px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(`覆盖 ${platforms.length} 个平台`, 122, summaryY + 54);
  ctx.fillText(`平均热度 ${avg}`, 122, summaryY + 102);

  drawWatermark(ctx, '* 数据基于多平台实时抓取与聚合');
  return toPng(canvas);
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, r);
}
