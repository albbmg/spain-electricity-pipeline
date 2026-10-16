// Optional real-browser checks; Python/SQL tests create the synthetic input HTML.
// Usage: node tests/browser/dashboard.cjs INPUT_HTML [CHROMIUM_PATH] [CAPTURE_DIR]
const assert = require('node:assert/strict');
const { mkdir } = require('node:fs/promises');
const { resolve, join } = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');

(async () => {
  assert(process.argv[2], 'Provide the synthetic dashboard HTML path');
  const browser = await chromium.launch({
    ...(process.argv[3] ? { executablePath: process.argv[3] } : {}),
    args: ['--disable-gpu', '--disable-dev-shm-usage'],
    headless: true,
  });
  try {
    const context = await browser.newContext({ offline: true, viewport: { width: 1280, height: 1000 } });
    const page = await context.newPage();
    const errors = [];
    const requests = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => {
      if (/^https?:/.test(request.url())) requests.push(request.url());
    });
    await page.goto(pathToFileURL(resolve(process.argv[2])).href);
    assert.equal(await page.locator('.eyebrow').textContent(), 'Synthetic verification data');
    const data = await page.locator('#dashboard-data').textContent().then(JSON.parse);
    const period = page.getByLabel('Period', { exact: true });
    const month = page.getByLabel('Month', { exact: true });
    const classification = page.getByLabel('Classification', { exact: true });
    const comparisonMonth = page.getByLabel('Comparison month', { exact: true });
    let cases = 0;
    let comparisonCases = 0;
    for (const [key, selection] of Object.entries(data.selections)) {
      await period.selectOption(key);
      assert.equal(await month.locator('option').count(), selection.months);
      assert.equal(await page.locator('#generation').textContent(), selection.generation_gwh);
      assert.equal(await page.locator('#share').textContent(), selection.renewable_share);
      assert.equal(await page.locator('#daily').textContent(), selection.daily_gwh);
      assert.equal(await page.locator('#evidence li').count(), selection.evidence.length);
      for (const row of selection.rows) {
        await comparisonMonth.selectOption(row.month);
        const comparison = row.comparison;
        assert.equal(await page.locator('#comparison-result').isVisible(), comparison !== null);
        if (comparison === null) {
          assert.match(await page.locator('#comparison-status').textContent(), /No previous-year comparison/);
          assert.equal(await page.locator('#comparison-rows tr').count(), 0);
          assert.equal(await page.locator('#comparison-current-evidence li').count(), 0);
        } else {
          const actual = await page.locator('#comparison-rows tr').evaluateAll(rows =>
            rows.map(row => Array.from(row.children, cell => cell.textContent)));
          assert.deepEqual(actual, [
            ['Calendar days', String(comparison.previous_days), String(row.days), '—'],
            ['Generation (GWh)', comparison.previous_generation_gwh, row.generation_gwh, comparison.generation_yoy],
            ['Daily average (GWh/day)', comparison.previous_daily_gwh, row.daily_gwh, comparison.daily_yoy],
            ['Renewable share', comparison.previous_renewable_share, row.renewable_share, comparison.share_change_pp + ' pp'],
          ]);
          for (const [id, records] of [['prior', comparison.previous_evidence], ['current', comparison.current_evidence]]) {
            for (const record of records) {
              assert(record[3].endsWith('+00:00') && record[4].endsWith('+00:00'));
            }
            const actualEvidence = await page.locator('#comparison-' + id + '-evidence li').allTextContents();
            assert.deepEqual(actualEvidence, records.map(([identity, first, last, updated, retrieved, sha]) =>
              'Window: ' + first + ' – ' + last + 'Retrieval: ' + identity + 'Provider last update: ' + updated +
              'Retrieved at: ' + retrieved + 'SHA-256: ' + sha));
          }
        }
        comparisonCases++;
        await month.selectOption(row.month);
        for (const kind of ['all', 'renewable', 'non-renewable']) {
          await classification.selectOption(kind);
          const visible = row.technologies.filter(t => kind === 'all' || t.renewable === (kind === 'renewable'));
          const actual = await page.locator('#technology-rows tr').evaluateAll(rows =>
            rows.map(row => Array.from(row.children, cell => cell.textContent)));
          assert.deepEqual(actual, visible.map(t => [
            t.name + 'ID: ' + t.id, t.renewable ? 'Renewable' : 'Non-renewable',
            t.days_observed + ' / ' + row.days, t.generation_gwh, t.system_share,
          ]));
          assert.equal(await page.locator('#technology-empty').isVisible(), visible.length === 0);
          assert.equal(await page.locator('#generation').textContent(), selection.generation_gwh);
          assert.equal(await page.locator('#evidence li').count(), selection.evidence.length);
          assert.equal(await comparisonMonth.inputValue(), row.month);
          cases++;
        }
      }
    }
    // Fixed corner cases independently check sparse, zero and missing observations.
    await period.selectOption('2024');
    await month.selectOption('2024-02');
    await classification.selectOption('all');
    assert.equal(await page.locator('#technology-rows tr').count(), 6);
    const zero = page.locator('#technology-rows tr').filter({ hasText: 'ID: zero' });
    assert.match(await zero.textContent(), /1 \/ 290\.0000\.00%/);
    const rare = page.locator('#technology-rows tr').filter({ hasText: 'ID: rare' });
    assert.match(await rare.textContent(), /1 \/ 290\.1000\.34%/);
    await period.selectOption('all');
    assert.equal(await month.inputValue(), '2024-02');
    await period.selectOption('2025');
    assert.equal(await month.inputValue(), '2025-12');
    await month.selectOption('2025-03');
    await classification.selectOption('non-renewable');
    assert.equal(await page.locator('#technology-rows tr').count(), 0);
    assert(await page.locator('#technology-empty').isVisible());

    // Keyboard activation and focusable mobile overflow preserve access to all columns.
    await period.selectOption('2024');
    await month.selectOption('2024-02');
    await classification.focus();
    await page.keyboard.press('Home');
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('Escape');
    assert.equal(await classification.inputValue(), 'renewable');
    assert.equal(await page.locator('#technology-rows tr').count(), 3);
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(() => document.activeElement.getAttribute('role')), 'region');
    await classification.selectOption('all');
    const captures = process.argv[4];
    if (captures) {
      await mkdir(captures, { recursive: true });
      await page.screenshot({ path: join(captures, 'technology-desktop.png'), fullPage: true });
    }
    await page.setViewportSize({ width: 390, height: 844 });
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    const scroll = page.getByRole('region', { name: 'Technology values, scroll horizontally on small screens' });
    await scroll.focus();
    await page.keyboard.press('End');
    await scroll.evaluate(element => { element.scrollLeft = element.scrollWidth; });
    assert(await scroll.evaluate(element => element.scrollLeft > 0));
    if (captures) {
      await page.screenshot({ path: join(captures, 'technology-mobile.png'), fullPage: true });
    }
    await period.selectOption('2025');
    await comparisonMonth.selectOption('2025-02');
    assert.equal(await page.locator('#comparison-prior').textContent(), '2024-02');
    assert.equal(await page.locator('#comparison-rows tr').nth(1).locator('td').last().textContent(), '+93.10%');
    assert.equal(await page.locator('#comparison-rows tr').nth(2).locator('td').last().textContent(), '+100.00%');
    await page.locator('#comparison-evidence-title').click();
    assert(await page.locator('#comparison-prior-evidence').isVisible());
    await comparisonMonth.focus();
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('Escape');
    assert.equal(await comparisonMonth.inputValue(), '2025-03');
    assert.equal(await page.locator('#comparison-current-evidence-title').textContent(), '2025-03');
    await comparisonMonth.selectOption('2025-02');
    await period.selectOption('all');
    assert.equal(await comparisonMonth.inputValue(), '2025-02');
    await period.selectOption('2024');
    assert.equal(await comparisonMonth.inputValue(), '2024-12');
    assert(!(await page.locator('#comparison-result').isVisible()));
    await period.selectOption('2025');
    await comparisonMonth.selectOption('2025-02');
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    const comparisonScroll = page.getByRole('region', { name: 'Year-on-year comparison values, scroll horizontally on small screens' });
    await comparisonScroll.evaluate(element => { element.scrollLeft = element.scrollWidth; });
    assert(await comparisonScroll.evaluate(element => element.scrollLeft > 0));
    if (captures) {
      await page.locator('[aria-labelledby="comparison-title"]').screenshot({ path: join(captures, 'comparison-mobile.png') });
      await page.setViewportSize({ width: 1280, height: 1000 });
      await page.locator('[aria-labelledby="comparison-title"]').screenshot({ path: join(captures, 'comparison-desktop.png') });
    }
    assert.deepEqual(errors, []);
    assert.deepEqual(requests, []);
    console.log(JSON.stringify({ browser: browser.version(), filterCases: cases, comparisonCases, offline: true,
      desktopWidth: 1280, mobileWidth: 390, pageErrors: errors.length, httpRequests: requests.length }));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
