# Security / Explicit Limitations

DRAIL V1 is a **source prototype, not production-ready**. It is deliberately a
permission primitive with zero asset custody.

## Defenses implemented

1. Owner-controlled immutable source URL and scoped agent identity.
2. Monitor/owner authorization, unauthorized callers cannot mutate state.
3. Canonical source envelope binds policy version, agent, chain, currency,
   effective status, and strict max size. Complete source is hashed. A replayed
   lower version or modified same version freezes execution.
4. Deterministic quote validation checks the action, cited amount, prohibition
   and per-operation scope; conflicting duplicate action clauses are denied.
5. Independent source fetches and comparative validation of action-driving
   fields; no validator should only check output syntax.
6. Citation substrings must exist in the retrieved page; three capabilities
   must all be resolvable, no guessed permissions.
7. Automatic cap reduction; increases are staged and require owner approval
   plus a new live source check of identical evidence digest and caps.
8. Fetch errors and ambiguity block authorization, without pretending that
   temporary unavailability is a true revocation.
9. Emergency pause after RPC/validator failure, when `poll` cannot commit.
10. Audited revisions record actor, excerpts, source hash and effective caps.
11. No transfers / reentrancy-sensitive payout path in V1.

## Threat matrix

| Threat | Current behavior | Residual risk |
|---|---|---|
| Caller injects their own evidence URL | No user URL accepted by poll | Owner may pick a poor URL at deploy |
| Source duplicates rules or contains a hidden late override | Reject duplicate action mentions; reject >8192 bytes | Complex natural language may still be misread |
| Source page contains hostile prompt | Prompt instructs to ignore; extracted excerpt checks | A malicious page may still deceive LLM validators |
| Source URL goes offline | On successful consensus about fetch failure, freeze | If consensus transaction reverts, previous gate stays open until authorized emergency pause |
| Source publisher replays old version | Freeze if version decreases or same version changes | Publisher can still forge higher version; signatures not implemented |
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

## Time-bounded enforcement (one hour)

The guard records `last_verified_at` after a successful consensus-validated `poll()` or fresh owner approval. The view `can_execute` denies calls after 3600 seconds without a successful observation, even if `health` remains `OK`. Invalid observations cannot extend the window. The GenVM transaction clock is deterministic, not host wall-clock time. This bounds the age of the *last verification*; it does **not** authenticate the policy publisher, prove that a new policy was published, enforce immediate revocation, prevent a compromised host serving different data, or guarantee external consumers read finalized state. Consumer integrations remain responsible for currency rates, replay/idempotency and finality. Conditional or exception-laden positive grants are rejected conservatively until separate prerequisite verification is supported.
