import { test, expect } from '@playwright/test';

test('landing page renders topic picker', async ({ page }) => {
  await page.goto('http://localhost:3000/');
  await expect(page.getByRole('heading', { name: 'AI Debate Partner' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Start debate' })).toBeVisible();
});
