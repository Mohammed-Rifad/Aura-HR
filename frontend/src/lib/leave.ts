/**
 * Working days between two dates, counting both ends.
 *
 * Mirrors working_days() in backend/leave/services.py. This copy exists only
 * to show the user a number while they pick dates — the number that actually
 * gets saved is the one the backend calculates. The browser can be wrong or
 * tampered with, so it never decides anything.
 */
export function workingDays(start: string, end: string): number {
  if (!start || !end) return 0;

  const from = new Date(start);
  const to = new Date(end);
  if (to < from) return 0;

  let days = 0;
  const cursor = new Date(from);

  while (cursor <= to) {
    // JavaScript: 0 = Sunday, 6 = Saturday.
    // Python: 5 = Saturday, 6 = Sunday. Same weekend, different numbering.
    const weekday = cursor.getDay();
    if (weekday !== 0 && weekday !== 6) days += 1;
    cursor.setDate(cursor.getDate() + 1);
  }

  return days;
}

/** Today as YYYY-MM-DD, for the `min` on a date input. */
export function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}
