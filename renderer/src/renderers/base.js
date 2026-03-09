/**
 * Shared renderer primitives for all data cards.
 * Title card keeps Xiaohongshu style in its own renderer.
 */

const WIDTH = 1080;
const HEIGHT = 1440;

const FONT_FAMILY = '"SF Pro Display", "SF Pro Text", -apple-system, "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif';
const EMOJI_FONT = '"Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif';

function createCard() {
  const canvas = document.createElement('canvas');
  canvas.width = WIDTH;
  canvas.height = HEIGHT;
  return canvas;
}

function drawGradientBg(ctx, startColor, endColor) {
  const g = ctx.createLinearGradient(0, 0, WIDTH, HEIGHT);
  g.addColorStop(0, startColor);
  g.addColorStop(1, endColor);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);
}

function drawAmbientOrbs(ctx, orbs = []) {
  orbs.forEach(({ x, y, r, color, alpha = 0.12 }) => {
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, withAlpha(color, alpha));
    g.addColorStop(1, withAlpha(color, 0));
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  });
}

function drawGridTexture(ctx, alpha = 0.016, gap = 54) {
  ctx.save();
  ctx.strokeStyle = `rgba(148, 163, 184, ${alpha})`;
  ctx.lineWidth = 1;
  for (let x = 0; x <= WIDTH; x += gap) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, HEIGHT);
    ctx.stroke();
  }
  for (let y = 0; y <= HEIGHT; y += gap) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(WIDTH, y);
    ctx.stroke();
  }
  ctx.restore();
}

function drawAppleBackdrop(ctx, {
  start = '#f8f9fc',
  end = '#eef1f6',
  topLight = '#ffffff',
  bottomTint = '#dbeafe',
  textureAlpha = 0.014,
} = {}) {
  drawGradientBg(ctx, start, end);

  const topGlow = ctx.createRadialGradient(WIDTH * 0.18, 120, 40, WIDTH * 0.18, 120, 760);
  topGlow.addColorStop(0, withAlpha(topLight, 0.72));
  topGlow.addColorStop(1, withAlpha(topLight, 0));
  ctx.fillStyle = topGlow;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

  const bottomGlow = ctx.createRadialGradient(WIDTH * 0.78, HEIGHT * 0.96, 80, WIDTH * 0.78, HEIGHT * 0.96, 620);
  bottomGlow.addColorStop(0, withAlpha(bottomTint, 0.18));
  bottomGlow.addColorStop(1, withAlpha(bottomTint, 0));
  ctx.fillStyle = bottomGlow;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

  drawGridTexture(ctx, textureAlpha, 64);
}

function drawPanel(ctx, x, y, w, h, {
  radius = 28,
  fill = 'rgba(255,255,255,0.72)',
  stroke = 'rgba(255,255,255,0.86)',
  shadow = 'rgba(15, 23, 42, 0.06)',
  shadowBlur = 28,
  shadowY = 10,
  lineWidth = 1.5,
} = {}) {
  ctx.save();
  ctx.shadowColor = shadow;
  ctx.shadowBlur = shadowBlur;
  ctx.shadowOffsetX = 0;
  ctx.shadowOffsetY = shadowY;
  ctx.fillStyle = fill;
  roundRect(ctx, x, y, w, h, radius);
  ctx.fill();
  ctx.restore();

  if (stroke) {
    ctx.save();
    ctx.strokeStyle = stroke;
    ctx.lineWidth = lineWidth;
    roundRect(ctx, x, y, w, h, radius);
    ctx.stroke();
    ctx.restore();
  }
}

function drawSectionLabel(ctx, text, x, y, accent = '#0a84ff') {
  const label = String(text || '');
  ctx.save();
  ctx.font = `600 24px ${FONT_FAMILY}`;
  const tagW = Math.max(110, ctx.measureText(label).width + 34);
  const tagH = 44;
  const tagY = y - 14;

  ctx.fillStyle = withAlpha(accent, 0.13);
  roundRect(ctx, x, tagY, tagW, tagH, 14);
  ctx.fill();

  ctx.strokeStyle = withAlpha(accent, 0.22);
  ctx.lineWidth = 1;
  roundRect(ctx, x, tagY, tagW, tagH, 14);
  ctx.stroke();

  ctx.fillStyle = withAlpha(accent, 0.95);
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText(label, x + 16, tagY + tagH / 2 + 1);
  ctx.restore();
}

function drawStatChip(ctx, {
  x,
  y,
  w,
  h,
  label,
  value,
  accent = '#0a84ff',
  valueColor = '#0f172a',
}) {
  drawPanel(ctx, x, y, w, h, {
    radius: 24,
    fill: 'rgba(255,255,255,0.66)',
    stroke: 'rgba(255,255,255,0.84)',
    shadow: withAlpha(accent, 0.09),
    shadowBlur: 20,
    shadowY: 8,
    lineWidth: 1.2,
  });

  const labelStr = String(label || '');
  const valueStr = String(value ?? '--');

  ctx.save();
  const dotX = x + 30;
  const dotY = y + 34;
  ctx.fillStyle = accent;
  ctx.beginPath();
  ctx.arc(dotX, dotY, 7, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = 'rgba(71, 85, 105, 0.9)';
  ctx.font = `520 24px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(labelStr, dotX + 18, y + 42);

  let valueSize = 42;
  ctx.fillStyle = valueColor;
  ctx.textBaseline = 'alphabetic';
  while (valueSize >= 30) {
    ctx.font = `700 ${valueSize}px ${FONT_FAMILY}`;
    if (ctx.measureText(valueStr).width <= w - 44) break;
    valueSize -= 2;
  }
  ctx.fillText(valueStr, x + 22, y + h - 26);
  ctx.restore();
}

function drawHeader(ctx, {
  emoji,
  title,
  bgColor = '#e8f2ff',
  textColor = '#0f172a',
}) {
  const headerY = 68;
  const headerH = 148;

  drawPanel(ctx, 56, headerY, WIDTH - 112, headerH, {
    radius: 36,
    fill: 'rgba(255,255,255,0.64)',
    stroke: 'rgba(255,255,255,0.88)',
    shadow: 'rgba(15, 23, 42, 0.05)',
    shadowBlur: 22,
    shadowY: 8,
    lineWidth: 1.2,
  });

  const iconX = 92;
  const iconY = headerY + 26;
  const iconSize = 96;
  const iconGradient = ctx.createLinearGradient(iconX, iconY, iconX + iconSize, iconY + iconSize);
  iconGradient.addColorStop(0, withAlpha(bgColor, 0.95));
  iconGradient.addColorStop(1, withAlpha('#ffffff', 0.92));
  ctx.fillStyle = iconGradient;
  roundRect(ctx, iconX, iconY, iconSize, iconSize, 28);
  ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,0.92)';
  ctx.lineWidth = 1;
  roundRect(ctx, iconX, iconY, iconSize, iconSize, 28);
  ctx.stroke();

  ctx.font = `58px ${EMOJI_FONT}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(emoji || '📄', iconX + iconSize / 2, iconY + iconSize / 2 + 2);

  const titleX = 222;
  const titleY = headerY + headerH / 2 + 4;
  const maxTitleW = WIDTH - titleX - 90;
  const titleText = String(title || '');

  let fontSize = 68;
  while (fontSize >= 48) {
    ctx.font = `700 ${fontSize}px ${FONT_FAMILY}`;
    if (ctx.measureText(titleText).width <= maxTitleW) break;
    fontSize -= 2;
  }

  ctx.fillStyle = textColor;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText(titleText, titleX, titleY);

  return headerY + headerH;
}

function drawWatermark(ctx, note) {
  ctx.fillStyle = 'rgba(100, 116, 139, 0.74)';
  ctx.font = `21px ${FONT_FAMILY}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(String(note || ''), WIDTH / 2, HEIGHT - 96);

  ctx.fillStyle = 'rgba(71, 85, 105, 0.8)';
  ctx.font = `24px ${FONT_FAMILY}`;
  ctx.fillText('@观潮GlobalInSight · AI舆情洞察', WIDTH / 2, HEIGHT - 60);
}

function wrapText(ctx, text, maxWidth) {
  if (!text) return [];
  const width = Math.max(24, maxWidth || 0);
  const paragraphs = String(text).split(/\r?\n/);
  const lines = [];

  paragraphs.forEach((paragraph, idx) => {
    const chars = paragraph.split('');
    let cur = '';
    for (const ch of chars) {
      const test = cur + ch;
      if (ctx.measureText(test).width > width && cur.length > 0) {
        lines.push(cur);
        cur = ch;
      } else {
        cur = test;
      }
    }
    if (cur) lines.push(cur);
    if (idx < paragraphs.length - 1) lines.push('');
  });

  return lines;
}

function clampLines(lines, maxLines) {
  if (!Array.isArray(lines)) return [];
  if (lines.length <= maxLines) return lines;
  const clamped = lines.slice(0, maxLines);
  const last = clamped[maxLines - 1] || '';
  clamped[maxLines - 1] = `${last.replace(/\s+$/g, '')}…`;
  return clamped;
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, r);
}

function withAlpha(color, alpha) {
  const a = Math.max(0, Math.min(1, alpha));
  if (typeof color !== 'string') return `rgba(15, 23, 42, ${a})`;

  if (color.startsWith('#')) {
    const hex = color.slice(1);
    const full = hex.length === 3
      ? hex.split('').map((c) => c + c).join('')
      : hex;
    const r = parseInt(full.slice(0, 2), 16);
    const g = parseInt(full.slice(2, 4), 16);
    const b = parseInt(full.slice(4, 6), 16);
    if ([r, g, b].some((v) => Number.isNaN(v))) return color;
    return `rgba(${r}, ${g}, ${b}, ${a})`;
  }
  return color;
}

function toPng(canvas) {
  return canvas.toDataURL('image/png');
}

export {
  WIDTH,
  HEIGHT,
  FONT_FAMILY,
  EMOJI_FONT,
  createCard,
  drawGradientBg,
  drawAmbientOrbs,
  drawGridTexture,
  drawAppleBackdrop,
  drawHeader,
  drawPanel,
  drawSectionLabel,
  drawStatChip,
  drawWatermark,
  wrapText,
  clampLines,
  roundRect,
  withAlpha,
  toPng,
};
