import type {
  Booking,
  BookingCreate,
  DaySlots,
  EventType,
  EventTypeCreate,
  Window,
} from "./api/generated";
import {
  cancelBooking as sdkCancelBooking,
  createBooking as sdkCreateBooking,
  createEventType as sdkCreateEventType,
  deleteEventType as sdkDeleteEventType,
  getAvailability as sdkGetAvailability,
  getSchedule as sdkGetSchedule,
  listBookings as sdkListBookings,
  listEventTypes as sdkListEventTypes,
  updateSchedule as sdkUpdateSchedule,
} from "./api/generated";
import { client } from "./api/generated/client.gen";

client.setConfig({ baseUrl: "" });

export * from "./api/generated";

export function errorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (error && typeof error === "object" && "detail" in error) {
    return String((error as { detail: unknown }).detail);
  }
  return "Неизвестная ошибка";
}

async function unwrap<T>(result: Promise<{ data?: T; error?: unknown }>): Promise<T> {
  const { data, error } = await result;
  if (error !== undefined) {
    throw new Error(errorMessage(error));
  }
  return data as T;
}

export function listEventTypes(): Promise<EventType[]> {
  return unwrap(sdkListEventTypes());
}

export function createEventType(body: EventTypeCreate): Promise<EventType> {
  return unwrap(sdkCreateEventType({ body }));
}

export function deleteEventType(id: string): Promise<void> {
  return unwrap(sdkDeleteEventType({ path: { id } }));
}

export function getAvailability(id: string, days = 14): Promise<DaySlots[]> {
  return unwrap(sdkGetAvailability({ path: { id }, query: { days } }));
}

export function getSchedule(): Promise<Window[]> {
  return unwrap(sdkGetSchedule());
}

export function updateSchedule(windows: Window[]): Promise<Window[]> {
  return unwrap(sdkUpdateSchedule({ body: { windows } }));
}

export function listBookings(upcoming = true): Promise<Booking[]> {
  return unwrap(sdkListBookings({ query: { upcoming } }));
}

export function createBooking(body: BookingCreate): Promise<Booking> {
  return unwrap(sdkCreateBooking({ body }));
}

export function cancelBooking(id: number): Promise<Booking> {
  return unwrap(sdkCancelBooking({ path: { id } }));
}
