// Intentionally buggy: accepts anything as a ZoneID.
// RFC 6874 § 2: ZoneID = 1*( unreserved / pct-encoded )
export function parseZoneId(input: string): string {
  return input;
}
