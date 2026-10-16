# DRAIL

**Evidence changes. Permissions adapt.**

DRAIL is a standalone GenLayer Intelligent Contract that reads an owner-pinned
HTTPS policy document and keeps three AI-wallet capabilities (`SEND`, `SWAP`,
`BRIDGE`) bound to independently verified, on-chain limits. It detects semantic
policy drift, applies **tightening immediately** after consensus, stages
**widening** for explicit owner approval plus another independent source check,
and freezes execution when evidence cannot be verified.

> **Status: V1 hardening candidate (2026-10-17).** 33 local shim tests,
> 3 official GenLayer DirectVM tests and GenVM lints passed. One Studionet
> bootstrap smoke test also passed; full live lifecycle and consumer finality
> remain unverified. Not audited, not a custody system. **Do not use for real funds.**

## Problem

Conventional smart contracts can check a document hash, but cannot determine
whether a natural-language rule meaningfully changes an agent's authority.
A naive AI oracle can return `ALLOW` without binding that answer to a trusted
source, let an attacker expand privileges, or interpret network failure as an
actual policy revocation. DRAIL is deliberately narrow: one pinned HTTPS
source, three scoped capabilities, exact cents, and permission state that other
contracts can enforce.

## What is new about the design?

1. **Pin the evidence boundary in state.** The owner chooses the trusted URL
   at deployment; callers to `poll()` cannot supply alternative evidence. The
   policy additionally declares its version, agent, chain, currency and status.
   Versions must increase monotonically, and content at a given version may not change.
2. **Reproducible comparative consensus.** Leader and validators independently
   fetch the pinned URL and extract decision-driving cents and verbatim source
   excerpts. The equivalence principle compares all three limits EXACTLY,
   requires matching source digest, and binds the meaning of each citation.
3. **Bounded and locally checked evidence.** No silent text truncation: policy
   files larger than 8192 UTF-8 bytes are rejected. Exactly one operative
   SEND/SWAP/BRIDGE rule is allowed. A quoted amount must agree with the
   cent value emitted by AI; conflicting quotes freeze execution. The digest
   covers the complete policy file, not a prefix.
4. **Asymmetric policy drift.** Consensus-approved decreases take immediate
   effect. Increases only stage `PENDING_WIDENING` until the owner approves and
   the latest source is re-read and matches the staged hash and caps.
5. **Mixed change safety.** When an update tightens SEND but loosens SWAP,
   SEND tightens immediately; SWAP cannot widen without owner consent.
6. **Fail-closed execution view.** `UNRESOLVED` blocks all new authorization
   even though last known policy limits remain preserved for future recovery.
   Deterministic `emergency_pause()` covers consensus disagreement or RPC
   failures that cause `poll()` itself to revert.
7. **Inspectable append-only audit trail.** Each material change stores caller,
   source digest, supporting quotes, all effective caps, and revision index.
8. **Composable enforcement.** Consumers call `can_execute(agent, action,
   amount_cents)`; an example secondary GenLayer contract demonstrates this
   read-based gate without moving assets.

## Structure

```text
contracts/drail.py                Main standalone Intelligent Contract
contracts/consumer_fixture.py     Optional downstream integration demonstrator
examples/policy_v1.txt           Baseline authority policy
examples/policy_v2.txt           Strict policy (automatic reduction)
examples/policy_v3.txt           Expanded policy (requires owner approval)
tests/test_local_contract.py      33 deterministic state/invariant tests
   tests/test_direct_genvm.py        3 official GenLayer direct-mode tests
studionet/test_live.py           Live GenLayer validation scaffold (not run)
docs/ARCHITECTURE.md             State model and trust assumptions
docs/SECURITY.md                 Threat model and limitations
docs/DEMO.md                     Studio walkthrough + evidence checklist
docs/SUBMISSION.md               Draft contribution information
```


## Strict source format (V1 security boundary)

DRAIL intentionally accepts a SMALL, canonical plain-text authority document.
A policy must be UTF-8 and <=8192 bytes, with LF newlines and this header:

```text
DRAIL_POLICY_V1
POLICY_VERSION: 1
AGENT: 0x3333333333333333333333333333333333333333
CHAIN_ID: 61999
CURRENCY: USD
STATUS: EFFECTIVE

Agents may SEND up to $100.00 per operation.
Agents may SWAP up to $250.00 per operation.
BRIDGE is prohibited.
```

These example address/chain values are NOT universally valid: change them to
match the constructor agent and actual chain before deployment. Each action
must be mentioned exactly once in the rule body. A positive cap needs one
unambiguous USD amount with an explicit maximum and per-operation scope.
Prohibitions or human approval requirements map to zero autonomous allowance.
Ambiguous/conflicting/oversized sources are rejected, not truncated or guessed.
Once version N is observed, its document bytes cannot change. A version N-1
rollback freezes policy execution. Published versions may increase, and widened
caps require owner approval plus a second matching consensus observation.

**Source trust limit:** the HTTPS URL is NOT a cryptographic publisher proof.
A compromised hosting account can publish a malicious higher policy version.
Monotonic versions are an anti-rollback check, not signature verification. Full
publisher signature verification, automatic expiry and token price conversion
are outside this prototype. Never rely on this for real assets without them.

## Contract API

Constructor: `Drail(authority_url: str, agent: Address, monitor: Address)`.
The deployer is owner. Initial authorizations are all denied until the **owner**
calls `poll()` and the pinned source is successfully validated.

| Method | Access | Behavior |
|---|---|---|
| `poll()` | owner / monitor | Independently validate source; tighten, freeze, or stage widening |
| `approve_widening()` | owner | Re-fetch and verify same version + source digest + caps before increasing grants |
| `emergency_pause()` | owner / monitor | Freeze authorizations without consensus (e.g. after failed transaction) |
| `change_monitor(address)` | owner | Change authorized watcher |
| `can_execute(agent, action, amount_cents)` | view | Enforce permission and approved cap |
| `status()` | view | Inspect effective/pending limits and evidence digest |
| `audit_count()`, `audit_at(i)` | view | Historical revision evidence and actor |

Caps are *USD cents*, not GEN or token units. **Consumer adapters are
responsible for trustworthy currency conversion and enforcing spending on the
actual asset.** No native value or ERC-20 is transferred here.

## Local tests (already executed)

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q tests/test_local_contract.py
# 33 passed in the authoring environment
python -m compileall -q contracts
```

The local tests use a fake GenLayer runtime and simulated leader answers. They
exercise deterministic state transitions but **do not prove validator
agreement**, real web retrieval, cross-contract call finality, or live ABI
compatibility. Those need SDK validation and Studio integration.

## Verified CI and Studionet evidence

- [GenVM lint + GenLayer DirectVM CI](https://github.com/bearbaba/DRAIL/actions/runs/38945186723): both contracts lint clean and 3 direct tests passed.
- [Studionet bootstrap smoke test](https://github.com/bearbaba/DRAIL/actions/runs/38944318539): deploy, denied monitor bootstrap, authorized owner poll and state readback passed.
- Both reports are specific to the referenced commits, not the final testnet lifecycle. See [DEMO](docs/DEMO.md) for missing evidence.

## Next verification steps

1. GitHub Actions includes an additional `genvm-validation` job. The local
   environment did not have GenVM tooling installed; ensure this job is green,
   using the actual SDK and runner, before claiming compatibility. Run
   `genvm-lint check contracts/drail.py` and
   `genvm-lint check contracts/consumer_fixture.py`.
2. Adapt `AGENT` and `CHAIN_ID` in ALL example policies to exactly match the
   deployment's agent and chain; preserve the strict metadata envelope, and
   publish version 1 then 2 then 3 at the SAME URL. Host `examples/policy_v1.txt`
   at a public, stable HTTPS URL with no dynamic
   ads/banners. Use that exact URL as `authority_url`.
3. Deploy to **Studionet**, owner-call `poll()`, confirm status and approved
   caps. Independently confirm read-back and transaction finality in Explorer.
4. Replace content **at the same URL** with v2 and test automatic tightening.
   Replace with v3 and test staged widening, denial before approval, denial by
   non-owner, fresh verification, and explicit owner approval.
5. Test a missing URL, conflicting policy, fabricated source excerpt,
   stale-pending-source approval, and a real deployed consumer fixture.
6. Capture actual contract addresses, transaction hashes, validated source
   and screenshots in the evidence table. Never claim success from a local
   shim test alone.

See [DEMO](docs/DEMO.md) and [SECURITY](docs/SECURITY.md).

## Upstream SDK reference

- https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle
- https://docs.genlayer.com/developers/intelligent-contracts/features/non-determinism
- https://docs.genlayer.com/developers/intelligent-contracts/features/storage
- https://docs.genlayer.com/developers/intelligent-contracts/features/interacting-with-intelligent-contracts

MIT license. Inspiration from published GenLayer consensus primitives; DRAIL's
source code and permission drift architecture are independently authored.
