# DRAIL Architecture — V1

## Scope

Authority-controlled AI-agent permissions for three wallet capabilities:
`SEND`, `SWAP`, and `BRIDGE`. Every operation has a non-negative maximum
amount in USD cents; 0 means autonomous action is prohibited. Missing rules
cannot be interpreted as 0 — that would silently invent a restriction.

## State variables

- Pinned: `authority_url`, `owner`, `agent`, `monitor`, `source_scope`.
- Current: `initialized`, `health`, `policy_status`, three approved caps,
  `last_source_hash`, `last_policy_version` and `chain_id`.
- Pending: three proposed caps, `pending_source_hash`, `pending_policy_version`.
- Append-only: `revision`, `audit` entries. Historical entries contain caller,
  action category, effective caps, source digest, actual supporting excerpts.

### Permission gate

`can_execute(who, action, cents)` is true **only** if the policy was initialized,
health is `OK`, the actor matches the pinned agent, the action is one of the
three known capabilities, the amount is a positive integer and fits the
currently approved cap. This is a view authorization result, NOT a transfer.

### State transition table

| Previous state | New evidence | Result |
|---|---|---|
| UNVERIFIED | valid pinned policy; owner submits | INITIALIZED; validated caps active |
| ACTIVE / RESTRICTED | next policy version and all caps decrease/equal | TIGHTENED/REVALIDATED; apply now |
| any initialized | old version or same version with different bytes | UNRESOLVED; retain proven caps, block execution |
| ACTIVE / RESTRICTED | any cap increases | PENDING_WIDENING; apply decreases now, do not grant increases |
| PENDING_WIDENING | owner approval + fresh same source hash/caps | WIDENED_BY_OWNER |
| any | source unreachable/unclear and consensus resolves that result | UNRESOLVED, block execution, preserve approved caps |
| any | validators cannot reach consensus | transaction may revert; monitor must call emergency_pause |
| UNRESOLVED | fresh valid consensus | OK with verified restrictive rules, or new staged widening |
| any | emergency_pause | UNRESOLVED until fresh valid poll |
| any | repeat identical successful poll | no duplicate audit record |

`policy_status` and `health` are orthogonal: a previously RESTRICTED policy can
be UNRESOLVED without implying the policy was revoked. A blocked read is not a
new statement about the source's true authority.

## Consensus and trust boundary

The independent work per validator is: fetch the same *stored* URL, extract
three caps from the source in one structured response, provide three actual
source excerpts, return the source text digest. The comparative principle
requires identical result kind, source digest and all three caps, and agreement
on what underlying rule each excerpt supports. A validator does NOT merely
check JSON formatting. Outside consensus the contract type-checks amounts and
digests before writing state.

The source is untrusted text: prompt injection attempts are ignored by
instruction, and the selected quotes must appear verbatim in the rendered page.
The `quote in page` check does not by itself prove a rule is authoritative;
validators must agree on the rule's meaning and scope. A known risk is that the
source host itself may be compromised or present conflicting versions. Authority
provenance is anchored in the constructor-chosen URL and HTTPS only, NOT a
publisher signature. **This is not sufficient for high-value asset control.**

## Asymmetric authorization

Tightening: each cap becomes `min(old, fresh)` and therefore can never increase
from a monitor-triggered `poll`. Widening: the proposed caps and full fetched
source digest are staged on-chain. Only the original owner may approve, and
only after another validator-backed live fetch returns the same digest and
limits. A pending record cannot be approved twice.

In mixed updates, only the lower cap on each dimension is installed while
other dimensions remain unchanged. This prevents a permissive update from
masking a simultaneous restrictive rule.

## Cross-contract consumer

The `consumer_fixture.py` contract uses `gl.get_contract_at(guard).view()` to
check authorization on a *write* that increments a demo counter. It holds no
funds and exists to demonstrate an actual inter-contract dependency. For real
money movement, a consumer must independently handle finality, caller identity,
asset denomination, stale-authorization races, and transaction atomicity.

## Network behavior

The core contract does not run by itself. A trusted owner/monitor must submit
`poll()` transactions. There is no on-chain guarantee that the remote policy is
current unless its updater is reliable. `gl.message.datetime` is not used, as
legacy runner compatibility is uncertain. Do not assume real-time expiry.

## Canonical envelope and numeric post-validation

The first seven lines of a small (<=8192-byte) UTF-8 policy are mandatory and
must bind VERSION, AGENT, CHAIN_ID, CURRENCY and STATUS. A version is immutable;
previously observed versions cannot be replayed, nor may same-version content
be edited. The entire document is hashed. A duplicate SEND, SWAP or BRIDGE
mention anywhere in the rule body fails rather than allowing the model to
silently choose a preferred clause. Only a single unambiguous USD amount per
permitted action is supported. A deterministic second check rejects a model
cap that contradicts its quoted amount. The model still interprets the prose
(rule type/permission) and validators check the same source independently.
This is a deliberately narrow safe subset, not a general compliance parser.

The version metadata remains publisher-controlled and is not cryptographically
signed. Freshness requires an external monitor because this runner does not
supply a verified expiry clock to DRAIL. Cross-contract consumers must wait for
finality and must not assume a `view` alone supplies global atomicity.

## Verification freshness and conditions

An authorized successful policy observation updates `last_verified_at` using the GenVM deterministic transaction clock. The permission view enforces `0 <= current_time - last_verified_at <= 3600`, and denies access if verification is missing, future-dated or expired. Revalidating an unchanged policy renews freshness without spamming the audit revision history. Failed or reverted consensus does not extend the age window. The view may return denied while the stored `health` remains `OK`, which represents the last agreed evidence outcome rather than freshness. Positive permission quotes that include conditions, approvals, exceptions or unbounded limits are deliberately not translated into a usable autonomous cap.
