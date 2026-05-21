# rfc-6874-zone-id-bug

URI parser that claims RFC 6874 compliance but accepts any string as the
ZoneID. The canonical failing-test target — `--apply-safe` should write
one focused test asserting `http://[fe80::1%25]/` is parseable while
`http://[fe80::1%illegal]/` is rejected.
