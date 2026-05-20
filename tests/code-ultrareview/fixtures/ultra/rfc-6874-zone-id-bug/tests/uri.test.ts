// Existing test — failing-test writer must not overwrite it.
import { describe, it, expect } from 'vitest';
import { parseZoneId } from '../src/uri/zone-id';

describe('parseZoneId', () => {
  it('returns input as-is', () => {
    expect(parseZoneId('eth0')).toBe('eth0');
  });
});
