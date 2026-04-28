/**
 * Key Findings Card renderer
 *
 * Input: { findings: [string, string, string] }
 */
import {
  WIDTH, HEIGHT, FONT_FAMILY,
  createCard, drawAppleBackdrop, drawAmbientOrbs,
  drawHeader, drawPanel, drawSectionLabel, drawWatermark,
  wrapText, clampLines, withAlpha, toPng,
} from './base.js';

const ACCENT = '#0a84ff';
const RANK_COLORS = ['#0a84ff', '#5e5ce6', '#30d158'];

export default function renderKeyFindings(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');

  const raw = ((data && data.findings) || [])
    .map((item) => String(item || '').trim())
    .filter(Boolean)
    .slice(0, 3);
  const findings = raw.length > 0 ? raw : ['暂无关键发现，等待更多样本。'];

  drawAppleBackdrop(ctx, {
    start: '#f8f9fc',
    end: '#eef1f6',
    topLight: '#ffffff',
    bottomTint: '#dbeafe',
    textureAlpha: 0.012,
  });
  drawAmbientOrbs(ctx, [
    { x: 170, y: 260, r: 240, color: '#dbeafe', alpha: 0.2 },
    { x: 910, y: 1120, r: 300, color: '#c7d2fe', alpha: 0.16 },
  ]);

  const headerBottom = drawHeader(ctx, {
    emoji: '✨',
    title: '关键发现',
    bgColor: '#dbeafe',
    textColor: '#0f172a',
  });

  const sectionY = headerBottom + 46;
  drawPanel(ctx, 58, sectionY, WIDTH - 116, 980, {
    radius: 36,
    fill: 'rgba(255,255,255,0.64)',
    stroke: 'rgba(255,255,255,0.88)',
    shadow: 'rgba(15, 23, 42, 0.06)',
    shadowBlur: 24,
    shadowY: 10,
  });
  drawSectionLabel(ctx, '发现摘要', 98, sectionY + 36, ACCENT);

  const itemCount = findings.length;
  const contentTop = sectionY + 108;
  const summaryY = sectionY + 860;
  const contentHeight = summaryY - contentTop - 24;
  const itemGap = itemCount === 1 ? 0 : 26;
  let itemHeight = Math.floor((contentHeight - itemGap * (itemCount - 1)) / itemCount);
  let startY = contentTop;
  if (itemCount === 1) {
    itemHeight = 360;
    startY = contentTop + Math.max(0, Math.floor((contentHeight - itemHeight) / 2));
  }

  findings.forEach((finding, i) => {
    const y = startY + i * (itemHeight + itemGap);
    const badgeColor = RANK_COLORS[i % RANK_COLORS.length];

    drawPanel(ctx, 86, y, WIDTH - 172, itemHeight, {
      radius: 26,
      fill: 'rgba(255,255,255,0.6)',
      stroke: 'rgba(255,255,255,0.86)',
      shadow: withAlpha(badgeColor, 0.08),
      shadowBlur: 16,
      shadowY: 6,
    });

    ctx.fillStyle = withAlpha(badgeColor, 0.14);
    roundRect(ctx, 106, y + 22, 88, itemHeight - 44, 24);
    ctx.fill();

    ctx.fillStyle = badgeColor;
    ctx.font = `700 40px ${FONT_FAMILY}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(String(i + 1), 150, y + itemHeight / 2 + 2);

    const textX = 224;
    const textW = WIDTH - 312;
    const lineHeight = itemCount === 1 ? 54 : 46;
    const maxLines = itemCount === 1 ? 5 : 3;
    const baseFont = itemCount === 1 ? 40 : 34;

    ctx.fillStyle = '#0f172a';
    ctx.font = `620 ${baseFont}px ${FONT_FAMILY}`;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    const lines = clampLines(wrapText(ctx, finding, textW), maxLines);
    lines.forEach((line, li) => {
      ctx.fillText(line || ' ', textX, y + 32 + li * lineHeight);
    });
  });

  drawPanel(ctx, 86, summaryY, WIDTH - 172, 96, {
    radius: 20,
    fill: 'rgba(248,250,252,0.8)',
    stroke: 'rgba(226,232,240,0.9)',
    shadow: 'rgba(15, 23, 42, 0.03)',
    shadowBlur: 10,
    shadowY: 4,
  });
  ctx.fillStyle = '#475569';
  ctx.font = `520 27px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText('按重要性排序，便于直接转为图文要点。', 118, summaryY + 50);

  drawWatermark(ctx, '* 关键发现由多维语义分析自动提取');

  return toPng(canvas);
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, r);
}
