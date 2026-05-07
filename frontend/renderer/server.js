/**
 * GlobalInSight Renderer Service
 *
 * Headless Chromium service that loads a Vite-built render bundle and
 * executes Canvas 2D card renderers via Playwright.
 *
 * Endpoints:
 *   POST /render/:type   — render a card; body = payload JSON
 *   GET  /types          — list available card types
 *   GET  /healthz        — health check
 *
 * Environment variables:
 *   PORT              — listen port (default 3001)
 *   RENDER_APP_URL    — override base URL for the render bundle
 */

import express from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const PORT = parseInt(process.env.PORT || '3001', 10);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DIST_DIR = path.join(__dirname, 'dist');
const RENDER_APP_URL = process.env.RENDER_APP_URL || `http://127.0.0.1:${PORT}`;
const RENDER_ROUTE = '/render.html';
const PAGE_TIMEOUT = 30_000;
const RENDER_TIMEOUT = 20_000;
const TITLE_CARD_STYLE = process.env.TITLE_CARD_STYLE || 'apple';

// ── Browser lifecycle ──────────────────────────────────────────────
let browser = null;
let browserContext = null;

async function initBrowser() {
  browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  browserContext = await browser.newContext({
    viewport: { width: 1120, height: 1500 },
    deviceScaleFactor: 1,
  });
  console.log('[renderer] Browser launched');
}

async function getReadyPage() {
  const page = await browserContext.newPage();
  await page.addInitScript((config) => {
    window.__CARD_RENDERER_CONFIG__ = config;
  }, {
    titleStyle: configOrDefault(TITLE_CARD_STYLE),
  });
  await page.goto(`${RENDER_APP_URL}${RENDER_ROUTE}`, {
    waitUntil: 'networkidle',
    timeout: PAGE_TIMEOUT,
  });
  await page.waitForFunction(() => window.__CARD_RENDERER__?.ready === true, {
    timeout: PAGE_TIMEOUT,
  });
  return page;
}

function configOrDefault(style) {
  const normalized = String(style || '').trim().toLowerCase();
  return normalized === 'legacy' ? 'legacy' : 'apple';
}

// ── Express app ────────────────────────────────────────────────────
const app = express();
app.use(express.json({ limit: '10mb' }));
app.use(express.static(DIST_DIR));

const VALID_TYPES = [
  'title', 'insight', 'debate_timeline',
  'trend', 'radar', 'key_findings', 'platform_heat',
];

const TYPE_ALIASES = {
  'debate-timeline': 'debate_timeline',
  'key-findings': 'key_findings',
  'platform-heat': 'platform_heat',
};

app.get('/healthz', (_req, res) => {
  res.json({ status: 'ok', browser: !!browser });
});

app.get('/types', async (_req, res) => {
  res.json({ types: VALID_TYPES });
});

app.post('/render/:type', async (req, res) => {
  const rawType = req.params.type;
  const cardType = TYPE_ALIASES[rawType] || rawType;

  if (!VALID_TYPES.includes(cardType)) {
    return res.status(400).json({
      success: false,
      error: `Unknown card type: ${rawType}. Valid: ${VALID_TYPES.join(', ')}`,
    });
  }

  let page = null;
  try {
    page = await getReadyPage();

    const result = await page.evaluate(
      async ({ type, payload }) => window.__CARD_RENDERER__.render(type, payload),
      { type: cardType, payload: req.body },
    );

    res.json({
      success: true,
      image_data_url: result,
      width: 1080,
      height: 1440,
      mime_type: 'image/png',
    });
  } catch (err) {
    console.error(`[renderer] Error rendering ${cardType}:`, err.message);
    res.status(500).json({ success: false, error: err.message });
  } finally {
    if (page) await page.close().catch(() => {});
  }
});

// ── Start ──────────────────────────────────────────────────────────
async function main() {
  await initBrowser();
  app.listen(PORT, () => {
    console.log(`[renderer] Listening on http://0.0.0.0:${PORT}`);
    console.log(`[renderer] Render app URL: ${RENDER_APP_URL}`);
    console.log(`[renderer] Card types: ${VALID_TYPES.join(', ')}`);
  });
}

process.on('SIGINT', async () => {
  console.log('[renderer] Shutting down…');
  if (browser) await browser.close();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  if (browser) await browser.close();
  process.exit(0);
});

main().catch((err) => {
  console.error('[renderer] Fatal:', err);
  process.exit(1);
});
