#!/usr/bin/env node
// Opens one URL on phone, tablet and desktop in Chromium, Firefox and WebKit,
// and writes a JSON report plus full-page screenshots. Every signal is always
// present in the report, so a 0 is a measure, not a missing check.
//
//   node probe-viewports.mjs <url> [--engines chromium,firefox,webkit]
//        [--widths 699,901] [--click <selector>]... [--storage-state <file>] [--out <dir>]
//
// Playwright is resolved from the current directory (the project under test),
// so run it from a folder where `playwright` or `@playwright/test` is installed.
// --click is opt-in: clicking every button of a real app can delete or submit.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const USAGE = 'usage: node probe-viewports.mjs <url> [--engines chromium,firefox,webkit] [--widths 699,901] [--click <selector>]... [--storage-state <file>] [--out <dir>]';
const SIGNALS = ['overflowX', 'clipped', 'smallTargets', 'closeTargets', 'imgNoAlt', 'lowContrast',
  'vhRules', 'unsupportedCss', 'pageErrors', 'httpErrors', 'requestsFailed', 'console', 'clickTimeouts'];
// What a headless engine on Linux cannot show of a real iPhone.
const NOT_VERIFIED = ['iOS address bar over 100vh', 'safe-area-inset', 'iOS zoom on inputs under 16px', 'real device identity (navigator.platform says Linux)'];
const DESKTOP = { chromium: 'Desktop Chrome', firefox: 'Desktop Firefox', webkit: 'Desktop Safari' };
const VIEWPORTS = {
  mobile: { device: 'iPhone 15', size: { width: 390, height: 844 } },
  tablet: { device: 'iPad (gen 7)', size: { width: 820, height: 1180 } },
  desktop: { device: null, size: { width: 1280, height: 900 } },
};

export function parseArgs(argv) {
  const opts = { url: null, engines: ['chromium', 'firefox', 'webkit'], widths: [], clicks: [], storageState: null, out: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i], next = () => { if (i + 1 >= argv.length) throw new Error(`${a} needs a value\n${USAGE}`); return argv[++i]; };
    if (a === '--engines') opts.engines = next().split(',').filter(Boolean);
    else if (a === '--widths') opts.widths = next().split(',').filter(Boolean).map(Number);
    else if (a === '--click') opts.clicks.push(next());
    else if (a === '--storage-state') opts.storageState = next();
    else if (a === '--out') opts.out = next();
    else if (a.startsWith('--')) throw new Error(`unknown option ${a}\n${USAGE}`);
    else if (!opts.url) opts.url = a;
    else throw new Error(`one URL only\n${USAGE}`);
  }
  if (!opts.url) throw new Error(USAGE);
  const badEngine = opts.engines.find((e) => !DESKTOP[e]);
  if (badEngine) throw new Error(`unknown engine ${badEngine}`);
  const badWidth = opts.widths.find((w) => !Number.isInteger(w) || w < 200);
  if (badWidth !== undefined) throw new Error(`bad width ${badWidth}`);
  return opts;
}

async function loadPlaywright() {
  const require = createRequire(path.join(process.cwd(), 'noop.js'));
  for (const name of ['playwright', '@playwright/test']) {
    let mod;
    try { mod = await import(pathToFileURL(require.resolve(name)).href); } catch { continue; }
    return mod.chromium ? mod : mod.default; // CommonJS entry: named exports sit under default

  }
  throw new Error(`playwright not found from ${process.cwd()}: run from the project, or npm i -D playwright`);
}

function contextOptions(devices, engine, name) {
  const vp = VIEWPORTS[name];
  const size = vp ? vp.size : { width: Number(name.slice(1)), height: 900 };
  const o = { ...devices[vp?.device || DESKTOP[engine]], viewport: size, screen: size };
  delete o.defaultBrowserType;
  if (engine === 'firefox') delete o.isMobile; // Firefox rejects it
  return o;
}

// Runs inside the page. Same checks as the claude-browser-eyes-bench audit.
async function audit() {
  const out = { notes: [] };
  const label = (e) => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.classList.length ? '.' + [...e.classList].join('.') : '');
  // Emulated Chromium widens innerWidth on an overflowing page; screen.width does not move.
  const coarse = matchMedia('(pointer:coarse)').matches;
  const W = coarse ? Math.min(innerWidth, screen.width || innerWidth) : innerWidth;
  out.viewport = { w: W, innerW: innerWidth, screenW: screen.width, h: innerHeight, dpr: devicePixelRatio, scrollW: document.documentElement.scrollWidth };

  out.overflowX = document.documentElement.scrollWidth > W + 1
    ? [...document.querySelectorAll('body *')].filter((e) => e.getBoundingClientRect().right > W + 1).slice(0, 5).map(label)
    : [];

  const targets = [...document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea')]
    .filter((e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; });
  out.smallTargets = targets.filter((e) => { const r = e.getBoundingClientRect(); return r.height < 44 || r.width < 44; })
    .map((e) => { const r = e.getBoundingClientRect(); return `${label(e)} ${Math.round(r.width)}x${Math.round(r.height)}`; });
  out.closeTargets = [];
  for (let i = 0; i < targets.length; i++) {
    for (let j = i + 1; j < targets.length; j++) {
      const a = targets[i].getBoundingClientRect(), b = targets[j].getBoundingClientRect();
      const gap = Math.hypot(Math.max(0, a.left - b.right, b.left - a.right), Math.max(0, a.top - b.bottom, b.top - a.bottom));
      if (gap < 8 && (a.height < 44 || b.height < 44)) out.closeTargets.push(`${label(targets[i])} ${label(targets[j])} ${Math.round(gap)}px`);
    }
  }

  out.imgNoAlt = [...document.querySelectorAll('img')].filter((i) => !i.hasAttribute('alt')).map((i) => i.getAttribute('src'));

  const parse = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const bg = (e) => { while (e) { const c = parse(getComputedStyle(e).backgroundColor); if (c && c.a > 0.9) return c; e = e.parentElement; } return { r: 255, g: 255, b: 255, a: 1 }; };
  out.lowContrast = [];
  for (const e of document.querySelectorAll('body *')) {
    if (![...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
    const fg = parse(getComputedStyle(e).color);
    if (!fg) continue; // oklch() and friends are not parsed: listed in notes below
    const l1 = lum(fg), l2 = lum(bg(e));
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    if (ratio < 4.5) out.lowContrast.push(`${label(e)} ${ratio.toFixed(2)}`);
  }
  if ([...document.querySelectorAll('body *')].some((e) => !/^rgba?\(/.test(getComputedStyle(e).color))) out.notes.push('some text colours are not rgb(): their contrast is not measured');

  out.clipped = [...document.querySelectorAll('body *')].filter((e) => {
    const s = getComputedStyle(e);
    return (s.overflow === 'hidden' || s.overflowY === 'hidden') && e.clientHeight > 0 && e.scrollHeight > e.clientHeight + 1;
  }).map((e) => `${label(e)} ${e.scrollHeight}>${e.clientHeight}`);

  // Static: in a headless engine 100vh equals innerHeight, so only the stylesheet shows it.
  out.vhRules = [];
  const sheets = [];
  const collect = (ss) => {
    if (sheets.includes(ss)) return;
    sheets.push(ss);
    let rules;
    try { rules = [...ss.cssRules]; } catch { out.notes.push('unreadable stylesheet: ' + (ss.href || 'inline')); return; }
    rules.forEach(walk);
  };
  const walk = (rule) => {
    if (rule.styleSheet) collect(rule.styleSheet);
    if (rule.style && /(^|[^a-z0-9.])\d*\.?\d+[l]?vh\b/.test(rule.style.height + ' ' + rule.style.minHeight + ' ' + rule.style.maxHeight)) {
      out.vhRules.push(rule.selectorText + ' {' + (rule.style.height || rule.style.minHeight || rule.style.maxHeight) + '}');
    }
    if (rule.cssRules) [...rule.cssRules].forEach(walk);
  };
  for (const ss of document.styleSheets) collect(ss);

  // A rejected declaration is dropped from the CSSOM, so read the stylesheet text.
  // The lookahead keeps an @supports (calc-size(...)) guard from counting as a use.
  const FEATURES = [/([a-z-]+)\s*:\s*(calc-size\((?:[^()]|\([^()]*\))*\))\s*(?=[;}!]|$)/g];
  out.unsupportedCss = [];
  for (const ss of sheets) {
    let text = '';
    try { text = ss.href ? await (await fetch(ss.href)).text() : (ss.ownerNode ? ss.ownerNode.textContent : ''); } catch { out.notes.push('stylesheet text not read: ' + (ss.href || 'inline')); continue; }
    text = text.replace(/\/\*[\s\S]*?\*\//g, '');
    for (const re of FEATURES) for (const m of text.matchAll(re)) if (!CSS.supports(m[1], m[2])) out.unsupportedCss.push(m[1] + ': ' + m[2]);
  }
  return out;
}

async function probe(pw, browser, engine, name, opts) {
  const ctx = await browser.newContext({ ...contextOptions(pw.devices, engine, name), storageState: opts.storageState || undefined });
  const page = await ctx.newPage();
  let phase = 'load';
  const events = { pageErrors: [], httpErrors: [], requestsFailed: [], console: [], clickTimeouts: [] };
  // Listeners before goto, or the load-time 404 is never seen.
  page.on('console', (m) => { if (m.type() === 'error') events.console.push(`${phase}: ${m.text()}`); });
  page.on('pageerror', (e) => events.pageErrors.push(`${phase}: ${e.message || e}`));
  page.on('response', (r) => { if (r.status() >= 400) events.httpErrors.push(`${phase}: ${r.status()} ${r.url()}`); });
  page.on('requestfailed', (r) => events.requestsFailed.push(`${phase}: ${r.failure()?.errorText} ${r.url()}`));
  await page.goto(opts.url, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready.then(() => null));
  const timing = await page.evaluate(() => {
    const n = performance.getEntriesByType('navigation')[0];
    const requests = performance.getEntriesByType('resource');
    const slowest = [...requests].sort((a, b) => b.duration - a.duration).slice(0, 3).map((r) => `${Math.round(r.duration)}ms ${r.name}`);
    return n && { ttfbMs: Math.round(n.responseStart), domReadyMs: Math.round(n.domContentLoadedEventEnd), loadMs: Math.round(n.loadEventEnd), requests: requests.length, slowest };
  });
  const shot = path.join(opts.out, `${engine}-${name}.png`);
  await page.screenshot({ path: shot, fullPage: true });
  const findings = await page.evaluate(audit);
  let clicked = 0;
  for (const selector of opts.clicks) {
    phase = `click ${selector}`;
    const all = page.locator(selector);
    const n = await all.count();
    if (!n) findings.notes.push(`--click ${selector}: no match`);
    for (let i = 0; i < n; i++) {
      try { await all.nth(i).click({ timeout: 3000 }); } catch (e) {
        if (e.name !== 'TimeoutError') throw e;
        // Emulated Chromium on an overflowing page: WebKit and Firefox click fine.
        events.clickTimeouts.push(`${selector}[${i}]`);
        await all.nth(i).dispatchEvent('click');
      }
      clicked++;
    }
  }
  if (clicked) await page.waitForTimeout(300);
  await ctx.close();
  const { notes, viewport, ...rest } = findings;
  const signals = { ...rest, ...events };
  return { viewport, timing, counts: Object.fromEntries(SIGNALS.map((s) => [s, signals[s].length])), clicked, signals, notes, screenshot: shot };
}

export async function run(opts) {
  opts.out = path.resolve(opts.out || fs.mkdtempSync(path.join(os.tmpdir(), 'probe-viewports-')));
  fs.mkdirSync(opts.out, { recursive: true });
  const pw = await loadPlaywright();
  const names = [...Object.keys(VIEWPORTS), ...opts.widths.map((w) => `w${w}`)];
  const report = { url: opts.url, generatedAt: new Date().toISOString(), clicks: opts.clicks, notVerified: NOT_VERIFIED, engines: {} };
  for (const engine of opts.engines) {
    const browser = await pw[engine].launch();
    report.engines[engine] = { version: browser.version(), viewports: {} };
    try {
      for (const name of names) report.engines[engine].viewports[name] = await probe(pw, browser, engine, name, opts);
    } finally { await browser.close(); }
  }
  const file = path.join(opts.out, 'report.json');
  fs.writeFileSync(file, JSON.stringify(report, null, 2));
  return { report, file };
}

export function summary({ report, file }) {
  const lines = [];
  for (const [engine, e] of Object.entries(report.engines)) {
    for (const [name, v] of Object.entries(e.viewports)) {
      const hits = Object.entries(v.counts).filter(([, n]) => n).map(([s, n]) => `${s} ${n}`);
      lines.push(`${engine} ${name} ${v.viewport.w}px load ${v.timing?.loadMs ?? '?'}ms: ${hits.join(', ') || 'clean'}${report.clicks.length ? ` (${v.clicked} clicks)` : ''}${v.notes.length ? ` [${v.notes.length} notes]` : ''}`);
    }
  }
  lines.push(`clicks: ${report.clicks.length ? report.clicks.join(' ') : 'none requested, errors on click not measured'}`);
  lines.push(`not verified: ${report.notVerified.join('; ')}`);
  lines.push(`report: ${file}`);
  return lines.join('\n');
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    console.log(summary(await run(parseArgs(process.argv.slice(2)))));
  } catch (e) {
    console.error(e.message);
    process.exit(1);
  }
}
