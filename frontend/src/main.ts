import "./styles.css";

import {
  createBooking,
  errorMessage,
  getAvailability,
  listEventTypes,
  type Booking,
  type DaySlots,
  type EventType,
  type Slot,
} from "./api";
import { formatSlotRange, weekdayName } from "./format";

const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;

const typeSelect = document.querySelector<HTMLSelectElement>("#event-type")!;
const typeDescription = document.querySelector<HTMLParagraphElement>("#type-description")!;
const daysEl = document.querySelector<HTMLDivElement>("#days")!;
const statusEl = document.querySelector<HTMLParagraphElement>("#status")!;
const confirmationEl = document.querySelector<HTMLDivElement>("#confirmation")!;
const dialog = document.querySelector<HTMLDialogElement>("#booking-dialog")!;
const form = document.querySelector<HTMLFormElement>("#booking-form")!;
const dialogTitle = document.querySelector<HTMLHeadingElement>("#dialog-title")!;
const dialogError = document.querySelector<HTMLParagraphElement>("#dialog-error")!;
const cancelBtn = document.querySelector<HTMLButtonElement>("#cancel-btn")!;

let eventTypes: EventType[] = [];
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
    button.dataset.start = slot.start;
    button.textContent = formatSlotRange(slot.start, slot.end, timeZone);
    button.addEventListener("click", () => openDialog(slot));
    grid.append(button);
  }
  section.append(grid);
  return section;
}

function renderDays(days: DaySlots[]): void {
  daysEl.replaceChildren();
  if (days.length === 0) {
    statusEl.textContent = "Свободных слотов пока нет.";
    return;
  }
  statusEl.textContent = "";
  for (const day of days) {
    daysEl.append(renderDay(day.date, day.weekday, day.slots));
  }
}

async function loadAvailability(): Promise<void> {
  const id = typeSelect.value;
  if (!id) {
    return;
  }
  const eventType = eventTypes.find((type) => type.id === id);
  typeDescription.textContent = eventType?.description ?? "";
  statusEl.textContent = "Загружаем свободные слоты…";
  daysEl.replaceChildren();
  try {
    const days = await getAvailability(id, 14);
    renderDays(days);
  } catch (error) {
    statusEl.textContent = `Не удалось загрузить слоты: ${errorMessage(error)}`;
  }
}

async function loadEventTypes(): Promise<void> {
  statusEl.textContent = "Загружаем типы встреч…";
  try {
    eventTypes = await listEventTypes();
    typeSelect.replaceChildren();
    for (const type of eventTypes) {
      const option = document.createElement("option");
      option.value = type.id;
      option.textContent = `${type.name} · ${type.duration_minutes} мин`;
      typeSelect.append(option);
    }
    if (eventTypes.length === 0) {
      statusEl.textContent = "Пока нет доступных типов встреч.";
      return;
    }
    await loadAvailability();
  } catch (error) {
    statusEl.textContent = `Не удалось загрузить типы встреч: ${errorMessage(error)}`;
  }
}

function showConfirmation(booking: Booking): void {
  confirmationEl.hidden = false;
  confirmationEl.replaceChildren();

  const heading = document.createElement("strong");
  heading.textContent = "Запись подтверждена";

  const detail = document.createElement("p");
  detail.textContent = `Мы ждём вас ${formatSlotRange(
    booking.slot_start,
    booking.slot_end,
    timeZone,
  )}. Подтверждение отправлено на ${booking.email}.`;

  confirmationEl.append(heading, detail);
  confirmationEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

async function submitBooking(): Promise<void> {
  if (!selected) {
    return;
  }
  dialogError.textContent = "";
  const data = new FormData(form);
  try {
    const booking = await createBooking({
      event_type_id: typeSelect.value,
      slot_start: selected.start,
      name: String(data.get("name") ?? ""),
      email: String(data.get("email") ?? ""),
      comment: String(data.get("comment") ?? ""),
    });
    dialog.close();
    showConfirmation(booking);
    await loadAvailability();
  } catch (error) {
    dialogError.textContent = errorMessage(error);
  }
}

typeSelect.addEventListener("change", () => {
  void loadAvailability();
});
cancelBtn.addEventListener("click", () => dialog.close());
form.addEventListener("submit", (event) => {
  event.preventDefault();
  void submitBooking();
});

void loadEventTypes();
