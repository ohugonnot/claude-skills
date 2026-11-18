// node --test probe-viewports.test.mjs
// The browser test needs Playwright and its browsers resolvable from the
// current directory; it is skipped otherwise. The argument tests always run.
import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { parseArgs, run, summary } from './probe-viewports.mjs';

test('parseArgs reads url, engines, widths and repeated clicks', () => {
  const opts = parseArgs(['http://x/', '--engines', 'webkit', '--widths', '699,901', '--click', '#a', '--click', '.b']);
  assert.deepEqual(opts.engines, ['webkit']);
  assert.deepEqual(opts.widths, [699, 901]);
  assert.deepEqual(opts.clicks, ['#a', '.b']);
});

test('parseArgs rejects what would silently skip a check', () => {
  assert.throws(() => parseArgs([]), /usage/);
  assert.throws(() => parseArgs(['http://x/', '--engines', 'chrome']), /unknown engine chrome/);
  assert.throws(() => parseArgs(['http://x/', '--widths', '7OO']), /bad width/);
  assert.throws(() => parseArgs(['http://x/', '--click']), /needs a value/);
  assert.throws(() => parseArgs(['http://x/', '--clik', 'a']), /unknown option/);
});

const BROKEN = `<!doctype html><meta name=viewport content="width=device-width">
<div style="width:600px">wide</div>
<img src="/missing.png">
<button id=go style="height:20px" onclick="notDefined()">go</button>`;
const CLEAN = `<!doctype html><meta name=viewport content="width=device-width">
<p>ok</p><button id=go style="min-height:44px;min-width:44px" onclick="1">go</button>`;
const tallPage = (px) => `<!doctype html><meta name=viewport content="width=device-width">
<body style="margin:0"><div style="height:${px}px">tall</div>`;

let hasPlaywright = true;
try { createRequire(path.join(process.cwd(), 'noop.js')).resolve('playwright'); } catch { hasPlaywright = false; }

test('a broken page shows each defect, a clean one shows none', { skip: !hasPlaywright && 'playwright not installed here' }, async () => {
  const server = http.createServer((req, res) => {
    const page = { '/broken': BROKEN, '/clean': CLEAN, '/tall': tallPage(3000), '/huge': tallPage(9000) }[req.url];
    res.writeHead(page ? 200 : 404, { 'content-type': 'text/html' }).end(page || 'no');
  });
  await new Promise((ok) => server.listen(0, '127.0.0.1', ok));
  const base = `http://127.0.0.1:${server.address().port}`;
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'probe-test-'));
  try {
    const broken = await run({ url: `${base}/broken`, engines: ['chromium'], widths: [], clicks: ['#go'], storageState: null, out: path.join(out, 'b') });
    const mobile = broken.report.engines.chromium.viewports.mobile;
    assert.equal(mobile.counts.overflowX > 0, true);
    assert.equal(mobile.viewport.w, 390, 'width is screen.width, not the widened innerWidth');
    assert.equal(mobile.counts.imgNoAlt, 1);
    assert.equal(mobile.counts.smallTargets, 1);
    assert.match(mobile.signals.httpErrors[0], /^load: 404 .*missing\.png/);
    assert.match(mobile.signals.pageErrors[0], /^click #go: .*notDefined/);
    assert.equal(broken.report.engines.chromium.viewports.desktop.counts.overflowX, 0);
    assert.ok(mobile.screenshots.length >= 1 && mobile.screenshots.every((f) => fs.existsSync(f)));
    assert.match(summary(broken), /chromium mobile 390px load \d+ms: overflowX/);

    // Claude shrinks any image whose long side passes 2576 px: a tall page must come as
    // screen-high slices, one pixel per CSS pixel even on a density-3 phone profile.
    const tall = await run({ url: `${base}/tall`, engines: ['chromium'], widths: [], clicks: [], storageState: null, out: path.join(out, 't') });
    const tallMobile = tall.report.engines.chromium.viewports.mobile;
    assert.equal(tallMobile.screenshots.length, 4, '3000 px page in 844 px screens');
    for (const f of tallMobile.screenshots) {
      const png = fs.readFileSync(f);
      assert.equal(png.readUInt32BE(16), 390, 'css scale, not 390 x 3');
      assert.ok(png.readUInt32BE(20) <= 844);
    }
    const huge = await run({ url: `${base}/huge`, engines: ['chromium'], widths: [], clicks: [], storageState: null, out: path.join(out, 'h') });
    const hugeMobile = huge.report.engines.chromium.viewports.mobile;
    assert.equal(hugeMobile.screenshots.length, 6);
    assert.ok(hugeMobile.notes.some((n) => /screenshots stop at 6 screens/.test(n)));

    const clean = await run({ url: `${base}/clean`, engines: ['chromium'], widths: [], clicks: [], storageState: null, out: path.join(out, 'c') });
    for (const v of Object.values(clean.report.engines.chromium.viewports)) {
      assert.deepEqual(Object.values(v.counts).filter(Boolean), []);
    }
    assert.match(summary(clean), /clicks: none requested, errors on click not measured/);
  } finally {
    server.close();
    fs.rmSync(out, { recursive: true, force: true });
  }
});
