/**
 * Base utilities shared across all card renderers.
 * Mirrors the style conventions from GlobalInSight Vue Canvas components.
 *
 * All cards: 1080 × 1440 px, PNG output via canvas.toDataURL('image/png').
 */

const WIDTH = 1080;
const HEIGHT = 1440;

const FONT_FAMILY = '"PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif';
const EMOJI_FONT = '"Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif';

/* ── helpers ─────────────────────────────────────────────── */

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

function drawHeader(ctx, { emoji, title, bgColor, textColor = '#1e293b' }) {
  const headerY = 80;
  const headerH = 120;
  const cy = headerY + headerH / 2;

  // icon circle
  ctx.fillStyle = bgColor;
  ctx.beginPath();
  ctx.arc(120, cy, 50, 0, Math.PI * 2);
  ctx.fill();

  // emoji
  ctx.font = `60px ${EMOJI_FONT}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(emoji, 120, cy);

  // title text
  ctx.fillStyle = textColor;
  ctx.font = `bold 72px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText(title, 200, cy);

  return headerY + headerH; // bottom of header
}

function drawWatermark(ctx, note) {
  ctx.fillStyle = '#cbd5e1';
  ctx.font = `22px ${FONT_FAMILY}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(note, WIDTH / 2, HEIGHT - 95);

  ctx.font = `24px ${FONT_FAMILY}`;
  ctx.fillText('@观潮GlobalInSight · AI舆情洞察', WIDTH / 2, HEIGHT - 60);
}

function wrapText(ctx, text, maxWidth) {
  const chars = text.split('');
  const lines = [];
  let cur = '';
  for (const ch of chars) {
    const test = cur + ch;
    if (ctx.measureText(test).width > maxWidth && cur.length > 0) {
      lines.push(cur);
      cur = ch;
    } else {
      cur = test;
    }
  }
  if (cur) lines.push(cur);
  return lines;
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, r);
}

function toPng(canvas) {
  return canvas.toDataURL('image/png');
}

export {
  WIDTH, HEIGHT, FONT_FAMILY, EMOJI_FONT,
  createCard, drawGradientBg, drawHeader, drawWatermark,
  wrapText, roundRect, toPng,
};
