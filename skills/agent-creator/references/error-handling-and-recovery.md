# Subagent error handling and recovery

Diagnose the observed failure before choosing recovery. Preserve the exact error and useful completed work. A long-running task is not failed solely because a fixed time budget from an example elapsed.

## Failure-specific response

| Failure | Response |
| --- | --- |
| Missing tool or package | Check the documented environment; report the exact prerequisite and rerun command. Do not install implicitly. |
| Authentication or permission denial | Preserve the denied action and error; continue unaffected authorized work. Do not bypass controls. |
| Transient service failure | Retry only when the operation is safe to repeat and the provider supports it; use its retry guidance and a bounded attempt budget. |
| Invalid input or deterministic error | Correct the input or hypothesis before retrying. Identical retries add no evidence. |
| Partial external write | Read back state before retrying, using an idempotency key when supported. |
| Missing official documentation | Try an authoritative alternative; report the unresolved contract. Never implement invented APIs from a fabricated stub document. |

## Progress and escalation

Keep the accepted scope fixed while changing implementation details that remain authorized. Ask the lead or user only for input they own or a real scope/authorization decision. Return completed artifacts and remaining evidence when blocked.

Circuit breakers, persistent retry queues and monitoring services belong in an application only when its reliability requirements justify them. Do not create this infrastructure merely to run a local subagent.

## Recovery check

Reproduce the original failure safely and demonstrate that the correction addresses it. Re-run affected required checks after relevant edits. A graceful partial result must name what remains missing; it is not a successful full completion.
