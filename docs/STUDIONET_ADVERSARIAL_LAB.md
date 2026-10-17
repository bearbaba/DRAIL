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
| Same-version conflict / recovery | Mutation `a247ed8`, restored `c347022` | `0x4c80788eA0A3c80906bd365b95f4813ea64D215a` | [`UNRESOLVED` FINALIZED](https://explorer-studio.genlayer.com/tx/0xa26822c69c44da50da6ae7fa564a83ec6498ac672510293f8e1aae72ce0cd59c); [`ACTIVE` recovery FINALIZED](https://explorer-studio.genlayer.com/tx/0xe3c1b26cdbaa646604634af2efc69d3b361b64d1eb0319f4cc89f81f03999a8c) | version-conflict audit, SEND 100 denied while frozen; post-recovery `health=OK`, revision 3, baseline hash/caps restored | TAMPERING & RECOVERY FULL PASS |
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

### Test B source publication — ready for on-chain execution

- **Published commit:** `a247ed8dc28292e5eee66cc8ea9a1a8f3f91fb49`.
- **Pinned lab source (unchanged URL):** https://raw.githubusercontent.com/bearbaba/DRAIL/studionet-adversarial-lab/examples/adversarial/current_policy.txt
- Confirmed GitHub raw source now reports **`POLICY_VERSION: 1`**, **SEND $90**, **SWAP $250**, **BRIDGE forbidden**. The initial V1 consensus accepted **SEND $100** and prior digest `43614571712be09b85df4452e8b797c6eb2943b422a408a1b4abda54843860a3`. Thus new source bytes conflict with a previously recorded same-version policy.
- The original demonstration branch `fix/security-hardening-v1` was separately checked and **still serves V3**. Original deployed demo `0xC67f64634b603cF3fe62fD3447FEedb3E4707E56` was not upgraded or touched.
- **Next action:** From the authorized Lab owner, call `poll()` on **Lab** `0x4c80788eA0A3c80906bd365b95f4813ea64D215a`, wait for Explorer FINALIZED, then copy `status()` and `audit_at(1)`.
- **Expected response:** `UNRESOLVED`; audit `FROZEN_VERSION_CONFLICT`; `health=UNRESOLVED`, old effective stored caps unchanged, all `can_execute()` requests denied due to health. No new authorization should result from a forbidden version rewrite.
- **Evidence status:** Same-version tampering `poll()` has FINALIZED and returned `UNRESOLVED` with old caps intact and `health=UNRESOLVED` per user-supplied Explorer receipt and Studio status. `audit_at(1)` confirms `FROZEN_VERSION_CONFLICT` with disputed source and preserved cap; the `can_execute` fail-closed readback has now been supplied, returning `false` for SEND 100 while health was UNRESOLVED.

**Next source action is to restore exact original baseline V1 bytes.** Both `audit_at(1)` and permission-denial readback are now supplied. Recovery will restore the archived exact original V1 snapshot, not publish another unauthorized version.

### Test B — same-version content tampering: FINALIZED evidence (2026-10-17)

**Source change:** Lab-only URL remained `https://raw.githubusercontent.com/bearbaba/DRAIL/studionet-adversarial-lab/examples/adversarial/current_policy.txt` while content was modified without incrementing policy version:
- Previously observed V1: SEND $100.00, SWAP $250.00, BRIDGE prohibited; stored hash `43614571712be09b85df4452e8b797c6eb2943b422a408a1b4abda54843860a3`.
- Tampered V1: SEND $90.00, SWAP $250.00, BRIDGE prohibited; new independently fetched `VALID` consensus observation hash `47a2a86548f4cf44f53d1b72e75f0b4b21c2ccbb401f4a41cd75f8f71391d6be`. Version was deliberately kept at `1`.

**Explorer transaction** (user-transcribed) https://explorer-studio.genlayer.com/tx/0xa26822c69c44da50da6ae7fa564a83ec6498ac672510293f8e1aae72ce0cd59c:

| Field | Evidence |
| --- | --- |
| Status | **FINALIZED** |
| Type / method | Call / `poll` |
| From | `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb` |
| To | `0x4c80788eA0A3c80906bd365b95f4813ea64D215a` |
| Nonce | `354` |
| Created at (Explorer display) | Oct 17, 2026, 11:40:18 AM |
| Execution mode | Normal (Full Consensus) |
| Initial validators / rotation | `5` / `0` |
| Consensus result | **Accepted** |
| GenVM execution | **SUCCESS** |
| Return | `"UNRESOLVED"` |
| Equivalence output | `result=VALID`, `policy_version=1`, SEND `9000`, SWAP `25000`, BRIDGE `0`, new digest above |

**Post-poll `status()`** provided by tester:

| Field | Observed |
| --- | --- |
| `initialized` | `true` |
| `health` | **`UNRESOLVED`** |
| `policy_status` | `ACTIVE` (historical policy label; not permission to execute) |
| `evidence_fresh` | `false` |
| `last_policy_version` | `1` |
| `last_source_hash` | **`43614571712be09b85df4452e8b797c6eb2943b422a408a1b4abda54843860a3`**, unchanged baseline |
| `send_cents` / `swap_cents` / `bridge_cents` | **`10000 / 25000 / 0`**, unchanged baseline |
| `revision` | `2` |
| `last_verified_at` | `1792211544`, unchanged |
| `pending` | `false` |

**Interpretation:** The source was intelligible to consensus but its source hash conflicted with the already-approved same-version baseline. The contract rejected the unauthorized in-place revision, kept its last effective limits, froze its health and returned UNRESOLVED. This is **PASS for detection/state freeze**. The audit reason is now directly confirmed by `audit_at(1)`; fail-closed authorization has now been confirmed with a `can_execute` readback; Test B is PASS.

The tester supplied `can_execute(agent, "SEND", 100) = false`. The exact V1 baseline may now be restored and polled for recovery. Main demo on `fix/security-hardening-v1` remains untouched.

### Test B — audit_at(1) readback (reported by tester)

The tester returned the full audit entry after the finalized same-version tampering `poll()`:

| Field | Readback |
| --- | --- |
| `actor` | `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb` |
| `kind` | **`FROZEN_VERSION_CONFLICT`** |
| `policy_version` | `1` |
| `revision` | `2` |
| `send_cents` | `10000` (preserved baseline cap) |
| `send_quote` | `Agents may SEND up to $90.00 per operation.` (disputed newer source) |
| `swap_cents` | `25000` (preserved) |
| `swap_quote` | `Agents may SWAP up to $250.00 per operation.` |
| `bridge_cents` | `0` (preserved) |
| `bridge_quote` | `BRIDGE is prohibited.` |
| `source_sha256` | `47a2a86548f4cf44f53d1b72e75f0b4b21c2ccbb401f4a41cd75f8f71391d6be` |
| `quote_sha256` | `8aad32d16d5286a4b033473fc8fc1907a4ebfbe13147b8235c641a225c1f8443` |

**Audit interpretation:** A quote from the invalid replacement document is retained as *evidence of an attempted policy change*, while the effective cap remains unchanged. The mismatched dollar amounts in quote and cap are intentional and accurately signal the conflict; they do NOT mean the tampered cap was accepted. The `source_sha256` records the conflicting document and the contract's `last_source_hash` stays on the original baseline. The explicit audit kind confirms why the contract froze.

**Test B verdict: PASS.** Same-version tamper detection, preservation of effective caps, audit `FROZEN_VERSION_CONFLICT`, and fail-closed authorization confirmed. The tester reported `can_execute(0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb, "SEND", 100) = false`. The response omitted the `who` field, inferred from the agreed test instructions. Restoration may proceed.

### Test B — Permission fail-closed readback (tester, 2026-10-17)

The tester called the prescribed view `can_execute(who=0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb,action="SEND",amount_cents=100)`. Their Studio response was **`false`** while the contract's health was `UNRESOLVED` after a FINALIZED `FROZEN_VERSION_CONFLICT` poll. The message gave `false SEND 100` but did not reprint the `who` field; the actor association is based on the previously specified input. This completes the live negative read test, without implying that the standalone permission view transferred any funds.

**Case B: PASS.** Next step is restoration of the exact archived version-1 content and a fresh `poll()` of the isolated lab contract. Neither the original demo contract nor its monitored source may be modified.

### Test C — exact V1 source restoration published; live recovery pending

- **Lab-only policy restoration commit:** `c347022de25f2a5234ad1ad27008853e1c2ac6f4`.
- **URL:** https://raw.githubusercontent.com/bearbaba/DRAIL/studionet-adversarial-lab/examples/adversarial/current_policy.txt
- GitHub raw fetch verified **byte-for-byte equality** with the archived `examples/adversarial/snapshots/01_baseline_v1.txt`, blob SHA `26558d9e2b36b5e1c45025e7b62f35bc1ff6b1a9`.
- Restored content: `POLICY_VERSION: 1`, SEND $100, SWAP $250, BRIDGE prohibited, correct lab agent and Studionet chain.
- Original accepted on-chain source digest before tampering: `43614571712be09b85df4452e8b797c6eb2943b422a408a1b4abda54843860a3`. The new `poll()` should independently recompute this **same** digest from the restored bytes.
- **NEXT ACTION:** Owner invokes `poll()` on the SAME Security Lab contract `0x4c80788eA0A3c80906bd365b95f4813ea64D215a`, **Normal (Full Consensus)**. Wait until `FINALIZED`, read `status()`, `audit_count()`, and last `audit_at()`.
- **Expected:** return `ACTIVE` (recovery), `health=OK`, `initialized=true`, `policy_status=ACTIVE`, `last_policy_version=1`, caps `[10000,25000,0]`, `evidence_fresh=true` (until TTL), `revision=3`, `audit_at(2).kind=RECOVERED`.
- After recovery, `can_execute(agent, "SEND", 100)` should return `true` **while evidence is fresh**. Do not mark case C PASS without live readbacks and transaction finality.
- The original demo policy on `fix/security-hardening-v1` was independently checked and still serves version 3. Its deployed reference contract must remain untouched.

**V2 publication is now authorized:** the Lab V1 recovery audit and post-recovery authorization readback have both been recorded.

### Test C — V1 source restoration and successful recovery poll (2026-10-17)

User copied the complete transaction Explorer overview and returned a new `status()` readback. The prior `FROZEN_VERSION_CONFLICT` freeze was lifted **without deploying a new instance or changing version**, once the exact original V1 document was restored at the same pinned Lab URL.

- **Transaction:** https://explorer-studio.genlayer.com/tx/0xe3c1b26cdbaa646604634af2efc69d3b361b64d1eb0319f4cc89f81f03999a8c
- **Explorer status (user-transcribed): FINALIZED**; method `poll`; from `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb`; to `0x4c80788eA0A3c80906bd365b95f4813ea64D215a`.
- Explorer creation timestamp: Oct 17, 2026, 11:52:18 AM; nonce `355`; execution mode Normal; five initial validators; rotation count `0`; consensus `Accepted`; GenVM `SUCCESS`; return `"ACTIVE"`.
- Equivalence output: `result=VALID`, `policy_version=1`, SEND `10000`, SWAP `25000`, BRIDGE `0`; source digest `43614571712be09b85df4452e8b797c6eb2943b422a408a1b4abda54843860a3` **identical to the original V1 baseline**.
- New `status()`: `initialized=true`, `health=OK`, `evidence_fresh=true`, `policy_status=ACTIVE`, `last_policy_version=1`, `revision=3`, effective caps `[10000,25000,0]`, `pending=false`.
- New `last_verified_at=1792212738`; `last_source_hash=43614571712be09b85df4452e8b797c6eb2943b422a408a1b4abda54843860a3`.
- Restored source was checked directly on GitHub: `examples/adversarial/current_policy.txt` has the exact same blob SHA (`26558d9e2b36b5e1c45025e7b62f35bc1ff6b1a9`) as the archived initial V1.
- The Lab contract **remains** `0x4c80788eA0A3c80906bd365b95f4813ea64D215a`; demo contract `0xC67f64634b603cF3fe62fD3447FEedb3E4707E56` and its policy not modified.

**Outcome: recovery FULL PASS**, confirmed by the user-transcribed FINALIZED transaction, status readback, `audit_at(2)` confirming `RECOVERED`, and a subsequent Studio Accepted read showing `can_execute(agent,"SEND",100) = true` (the `who` field was not reprinted). The precondition to publish the V2 tightening fixture is satisfied.

### Test C — recovery audit_at(2) confirmed (tester-reported)

After the successful and FINALIZED recovery `poll()` transaction `0xe3c1b26cdbaa646604634af2efc69d3b361b64d1eb0319f4cc89f81f03999a8c`, tester supplied the complete `audit_at(2)` result:

| Audit field | Observed |
| --- | --- |
| `kind` | **`RECOVERED`** |
| `actor` | `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb` |
| `policy_version` | `1` |
| `revision` | `3` |
| `send_cents` / `swap_cents` / `bridge_cents` | `10000 / 25000 / 0` |
| `send_quote` | `Agents may SEND up to $100.00 per operation.` |
| `swap_quote` | `Agents may SWAP up to $250.00 per operation.` |
| `bridge_quote` | `BRIDGE is prohibited.` |
| `source_sha256` | `43614571712be09b85df4452e8b797c6eb2943b422a408a1b4abda54843860a3` |
| `quote_sha256` | `87b1fa57d2a2c63bb0bc3a376af9d96b604fed653c40782cfca3089a92e2ec1c` |

The recovered source and quote digests **exactly match** the original `audit_at(0)` baseline, and this is a new record at revision 3, preserving the earlier revision-2 `FROZEN_VERSION_CONFLICT` evidence. Both source and audit history were retained with no redeployment.

**Recovery ledger status: FULL PASS** for finalized recovery, audit, and restored authorization. The tester supplied the expected **post-recovery authorization** readback (`true SEND 100`) in the Studio Accepted read response. While `evidence_fresh=true`, call `can_execute(who=owner/agent, action="SEND", amount_cents=100)`, expected **`true`**. Because this contract enforces a one-hour evidence TTL, if it has expired before this check, first renew the observation via `poll()` and recapture the latest `status()`. Keep the Lab source at original V1 until authorization verification is complete.

### Test C — post-recovery authorization confirmed (tester, 2026-10-17)

- Test requested: `can_execute(who=0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb, action="SEND", amount_cents=100)`.
- Studio read reported **Response (Accepted): `true`**, with the action `SEND` and amount `100`. The `who` field was not copied in the text; association to the configured agent comes from the agreed call parameters.
- Prior same-argument read while `health=UNRESOLVED` returned `false`. After the exact V1 bytes were restored and a fresh `poll()` finalized, `health=OK`, `evidence_fresh=true`, the read returned `true`.
- This completes the isolated Lab case **tamper detection → fail-closed freeze → exact-source recovery → restored authorization**, without an asset transfer or redeploy.

**Case B & Case C: FULL PASS.** Lab policy V2 tightening may now be published at the *same Lab-only URL* to prepare the rollback test. Stop and record its poll and audit before publishing a V1 rollback source.
