// Render infographics to PNG at print size x3.
// usage: node design/infographics/render.js [id ...]   (no ids: every *.html here)
// Writes src/assets/figures/<id>.png and design/infographics/out/<id>.png (a 1x preview).
// Fails if a figure is wider than 672 px, taller than 690 px, or text overflows its box.
const fs = require('fs');
const path = require('path');
const puppeteer = require(path.resolve(__dirname, '../../build/node_modules/puppeteer-core'));

const HERE = __dirname;
const ROOT = path.resolve(HERE, '../..');
const OUT = path.join(ROOT, 'src/assets/figures');
const PREVIEW = path.join(HERE, 'out');
const CHROME = [process.env.CHROME, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/chromium'].filter(Boolean).find(p => fs.existsSync(p));
const MAX_H = 690;

(async () => {
  let ids = process.argv.slice(2);
  if (!ids.length) ids = fs.readdirSync(HERE).filter(f => f.endsWith('.html')).map(f => f.replace(/\.html$/, ''));
  fs.mkdirSync(OUT, {recursive: true}); fs.mkdirSync(PREVIEW, {recursive: true});
  const browser = await puppeteer.launch({executablePath: CHROME, headless: true,
    args: ['--allow-file-access-from-files', '--font-render-hinting=none']});
  let bad = 0;
  for (const id of ids) {
    const page = await browser.newPage();
    page.on('pageerror', e => { console.error(`[${id}] pageerror`, e.message); bad++; });
    page.on('requestfailed', r => { console.error(`[${id}] missing`, r.url()); bad++; });
    await page.setViewport({width: 700, height: 900, deviceScaleFactor: 3});
    await page.goto('file://' + path.join(HERE, id + '.html'), {waitUntil: 'load'});
    await page.evaluate(async () => { await document.fonts.ready; });
    const info = await page.evaluate(() => {
      const fig = document.getElementById('fig');
      if (!fig) return {err: 'no #fig'};
      const r = fig.getBoundingClientRect();
      const over = [];
      fig.querySelectorAll('*').forEach(el => {
        if (el.closest('svg')) return;
        if (el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).overflow !== 'visible') over.push(el.className || el.tagName);
      });
      const fonts = [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family);
      const small = [...fig.querySelectorAll('*')].filter(el => el.childNodes.length && [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()))
        .map(el => parseFloat(getComputedStyle(el).fontSize)).filter(s => s < 11).length;
      const svgSmall = [...fig.querySelectorAll('svg text')].map(t => parseFloat(getComputedStyle(t).fontSize) *
        (t.ownerSVGElement.getBoundingClientRect().width / (t.ownerSVGElement.viewBox.baseVal.width || t.ownerSVGElement.getBoundingClientRect().width))).filter(s => s < 10.5).length;
      return {w: r.width, h: r.height, over, fonts: [...new Set(fonts)], small, svgSmall};
    });
    if (info.err) { console.error(`[${id}] ${info.err}`); bad++; continue; }
    const problems = [];
    if (info.w > 672.5) problems.push(`width ${info.w}`);
    if (info.h > MAX_H) problems.push(`height ${Math.round(info.h)} > ${MAX_H}`);
    if (info.over.length) problems.push(`overflow in ${info.over.slice(0, 3).join(', ')}`);
    if (info.small) problems.push(`${info.small} text runs under 11px`);
    if (info.svgSmall) problems.push(`${info.svgSmall} svg labels under ~10.5px at print size`);
    if (!info.fonts.includes('Fig Sans')) problems.push('kit fonts not loaded');
    const el = await page.$('#fig');
    await el.screenshot({path: path.join(OUT, id + '.png'), omitBackground: false});
    const p2 = await browser.newPage();
    await p2.setViewport({width: 700, height: 900, deviceScaleFactor: 1});
    await p2.goto('file://' + path.join(HERE, id + '.html'), {waitUntil: 'load'});
    await p2.evaluate(async () => { await document.fonts.ready; });
    await (await p2.$('#fig')).screenshot({path: path.join(PREVIEW, id + '.png')});
    await p2.close();
    console.log(`${problems.length ? 'FAIL' : 'ok  '} ${id}  ${Math.round(info.w)}x${Math.round(info.h)}${problems.length ? '  ' + problems.join('; ') : ''}`);
    if (problems.length) bad++;
    await page.close();
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
