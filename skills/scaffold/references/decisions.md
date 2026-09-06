# Decisions beyond the scaffold

The scaffold creates a framework foundation and installs declared dependencies. It does not implement application authentication, schema, content workflows or external integrations. Discuss a decision only when the accepted brief requires it; do not turn every new project into a questionnaire.

## Identify the needed decision

| Concern | Evidence to collect before choosing |
| --- | --- |
| Internationalization | Required locales, routing, translation ownership and framework compatibility |
| Public/admin authentication | Actors, permissions, session boundaries and provider requirements |
| Search | Corpus, query types, languages, freshness and measured quality |
| Rich text | Authoring needs, stored format, safe rendering and existing components |
| Social previews | Required content, update timing and verified rendering environment |
| Machine translation | Languages, review process, data transfer and evaluated quality |
| Theme persistence | User preference, server rendering and cache behavior |
| Cache invalidation | Mutation paths, freshness requirements and adapter support |
| Media upload | File limits, ownership, authorization and storage access |
| CRM sync | Source of truth, delivery requirements, retries and external-write authorization |

## Decide within scope

Start with existing project conventions and available dependencies. Consult current primary documentation for provider contracts, limits and prices. Compare actual requirements and evidence rather than unsupported rankings, latency estimates or promised cost savings.

Record the chosen option and the reason in the application's owning document. Leave unrelated concerns unimplemented. A dependency in package.json does not mean its feature, schema or provider account has been configured.

## Verify

Test the behavior the choice is meant to provide, including relevant failure modes. Keep provider activation, public storage, deployment and outbound communication inside their explicit authorization boundaries. Do not publish automatically because the scaffold completed.
