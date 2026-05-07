/**
 * render-entry.js — Browser-side entry point loaded by render.html
 *
 * Exposes window.__CARD_RENDERER__ for Playwright to call from server.js.
 */
import * as renderers from './src/renderers/index.js';

const statusNode = document.getElementById('app');

function setStatus(text) {
  if (statusNode) statusNode.textContent = text;
}

window.__CARD_RENDERER__ = {
  ready: false,

  listTypes: () => Object.keys(renderers),

  render: async (type, payload) => {
    const fn = renderers[type];
    if (!fn) throw new Error(`Unknown card type: ${type}`);
    setStatus(`rendering ${type}…`);
    const result = await fn(payload);
    setStatus('done');
    return result;
  },
};

window.__CARD_RENDERER__.ready = true;
setStatus('ready');
