import { describe, expect, it } from "vitest";

import { formatSlotRange, weekdayName } from "./format";

describe("weekdayName", () => {
  it("returns Russian short names", () => {
    expect(weekdayName(0)).toBe("Пн");
    expect(weekdayName(6)).toBe("Вс");
  });

  it("returns an empty string for an out-of-range weekday", () => {
    expect(weekdayName(9)).toBe("");
  });
});

describe("formatSlotRange", () => {
  it("renders a start and end time in the given timezone", () => {
    const range = formatSlotRange(
      "2026-10-19T07:00:00+00:00",
      "2026-10-19T07:30:00+00:00",
      "UTC",
    );
    expect(range).toBe("07:00–07:30");
  });
});
