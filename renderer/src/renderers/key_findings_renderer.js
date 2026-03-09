/**
 * Key Findings Card renderer – mirrors KeyFindingsCanvas.vue generateImage()
 *
 * Input: { findings: [string, string, string] }
 */
import {
  WIDTH, HEIGHT, FONT_FAMILY, EMOJI_FONT,
  createCard, drawGradientBg, drawHeader, wrapText, toPng,
} from './base.js';

export default function renderKeyFindings(data) {
  const canvas = createCard();
  const ctx = canvas.getContext('2d');
  const findings = ((data && data.findings) || []).slice(0, 3);

  // 1. Warm gradient background
  drawGradientBg(ctx, '#fff7ed', '#fef3c7');

  // 2. Header
  drawHeader(ctx, {
    emoji: '✨', title: '关键发现', bgColor: '#fed7aa', textColor: '#78350f',
  });
  const headerBottom = 80 + 120;

  // 3. Findings list
  const listY = headerBottom + 80;
  const spacing = 180;
  const maxW = WIDTH - 280;

  findings.forEach((finding, i) => {
    const itemY = listY + i * spacing;

    // numbered circle
    ctx.fillStyle = '#f97316';
    ctx.beginPath();
    ctx.arc(120, itemY, 35, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#ffffff';
    ctx.font = `bold 48px ${FONT_FAMILY}`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(String(i + 1), 120, itemY);

    // text
    ctx.fillStyle = '#78350f';
    ctx.font = `42px ${FONT_FAMILY}`;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    const lines = wrapText(ctx, finding, maxW);
    lines.forEach((line, li) => ctx.fillText(line, 200, itemY - 20 + li * 60));
  });

  // 4. Decorative wave
  ctx.fillStyle = 'rgba(251,146,60,0.1)';
  ctx.beginPath();
  ctx.moveTo(0, HEIGHT - 200);
  for (let x = 0; x <= WIDTH; x += 50) {
    ctx.lineTo(x, HEIGHT - 200 + Math.sin(x / 100) * 30);
  }
  ctx.lineTo(WIDTH, HEIGHT);
  ctx.lineTo(0, HEIGHT);
  ctx.closePath();
  ctx.fill();

  // 5. Watermark (orange tint matching theme)
  ctx.fillStyle = '#d97706';
  ctx.font = `22px ${FONT_FAMILY}`;
  ctx.textAlign = 'center';
  ctx.fillText('* 关键发现由 LLM 多维度分析自动提取', WIDTH / 2, HEIGHT - 95);
  ctx.font = `24px ${FONT_FAMILY}`;
  ctx.fillText('@观潮GlobalInSight · AI舆情洞察', WIDTH / 2, HEIGHT - 60);

  return toPng(canvas);
}
