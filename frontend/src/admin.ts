import "./styles.css";

import {
  cancelBooking,
  createEventType,
  deleteEventType,
  errorMessage,
  getSchedule,
  listBookings,
  listEventTypes,
  updateSchedule,
  type Booking,
  type EventType,
  type Window,
} from "./api";
import { weekdayName } from "./format";

const scheduleRows = document.querySelector<HTMLDivElement>("#schedule-rows")!;
const addWindowBtn = document.querySelector<HTMLButtonElement>("#add-window")!;
const saveScheduleBtn = document.querySelector<HTMLButtonElement>("#save-schedule")!;
const scheduleStatus = document.querySelector<HTMLParagraphElement>("#schedule-status")!;

const typesEl = document.querySelector<HTMLDivElement>("#event-types")!;
const typeForm = document.querySelector<HTMLFormElement>("#event-type-form")!;
const typesStatus = document.querySelector<HTMLParagraphElement>("#types-status")!;

const bookingsEl = document.querySelector<HTMLDivElement>("#bookings")!;
const bookingsStatus = document.querySelector<HTMLParagraphElement>("#bookings-status")!;

const typeById = new Map<string, EventType>();

function renderWindowRow(window: Window): void {
  const row = document.createElement("div");
  row.className = "schedule-row";

  const select = document.createElement("select");
  for (let day = 0; day < 7; day += 1) {
    const option = document.createElement("option");
    option.value = String(day);
    option.textContent = weekdayName(day);
    if (day === window.weekday) {
      option.selected = true;
    }
    select.append(option);
  }

  const start = document.createElement("input");
  start.type = "time";
  start.value = window.start_time;

  const end = document.createElement("input");
  end.type = "time";
  end.value = window.end_time;

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "secondary";
  remove.textContent = "Удалить";
  remove.addEventListener("click", () => row.remove());

  row.append(select, start, end, remove);
  scheduleRows.append(row);
}

function readWindows(): Window[] {
  const windows: Window[] = [];
  scheduleRows.querySelectorAll<HTMLDivElement>(".schedule-row").forEach((row) => {
    const select = row.querySelector("select")!;
    const inputs = row.querySelectorAll<HTMLInputElement>("input");
    windows.push({
      weekday: Number(select.value),
      start_time: inputs[0].value,
      end_time: inputs[1].value,
    });
  });
  return windows;
}

function renderType(eventType: EventType): void {
  const row = document.createElement("div");
  row.className = "booking-row";

  const info = document.createElement("div");
  info.className = "booking-info";

  const name = document.createElement("strong");
  name.textContent = `${eventType.name} · ${eventType.duration_minutes} мин`;

  const meta = document.createElement("span");
  meta.className = "muted";
  meta.textContent = `${eventType.id} — ${eventType.description || "без описания"}`;

  info.append(name, meta);

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "secondary";
  remove.textContent = "Удалить";
  remove.addEventListener("click", () => {
    void removeType(eventType.id);
  });

  row.append(info, remove);
  typesEl.append(row);
}

function renderBooking(booking: Booking): void {
  const row = document.createElement("div");
  row.className = "booking-row";

  const info = document.createElement("div");
  info.className = "booking-info";

  const when = document.createElement("strong");
  when.textContent = new Date(booking.slot_start).toLocaleString("ru-RU");

  const type = typeById.get(booking.event_type_id);
  const who = document.createElement("span");
  who.textContent = `${type?.name ?? booking.event_type_id} · ${booking.name} · ${booking.email}`;

  const comment = document.createElement("span");
  comment.className = "muted";
  comment.textContent = booking.comment || "—";

  info.append(when, who, comment);

  const cancel = document.createElement("button");
  cancel.type = "button";
  cancel.className = "secondary";
  cancel.textContent = "Отменить";
  cancel.addEventListener("click", () => {
    void removeBooking(booking.id);
  });

  row.append(info, cancel);
  bookingsEl.append(row);
}

async function loadSchedule(): Promise<void> {
  scheduleStatus.textContent = "Загружаем расписание…";
  try {
    const windows = await getSchedule();
    scheduleRows.replaceChildren();
    windows.forEach(renderWindowRow);
    scheduleStatus.textContent = "";
  } catch (error) {
    scheduleStatus.textContent = errorMessage(error);
  }
}

async function loadTypes(): Promise<void> {
  typesStatus.textContent = "Загружаем типы встреч…";
  try {
    const types = await listEventTypes();
    typeById.clear();
    typesEl.replaceChildren();
    types.forEach((type) => {
      typeById.set(type.id, type);
      renderType(type);
    });
    typesStatus.textContent = types.length === 0 ? "Типов встреч пока нет." : "";
  } catch (error) {
    typesStatus.textContent = errorMessage(error);
  }
}

async function loadBookings(): Promise<void> {
  bookingsStatus.textContent = "Загружаем встречи…";
  try {
    const bookings = await listBookings(true);
    bookingsEl.replaceChildren();
    bookingsStatus.textContent = bookings.length === 0 ? "Предстоящих встреч нет." : "";
    bookings.forEach(renderBooking);
  } catch (error) {
    bookingsStatus.textContent = errorMessage(error);
  }
}

async function removeType(id: string): Promise<void> {
  try {
    await deleteEventType(id);
    await Promise.all([loadTypes(), loadBookings()]);
  } catch (error) {
    typesStatus.textContent = errorMessage(error);
  }
}

async function removeBooking(id: number): Promise<void> {
  try {
    await cancelBooking(id);
    await loadBookings();
  } catch (error) {
    bookingsStatus.textContent = errorMessage(error);
  }
}

addWindowBtn.addEventListener("click", () => {
  renderWindowRow({ weekday: 0, start_time: "10:00", end_time: "18:00" });
});

saveScheduleBtn.addEventListener("click", () => {
  scheduleStatus.textContent = "Сохраняем…";
  void updateSchedule(readWindows())
    .then(() => {
      scheduleStatus.textContent = "Расписание сохранено.";
    })
    .catch((error: unknown) => {
      scheduleStatus.textContent = errorMessage(error);
    });
});

typeForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const data = new FormData(typeForm);
  typesStatus.textContent = "Сохраняем тип встречи…";
  void createEventType({
    id: String(data.get("id") ?? ""),
    name: String(data.get("name") ?? ""),
    description: String(data.get("description") ?? ""),
    duration_minutes: Number(data.get("duration_minutes") ?? 30),
  })
    .then(() => {
      typeForm.reset();
      typesStatus.textContent = "Тип встречи сохранён.";
      return Promise.all([loadTypes(), loadBookings()]);
    })
    .catch((error: unknown) => {
      typesStatus.textContent = errorMessage(error);
    });
});

void loadSchedule();
void loadTypes();
void loadBookings();
