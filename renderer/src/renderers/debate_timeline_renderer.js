/**
 * Debate Timeline renderer – mirrors DebateTimelineCanvas.vue generateImage()
 *
 * Input: { timeline: [{ round, title, insight, summary }] }
 */
import {
  WIDTH, HEIGHT, FONT_FAMILY, EMOJI_FONT,
  createCard, drawGradientBg, drawHeader, drawWatermark, wrapText, toPng,
} from './base.js';

function extractKeyPoint(item) {
  if (item.summary) return item.summary;
  const text = item.insight || '';
  const m = text.match(/^[^。！？.!?]+[。！？.!?]/);
  return m ? m[0] : text.substring(0, 30);
}

function calculateLayout(roundCount, availableHeight) {
  const minCardH = 120, maxCardH = 200;
  const spacePerRound = availableHeight / roundCount;
  let cardH = Math.floor(spacePerRound * 0.75);
  cardH = Math.max(minCardH, Math.min(maxCardH, cardH));

  let titleFont, contentFont;
  if (cardH >= 180) { titleFont = 32; contentFont = 26; }
  else if (cardH >= 150) { titleFont = 30; contentFont = 24; }
  else if (cardH >= 130) { titleFont = 28; contentFont = 22; }
  else { titleFont = 26; contentFont = 20; }

  return { itemSpacing: spacePerRound, cardHeight: cardH, titleFont, contentFont };
}

export default function renderDebateTimeline(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');

  const timelineRaw = (data && data.timeline) || [];
  const maxRounds = Math.min(timelineRaw.length, 8);
  const timeline = timelineRaw.slice(0, maxRounds);

  // 1. Background
  drawGradientBg(ctx, '#ffffff', '#eff6ff');

  // 2. Header
  const headerBottom = drawHeader(ctx, {
    emoji: '🔀', title: '辩论演化过程', bgColor: '#e9d5ff', textColor: '#1e293b',
  });

  // 3. Layout
  const PAD_TOP = 40;
  const SUMMARY_H = 100;
  const WATERMARK_AREA = 140;
  const PAD_BOTTOM = 30;

  const areaTop = headerBottom + PAD_TOP;
  const areaBottom = HEIGHT - WATERMARK_AREA - SUMMARY_H - PAD_BOTTOM;
  const availH = areaBottom - areaTop;
  const layout = calculateLayout(timeline.length, availH);

  const tlHeight = (timeline.length - 1) * layout.itemSpacing;
  const startY = areaTop + layout.cardHeight / 2 + (availH - tlHeight - layout.cardHeight) / 2;

  const circleX = 125;
  const cardX = 200;
  const cardW = WIDTH - cardX - 80;

  timeline.forEach((item, i) => {
    const itemY = startY + i * layout.itemSpacing;

    // dashed connector
    if (i < timeline.length - 1) {
      ctx.strokeStyle = '#60a5fa';
      ctx.lineWidth = 3;
      ctx.setLineDash([8, 8]);
      ctx.beginPath();
      ctx.moveTo(circleX, itemY + 45);
      ctx.lineTo(circleX, itemY + layout.itemSpacing - 45);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // circle badge
    ctx.fillStyle = '#3b82f6';
    ctx.beginPath();
    ctx.arc(circleX, itemY, 45, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#ffffff';
    ctx.font = `bold 40px ${FONT_FAMILY}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`R${item.round}`, circleX, itemY);

    // card
    const cardY = itemY - layout.cardHeight / 2;
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.roundRect(cardX, cardY, cardW, layout.cardHeight, 12);
    ctx.fill();

    // left blue bar
    ctx.fillStyle = '#3b82f6';
    ctx.beginPath();
    ctx.roundRect(cardX, cardY, 8, layout.cardHeight, [12, 0, 0, 12]);
    ctx.fill();

    // title
    ctx.fillStyle = '#1e293b';
    ctx.font = `bold ${layout.titleFont}px ${FONT_FAMILY}`;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    const titleText = item.title.length > 18 ? item.title.substring(0, 18) + '...' : item.title;
    ctx.fillText(titleText, cardX + 24, cardY + 20);

    // content
    ctx.fillStyle = '#64748b';
    ctx.font = `${layout.contentFont}px ${FONT_FAMILY}`;
    const kp = extractKeyPoint(item);
    const lines = wrapText(ctx, kp, cardW - 48);
    lines.slice(0, 3).forEach((line, li) => {
      ctx.fillText(line, cardX + 24, cardY + 20 + layout.titleFont + 12 + li * (layout.contentFont + 8));
    });
  });

  // 4. Summary box
  const summaryY = HEIGHT - WATERMARK_AREA - SUMMARY_H;
  ctx.fillStyle = '#d1fae5';
  ctx.beginPath();
  ctx.roundRect(80, summaryY, WIDTH - 160, SUMMARY_H, 16);
  ctx.fill();

  ctx.fillStyle = '#059669';
  ctx.font = `48px ${EMOJI_FONT}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText('✓', 120, summaryY + 50);

  ctx.fillStyle = '#065f46';
  ctx.font = `bold 32px ${FONT_FAMILY}`;
  const sumText = timelineRaw.length > maxRounds
    ? `展示前 ${maxRounds} 轮，共 ${timelineRaw.length} 轮辩论收敛`
    : `经过 ${timeline.length} 轮辩论，AI推理最终收敛`;
  ctx.fillText(sumText, 190, summaryY + 50);

  // 5. Watermark
  drawWatermark(ctx, '* 推理过程由 Multi-Agent Debate 框架自动生成');

  return toPng(canvas);
}
