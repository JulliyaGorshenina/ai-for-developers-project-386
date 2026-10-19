import "./styles.css";

import { cancelBooking, getBookings, getSchedule, updateSchedule } from "./api";
import { weekdayName } from "./format";
import type { Booking, Window } from "./types";

const TOKEN_KEY = "booking-admin-token";

const tokenInput = document.querySelector<HTMLInputElement>("#token-input")!;
const saveTokenBtn = document.querySelector<HTMLButtonElement>("#save-token")!;
const tokenStatus = document.querySelector<HTMLParagraphElement>("#token-status")!;
const scheduleRows = document.querySelector<HTMLDivElement>("#schedule-rows")!;
const addWindowBtn = document.querySelector<HTMLButtonElement>("#add-window")!;
const saveScheduleBtn = document.querySelector<HTMLButtonElement>("#save-schedule")!;
const scheduleStatus = document.querySelector<HTMLParagraphElement>("#schedule-status")!;
const bookingsEl = document.querySelector<HTMLDivElement>("#bookings")!;
const bookingsStatus = document.querySelector<HTMLParagraphElement>("#bookings-status")!;

let token = localStorage.getItem(TOKEN_KEY) ?? "";

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

function renderBooking(booking: Booking): void {
  const row = document.createElement("div");
  row.className = "booking-row";

  const info = document.createElement("div");
  info.className = "booking-info";

  const when = document.createElement("strong");
  when.textContent = new Date(booking.slot_start).toLocaleString("ru-RU");

  const who = document.createElement("span");
  who.textContent = `${booking.name} · ${booking.email}`;

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
  if (!token) {
    return;
  }
  scheduleStatus.textContent = "Загружаем расписание…";
  try {
    const windows = await getSchedule(token);
    scheduleRows.replaceChildren();
    windows.forEach(renderWindowRow);
    scheduleStatus.textContent = "";
  } catch (error) {
    scheduleStatus.textContent = (error as Error).message;
  }
}

async function loadBookings(): Promise<void> {
  if (!token) {
    return;
  }
  bookingsStatus.textContent = "Загружаем встречи…";
  try {
    const bookings = await getBookings(token);
    bookingsEl.replaceChildren();
    bookingsStatus.textContent = bookings.length === 0 ? "Предстоящих встреч нет." : "";
    bookings.forEach(renderBooking);
  } catch (error) {
    bookingsStatus.textContent = (error as Error).message;
  }
}

async function removeBooking(id: number): Promise<void> {
  try {
    await cancelBooking(token, id);
    await loadBookings();
  } catch (error) {
    bookingsStatus.textContent = (error as Error).message;
  }
}

saveTokenBtn.addEventListener("click", () => {
  token = tokenInput.value.trim();
  localStorage.setItem(TOKEN_KEY, token);
  tokenStatus.textContent = token ? "Токен сохранён." : "Токен очищен.";
  void loadSchedule();
  void loadBookings();
});

addWindowBtn.addEventListener("click", () => {
  renderWindowRow({ weekday: 0, start_time: "10:00", end_time: "18:00" });
});

saveScheduleBtn.addEventListener("click", () => {
  scheduleStatus.textContent = "Сохраняем…";
  void updateSchedule(token, readWindows())
    .then(() => {
      scheduleStatus.textContent = "Расписание сохранено.";
    })
    .catch((error: Error) => {
      scheduleStatus.textContent = error.message;
    });
});

tokenInput.value = token;
if (token) {
  void loadSchedule();
  void loadBookings();
}
