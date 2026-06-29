/**
 * Returns today's date as YYYY-MM-DD in the BROWSER'S LOCAL timezone.
 *
 * Using `new Date().toISOString()` is a common bug here: toISOString()
 * always converts to UTC first, so anywhere west of UTC (or late at night
 * in a timezone ahead of UTC, close to midnight) can report the WRONG day
 * — e.g. it's already "tomorrow" locally but still "today" in UTC, or
 * vice versa. This helper builds the date string from local getters
 * instead, so it always matches the date on the user's wall clock.
 */
export function getLocalDateString(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
