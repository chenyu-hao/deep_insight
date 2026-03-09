/**
 * Platform Heat renderer – mirrors PlatformHeatCanvas.vue generateImage()
 *
 * Input: { platforms: [{ name, value, percentage }] }
 */
import {
  WIDTH, HEIGHT, FONT_FAMILY, EMOJI_FONT,
  createCard, drawHeader, drawWatermark, toPng,
} from './base.js';

const COLORS = ['#3b82f6', '#10b981', '#a855f7', '#f97316', '#ec4899', '#6366f1', '#ef4444'];

export default function renderPlatformHeat(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');
  const platforms = ((data && data.platforms) || []).slice(0, 7);

  // 1. White background
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

  // 2. Header
  const headerBottom = drawHeader(ctx, {
    emoji: '📊', title: '平台热度分布', bgColor: '#dbeafe',
  });

  // 3. Platform bars
  const listY = headerBottom + 80;
  const itemH = 140;
  const barMaxW = WIDTH - 280;
  const barH = 40;

  platforms.forEach((p, i) => {
    const y = listY + i * itemH;
    const color = COLORS[i % COLORS.length];

    // name
    ctx.fillStyle = '#475569';
    ctx.font = `bold 48px ${FONT_FAMILY}`;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText(p.name, 80, y);

    // value
    ctx.fillStyle = '#94a3b8';
    ctx.font = `36px ${FONT_FAMILY}`;
    ctx.textAlign = 'right';
    ctx.fillText(String(p.value), WIDTH - 80, y);

    // bar background
    const barY = y + 70;
    ctx.fillStyle = '#f1f5f9';
    ctx.fillRect(80, barY, barMaxW, barH);

    // bar fill
    ctx.fillStyle = color;
    ctx.fillRect(80, barY, barMaxW * (p.percentage / 100), barH);
  });

  // 4. Summary
  const sumY = listY + platforms.length * itemH + 60;
  ctx.fillStyle = '#f8fafc';
  ctx.fillRect(80, sumY, WIDTH - 160, 120);

  const avg = platforms.length
    ? (platforms.reduce((s, p) => s + p.value, 0) / platforms.length).toFixed(1)
    : '0.0';
  ctx.fillStyle = '#64748b';
  ctx.font = `36px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.fillText(`覆盖 ${platforms.length} 个平台`, 120, sumY + 40);
  ctx.fillText(`平均热度 ${avg}`, 120, sumY + 85);

  // 5. Watermark
  drawWatermark(ctx, '* 数据基于多平台实时爬取');

  return toPng(canvas);
}
