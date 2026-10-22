import { describe, expect, it } from "vitest";

import homeHtml from "../index.html?raw";

describe("main page (index.html)", () => {
  it("has a title", () => {
    expect(homeHtml).toMatch(/<title>.+<\/title>/);
  });

  it("links to the booking page", () => {
    expect(homeHtml).toContain('href="/booking.html"');
  });

  it("describes the service", () => {
    expect(homeHtml).toMatch(/слот/i);
    expect(homeHtml).toMatch(/звонок/i);
  });
});
