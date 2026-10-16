# DRAIL

**Evidence changes. Permissions adapt.**

DRAIL is a standalone GenLayer Intelligent Contract that reads an owner-pinned
HTTPS policy document and keeps three AI-wallet capabilities (`SEND`, `SWAP`,
`BRIDGE`) bound to independently verified, on-chain limits. It detects semantic
policy drift, applies **tightening immediately** after consensus, stages
**widening** for explicit owner approval plus another independent source check,
and freezes execution when evidence cannot be verified.

> **Status: V1 source prototype (2026-10-16).** Python compilation and 13
> deterministic shim tests pass. NOT yet validated with `genvm-lint`, live
> GenLayer validators, GenLayer Studio, or a verified deployed address. This is
> not an audited contract, payment custody system, autonomous scheduler, or
> guarantee of policy correctness. **Do not use to control real funds.**

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
   at deployment; callers to `poll()` cannot supply alternative evidence.
2. **Reproducible comparative consensus.** Leader and validators independently
   fetch the pinned URL and extract decision-driving cents and verbatim source
   excerpts. The equivalence principle compares all three limits EXACTLY,
   requires matching source digest, and binds the meaning of each citation.
3. **Asymmetric policy drift.** Consensus-approved decreases take immediate
   effect. Increases only stage `PENDING_WIDENING` until the owner approves and
   the latest source is re-read and matches the staged hash and caps.
4. **Mixed change safety.** When an update tightens SEND but loosens SWAP,
   SEND tightens immediately; SWAP cannot widen without owner consent.
5. **Fail-closed execution view.** `UNRESOLVED` blocks all new authorization
   even though last known policy limits remain preserved for future recovery.
   Deterministic `emergency_pause()` covers consensus disagreement or RPC
   failures that cause `poll()` itself to revert.
6. **Inspectable append-only audit trail.** Each material change stores caller,
   source digest, supporting quotes, all effective caps, and revision index.
7. **Composable enforcement.** Consumers call `can_execute(agent, action,
   amount_cents)`; an example secondary GenLayer contract demonstrates this
   read-based gate without moving assets.

## Structure

```text
contracts/drail.py                Main standalone Intelligent Contract
contracts/consumer_fixture.py     Optional downstream integration demonstrator
examples/policy_v1.txt           Baseline authority policy
examples/policy_v2.txt           Strict policy (automatic reduction)
examples/policy_v3.txt           Expanded policy (requires owner approval)
tests/test_local_contract.py      13 deterministic state/invariant tests
studionet/test_live.py           Live GenLayer validation scaffold (not run)
docs/ARCHITECTURE.md             State model and trust assumptions
docs/SECURITY.md                 Threat model and limitations
docs/DEMO.md                     Studio walkthrough + evidence checklist
docs/SUBMISSION.md               Draft contribution information
```

## Contract API

Constructor: `Drail(authority_url: str, agent: Address, monitor: Address)`.
The deployer is owner. Initial authorizations are all denied until the **owner**
calls `poll()` and the pinned source is successfully validated.

| Method | Access | Behavior |
|---|---|---|
| `poll()` | owner / monitor | Independently validate source; tighten, freeze, or stage widening |
| `approve_widening()` | owner | Re-fetch and verify same source digest + same caps before increasing grants |
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
# 13 passed in the authoring environment
python -m compileall -q contracts
```

These tests use a fake GenLayer runtime and simulated leader answers. They
exercise deterministic state transitions but **do not prove validator
agreement**, real web retrieval, cross-contract call finality, or live ABI
compatibility. Those need SDK validation and Studio integration.

## Next verification steps

1. Install the official GenVM lint tools and run
   `genvm-lint check contracts/drail.py` and
   `genvm-lint check contracts/consumer_fixture.py`.
2. Host `examples/policy_v1.txt` at a public, stable HTTPS URL with no dynamic
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
