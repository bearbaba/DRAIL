# DRAIL — GenLayer Intelligent Contracts Submission (2026-10-17)

## Form

- Category: **Builder → Intelligent Contracts** (standalone reusable primitive, not a full Project).
- Contribution date: **17/10/2026**.
- Title: **DRAIL — Consensus-Bound Agent Policy Guard**
- Notes / Description (943 characters, limit 1,000):

DRAIL is a reusable GenLayer Intelligent Contract that turns an owner-pinned, versioned web policy into on-chain SEND/SWAP/BRIDGE permission limits for AI agents. Validators independently fetch the same source and use comparative consensus to agree on action-specific USD-cent caps, the full document hash and supporting source quotes.

Tightening takes effect automatically. Widening requires owner approval and a fresh matching consensus read. Same-version edits, rollbacks, wrong-agent metadata and unverifiable evidence freeze authorization without overwriting previously verified limits.

DRAIL provides can_execute(), a revision-indexed audit trail, a one-hour evidence-freshness gate and emergency pause. FINALIZED Studionet receipts demonstrate initialization, tightening, owner-gated widening, adversarial freezes and recovery.

This is a non-custodial, reusable permission primitive with a consumer fixture, not a live-funds product.

## Prioritized links to paste into Evidence

1. **Primary reviewed smart contract — complete hardened source:** https://github.com/bearbaba/DRAIL/blob/fix/security-hardening-v1/contracts/drail.py
2. **Production-like main Studionet demo evidence and state audit:** https://github.com/bearbaba/DRAIL/blob/fix/security-hardening-v1/docs/STUDIONET_EVIDENCE.md
3. **Live original GenLayer Intelligent Contract:** https://explorer-studio.genlayer.com/address/0xC67f64634b603cF3fe62fD3447FEedb3E4707E56
4. **Owner-only widening FINALIZED with re-observed source digest:** https://explorer-studio.genlayer.com/tx/0x78addae43112dfeeb2264a7c33a53f73e758d19cc857689bd1dd56a8c0c077d3
5. **Isolated adversarial study and indexed on-chain readbacks:** https://github.com/bearbaba/DRAIL/blob/studionet-adversarial-lab/docs/STUDIONET_ADVERSARIAL_LAB.md
6. **Original code architecture, security limits and consumer contract:** https://github.com/bearbaba/DRAIL/blob/studionet-adversarial-lab/docs/ARCHITECTURE.md and https://github.com/bearbaba/DRAIL/blob/studionet-adversarial-lab/contracts/consumer_fixture.py
7. **CI / GenVM lint + official DirectVM evidence (known successful run):** https://github.com/bearbaba/DRAIL/actions/runs/39002252067

## Live evidence (only what has been documented)

- Main demo contract `0xC67f64634b603cF3fe62fD3447FEedb3E4707E56`: successful `INITIALIZED`, V2 `TIGHTENED`, V3 `PENDING_WIDENING`, unauthorized approve rejected, `WIDENED_BY_OWNER`; owner widening has an explicitly user-transcribed **FINALIZED** receipt. Earlier V2/staging transaction finality is not fully verified in the primary ledger; do not upgrade those claims.
- Separate security lab `0x4c80788eA0A3c80906bd365b95f4813ea64D215a`: V1 activation, same-version tamper `FROZEN_VERSION_CONFLICT`, V2 tightening, V2→V1 `FROZEN_ROLLBACK`, wrong-agent `FROZEN_UNCLEAR`, restorations `RECOVERED`. Tester provided FINALIZED receipts and matching state/audit/permission readbacks. The wrong-chain source fixture was **prepared but not run**; do not say it passed.
- The `can_execute` read only expresses a policy permission; it does **not** move funds, execute swaps or bridge value. The secondary `consumer_fixture.py` source exists, but the complete live cross-contract consumer lifecycle has **not** been verified.
- Security caveats: pinned HTTPS URL is **not** publisher-signature authentication; validator agreement does not guarantee semantic correctness; an external monitor must poll; evidence expires after 3600 seconds. Not audited or certified for mainnet funds.

## Release and reviewer cautions

- The repository default `main` currently points to an earlier prototype. **Use the explicitly linked `fix/security-hardening-v1` source** for the original deployed contract and `studionet-adversarial-lab` for adversarial receipts. Do not imply `main` represents the deployed hardened version.
- The historical README and DEMO notes may contain stale `TODO` labels; this page and the two receipts ledgers identify what is verified. Do not confuse an **ACCEPTED** receipt with **FINALIZED**.
- The security Lab's mutable policy URL has been restored to approved V2 and is not the original demo's V3 policy URL.
- GitHub Actions fixture assertion had a stale V1-only assumption after changing the isolated Lab policy to V2. Patch commit `03e22881be03bd076f46f5d54aaa05743a5ecb4f` updates the static test to accept one of the checked-in snapshots; check a new CI run before claiming the current branch is green.

## Distinction from generic AI page classification

The verified decision changes permission-gating state: `can_execute(agent,action,cents)` denies after ambiguity, rollback or conflicting evidence; automatic tightening and owner-only widening have asymmetric consequences. GenLayer validators independently retrieve evidence and compare the decision-driving caps, source hash and quotes, while immutable source versions and the audit ledger make permission drift inspectable.

## Form submission status

**Draft ready to paste. Not submitted to the GenLayer website by this file update.** Submission requires the user or an authorized web agent to complete the platform form and press `Submit Contribution`.
