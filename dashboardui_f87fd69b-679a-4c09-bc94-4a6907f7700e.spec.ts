
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('DashboardUI_2025-08-16', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('http://localhost:3000');

    // Take screenshot
    await page.screenshot({ path: 'dashboard_current_ui.png', { fullPage: true } });

    // Navigate to URL
    await page.goto('http://localhost:3000');

    // Take screenshot
    await page.screenshot({ path: 'dashboard_beautified_ui.png', { fullPage: true } });

    // Navigate to URL
    await page.goto('http://localhost:3000');

    // Take screenshot
    await page.screenshot({ path: 'dashboard_final_beautified.png', { fullPage: true } });
});