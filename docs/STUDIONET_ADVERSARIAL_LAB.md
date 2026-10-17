# DRAIL — Isolated Studionet Adversarial Lab

> **Testnet only. No funds, payment, escrow, or live agent transactions.**

## Isolation guarantee

This experiment uses a **separate Git branch** (`studionet-adversarial-lab`), a **separate mutable raw policy URL**, and a **new GenLayer contract instance**. Do not modify, upgrade, redeploy, or reuse the established demo contract `0xC67f64634b603cF3fe62fD3447FEedb3E4707E56`.

Reference evidence for the original demo: [STUDIONET_EVIDENCE.md](../docs/STUDIONET_EVIDENCE.md). The original demo's monitored `fix/security-hardening-v1/examples/policy_v1.txt` must stay at V3.

## Deploy the disposable adversarial instance

**Contract source (identical initial DRAIL code):**
https://raw.githubusercontent.com/bearbaba/DRAIL/studionet-adversarial-lab/contracts/drail.py

**New, lab-only policy URL — use EXACTLY this URL for the constructor:**
https://raw.githubusercontent.com/bearbaba/DRAIL/studionet-adversarial-lab/examples/adversarial/current_policy.txt

Deploy via GenLayer Studio, **Normal (Full Consensus)**, chain **61999 (Studionet)**, with:

| Constructor field | Exact value |
| --- | --- |
| `authority_url` | URL shown above |
| `agent` | `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb` |
| `monitor` | `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb` |
| Deployer/owner wallet | **Same** `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb` |

**Why this agent?** The previous demonstration used an artificial `0x333...3333` agent which cannot sign transactions. This lab uses the wallet you control so that `DrailConsumerFixture.execute()` can be tested through an actual separate contract without transferring assets. Never enter a private key, seed phrase, or API secret in any policy document.

The live source currently contains **version 1** with SEND $100, SWAP $250, BRIDGE prohibited. Its header binds the policy to the agent above and chain 61999. Keep the lab URL unchanged until the new instance has been deployed, `poll()` has FINALIZED, and `status()` + `audit_at(0)` are captured.

## Evidence protocol

For each test: (1) record policy source commit and URL; (2) allow GitHub raw propagation; (3) call the specified contract write with authorized account; (4) capture transaction hash, FINALIZED/ERROR status, and validator consensus output; (5) read `status()`, `can_execute()`, `audit_count()`, and the newest `audit_at()`; (6) mark as PASS only if observed values match expected values. An **ACCEPTED** tx is not automatically **FINALIZED**. A reverted consensus transaction should **not** be treated as a successful state transition. Never infer an allowed right from a quote without checking effective caps.

**The assistant will copy a named snapshot into `current_policy.txt` only after the preceding step was observed.** Snapshots are immutable reference files; the *same* `current_policy.txt` URL is deliberately mutable for the experiment. Use the protected hardening branch for the existing demo, and this isolated branch for the lab.

### Step-by-step matrix

| Phase | Snapshot published at **lab-only** current URL | Action | Expected security property |
| --- | --- | --- | --- |
| A — bootstrap | `01_baseline_v1.txt` (already live) | Owner `poll()` | `INITIALIZED`, V1, caps `[10000,25000,0]`, health `OK` |
| B — immutable version | `02_same_version_mutation_v1.txt` | Owner `poll()` | `UNRESOLVED`, audit `FROZEN_VERSION_CONFLICT`, old caps retained but **all actions denied** |
| C — recovery | Restore exact `01_baseline_v1.txt` bytes | Owner `poll()` | Health `OK`, same V1 digest, rights restored; likely audit `RECOVERED` |
| D — tightening | `03_tightened_v2.txt` | Owner `poll()` | `RESTRICTED`, caps `[5000,15000,0]` without approval |
| E — rollback | `04_rollback_v1.txt` | Owner `poll()` | `UNRESOLVED`, `FROZEN_ROLLBACK`; V2 caps preserved but denied |
| F — recovery | Restore `03_tightened_v2.txt` | Owner `poll()` | Health `OK`, effective V2 caps restored |
| G — wrong agent | `05_wrong_agent_v2.txt` | Owner `poll()` | `FROZEN_UNCLEAR`; verified envelope does not match constructor agent |
| H — wrong chain | Restore V2, then publish `06_wrong_chain_v2.txt` | Poll after healthy recovery | `FROZEN_UNCLEAR`, execution frozen |
| I — duplicate rule | Restore V2, then publish `07_duplicate_send_v2.txt` | Poll after healthy recovery | `FROZEN_UNCLEAR`, conflicting SEND clauses rejected |
| J — oversized source | Restore V2, then publish `08_oversized_v2.txt` | Poll after healthy recovery | `FROZEN_UNCLEAR`; full file exceeds 8192 UTF-8 bytes |
| K — staged widening | Restore V2 then publish `09_widening_v3.txt` | Owner `poll()` | `PENDING_WIDENING`, pending caps `[20000,35000,2500]`; **effective remains `[5000,15000,0]`** |
| L — stale approval | `10_stale_widening_v3.txt` (same version, changed SWAP) | Owner `approve_widening()` | **ERROR/rollback** on source mismatch; effective caps remain V2, `pending=true` |
| M — recheck and approve | Restore **exact** `09_widening_v3.txt` | Owner `approve_widening()` | On successful consensus: caps `[20000,35000,2500]`, `ACTIVE`, audit `WIDENED_BY_OWNER` |
| N — deterministic pause | Leave V3 source unchanged | Owner `emergency_pause()` | `UNRESOLVED`; permission view denies all actions without modifying caps |
| O — recovery | Leave V3 source unchanged | Owner `poll()` | Health `OK`; policy V3 privileges restored after fresh consensus |

**Avoid testing multiple invalid inputs consecutively without restoring a healthy source**: DRAIL is designed not to append another frozen audit entry when it is already `UNRESOLVED` with no pending proposal. Audit indices and revision counts will vary; always use `audit_count()-1` instead of assuming a fixed new index.

### Cross-contract integration — separate consumer fixture

Use `contracts/consumer_fixture.py` as a second contract deployed on Studionet with constructor `guard = <NEW LAB DRAIL ADDRESS>`, **not** the original demo contract address.

- Caller must be the actual registered agent, namely `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb`.
- With V3 `ACTIVE` and evidence fresh: `execute("SEND",8000)` should succeed and `count()` increase by 1.
- `execute("SEND",25000)` must reject and leave `count()` unchanged.
- After `emergency_pause()`, `execute("SEND",100)` must reject and leave `count()` unchanged.
- `count()` is only a dry-run counter: **it does not send, swap or bridge tokens.**

### Optional tests requiring care

- **Network failure / 404:** Cannot be simulated merely by publishing invalid content. A genuine `FETCH_FAILED` may require temporarily removing the lab's `current_policy.txt` or a controlled offline endpoint, which can involve GitHub caching and validator disagreement. Do this only after explicit planning. If the `poll()` transaction itself reverts or consensus fails, use `emergency_pause()` to deny permissions.
- **Freshness expiry:** `can_execute` must deny after 3600 seconds without successful re-verification. Test using a controlled delay or deterministic local harness; do not misclassify network timestamp/clock drift as policy drift.
- **Stale proposal safety:** Do not call `poll()` on a changed same-version V3 source before the intended `approve_widening()` stale-hash rejection, or the flow may freeze as `VERSION_CONFLICT` for a different reason.

## Evidence log — separate from primary V1–V3 demo

| Test | Source commit | New contract | TX / Explorer | State + audit | Verdict |
| --- | --- | --- | --- | --- | --- |
| Lab deployment + baseline | Initial branch commit | TBD | TBD | TBD | PENDING |
| Same-version conflict / recovery | TBD | TBD | TBD | TBD | PENDING |
| V2 rollback + recovery | TBD | TBD | TBD | TBD | PENDING |
| Invalid metadata / conflict / oversize | TBD | TBD | TBD | TBD | PENDING |
| V3 stale widening approval | TBD | TBD | TBD | TBD | PENDING |
| Pause + recover | TBD | TBD | TBD | TBD | PENDING |
| Consumer fixture allow/deny | TBD | TBD | TBD | TBD | PENDING |

**No adversarial-lab live tests have been claimed or performed by creating these fixtures.** User must deploy the new contract instance and run the transactions. Use this document to track actual evidence rather than guessing receipts.
