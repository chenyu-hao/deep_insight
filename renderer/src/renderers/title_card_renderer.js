/**
 * Title Card renderer router.
 *
 * Keeps `title` output stable while allowing style fallback:
 * - apple  (default)
 * - legacy
 */
import renderAppleTitleCard from './title_card_renderer_apple.js';
import renderLegacyTitleCard from './title_card_renderer_legacy.js';

function resolveStyle(data) {
  const payloadStyle = (data && (data.title_style || data.titleStyle || data.style)) || null;
  if (payloadStyle) return String(payloadStyle).toLowerCase();

  const globalStyle = globalThis.__CARD_RENDERER_CONFIG__?.titleStyle;
  if (globalStyle) return String(globalStyle).toLowerCase();

  return 'apple';
}

export default function renderTitleCard(data) {
  const style = resolveStyle(data);
  if (style === 'legacy') return renderLegacyTitleCard(data);
  return renderAppleTitleCard(data);
}
