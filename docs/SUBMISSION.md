# DRAIL — Intelligent Contracts submission draft

**Contribution type:** Builder → Intelligent Contracts (standalone primitive)

**Title:** DRAIL — Consensus-Bound Policy Drift Guard

**Description (below 1000 chars; only submit after real network evidence exists):**

DRAIL is a reusable GenLayer Intelligent Contract for AI-agent permissions that depend on changing authoritative web policies. The contract pins a trusted HTTPS source and uses comparative consensus: validators independently read the policy, verify three action-specific caps (SEND/SWAP/BRIDGE), and bind concrete evidence quotes and source hashes to decisions. Tightening takes effect immediately; widening never auto-grants and requires owner approval plus a fresh, matching consensus read. Ambiguous/unavailable sources freeze execution without falsifying the last verified policy. Includes an append-only audit log, authorized monitor role, emergency pause, and a second contract that consumes can_execute(). Designed as a standalone permission primitive rather than an LLM text classifier.

**Do not submit yet.** Verified deployment and adversarial consensus evidence
still need to be completed; never claim live test passes before execution.

Suggested evidence: source path, tests, architecture, security, proof of live
consensus/validator receipts, explicit tightening/widening state readbacks,
cross-contract consumer accepted/rejected writes, challenge against stale
source / incorrect actor.


## Hardening disclosure (2026-10-17)

V1 has an additional strict source envelope (monotonic policy version,
agent/chain binding), whole-document digest, 8192-byte rejection limit,
deterministic quote/cap checks, duplicate-action rejection, and consumer input
validation. These changes are covered by 33 LOCAL shim tests, 3 official DirectVM tests, both GenVM lints and a
single Studionet bootstrap smoke test. The full tightening/widening lifecycle
and finality-aware consumer check still need real network evidence. Do not claim 500 points, audited safety, signed
publisher authenticity, real-world funds protection, or live validator proof.
