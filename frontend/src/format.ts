export const WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"] as const;

export function weekdayName(weekday: number): string {
  return WEEKDAYS[weekday] ?? "";
}

function formatTime(iso: string, timeZone: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone,
  }).format(new Date(iso));
}

export function formatSlotRange(startIso: string, endIso: string, timeZone: string): string {
  return `${formatTime(startIso, timeZone)}–${formatTime(endIso, timeZone)}`;
}
