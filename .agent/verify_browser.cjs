// Reproducible phase 4 gate. Pass the installed playwright module directory as argv[2].
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { spawn, spawnSync } = require('node:child_process');
const { chromium } = require(process.argv[2] || 'playwright');
const repo = path.resolve(__dirname, '..');
const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'docsite-browser-'));
const shots = path.join(__dirname, 'shots');
fs.mkdirSync(shots, { recursive: true });
fs.cpSync(path.join(repo, 'docs'), path.join(fixture, 'docs'), {
  recursive: true, filter: p => !/[\\/](dist|cache)([\\/]|$)/.test(p)
});
fs.symlinkSync(path.join(repo, 'node_modules'), path.join(fixture, 'node_modules'), 'junction');
const config = path.join(fixture, 'docs/.vitepress/config.mts');
fs.writeFileSync(config, fs.readFileSync(config, 'utf8').replace("base: '/docsite/'", "base: '/PixivFlow/'"));
fs.writeFileSync(path.join(fixture, 'docs/qa-code.md'), '# Long code\n\n```python\n' +
  Array.from({length: 80}, (_, i) => `result_${i} = "${'long_code_value_'.repeat(20)}"`).join('\n') + '\n```\n');
fs.writeFileSync(path.join(fixture, 'docs/qa-table.md'), '# Long table\n\n| Platform | Asset | Notes |\n| --- | --- | --- |\n' +
  Array.from({length: 40}, (_, i) => `| Linux ${i} | \`${'archive-name-'.repeat(15)}.tar.gz\` | Release asset |`).join('\n'));
const payload = {tag_name: 'v1.2.3', html_url: 'https://github.com/owner/project/releases/tag/v1.2.3',
  published_at: '2026-10-30T00:00:00Z', assets: [{name: 'project-linux-x64.tar.gz', size: 1048576,
  browser_download_url: 'https://github.com/owner/project/releases/download/v1.2.3/project-linux-x64.tar.gz'}]};
fs.writeFileSync(path.join(fixture, 'release.json'), JSON.stringify(payload));
function run(exe, args) {
  const result = spawnSync(exe, args, {cwd: fixture, encoding: 'utf8', env: {...process.env, PYTHONUTF8: '1'}});
  if (result.status !== 0) throw new Error(result.stdout + result.stderr);
  process.stdout.write(result.stdout);
}
run('python', [path.join(repo, 'template/download-page.py'), 'owner/project', '--input-json', 'release.json', '--tag', 'v1.2.3', '--force']);
const cli = path.join(repo, 'node_modules/vitepress/bin/vitepress.js');
run(process.execPath, [cli, 'build', path.join(fixture, 'docs')]);
const server = spawn(process.execPath, [cli, 'preview', path.join(fixture, 'docs'), '--host', '127.0.0.1', '--port', '4175'], {cwd: fixture, stdio: 'ignore'});
const origin = 'http://127.0.0.1:4175';
const pages = {home: '', document: 'QUICKSTART.html', code: 'qa-code.html', table: 'qa-table.html', download: 'download.html', english: 'en/QUICKSTART.html'};
(async () => {
  let browser;
  try {
    for (let i = 0; i < 60; i++) {
      try { if ((await fetch(origin + '/PixivFlow/')).ok) break; } catch {}
      await new Promise(resolve => setTimeout(resolve, 250));
    }
    browser = await chromium.launch({headless: true, channel: process.env.DOCSITE_BROWSER_CHANNEL || 'msedge'});
    const errors = [], checks = [];
    for (const theme of ['light', 'dark']) {
      const context = await browser.newContext({colorScheme: theme});
      const page = await context.newPage();
      page.on('response', r => {if (r.url().startsWith(origin) && r.status() >= 400) errors.push(`${r.status()} ${r.url()}`);});
      page.on('pageerror', e => errors.push(e.message));
      for (const width of [1440, 1024, 390, 320, 430, 768]) {
        await page.setViewportSize({width, height: 1000});
        for (const [name, route] of Object.entries(pages)) {
          await page.goto(origin + '/PixivFlow/' + route, {waitUntil: 'networkidle'});
          await page.locator('.VPDoc').waitFor();
          const metrics = await page.evaluate(() => ({width: innerWidth, scroll: document.documentElement.scrollWidth,
            dark: document.documentElement.classList.contains('dark'), title: document.querySelector('h1')?.textContent}));
          if (metrics.scroll > width + 1 || metrics.dark !== (theme === 'dark')) errors.push(JSON.stringify({name, theme, ...metrics}));
          checks.push({name, theme, ...metrics});
          if ([1440,1024,390].includes(width)) await page.screenshot({path: path.join(shots, `${name}-${theme}-${width}.png`)});
        }
      }
      await context.close();
    }
    const page = await browser.newPage({viewport: {width: 1440, height: 1000}});
    await page.goto(origin + '/PixivFlow/QUICKSTART.html');
    await page.locator('.VPNavBarTranslations button').click();
    await page.locator('.VPNavBarTranslations a').filter({hasText: 'English'}).click();
    await page.waitForURL('**/en/QUICKSTART*');
    await page.locator('.VPNavBarSearch button').click();
    await page.locator('#localsearch-input').fill('VitePress');
    await page.locator('.VPLocalSearchBox .results').waitFor();
    await page.screenshot({path: path.join(shots, 'search.png')});
    const report = {base: '/PixivFlow/', fixture, checks, errors, localeSwitch: page.url(), search: 'VitePress results rendered', download: 'exact tag v1.2.3 generated in zh/en, built and served'};
    fs.writeFileSync(path.join(shots, 'report.json'), JSON.stringify(report, null, 2));
    if (errors.length) throw new Error(JSON.stringify(errors));
    console.log(`PASS: ${checks.length} rendered pages; 36 matrix screenshots; no overflow/HTTP errors.`);
  } finally {if (browser) await browser.close(); server.kill();}
})().catch(e => { console.error(e); process.exitCode = 1; });
