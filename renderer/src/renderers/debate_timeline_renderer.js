/**
 * Debate Timeline renderer
 *
 * Input: { timeline: [{ round, title, insight, summary }] }
 */
import {
  WIDTH, HEIGHT, FONT_FAMILY,
  createCard, drawAppleBackdrop, drawAmbientOrbs,
  drawHeader, drawPanel, drawSectionLabel, drawWatermark,
  wrapText, clampLines, toPng,
} from './base.js';

const ACCENT = '#5e5ce6';

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
  const minCardH = 128;
  const maxCardH = 206;
  const safeCount = Math.max(roundCount, 1);
  const spacePerRound = availableHeight / safeCount;
  let cardH = Math.floor(spacePerRound * 0.74);
  cardH = Math.max(minCardH, Math.min(maxCardH, cardH));

  let titleFont;
  let contentFont;
  if (cardH >= 182) {
    titleFont = 33;
    contentFont = 25;
  } else if (cardH >= 158) {
    titleFont = 31;
    contentFont = 24;
  } else {
    titleFont = 28;
    contentFont = 22;
  }

  return {
    itemSpacing: spacePerRound,
    cardHeight: cardH,
    titleFont,
    contentFont,
  };
}

export default function renderDebateTimeline(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');

  const timelineRaw = normalizeTimeline(data);
  const timeline = timelineRaw.slice(0, 8);

  drawAppleBackdrop(ctx, {
    start: '#f8f9fc',
    end: '#edf1f7',
    topLight: '#ffffff',
    bottomTint: '#ddd6fe',
    textureAlpha: 0.012,
  });
  drawAmbientOrbs(ctx, [
    { x: 190, y: 1180, r: 260, color: '#dbeafe', alpha: 0.16 },
    { x: 940, y: 220, r: 220, color: '#ddd6fe', alpha: 0.2 },
  ]);

  const headerBottom = drawHeader(ctx, {
    emoji: '🔀',
    title: '辩论演化过程',
    bgColor: '#ddd6fe',
    textColor: '#0f172a',
  });

  const trackPanelY = headerBottom + 44;
  drawPanel(ctx, 56, trackPanelY, WIDTH - 112, 986, {
    radius: 34,
    fill: 'rgba(255,255,255,0.66)',
    stroke: 'rgba(255,255,255,0.88)',
    shadow: 'rgba(15, 23, 42, 0.06)',
    shadowBlur: 24,
    shadowY: 10,
  });
  drawSectionLabel(ctx, '推理时间线', 100, trackPanelY + 34, ACCENT);

  const PAD_TOP = 130;
  const SUMMARY_H = 102;
  const PAD_BOTTOM = 38;
  const areaTop = trackPanelY + PAD_TOP;
  const areaBottom = trackPanelY + 986 - SUMMARY_H - PAD_BOTTOM;
  const availableHeight = areaBottom - areaTop;
  const layout = calculateLayout(timeline.length, availableHeight);

  const timelineHeight = (timeline.length - 1) * layout.itemSpacing;
  const startY = areaTop + layout.cardHeight / 2 + (availableHeight - timelineHeight - layout.cardHeight) / 2;

  const circleX = 140;
  const cardX = 236;
  const cardW = WIDTH - cardX - 84;

  timeline.forEach((item, idx) => {
    const centerY = startY + idx * layout.itemSpacing;

    if (idx < timeline.length - 1) {
      ctx.strokeStyle = 'rgba(94, 92, 230, 0.34)';
      ctx.lineWidth = 2.5;
      ctx.setLineDash([9, 9]);
      ctx.beginPath();
      ctx.moveTo(circleX, centerY + 40);
      ctx.lineTo(circleX, centerY + layout.itemSpacing - 40);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    const dotGradient = ctx.createLinearGradient(circleX - 42, centerY - 42, circleX + 42, centerY + 42);
    dotGradient.addColorStop(0, '#7c3aed');
    dotGradient.addColorStop(1, '#5e5ce6');
    ctx.fillStyle = dotGradient;
    ctx.beginPath();
    ctx.arc(circleX, centerY, 40, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#ffffff';
    ctx.font = `700 34px ${FONT_FAMILY}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`R${item.round}`, circleX, centerY + 1);

    const cardY = centerY - layout.cardHeight / 2;
    drawPanel(ctx, cardX, cardY, cardW, layout.cardHeight, {
      radius: 24,
      fill: 'rgba(255,255,255,0.62)',
      stroke: 'rgba(255,255,255,0.86)',
      shadow: 'rgba(94, 92, 230, 0.1)',
      shadowBlur: 16,
      shadowY: 6,
    });

    ctx.fillStyle = 'rgba(94, 92, 230, 0.11)';
    roundRect(ctx, cardX + 18, cardY + 16, cardW - 36, layout.cardHeight - 32, 16);
    ctx.fill();

    ctx.fillStyle = '#0f172a';
    ctx.font = `700 ${layout.titleFont}px ${FONT_FAMILY}`;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    const titleRaw = item.title || `第${idx + 1}轮`;
    const title = titleRaw.length > 18 ? `${titleRaw.slice(0, 18)}…` : titleRaw;
    ctx.fillText(title, cardX + 26, cardY + 18);

    ctx.fillStyle = 'rgba(71,85,105,0.94)';
    ctx.font = `520 ${layout.contentFont}px ${FONT_FAMILY}`;
    const content = extractKeyPoint(item) || '等待更多辩论内容。';
    const lines = clampLines(wrapText(ctx, content, cardW - 52), 3);
    lines.forEach((line, lineIdx) => {
      ctx.fillText(line || ' ', cardX + 26, cardY + 20 + layout.titleFont + 12 + lineIdx * (layout.contentFont + 8));
    });
  });

  const summaryY = trackPanelY + 986 - SUMMARY_H - 20;
  drawPanel(ctx, 82, summaryY, WIDTH - 164, SUMMARY_H, {
    radius: 18,
    fill: 'rgba(248,250,252,0.82)',
    stroke: 'rgba(226,232,240,0.9)',
    shadow: 'rgba(15, 23, 42, 0.03)',
    shadowBlur: 10,
    shadowY: 4,
  });

  const summaryText = data && Array.isArray(data.timeline) && data.timeline.length > 8
    ? `展示前 8 轮，共 ${data.timeline.length} 轮辩论推演`
    : `共 ${timelineRaw.length} 轮推演，结论逐步收敛`;
  ctx.fillStyle = '#334155';
  ctx.font = `620 30px ${FONT_FAMILY}`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText(summaryText, 116, summaryY + SUMMARY_H / 2 + 1);

  drawWatermark(ctx, '* 推理过程由 Multi-Agent Debate 框架自动生成');
  return toPng(canvas);
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, r);
}
