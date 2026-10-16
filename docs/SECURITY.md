# Security / Explicit Limitations

DRAIL V1 is a **source prototype, not production-ready**. It is deliberately a
permission primitive with zero asset custody.

## Defenses implemented

1. Owner-controlled immutable source URL and scoped agent identity.
2. Monitor/owner authorization, unauthorized callers cannot mutate state.
3. Independent source fetches and comparative validation of action-driving
   fields; no validator should only check output syntax.
4. Citation substrings must exist in the retrieved page; three capabilities
   must all be resolvable, no guessed permissions.
5. Automatic cap reduction; increases are staged and require owner approval
   plus a new live source check of identical evidence digest and caps.
6. Fetch errors and ambiguity block authorization, without pretending that
   temporary unavailability is a true revocation.
7. Emergency pause after RPC/validator failure, when `poll` cannot commit.
8. Audited revisions record actor, excerpts, source hash and effective caps.
9. No transfers / reentrancy-sensitive payout path in V1.

## Threat matrix

| Threat | Current behavior | Residual risk |
|---|---|---|
| Caller injects their own evidence URL | No user URL accepted by poll | Owner may pick a poor URL at deploy |
| Source page contains hostile prompt | Prompt instructs to ignore; extracted excerpt checks | A malicious page may still deceive LLM validators |
| Source URL goes offline | On successful consensus about fetch failure, freeze | If consensus transaction reverts, previous gate stays open until authorized emergency pause |
| Content differs between validators | Source digest required to match; likely consensus fails | No automatic freshness shutoff without a clock or monitor |
| Increase after compromise | Staged until owner approval and fresh source verification | Compromised owner can approve; no multi-sig in V1 |
| Old pending proposal after source changes | New source hash/caps checked before approval | Content same in digest but source host later changes again (TOCTOU) |
| AI misreads numeric/semantic policy | Independent validators must agree on 3 caps and cited clauses | Multi-model agreement does NOT prove semantic truth |
| Consumer ignores guard | Not enforceable | Integration must actually call can_execute |
| Fiat/USD vs token units | Cents are integers; no token transfer | Real exchange-rate conversion is intentionally out of scope |
| Historical page changes | Store hash and quoted excerpts | Full historical page snapshots must be archived off-chain |
| Malicious monitor | Can freeze/tighten but not grant | Denial-of-service possible; owner can rotate monitor |

## Design constraints for next phase

- Publisher-signed canonical policy snapshots or immutable content-addressed
  source versions, with monotonic version authentication.
- Replay-resistant, finality-aware execution or attestations for external
  consumers; never trust an `ACCEPTED` result as irreversible.
- Source freshness/expiry controls using runtime-verified timestamp support,
  not speculative message fields.
- Distinct named policy subjects (agent identity, environment, currency,
  effective date), multiple verified publisher endpoints and conflict policy.
- Adversarial multi-validator network tests, ABI lint, reproducible evidence
  receipts, independent review, and audit before funds are permitted.

## Most important known gap

Consensus failure cannot update contract storage. A permanently stalled or
reverted `poll()` leaves the last successfully committed health unchanged.
Therefore `emergency_pause()` must be called by an authorized actor after a
failed consensus verification. Without a freshness mechanism and a reliable
monitor, DRAIL cannot promise continuous policy enforcement.
