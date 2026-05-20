# ADR-0004 - Notification Delivery Strategy

## Status
Accepted

- **Current status**: Accepted
- **Date accepted**: 2025-03-12
- **Review-by date**: 2025-09-12
- **Superseded by**: -
- **Review notes**: -

## Context
Bloom's core value proposition is timely plant care reminders - watering, fertilising, repotting. Without reliable delivery, the product does not work. We need to choose how reminders reach users before building the reminder scheduler in Phase 3.

The team is two engineers. v1 is a REST API with a React web app; native mobile apps are not in scope until v2.

## Decision Drivers

1. **Deliverability** - reminders must reliably reach users; missed reminders break the product promise
2. **v1 scope** - implementation must fit within a two-week sprint; no native app in scope
3. **Cost** - startup budget; pay-as-you-go pricing strongly preferred over monthly minimums
4. **User trust** - notifications must feel helpful, not spammy; easy to unsubscribe
5. **Compliance** - CAN-SPAM and GDPR require unsubscribe mechanisms and sender identification

## Options Considered

### Option A: Email only (SendGrid)
**Description**: Send all reminders as transactional email via SendGrid's API. Users provide an email address on registration.

**Pros**:
- Universally available - no app install or permission required
- SendGrid free tier (100 emails/day) covers early growth
- Simple integration - one HTTP call per reminder
- Established deliverability infrastructure

**Cons**:
- Email inboxes are noisy; open rates lower than push
- Requires managing bounce handling and unsubscribe lists
- Templates add maintenance overhead

**Risks**:
- A02 (Cryptographic Failures) - email content must not include sensitive data (indexed by mail servers)
- Deliverability risk if domain reputation is not maintained (SPF/DKIM/DMARC required)

### Option B: Push notifications only (Firebase FCM)
**Description**: Send reminders as web push notifications via Firebase Cloud Messaging.

**Pros**:
- Higher engagement rates than email
- No inbox noise

**Cons**:
- Requires service worker setup in the web app - out of scope for v1
- Users must explicitly grant browser permission; many decline
- Zero delivery if the browser is closed

**Risks**:
- High implementation risk within v1 timeline
- Permission denial rate could be 40-60% for a new product

### Option C: Email + Push
**Description**: Deliver reminders via both channels; user chooses preference.

**Pros**:
- Best coverage across user preferences

**Cons**:
- Double the implementation effort
- Preference management UI required

**Risks**:
- Scope risk for v1; increases surface area for bugs

### Option D: In-app notifications only
**Description**: Store reminders in the database; surface them only when the user opens the app.

**Pros**:
- Zero external dependency; simplest implementation

**Cons**:
- Requires the user to open the app to see the reminder - defeats the purpose
- No value if user forgets to open app

**Risks**:
- High risk of product failure; reminder app that requires manual checking is not a reminder app

## Decision
**Option A - Email only via SendGrid**, with in-app notification as a secondary indicator. Push notifications deferred to v2 when the mobile app is in scope.

## Justification
Email is the only channel that satisfies all five decision drivers simultaneously for v1. It is universally available (no app install), fits the budget, and has well-understood compliance requirements. Option D is disqualifying. Options B and C both carry timeline risk that is unjustified before we have evidence that email open rates are insufficient.

## Consequences

### Positive
- Reminder delivery works on day one with no app install required
- SendGrid free tier eliminates cost risk for the first several thousand users
- Compliance is straightforward - standard unsubscribe link in every email

### Negative
- Email open rates (~25-35%) mean some reminders will be missed; acceptable for v1
- Domain reputation requires SPF, DKIM, and DMARC records to be configured before launch
- Bounce and unsubscribe handling must be implemented to stay within SendGrid's policies

### Follow-up Work
- Configure SPF/DKIM/DMARC DNS records before first email is sent (DevOps)
- Implement webhook handler for SendGrid bounce/unsubscribe events (change proposal)
- Evaluate push notification delivery rates after v1 launch; revisit in v2 ADR

## Security Notes
- **Threats considered**: email subject line indexing by mail servers, notification spam/abuse, unsubscribe non-compliance
- **Mitigations required**: never include plant names, user data, or any PII in email subjects; rate-limit reminder dispatch to prevent a misconfigured schedule from flooding a user; include one-click unsubscribe in every email
- **Controls to implement**: #26 (service-to-service auth for SendGrid API key), #41 (API key stored in secrets manager, not env var) from `catalogs/owasp-secure-coding-100.md`

## Rollback / Reversal Plan
Disable the `BLOOM_EMAIL_ENABLED` feature flag. Reminder records will continue to be created in the database; they will surface as in-app notifications only until an alternative delivery channel is implemented. No data migration required.

## Approval
- **Approved by**: Jordan (project owner)
- **Date**: 2025-03-12
- **Notes**: Agreed to revisit push notifications after first 500 active users.

## References
- [SendGrid Transactional Email API](https://docs.sendgrid.com/api-reference/mail-send)
- [CAN-SPAM Act compliance checklist](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)
- [Google Postmaster Tools](https://postmaster.google.com/) - monitor domain reputation

---
*Template: `templates/documents/adr.md`*
