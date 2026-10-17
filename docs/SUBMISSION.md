# DRAIL — Intelligent Contracts submission package

## Form fields
- Contribution Type: **Builder**
- Category: **Intelligent Contracts**
- Contribution Date: **17/10/2026**
- Title: **DRAIL — Consensus-Bound Agent Policy Guard**
- Notes / Description: **936/1000 characters**

DRAIL is a GenLayer Intelligent Contract that converts an owner-pinned, versioned web policy into on-chain SEND, SWAP and BRIDGE limits for AI agents. Validators independently retrieve the source; comparative consensus verifies limits, the full source hash and supporting quotes.

Restrictions apply automatically; increases require owner approval and fresh consensus verification. Conflicting edits, rollbacks, incorrect agent metadata and unverifiable sources freeze authorization while preserving verified limits.

DRAIL exposes can_execute() for downstream integration, an on-chain audit trail, evidence freshness enforcement and emergency pause.

Two Studionet deployments demonstrate the workflow: the main contract covers policy initialization, tightening and owner-approved widening; the security lab covers adversarial freezes and recovery. Reviewers can inspect FINALIZED transactions, audit records and authorization results.

## Evidence & Supporting Information (clean links)

1. **GitHub Repository — DRAIL**  
   https://github.com/bearbaba/DRAIL
2. **GitHub File — Main hardened contract source**  
   https://github.com/bearbaba/DRAIL/blob/fix/security-hardening-v1/contracts/drail.py
3. **GenLayer Explorer Contract — Main DRAIL deployment (V1 → V3)**  
   https://explorer-studio.genlayer.com/address/0xC67f64634b603cF3fe62fD3447FEedb3E4707E56
4. **GenLayer Explorer Contract — Isolated DRAIL security-lab deployment**  
   https://explorer-studio.genlayer.com/address/0x4c80788eA0A3c80906bd365b95f4813ea64D215a
5. **GitHub File — Main Studionet lifecycle evidence and audit**  
   https://github.com/bearbaba/DRAIL/blob/fix/security-hardening-v1/docs/STUDIONET_EVIDENCE.md
6. **GitHub File — Security lab adversarial evidence and recovery**  
   https://github.com/bearbaba/DRAIL/blob/studionet-adversarial-lab/docs/STUDIONET_ADVERSARIAL_LAB.md
7. **Other — Main owner widening FINALIZED TX**  
   https://explorer-studio.genlayer.com/tx/0x78addae43112dfeeb2264a7c33a53f73e758d19cc857689bd1dd56a8c0c077d3
8. **Other — Security lab wrong-agent freeze FINALIZED TX**  
   https://explorer-studio.genlayer.com/tx/0x22ee0b9ec759f7f78ebc135d227660bc4cc6732bf456ee8c4710ddce18c388c6
9. **Other — Security lab recovery FINALIZED TX**  
   https://explorer-studio.genlayer.com/tx/0x822e81fbfc60a8a0c2a30287786271248221ccf42c3a82833e2818d6ac8938ac
10. **Other — Green GitHub Actions CI**  
   https://github.com/bearbaba/DRAIL/actions/runs/39008422126

## Direct Studio inspection links (reviewer convenience)

- Main deployment: https://studio.genlayer.com/?import-contract=0xC67f64634b603cF3fe62fD3447FEedb3E4707E56
- Security Lab deployment: https://studio.genlayer.com/?import-contract=0x4c80788eA0A3c80906bd365b95f4813ea64D215a

## Optional brief evidence note (only if the form has a separate field)

Main DRAIL: V1 policy activation, V2 automatic tightening and V3 owner-approved widening. Security Lab: same-version conflict detection, rollback protection, invalid agent scope, fail-closed authorization and recovery. Inspect the linked FINALIZED receipts, audit entries and permission readbacks for on-chain evidence.

## Reviewer accuracy (repository only, not form notes)

- Two Studionet **deployments of the DRAIL contract design**, not two different standalone primitives.
- The main demonstration and security lab were intentionally isolated, using distinct policy URLs.
- The wrong-chain policy fixture was published but never polled on-chain; no PASS claim is made for it.
- No independent smart contract audit or real-asset transfer is implied by these records.
- The default `main` branch contains an earlier version. Use the linked hardening source and evidence branch files.
- Reviewers can inspect `status()`, `audit_at()` and `can_execute()` in Studio; if evidence is older than the 3600-second TTL, a current read denial does not negate historical FINALIZED evidence.
- The platform submission remains pending until the owner actually presses `Submit Contribution`.
