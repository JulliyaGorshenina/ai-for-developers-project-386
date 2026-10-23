import { expect, test } from "@playwright/test";

test("guest books a slot and the owner sees the meeting", async ({ page }) => {
  await page.goto("/booking.html");

  const eventType = page.locator("#event-type");
  await expect(eventType).toBeVisible();

  const firstSlot = page.locator(".slot").first();
  await expect(firstSlot).toBeVisible();
  await firstSlot.click();

  await page.fill('input[name="name"]', "E2E Гость");
  await page.fill('input[name="email"]', "e2e@example.com");
  await page.fill('textarea[name="comment"]', "проверка сквозного сценария");
  await page.click('#booking-form button[type="submit"]');

  const confirmation = page.locator("#confirmation");
  await expect(confirmation).toBeVisible();
  await expect(confirmation).toContainText("Запись подтверждена");

  await page.goto("/admin.html");
  await expect(page.locator("#bookings")).toContainText("E2E Гость");
});
