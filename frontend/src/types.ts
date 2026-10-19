export interface Slot {
  start: string;
  end: string;
}

export interface DaySlots {
  date: string;
  weekday: number;
  slots: Slot[];
}

export interface Booking {
  id: number;
  slot_start: string;
  slot_end: string;
  name: string;
  email: string;
  comment: string;
  status: string;
  created_at: string;
}

export interface BookingCreate {
  slot_start: string;
  name: string;
  email: string;
  comment?: string;
}

export interface Window {
  weekday: number;
  start_time: string;
  end_time: string;
}
