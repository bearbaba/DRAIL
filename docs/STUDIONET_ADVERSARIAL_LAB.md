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
| Lab deployment + baseline | Lab V1 published in branch | `0x4c80788eA0A3c80906bd365b95f4813ea64D215a` | [`poll()` FINALIZED](https://explorer-studio.genlayer.com/tx/0xb3fd92a84b91c250c9dc2e75df55646f2db3dff6c0380032add7275c6672f943) (tester-transcribed Explorer details) | `ACTIVE`, V1 caps `[10000,25000,0]`, `audit_at(0)=INITIALIZED`, revision 1 | BASELINE PASS |
| Same-version conflict / recovery | TBD | TBD | TBD | TBD | PENDING |
| V2 rollback + recovery | TBD | TBD | TBD | TBD | PENDING |
| Invalid metadata / conflict / oversize | TBD | TBD | TBD | TBD | PENDING |
| V3 stale widening approval | TBD | TBD | TBD | TBD | PENDING |
| Pause + recover | TBD | TBD | TBD | TBD | PENDING |
| Consumer fixture allow/deny | TBD | TBD | TBD | TBD | PENDING |

**Lab deployment has now been reported with a fresh contract address and constructor-state readback.** This is not evidence of a finalized deployment receipt or any adversarial test passing. The V1 `poll()` transaction and updated `status()` readback have now been submitted; Explorer finality and `audit_at(0)` are still outstanding, and all adversarial scenarios remain pending. Capture actual transactions and status before recording outcomes.

### Security Lab instance — initial Studio readback, 2026-10-17

- **New isolated contract**: `0x4c80788eA0A3c80906bd365b95f4813ea64D215a`
- Studio URL: https://studio.genlayer.com/?import-contract=0x4c80788eA0A3c80906bd365b95f4813ea64D215a
- **Network:** GenLayer Studionet (`chain_id=61999`)
- **Pinned source**: `https://raw.githubusercontent.com/bearbaba/DRAIL/studionet-adversarial-lab/examples/adversarial/current_policy.txt`
- **Owner / Monitor / Agent:** `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb`
- **Constructor state observed in user-provided `status()`**: `initialized=false`, `health=UNRESOLVED`, `policy_status=UNVERIFIED`, `revision=0`, `last_policy_version=0`, `evidence_fresh=false`, effective caps `[0,0,0]`, `pending=false`.
- **Update:** owner `poll()` was invoked and the post-poll `status()` readback matches V1 initialization. Confirm Explorer **FINALIZED** and collect `audit_at(0)` before publishing any adversarial source.
- **Do not change** `current_policy.txt` until the Lab V1 transaction finalizes and its audit is captured.
- **Original reference contract untouched**: `0xC67f64634b603cF3fe62fD3447FEedb3E4707E56`.

**Evidence quality:** Studio state readback only; deployment TX hash and finalized status not supplied.

### Baseline V1 poll — state readback and TX submitted (2026-10-17)

- Transaction: https://explorer-studio.genlayer.com/tx/0xb3fd92a84b91c250c9dc2e75df55646f2db3dff6c0380032add7275c6672f943
- Tester copied Explorer details explicitly showing **Status: FINALIZED**, **GenVM SUCCESS**, **Consensus Accepted**, five initial validators, `poll()` return `INITIALIZED`. The explorer UI was not independently retrieved via automated tooling.
- Contract: `0x4c80788eA0A3c80906bd365b95f4813ea64D215a`
- Policy URL: `https://raw.githubusercontent.com/bearbaba/DRAIL/studionet-adversarial-lab/examples/adversarial/current_policy.txt`
- Agent, monitor, owner: `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb`; chain `61999`.

| State field | User-submitted `status()` |
| --- | --- |
| `initialized` | `true` |
| `health` | `OK` |
| `policy_status` | `ACTIVE` |
| `evidence_fresh` | `true` (at test time) |
| `last_policy_version` | `1` |
| `send_cents` / `swap_cents` / `bridge_cents` | `10000 / 25000 / 0` |
| `revision` | `1` |
| `pending` | `false` |
| `last_verified_at` | `1792211544` |
| `last_source_hash` | `43614571712be09b85df4452e8b797c6eb2943b422a408a1b4abda54843860a3` |

**Assessment:** V1 baseline passed at the Studio contract-state, consensus-receipt and audit levels, based on the tester's copied data. The original lab V1 source has been verified byte-for-byte against immutable `01_baseline_v1.txt`. Both prerequisites to publish same-version mutation are satisfied. This does NOT imply that subsequent adversarial case is already tested.

### Baseline V1 — finalized Explorer receipt and audit_at(0) (user evidence)

- TX: https://explorer-studio.genlayer.com/tx/0xb3fd92a84b91c250c9dc2e75df55646f2db3dff6c0380032add7275c6672f943
- **Explorer status: FINALIZED**, execution **SUCCESS**, consensus **Accepted**, five initial validators (user-transcribed receipt).
- Caller: `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb`; target: `0x4c80788eA0A3c80906bd365b95f4813ea64D215a`.
- Method: `poll`; return: `"INITIALIZED"`; nonce `353`; creation time shown: October 17, 2026, 11:32:24 AM.
- Equivalence output: `VALID`, policy 1, caps `10000/25000/0`, source digest `43614571712be09b85df4452e8b797c6eb2943b422a408a1b4abda54843860a3`.
- `audit_at(0)`: `kind=INITIALIZED`, `revision=1`, `policy_version=1`, `actor=0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb`, caps `10000/25000/0`.
- `source_sha256`: `43614571712be09b85df4452e8b797c6eb2943b422a408a1b4abda54843860a3` (matches status and consensus).
- `quote_sha256`: `87b1fa57d2a2c63bb0bc3a376af9d96b604fed653c40782cfca3089a92e2ec1c`.
- Quotes: "Agents may SEND up to $100.00 per operation.", "Agents may SWAP up to $250.00 per operation.", "BRIDGE is prohibited."

**Baseline verdict: PASS.** First adversarial live case may now begin. Keep the original proof/demo contract and its branch unchanged. The lab's frozen V1 snapshot remains at `examples/adversarial/snapshots/01_baseline_v1.txt`.

### Test B — same-version content mutation, awaiting live poll

- Deliberate mutation fixture: `examples/adversarial/snapshots/02_same_version_mutation_v1.txt`.
- The existing lab policy V1 has been read as SEND $100 / SWAP $250 / BRIDGE prohibited.
- Mutated version **still claims `POLICY_VERSION: 1`** but says SEND $90 / SWAP $250 / BRIDGE prohibited.
- On the next owner `poll()`: expected `"UNRESOLVED"`, `health=UNRESOLVED`, `policy_status` remains the last known effective policy status (typically `ACTIVE`), `last_policy_version=1`, stored caps remain `10000/25000/0` but `can_execute` returns **false** for any amount.
- Expected audit at `audit_at(1)`: `kind=FROZEN_VERSION_CONFLICT`, `revision=2` and a new document digest.
- **Do not assert test B PASS** until a new transaction ID, finalized result, `status()` and audit readback are collected.
