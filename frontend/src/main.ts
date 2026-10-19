import "./styles.css";

import { createBooking, getAvailability } from "./api";
import { formatSlotRange, weekdayName } from "./format";
import type { BookingCreate, Slot } from "./types";

const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;

const daysEl = document.querySelector<HTMLDivElement>("#days")!;
const statusEl = document.querySelector<HTMLParagraphElement>("#status")!;
const dialog = document.querySelector<HTMLDialogElement>("#booking-dialog")!;
const form = document.querySelector<HTMLFormElement>("#booking-form")!;
const dialogTitle = document.querySelector<HTMLHeadingElement>("#dialog-title")!;
const dialogError = document.querySelector<HTMLParagraphElement>("#dialog-error")!;
const cancelBtn = document.querySelector<HTMLButtonElement>("#cancel-btn")!;

let selected: Slot | null = null;

function openDialog(slot: Slot): void {
  selected = slot;
  dialogTitle.textContent = `Запись на ${formatSlotRange(slot.start, slot.end, timeZone)}`;
  dialogError.textContent = "";
  form.reset();
  dialog.showModal();
}

function renderDay(date: string, weekday: number, slots: Slot[]): HTMLElement {
  const section = document.createElement("section");
  section.className = "day";

  const heading = document.createElement("h2");
  heading.textContent = `${weekdayName(weekday)}, ${date}`;
  section.append(heading);

  const grid = document.createElement("div");
  grid.className = "slots";
  for (const slot of slots) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "slot";
    button.textContent = formatSlotRange(slot.start, slot.end, timeZone);
    button.addEventListener("click", () => openDialog(slot));
    grid.append(button);
  }
  section.append(grid);
  return section;
}

async function load(): Promise<void> {
  statusEl.textContent = "Загружаем свободные слоты…";
  daysEl.replaceChildren();
  try {
    const days = await getAvailability(14);
    if (days.length === 0) {
      statusEl.textContent = "Свободных слотов пока нет.";
      return;
    }
    statusEl.textContent = "";
    for (const day of days) {
      daysEl.append(renderDay(day.date, day.weekday, day.slots));
    }
  } catch (error) {
    statusEl.textContent = `Не удалось загрузить слоты: ${(error as Error).message}`;
  }
}

async function submitBooking(payload: BookingCreate): Promise<void> {
  dialogError.textContent = "";
  try {
    await createBooking(payload);
    dialog.close();
    await load();
  } catch (error) {
    dialogError.textContent = (error as Error).message;
  }
}

cancelBtn.addEventListener("click", () => dialog.close());

form.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!selected) {
    return;
  }
  const data = new FormData(form);
  void submitBooking({
    slot_start: selected.start,
    name: String(data.get("name") ?? ""),
    email: String(data.get("email") ?? ""),
    comment: String(data.get("comment") ?? ""),
  });
});

void load();
