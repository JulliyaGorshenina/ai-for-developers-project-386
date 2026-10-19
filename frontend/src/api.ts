import type { Booking, BookingCreate, DaySlots, Slot, Window } from "./types";

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new Error(body.detail ?? `Ошибка запроса (${response.status})`);
  }
  return (await response.json()) as T;
}

export function getAvailability(days = 14): Promise<DaySlots[]> {
  return request<DaySlots[]>(`/availability?days=${days}`);
}

export function getSlots(date: string): Promise<Slot[]> {
  return request<Slot[]>(`/slots?date=${encodeURIComponent(date)}`);
}

export function createBooking(payload: BookingCreate): Promise<Booking> {
  return request<Booking>("/bookings", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getSchedule(token: string): Promise<Window[]> {
  return request<Window[]>("/admin/schedule", {
    headers: { "X-Admin-Token": token },
  });
}

export function updateSchedule(token: string, windows: Window[]): Promise<Window[]> {
  return request<Window[]>("/admin/schedule", {
    method: "PUT",
    headers: { "X-Admin-Token": token },
    body: JSON.stringify({ windows }),
  });
}

export function getBookings(token: string, upcoming = true): Promise<Booking[]> {
  return request<Booking[]>(`/admin/bookings?upcoming=${upcoming}`, {
    headers: { "X-Admin-Token": token },
  });
}

export function cancelBooking(token: string, id: number): Promise<Booking> {
  return request<Booking>(`/admin/bookings/${id}`, {
    method: "DELETE",
    headers: { "X-Admin-Token": token },
  });
}
