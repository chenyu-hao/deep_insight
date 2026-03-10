/**
 * Debate Timeline renderer
 *
 * Input: { timeline: [{ round, title, insight, summary }] }
 */
import {
  WIDTH, HEIGHT, FONT_FAMILY,
  createCard, drawStudioBackdrop, drawShowcaseHeader, drawGlassPanel,
  drawFloatingLabel, drawWatermark, wrapText, clampLines, withAlpha, toPng,
} from './base.js';

const ACCENT = '#6e6cf6';

function extractKeyPoint(item) {
  if (item && item.summary) return String(item.summary);
  const text = String((item && item.insight) || '');
  const matched = text.match(/^[^。！？.!?]+[。！？.!?]/);
  return matched ? matched[0] : text;
}

function normalizeTimeline(data) {
  const list = Array.isArray(data && data.timeline) ? data.timeline : [];
  const mapped = list
    .map((item, idx) => ({
      round: Number(item && item.round) || idx + 1,
      title: String((item && item.title) || `第${idx + 1}轮推演`).trim(),
      insight: String((item && item.insight) || '').trim(),
      summary: String((item && item.summary) || '').trim(),
    }))
    .slice(0, 8);

  if (mapped.length > 0) return mapped;

  return [
    {
      round: 1,
      title: '观点对齐',
      summary: '暂无辩论过程数据，等待后续推演补全。',
      insight: '',
    },
  ];
}

function calculateLayout(roundCount, availableHeight) {
  const safeCount = Math.max(roundCount, 1);
  const spacePerRound = availableHeight / safeCount;
  let cardHeight = Math.floor(spacePerRound * 0.7);
  cardHeight = Math.max(122, Math.min(178, cardHeight));

  let titleFont = 31;
  let metaFont = 18;
  let contentFont = 22;
  let maxLines = 3;

  if (cardHeight < 146) {
    titleFont = 27;
    metaFont = 17;
    contentFont = 20;
    maxLines = 2;
  } else if (cardHeight > 168) {
    titleFont = 34;
    metaFont = 19;
    contentFont = 23;
    maxLines = 3;
  }

  return {
    itemSpacing: spacePerRound,
    cardHeight,
    titleFont,
    metaFont,
    contentFont,
    maxLines,
  };
}

function drawRoundMarker(ctx, x, y, round) {
  const halo = ctx.createRadialGradient(x, y, 10, x, y, 64);
  halo.addColorStop(0, withAlpha(ACCENT, 0.18));
  halo.addColorStop(1, withAlpha(ACCENT, 0));
  ctx.fillStyle = halo;
  ctx.beginPath();
  ctx.arc(x, y, 64, 0, Math.PI * 2);
  ctx.fill();

  const ring = ctx.createLinearGradient(x - 40, y - 40, x + 40, y + 40);
  ring.addColorStop(0, 'rgba(255,255,255,0.96)');
  ring.addColorStop(1, 'rgba(230,234,255,0.88)');
  ctx.fillStyle = ring;
  ctx.beginPath();
  ctx.arc(x, y, 41, 0, Math.PI * 2);
  ctx.fill();

  ctx.strokeStyle = 'rgba(255,255,255,0.92)';
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  ctx.arc(x, y, 41, 0, Math.PI * 2);
  ctx.stroke();

  const inner = ctx.createLinearGradient(x - 28, y - 28, x + 28, y + 28);
  inner.addColorStop(0, '#7c79ff');
  inner.addColorStop(1, '#5d5bf2');
  ctx.fillStyle = inner;
  ctx.beginPath();
  ctx.arc(x, y, 29, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = '#ffffff';
  ctx.font = `700 28px ${FONT_FAMILY}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(String(round).padStart(2, '0'), x, y + 1);
}

function drawRoundCard(ctx, item, idx, x, y, w, layout) {
  drawGlassPanel(ctx, x, y, w, layout.cardHeight, {
    radius: 30,
    accent: '#d7d7ff',
    fillTop: 'rgba(255,255,255,0.92)',
    fillBottom: 'rgba(243,244,255,0.72)',
    shadow: 'rgba(77, 82, 196, 0.1)',
    shadowBlur: 24,
    shadowY: 10,
  });

  ctx.save();
  ctx.beginPath();
  ctx.roundRect(x, y, w, layout.cardHeight, 30);
  ctx.clip();

  const sweep = ctx.createRadialGradient(x + w - 20, y + 24, 20, x + w - 20, y + 24, 200);
  sweep.addColorStop(0, withAlpha('#ffffff', 0.32));
  sweep.addColorStop(1, withAlpha(ACCENT, 0));
  ctx.fillStyle = sweep;
  ctx.fillRect(x + w - 200, y - 30, 240, 220);

  ctx.restore();

  const metaText = `ROUND ${String(item.round).padStart(2, '0')}`;
  ctx.fillStyle = 'rgba(110,108,246,0.78)';
  ctx.font = `600 ${layout.metaFont}px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(metaText, x + 28, y + 34);

  ctx.fillStyle = '#0f172a';
  ctx.font = `700 ${layout.titleFont}px ${FONT_FAMILY}`;
  const title = item.title.length > 20 ? `${item.title.slice(0, 20)}…` : item.title;
  ctx.fillText(title, x + 28, y + 72);

  ctx.fillStyle = 'rgba(71, 85, 105, 0.92)';
  ctx.font = `500 ${layout.contentFont}px ${FONT_FAMILY}`;
  const keyPoint = extractKeyPoint(item) || '等待更多辩论内容。';
  const lines = clampLines(wrapText(ctx, keyPoint, w - 56), layout.maxLines);
  lines.forEach((line, lineIndex) => {
    ctx.fillText(line || ' ', x + 28, y + 108 + lineIndex * (layout.contentFont + 8));
  });

  const accentY = y + layout.cardHeight - 20;
  const accentW = Math.min(w - 56, 148 + idx * 36);
  const bar = ctx.createLinearGradient(x + 28, accentY, x + 28 + accentW, accentY);
  bar.addColorStop(0, withAlpha(ACCENT, 0.9));
  bar.addColorStop(1, withAlpha('#ffffff', 0.08));
  ctx.strokeStyle = bar;
  ctx.lineWidth = 4;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(x + 28, accentY);
  ctx.lineTo(x + 28 + accentW, accentY);
  ctx.stroke();
}

function drawTimelineGlyph(ctx, { x, y, size, accent }) {
  const cx = x + size / 2;
  const topY = y + 26;
  const bottomY = y + size - 26;

  ctx.save();
  ctx.strokeStyle = withAlpha(accent, 0.42);
  ctx.lineWidth = 4;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(cx, topY + 10);
  ctx.lineTo(cx, bottomY - 10);
  ctx.stroke();

  const stops = [topY + 10, y + size / 2, bottomY - 10];
  stops.forEach((py, idx) => {
    ctx.fillStyle = idx === 1 ? accent : withAlpha(accent, 0.78);
    ctx.beginPath();
    ctx.arc(cx, py, idx === 1 ? 11 : 7, 0, Math.PI * 2);
    ctx.fill();
  });
  ctx.restore();
}

export default function renderDebateTimeline(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');

  const timelineRaw = normalizeTimeline(data);
  const timeline = timelineRaw.slice(0, 8);

  drawStudioBackdrop(ctx, {
    start: '#f7f8fb',
    end: '#eceff5',
    primary: '#8b7cff',
    secondary: '#99c6ff',
  });

  const headerBottom = drawShowcaseHeader(ctx, {
    title: '辩论演化过程',
    kicker: 'Debate Sequence',
    accent: ACCENT,
    glow: '#dfdcff',
    iconRenderer: drawTimelineGlyph,
  });

  const shellY = headerBottom + 34;
  const shellH = 1040;
  drawGlassPanel(ctx, 48, shellY, WIDTH - 96, shellH, {
    radius: 40,
    accent: '#dcd9ff',
    fillTop: 'rgba(255,255,255,0.9)',
    fillBottom: 'rgba(244,245,255,0.72)',
    shadow: 'rgba(15, 23, 42, 0.06)',
    shadowBlur: 26,
    shadowY: 10,
  });

  drawFloatingLabel(ctx, '推理轨迹', 88, shellY + 34, {
    accent: ACCENT,
    fillAlpha: 0.08,
    strokeAlpha: 0.14,
    height: 42,
  });

  ctx.fillStyle = 'rgba(100, 116, 139, 0.88)';
  ctx.font = `520 21px ${FONT_FAMILY}`;
  ctx.textAlign = 'right';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(`${timelineRaw.length} rounds`, WIDTH - 92, shellY + 68);

  const summaryH = 140;
  const topInset = 146;
  const bottomInset = 48;
  const contentTop = shellY + topInset;
  const contentBottom = shellY + shellH - summaryH - bottomInset;
  const contentHeight = contentBottom - contentTop;
  const layout = calculateLayout(timeline.length, contentHeight);
  const timelineHeight = (timeline.length - 1) * layout.itemSpacing;
  const startY = contentTop + layout.cardHeight / 2 + (contentHeight - timelineHeight - layout.cardHeight) / 2;

  const railX = 154;
  const cardX = 238;
  const cardW = WIDTH - cardX - 88;

  ctx.save();
  const rail = ctx.createLinearGradient(railX, contentTop, railX, contentBottom);
  rail.addColorStop(0, withAlpha(ACCENT, 0.08));
  rail.addColorStop(0.16, withAlpha(ACCENT, 0.42));
  rail.addColorStop(0.86, withAlpha(ACCENT, 0.28));
  rail.addColorStop(1, withAlpha(ACCENT, 0.08));
  ctx.strokeStyle = rail;
  ctx.lineWidth = 3;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(railX, contentTop + 12);
  ctx.lineTo(railX, contentBottom - 12);
  ctx.stroke();
  ctx.restore();

  timeline.forEach((item, idx) => {
    const centerY = startY + idx * layout.itemSpacing;
    drawRoundMarker(ctx, railX, centerY, item.round);
    drawRoundCard(ctx, item, idx, cardX, centerY - layout.cardHeight / 2, cardW, layout);
  });

  const summaryY = shellY + shellH - summaryH - 26;
  drawGlassPanel(ctx, 74, summaryY, WIDTH - 148, summaryH, {
    radius: 28,
    accent: '#ddd9ff',
    fillTop: 'rgba(255,255,255,0.88)',
    fillBottom: 'rgba(248,249,255,0.76)',
    shadow: 'rgba(15,23,42,0.04)',
    shadowBlur: 16,
    shadowY: 6,
  });

  ctx.fillStyle = withAlpha(ACCENT, 0.92);
  ctx.font = `700 54px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText(String(timelineRaw.length).padStart(2, '0'), 112, summaryY + 72);

  ctx.fillStyle = '#475569';
  ctx.font = `560 24px ${FONT_FAMILY}`;
  ctx.fillText('轮推演', 170, summaryY + 52);

  ctx.fillStyle = '#0f172a';
  ctx.font = `650 34px ${FONT_FAMILY}`;
  const summaryText = data && Array.isArray(data.timeline) && data.timeline.length > 8
    ? `展示前 8 轮，完整链路共 ${data.timeline.length} 轮`
    : '结论在多轮碰撞中逐步收敛';
  ctx.fillText(summaryText, 318, summaryY + 70);

  ctx.strokeStyle = 'rgba(226,232,240,0.92)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(270, summaryY + 32);
  ctx.lineTo(270, summaryY + summaryH - 32);
  ctx.stroke();

  drawWatermark(ctx, '* 推理过程由 Multi-Agent Debate 框架自动生成');
  return toPng(canvas);
}
