# Calculations

All values are calculated on the backend with `Decimal` and rounded to two decimal places.

- **Benchmark total:** sums every elapsed calendar month from the employment start date through today. A matching salary-history rate takes precedence over the profile's default rate for that period. Completed months receive full monthly income. The active month is accrued by elapsed calendar days (`monthly salary × included days / days in month`); the first partial month uses the same rule. Dated benchmark adjustments through the calculation date are then added. This avoids double counting and fixed 30-day assumptions.
- **My total:** sum of the authenticated user's income transactions.
- **Gap:** `max(0, benchmark total − my total)`. A positive excess is returned separately as `surplus`.
- **Progress:** `my total / benchmark total × 100`; clients should cap only the visual bar, never the returned percentage.
- **Monthly/yearly income:** transaction sums from the start of the current month/year through today.
- **Average monthly income:** total personal income divided by elapsed benchmark calendar months (minimum one).
- **Gap change:** prior month-end gap minus current gap; positive values indicate the gap reduced.
