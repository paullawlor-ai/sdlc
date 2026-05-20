# Top 100 Engineering Controls (Curated)

These controls are phrased for **implementation and review** (agent-friendly).
Use them as acceptance criteria in change docs and reviews.

## Input Validation (1-10)

1. Validate all untrusted inputs server-side; never rely on client validation.
2. Use allowlists for formats, types, ranges, and lengths wherever possible.
3. Normalize/standardize encodings (e.g., UTF-8) before validation to prevent bypasses.
4. Reject unknown fields by default for structured inputs (JSON, forms).
5. Validate protocol headers and metadata (Host, Content-Type) against strict expectations.
6. Use one centralized validation layer rather than scattered ad-hoc checks.
7. Treat data from databases, caches, queues, and files as untrusted unless provenance is guaranteed.
8. Apply strict parsing with explicit error handling; never 'best effort' parse security boundaries.
9. Defend against deserialization risks: avoid unsafe serializers; validate schema and type.
10. Validate all redirect targets and callback URLs (prevent open redirects).

## Output Encoding & Injection Resistance (11-18)

11. Use parameterized queries for SQL; never string-concatenate SQL.
12. Use parameterized APIs for OS commands; avoid shell invocation where possible.
13. Contextual output encoding for HTML, attributes, URLs, and JavaScript contexts.
14. Escape/encode data before rendering into logs or dashboards that may interpret markup.
15. Prevent template injection by separating templates from untrusted data and restricting template features.
16. Sanitize untrusted values used in LDAP/XPath/XML queries; prefer safe libraries.
17. Prefer safe YAML/JSON loaders that do not execute code.
18. Apply strict CORS policies; do not use wildcard origins for authenticated endpoints.

## Authentication (19-26)

19. Adopt a single authentication approach (OIDC/SAML) and reuse it consistently.
20. Fail authentication securely: no partial logins, no verbose failure hints.
21. Implement MFA for privileged accounts and high-risk operations.
22. Protect credential entry and transport: HTTPS only, POST only for credentials.
23. Store passwords only as strong salted hashes if you must store them at all.
24. Use short-lived tokens; validate issuer, audience, and signature.
25. Re-authenticate before sensitive actions (key rotation, role changes, exports).
26. Secure service-to-service auth with workload identity where possible (avoid static secrets).

## Session Management (27-32)

27. Use HttpOnly + Secure cookies where cookie sessions are used.
28. Rotate session identifiers after login and after privilege changes.
29. Never place session identifiers in URLs.
30. Enforce inactivity timeouts and absolute session lifetimes for high-risk apps.
31. Invalidate sessions on logout and credential reset.
32. Prevent session fixation by creating fresh sessions on auth transitions.

## Authorization & Access Control (33-38)

33. Enforce authorization on every request (including internal endpoints).
34. Deny by default; grant only what is needed (least privilege).
35. Implement object-level authorization checks (IDOR resistance).
36. Keep authorization logic centralized (policy decision point).
37. Ensure admin actions are explicitly gated and audited.
38. Rate-limit and monitor privileged operations.

## Cryptography & Key Management (39-44)

39. Use modern, well-vetted cryptographic libraries; do not implement crypto yourself.
40. Encrypt sensitive data at rest where appropriate and always in transit.
41. Use KMS/HSM-backed key storage where possible; rotate keys on schedule.
42. Use cryptographically secure RNG for tokens/identifiers.
43. Separate encryption from integrity: use authenticated encryption where applicable.
44. Never log secrets, private keys, or full tokens.

## Error Handling & Logging (45-50)

45. Return generic error messages to clients; keep details server-side.
46. Ensure debug mode is never enabled in production deployments.
47. Log security-relevant events: auth failures, access denials, validation failures.
48. Redact sensitive data in logs by default; allow explicit opt-in for secure environments.
49. Protect logs from tampering and restrict access (least privilege).
50. Add correlation identifiers to logs and responses for traceability.

## Data Protection & Privacy (51-55)

51. Classify data (public/internal/confidential) and enforce handling rules.
52. Minimize data collection and retention; delete data when no longer needed.
53. Avoid placing sensitive data in URLs (query strings) or client-side storage.
54. Disable client-side caching for sensitive pages/responses where relevant.
55. Protect source code and internal docs from being served publicly.

## Communication Security (56-59)

56. Use TLS everywhere; do not allow downgrade/fallback to insecure transport.
57. Validate certificates and hostnames in outbound connections.
58. Set strict transport security headers (HSTS) where applicable.
59. Use mTLS for high-trust internal service meshes when feasible.

## System Configuration & Hardening (60-64)

60. Use secure defaults: least privilege, minimal exposure, no debug endpoints.
61. Maintain separate configs for dev/test/prod; avoid 'works on my machine' drift.
62. Pin dependency versions and keep them updated with a controlled process.
63. Remove/disable sample endpoints, default accounts, and vendor defaults.
64. Limit request body sizes and set server-level timeouts.

## Database Security (65-69)

65. Use dedicated DB roles for app runtime vs migrations; least privilege for each.
66. Enable TLS to the database and require encrypted connections.
67. Use connection pooling with sane limits to prevent resource exhaustion.
68. Protect backups; test restore procedures regularly.
69. Apply row-level security when multi-tenant boundaries demand it.

## File & Object Handling (70-73)

70. Validate uploaded file types and sizes; store outside web roots.
71. Scan or sandbox untrusted files where risk justifies it.
72. Use safe filenames; avoid path traversal by joining paths safely and restricting directories.
73. Set strict permissions on generated files and temporary directories.

## Dependency & Supply Chain (74-77)

74. Use a lockfile; verify integrity of dependencies (hashes/signatures if available).
75. Run SCA (dependency vulnerability scanning) in CI.
76. Restrict who can publish artifacts; sign releases if distributing widely.
77. Review licenses for new dependencies; avoid unknown maintainers for critical paths.

## Observability & Operations (78-81)

78. Expose health checks (liveness/readiness) without leaking sensitive internals.
79. Instrument latency, error rate, and key security events with metrics.
80. Set alert thresholds for auth failure spikes and unusual access patterns.
81. Document runbooks for common failure and incident scenarios.

## AI/Agent-Specific Controls (82-87)

82. Treat retrieved content as untrusted; strip instructions from RAG sources.
83. Constrain tools with allowlists and validate parameters (domains, commands, tables).
84. Apply output policy checks (redaction/blocking) after model inference.
85. Cap token usage, concurrency, and timeouts to reduce DoS and runaway cost.
86. Log AI actions as auditable events without storing sensitive prompts verbatim by default.
87. Implement tenant- and role-scoped retrieval boundaries to prevent data leakage.

## General Coding Practices (88-100)

88. Use explicit, documented defaults for configuration; never rely on implicit framework defaults.
89. Prefer immutable data structures where practical to prevent unintended mutations.
90. Use type hints and static analysis to catch errors early.
91. Keep functions small and focused; avoid side effects where possible.
92. Handle all error cases explicitly; avoid silent failures.
93. Use constants for magic values; document their purpose.
94. Implement graceful degradation for non-critical failures.
95. Use feature flags for risky changes; enable gradual rollout.
96. Write tests for security-critical paths; include negative/abuse cases.
97. Document public APIs with examples and error conditions.
98. Use structured logging with consistent field names.
99. Implement circuit breakers for external service calls.
100. Review and update dependencies on a regular schedule.

