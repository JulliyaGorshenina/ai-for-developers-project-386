import "@typespec/http";

using TypeSpec.Http;

@service(#{ title: "Call Booking Service" })
@server("http://127.0.0.1:8000", "Local development server")
@route("/api")
namespace BookingService;

// ---------------------------------------------------------------------------
// Models
// ---------------------------------------------------------------------------

/** A published meeting type a guest can book. `id` is the owner-chosen slug. */
model EventType {
  @pattern("^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
  @minLength(1)
  @maxLength(64)
  id: string;

  @minLength(1)
  @maxLength(200)
  name: string;

  @maxLength(1000)
  description: string;

  @minValue(1)
  @maxValue(600)
  duration_minutes: int32;
}

/** Payload for creating or replacing a meeting type. */
model EventTypeCreate {
  @pattern("^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
  @minLength(1)
  @maxLength(64)
  id: string;

  @minLength(1)
  @maxLength(200)
  name: string;

  @maxLength(1000)
  description: string;

  @minValue(1)
  @maxValue(600)
  duration_minutes: int32;
}

/** A continuous availability interval inside one weekday. */
model Window {
  @minValue(0)
  @maxValue(6)
  weekday: int32;

  @pattern("^([01]\\d|2[0-3]):[0-5]\\d$")
  start_time: string;

  @pattern("^([01]\\d|2[0-3]):[0-5]\\d$")
  end_time: string;
}

/** Full weekly schedule replacement payload. */
model WindowList {
  windows: Window[];
}

/** A bookable time interval derived from the schedule grid. */
model Slot {
  start: utcDateTime;
  end: utcDateTime;
}

/** Free slots of a single day. */
model DaySlots {
  date: plainDate;
  weekday: int32;
  slots: Slot[];
}

/** A booked (or cancelled) meeting. */
model Booking {
  id: int32;
  event_type_id: string;
  slot_start: utcDateTime;
  slot_end: utcDateTime;
  name: string;
  email: string;
  comment: string;
  status: string;
  created_at: utcDateTime;
}

/** Guest booking payload. */
model BookingCreate {
  @pattern("^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
  @minLength(1)
  @maxLength(64)
  event_type_id: string;

  slot_start: utcDateTime;

  @minLength(1)
  @maxLength(200)
  name: string;

  @pattern("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")
  @maxLength(200)
  email: string;

  @maxLength(1000)
  comment?: string;
}

/** Machine-readable error body shared by all failures. */
model ErrorBody {
  detail: string;
}

model CreateEventTypeResponse {
  @statusCode statusCode: 201;
  @body body: EventType;
}

model CreateBookingResponse {
  @statusCode statusCode: 201;
  @body body: Booking;
}

model NoContentResponse {
  @statusCode statusCode: 204;
}

@error
model BadRequestError {
  @statusCode statusCode: 400;
  @body body: ErrorBody;
}

@error
model NotFoundError {
  @statusCode statusCode: 404;
  @body body: ErrorBody;
}

@error
model ConflictError {
  @statusCode statusCode: 409;
  @body body: ErrorBody;
}

@error
model ValidationError {
  @statusCode statusCode: 422;
  @body body: ErrorBody;
}

// ---------------------------------------------------------------------------
// Operations
// ---------------------------------------------------------------------------

/** List every published meeting type. */
@route("/event-types")
@get
op listEventTypes(): EventType[];

/** Publish a new meeting type. */
@route("/event-types")
@post
op createEventType(@body body: EventTypeCreate): CreateEventTypeResponse | ConflictError | ValidationError;

/** Replace an existing meeting type. */
@route("/event-types/{id}")
@put
op updateEventType(@path id: string, @body body: EventTypeCreate): EventType | NotFoundError | ValidationError;

/** Remove a meeting type. */
@route("/event-types/{id}")
@delete
op deleteEventType(@path id: string): NoContentResponse | NotFoundError;

/** Free days and slots for a meeting type over the booking window. */
@route("/event-types/{id}/availability")
@get
op getAvailability(
  @path id: string,
  @query @minValue(1) @maxValue(60) days?: int32,
): DaySlots[] | NotFoundError;

/** Free slots of a meeting type on a single day. */
@route("/event-types/{id}/slots")
@get
op getSlotsForDate(@path id: string, @query date: plainDate): Slot[] | BadRequestError | NotFoundError;

/** Book a slot for a guest. */
@route("/bookings")
@post
op createBooking(
  @body body: BookingCreate,
): CreateBookingResponse | BadRequestError | NotFoundError | ConflictError | ValidationError;

/** List meetings; by default only the upcoming ones. */
@route("/bookings")
@get
op listBookings(@query upcoming?: boolean): Booking[];

/** Cancel a meeting, freeing its slot. */
@route("/bookings/{id}")
@delete
op cancelBooking(@path id: int32): Booking | NotFoundError;

/** Read the owner's weekly availability. */
@route("/schedule")
@get
op getSchedule(): Window[];

/** Replace the owner's weekly availability. */
@route("/schedule")
@put
op updateSchedule(@body body: WindowList): Window[] | BadRequestError | ValidationError;

/** Service liveness probe. */
@route("/health")
@get
op health(): {
  status: string;
};
