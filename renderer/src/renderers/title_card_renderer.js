/**
 * Title Card renderer – mirrors XiaohongshuCard.vue generateImage()
 *
 * Input: { title, emoji, theme, emojiPos }
 */
import {
  WIDTH, HEIGHT, FONT_FAMILY, EMOJI_FONT,
  createCard, toPng,
} from './base.js';

const THEME_COLORS = {
  warm:     { gradientStart: '#fff7ed', gradientEnd: '#fef3c7', textColor: '#78350f' },
  peach:    { gradientStart: '#ffedd5', gradientEnd: '#fce7f3', textColor: '#7c2d12' },
  sunset:   { gradientStart: '#fef3c7', gradientEnd: '#ffe4e6', textColor: '#78350f' },
  cool:     { gradientStart: '#eef2ff', gradientEnd: '#cffafe', textColor: '#1e293b' },
  ocean:    { gradientStart: '#dbeafe', gradientEnd: '#ccfbf1', textColor: '#1e3a8a' },
  mint:     { gradientStart: '#ecfdf5', gradientEnd: '#ccfbf1', textColor: '#064e3b' },
  sky:      { gradientStart: '#e0f2fe', gradientEnd: '#dbeafe', textColor: '#0c4a6e' },
  lavender: { gradientStart: '#faf5ff', gradientEnd: '#ede9fe', textColor: '#581c87' },
  grape:    { gradientStart: '#ede9fe', gradientEnd: '#fae8ff', textColor: '#5b21b6' },
  forest:   { gradientStart: '#f0fdf4', gradientEnd: '#d1fae5', textColor: '#14532d' },
  lime:     { gradientStart: '#f7fee7', gradientEnd: '#dcfce7', textColor: '#365314' },
  alert:    { gradientStart: '#fee2e2', gradientEnd: '#fecdd3', textColor: '#7f1d1d' },
  dark:     { gradientStart: '#1e293b', gradientEnd: '#0f172a', textColor: '#ffffff' },
  cream:    { gradientStart: '#fafaf9', gradientEnd: '#fffbeb', textColor: '#292524' },
};

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

export default function renderTitleCard(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');

  const title = data.topic || data.title || '标题生成中...';
  const emoji = data.emoji || '🤔';
  const theme = data.theme || 'cool';
  const emojiPos = data.emojiPos || 'bottom-right';
  const colors = THEME_COLORS[theme] || THEME_COLORS.cool;

  // 1. Background gradient
  const g = ctx.createLinearGradient(0, 0, WIDTH, HEIGHT);
  g.addColorStop(0, colors.gradientStart);
  g.addColorStop(1, colors.gradientEnd);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

  // 2. Emoji
  const emojiMarginX = WIDTH * 0.08;
  const emojiMarginY = HEIGHT * 0.08;
  const emojiSize = 250;
  const half = emojiSize / 2;

  let emojiX, emojiY;
  switch (emojiPos) {
    case 'top-left':
      emojiX = emojiMarginX + half; emojiY = emojiMarginY + half; break;
    case 'top-right':
      emojiX = WIDTH - emojiMarginX - half; emojiY = emojiMarginY + half; break;
    case 'bottom-left':
      emojiX = emojiMarginX + half; emojiY = HEIGHT - emojiMarginY - half; break;
    case 'bottom-right': default:
      emojiX = WIDTH - emojiMarginX - half; emojiY = HEIGHT - emojiMarginY - half; break;
  }

  ctx.font = `${emojiSize}px ${EMOJI_FONT}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.save();
  ctx.translate(emojiX, emojiY);
  ctx.rotate((Math.random() * 20 - 10) * Math.PI / 180);
  ctx.fillText(emoji, 0, 0);
  ctx.restore();

  // 3. Title text
  const textMarginX = WIDTH * 0.12;
  const textMarginY = HEIGHT * 0.18;
  const maxTitleWidth = WIDTH * 0.72;

  ctx.fillStyle = colors.textColor;
  ctx.shadowColor = 'rgba(0,0,0,0.1)';
  ctx.shadowBlur = 10;
  ctx.shadowOffsetX = 4;
  ctx.shadowOffsetY = 4;

  let textX, textY, textAlign;
  switch (emojiPos) {
    case 'top-left':
      textX = WIDTH - textMarginX; textY = HEIGHT - textMarginY; textAlign = 'right'; break;
    case 'top-right':
      textX = textMarginX; textY = HEIGHT - textMarginY; textAlign = 'left'; break;
    case 'bottom-left':
      textX = WIDTH - textMarginX; textY = textMarginY; textAlign = 'right'; break;
    case 'bottom-right': default:
      textX = textMarginX; textY = textMarginY; textAlign = 'left'; break;
  }

  ctx.textAlign = textAlign;
  ctx.textBaseline = 'middle';

  // Exclusion zone for emoji
  const padding = 60;
  const emojiBox = {
    left: emojiX - half - padding,
    right: emojiX + half + padding,
    top: emojiY - half - padding,
    bottom: emojiY + half + padding,
  };

  const getLayoutForLine = (lineY, lineHeight) => {
    const lineTop = lineY - lineHeight / 2;
    const lineBottom = lineY + lineHeight / 2;
    if (lineBottom < emojiBox.top || lineTop > emojiBox.bottom) {
      return { width: maxTitleWidth };
    }
    let available = maxTitleWidth;
    if (textAlign === 'left') {
      const textRight = textX + maxTitleWidth;
      if (emojiBox.left < textRight && emojiBox.right > textX) {
        available = Math.max(0, emojiBox.left - textX);
      }
    } else {
      const textLeft = textX - maxTitleWidth;
      if (emojiBox.right > textLeft && emojiBox.left < textX) {
        available = Math.max(0, textX - emojiBox.right);
      }
    }
    return { width: available };
  };

  // Auto-size font
  let fontSize = 128;
  let lines;
  const maxLines = 6;
  while (fontSize >= 60) {
    ctx.font = `900 ${fontSize}px ${FONT_FAMILY}`;
    lines = [];
    const tempLines = wrapText(ctx, title, maxTitleWidth);
    let ok = true;
    const lineH = fontSize * 1.3;
    const isBottom = emojiPos === 'top-left' || emojiPos === 'top-right';
    for (let i = 0; i < tempLines.length; i++) {
      const ly = isBottom
        ? textY - (tempLines.length - 1 - i) * lineH
        : textY + i * lineH;
      const layout = getLayoutForLine(ly, lineH);
      const reWrapped = wrapText(ctx, tempLines[i], layout.width);
      if (reWrapped.length > 1) { ok = false; break; }
      lines.push({ text: tempLines[i], y: ly });
    }
    if (ok && lines.length <= maxLines) break;
    fontSize -= 5;
  }

  // Draw lines
  ctx.font = `900 ${fontSize}px ${FONT_FAMILY}`;
  if (lines) {
    for (const l of lines) {
      ctx.fillText(l.text, textX, l.y);
    }
  }

  // Reset shadow
  ctx.shadowColor = 'transparent';
  ctx.shadowBlur = 0;
  ctx.shadowOffsetX = 0;
  ctx.shadowOffsetY = 0;

  return toPng(canvas);
}
