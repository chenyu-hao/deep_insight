/**
 * Apple-style Title Card renderer.
 *
 * Input: { title, emoji, theme, emojiPos }
 */
import {
  WIDTH, HEIGHT, FONT_FAMILY, EMOJI_FONT,
  createCard, drawStudioBackdrop, drawGlassPanel, withAlpha, toPng,
} from './base.js';

const THEME_STYLES = {
  warm: { accent: '#ff9f0a', secondary: '#ffd89b', text: '#1f2937' },
  peach: { accent: '#ff7a59', secondary: '#ffc5d3', text: '#1f2937' },
  sunset: { accent: '#ff8a34', secondary: '#ffb6b9', text: '#1f2937' },
  cool: { accent: '#0a84ff', secondary: '#a8d5ff', text: '#0f172a' },
  ocean: { accent: '#007aff', secondary: '#7ed6df', text: '#0f172a' },
  mint: { accent: '#34c759', secondary: '#9be7c6', text: '#0f172a' },
  sky: { accent: '#38bdf8', secondary: '#bfdcff', text: '#0f172a' },
  lavender: { accent: '#8b5cf6', secondary: '#ddd6fe', text: '#0f172a' },
  grape: { accent: '#635bff', secondary: '#d8b4fe', text: '#0f172a' },
  forest: { accent: '#228b5a', secondary: '#b6e2c4', text: '#10251a' },
  lime: { accent: '#84cc16', secondary: '#d9f99d', text: '#1f2937' },
  alert: { accent: '#ff453a', secondary: '#ffc0cb', text: '#2b1717' },
  dark: { accent: '#7dd3fc', secondary: '#475569', text: '#f8fafc', dark: true },
  cream: { accent: '#c58b3c', secondary: '#f5deb3', text: '#292524' },
};

function getTheme(theme) {
  return THEME_STYLES[theme] || THEME_STYLES.cool;
}

function wrapText(ctx, text, maxWidth) {
  const chars = String(text || '').split('');
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

function getEmojiAnchor(emojiPos) {
  switch (emojiPos) {
    case 'top-left':
      return { x: 190, y: 220, align: 'left' };
    case 'top-right':
      return { x: WIDTH - 190, y: 220, align: 'right' };
    case 'bottom-left':
      return { x: 190, y: HEIGHT - 220, align: 'left' };
    case 'bottom-right':
    default:
      return { x: WIDTH - 190, y: HEIGHT - 220, align: 'right' };
  }
}

function fitTitle(ctx, title, maxWidth) {
  let fontSize = 116;
  let lines = [];

  while (fontSize >= 64) {
    ctx.font = `700 ${fontSize}px ${FONT_FAMILY}`;
    lines = wrapText(ctx, title, maxWidth);
    if (lines.length <= 4) break;
    fontSize -= 6;
  }

  return {
    fontSize,
    lines: lines.slice(0, 4),
    lineHeight: Math.round(fontSize * 1.08),
  };
}

function drawHeroOrb(ctx, x, y, accent, secondary) {
  const orb = ctx.createRadialGradient(x, y, 20, x, y, 260);
  orb.addColorStop(0, withAlpha(accent, 0.22));
  orb.addColorStop(0.45, withAlpha(secondary, 0.12));
  orb.addColorStop(1, withAlpha(accent, 0));
  ctx.fillStyle = orb;
  ctx.beginPath();
  ctx.arc(x, y, 260, 0, Math.PI * 2);
  ctx.fill();
}

export default function renderAppleTitleCard(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');

  const title = data.topic || data.title || '标题生成中...';
  const emoji = data.emoji || '✦';
  const themeName = data.theme || 'cool';
  const emojiPos = data.emojiPos || 'bottom-right';
  const theme = getTheme(themeName);
  const anchor = getEmojiAnchor(emojiPos);

  drawStudioBackdrop(ctx, {
    start: theme.dark ? '#12161f' : '#f6f7fb',
    end: theme.dark ? '#1b2330' : '#ebeef5',
    primary: theme.accent,
    secondary: theme.secondary,
    topLight: theme.dark ? '#1e293b' : '#ffffff',
  });

  drawHeroOrb(ctx, anchor.x, anchor.y, theme.accent, theme.secondary);

  if (theme.dark) {
    const darkWash = ctx.createLinearGradient(0, 0, 0, HEIGHT);
    darkWash.addColorStop(0, 'rgba(255,255,255,0.02)');
    darkWash.addColorStop(1, 'rgba(0,0,0,0.16)');
    ctx.fillStyle = darkWash;
    ctx.fillRect(0, 0, WIDTH, HEIGHT);
  }

  const panelX = 56;
  const panelY = 56;
  const panelW = WIDTH - 112;
  const panelH = HEIGHT - 112;

  drawGlassPanel(ctx, panelX, panelY, panelW, panelH, {
    radius: 48,
    accent: theme.secondary,
    fillTop: theme.dark ? 'rgba(24,29,40,0.84)' : 'rgba(255,255,255,0.9)',
    fillBottom: theme.dark ? 'rgba(28,35,48,0.74)' : 'rgba(244,247,255,0.72)',
    stroke: theme.dark ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.92)',
    shadow: theme.dark ? 'rgba(0,0,0,0.22)' : 'rgba(15,23,42,0.07)',
    shadowBlur: 34,
    shadowY: 16,
  });

  const badgeX = panelX + 44;
  const badgeY = panelY + 40;
  const badgeW = 238;
  const badgeH = 56;
  drawGlassPanel(ctx, badgeX, badgeY, badgeW, badgeH, {
    radius: 28,
    accent: theme.accent,
    fillTop: theme.dark ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.82)',
    fillBottom: theme.dark ? 'rgba(255,255,255,0.04)' : 'rgba(247,250,255,0.64)',
    stroke: theme.dark ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.74)',
    shadow: 'rgba(0,0,0,0)',
    shadowBlur: 0,
    shadowY: 0,
  });

  ctx.fillStyle = withAlpha(theme.accent, theme.dark ? 0.92 : 0.85);
  ctx.font = `650 20px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText('GLOBALINSIGHT / TITLE', badgeX + 24, badgeY + badgeH / 2 + 1);

  const frameX = panelX + 52;
  const frameY = panelY + 144;
  const frameW = panelW - 104;
  const frameH = panelH - 220;
  drawGlassPanel(ctx, frameX, frameY, frameW, frameH, {
    radius: 38,
    accent: theme.secondary,
    fillTop: theme.dark ? 'rgba(255,255,255,0.045)' : 'rgba(255,255,255,0.68)',
    fillBottom: theme.dark ? 'rgba(255,255,255,0.02)' : 'rgba(246,248,255,0.54)',
    stroke: theme.dark ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.72)',
    shadow: 'rgba(0,0,0,0)',
    shadowBlur: 0,
    shadowY: 0,
  });

  const emojiBoxSize = 156;
  const emojiBoxX = anchor.align === 'left' ? frameX + 36 : frameX + frameW - emojiBoxSize - 36;
  const emojiBoxY = anchor.y < HEIGHT / 2 ? frameY + 40 : frameY + frameH - emojiBoxSize - 40;
  drawGlassPanel(ctx, emojiBoxX, emojiBoxY, emojiBoxSize, emojiBoxSize, {
    radius: 36,
    accent: theme.accent,
    fillTop: theme.dark ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.84)',
    fillBottom: theme.dark ? 'rgba(255,255,255,0.03)' : 'rgba(245,247,255,0.62)',
    stroke: theme.dark ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.88)',
    shadow: theme.dark ? 'rgba(0,0,0,0.12)' : 'rgba(15,23,42,0.04)',
    shadowBlur: 20,
    shadowY: 8,
  });

  ctx.font = `88px ${EMOJI_FONT}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(emoji, emojiBoxX + emojiBoxSize / 2, emojiBoxY + emojiBoxSize / 2 + 2);

  ctx.save();
  ctx.font = `260px ${EMOJI_FONT}`;
  ctx.textAlign = anchor.align === 'left' ? 'left' : 'right';
  ctx.textBaseline = 'middle';
  ctx.globalAlpha = theme.dark ? 0.08 : 0.13;
  ctx.fillText(
    emoji,
    anchor.align === 'left' ? frameX + 26 : frameX + frameW - 26,
    anchor.y < HEIGHT / 2 ? frameY + 170 : frameY + frameH - 170,
  );
  ctx.restore();

  const titleBlockX = frameX + 54;
  const titleBlockY = frameY + 260;
  const titleMaxW = frameW - 108;
  const layout = fitTitle(ctx, title, titleMaxW);

  ctx.fillStyle = theme.text;
  ctx.font = `700 ${layout.fontSize}px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'top';
  layout.lines.forEach((line, index) => {
    ctx.fillText(line, titleBlockX, titleBlockY + index * layout.lineHeight);
  });

  const underlineY = titleBlockY + layout.lines.length * layout.lineHeight + 28;
  const lineGradient = ctx.createLinearGradient(titleBlockX, underlineY, titleBlockX + 320, underlineY);
  lineGradient.addColorStop(0, withAlpha(theme.accent, 0.9));
  lineGradient.addColorStop(1, withAlpha(theme.accent, 0.08));
  ctx.strokeStyle = lineGradient;
  ctx.lineWidth = 6;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(titleBlockX, underlineY);
  ctx.lineTo(titleBlockX + 320, underlineY);
  ctx.stroke();

  ctx.fillStyle = withAlpha(theme.text, 0.5);
  ctx.font = `560 26px ${FONT_FAMILY}`;
  ctx.fillText('观潮 GlobalInSight · AI 舆情观察', titleBlockX, underlineY + 34);

  return toPng(canvas);
}
