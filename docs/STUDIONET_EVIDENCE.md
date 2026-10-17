# DRAIL Studionet evidence ledger

This ledger separates **observed state submitted by the tester**, **automated CI tests**, and **independently verified finality**. Never interpret the presence of a transaction hash as proof of `FINALIZED`.

## Deployment and initial policy activation — 2026-10-17

- Network: GenLayer Studionet (`chain_id=61999`)
- Contract: `0xC67f64634b603cF3fe62fD3447FEedb3E4707E56`
- Studio import: https://studio.genlayer.com/?import-contract=0xC67f64634b603cF3fe62fD3447FEedb3E4707E56
- Bootstrap `poll()` transaction (tester-provided): `0xbe88150877b36ce3c9b13b89b69340d606242b0c9e0b061c723a08d9ee23cdf2`
- Explorer transaction details provided by tester: https://explorer-studio.genlayer.com/tx/0xbe88150877b36ce3c9b13b89b69340d606242b0c9e0b061c723a08d9ee23cdf2
- Source URL: https://raw.githubusercontent.com/bearbaba/DRAIL/fix/security-hardening-v1/examples/policy_v1.txt
- Agent: `0x3333333333333333333333333333333333333333`
- Owner and monitor: `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb`

### Readback after `poll()` (reported by tester)

| Field | Readback |
| --- | --- |
| `initialized` | `true` |
| `health` | `OK` |
| `policy_status` | `ACTIVE` |
| `last_policy_version` | `1` |
| `send_cents` | `10000` |
| `swap_cents` | `25000` |
| `bridge_cents` | `0` |
| `revision` | `1` |
| `evidence_fresh` | `true` at time of readback |
| `last_verified_at` | `1792204573` |
| `last_source_hash` | `5a51bed000831d0bef023e0be671439386addf2217f0afea97de927c3f145c81` |
| `pending` | `false` |

### Transaction details copied from GenLayer Explorer by tester

| Explorer field | Reported value |
| --- | --- |
| Transaction status | **FINALIZED** |
| Execution mode | Normal (Full Consensus) |
| GenVM execution | SUCCESS |
| Method | `poll` |
| Return value | `"INITIALIZED"` |
| Consensus result | Accepted |
| Initial validators | 5 |
| Rotation count | 0 |
| Created at (Explorer display) | 2026-10-17 09:36:13 |
| Sender | `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb` |
| Target | `0xC67f64634b603cF3fe62fD3447FEedb3E4707E56` |
| Value | 0 GEN |
| Transaction nonce | 348 |

Full equivalence-principle return value reproduced by the tester:

```json
{"bridge_cents":0,"bridge_quote":"BRIDGE is prohibited.","policy_version":1,"result":"VALID","send_cents":10000,"send_quote":"Agents may SEND up to $100.00 per operation.","source_hash":"5a51bed000831d0bef023e0be671439386addf2217f0afea97de927c3f145c81","swap_cents":25000,"swap_quote":"Agents may SWAP up to $250.00 per operation."}
```

**Evidence level:** Tester-supplied full Studio state readback **plus Explorer transaction-details transcription explicitly showing FINALIZED, SUCCESS and consensus Accepted**. This supports a finalized, successful first policy activation on Studionet. The Explorer SPA was not independently accessible via automated web retrieval, so the original transaction page should be reviewed directly by stewards. It does not prove the full version-change lifecycle, individual validator votes, publisher signatures, or production readiness. The deployed bytecode/source-to-commit linkage has not yet been independently attested.

### Outstanding live cases

- [x] Tester inspected Explorer and supplied `poll()` status **FINALIZED**, GenVM **SUCCESS**, consensus **Accepted** (five initial validators). Independent external retrieval of the Explorer page still pending.
- [x] Tester supplied `audit_at(0)` and confirmed `INITIALIZED`, revision 1, policy version 1, all three source quotes and the expected digest.
- [x] `can_execute(agent, "SEND", 8000)` => `true` (reported from Studio Accepted read).
- [x] `can_execute(agent, "SEND", 12000)` => `false` (reported from Studio Accepted read).
- [ ] `can_execute(agent, "BRIDGE", 100)` => false.
- [x] Tighten version 2 at the same pinned URL; user-provided Studio `status()` confirms caps 5000 / 15000 / 0, `RESTRICTED`, `revision=2`, `pending=false`. **V2 poll transaction hash supplied; its FINALIZED status not independently verified.**
- [ ] Stage version 3; expected `PENDING_WIDENING`, no increases effective before owner approval.
- [ ] Reject unauthorized approval; approve by owner with fresh same-policy observation.
- [ ] Verify source rollback/failure/contradictions and consumer fixture, with transaction hashes and receipts.

**Version-1 snapshot is archived at `examples/archive/policy_v1_finalized_2026-10-17.txt`, plus its original commit SHA.** The contract's pinned `examples/policy_v1.txt` path is a deliberately mutable *live policy endpoint*; changing that path to version 2 triggers the next consensus case. The live endpoint filename is historical, not a guarantee that its content remains at version 1. Tester responses for SWAP and BRIDGE were provided without their original input fields, so those checks remain conditional until independently repeated with recorded inputs.

### User-supplied on-chain audit record (2026-10-17)

- `actor`: `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb`
- `kind`: `INITIALIZED`; `revision`: `1`; `policy_version`: `1`
- `send_cents`: `10000`, quote: `Agents may SEND up to $100.00 per operation.`
- `swap_cents`: `25000`, quote: `Agents may SWAP up to $250.00 per operation.`
- `bridge_cents`: `0`, quote: `BRIDGE is prohibited.`
- `source_sha256`: `5a51bed000831d0bef023e0be671439386addf2217f0afea97de927c3f145c81`
- `quote_sha256`: `87b1fa57d2a2c63bb0bc3a376af9d96b604fed653c40782cfca3089a92e2ec1c`

### Tightening V2 preparation

- Original V1 copied verbatim to `examples/archive/policy_v1_finalized_2026-10-17.txt` prior to changing the live GitHub URL.
- Expected V2 `policy_version=2`, `send_cents=5000`, `swap_cents=15000`, `bridge_cents=0`, result `RESTRICTED`, `revision=2`.
- Live V2 TX: 0x1c795d57bc357c98024c993424fd47a88b118a3ab3de2b5030f2754f37ff3df0. User supplied Explorer link; separate FINALIZED check outstanding.

### Policy V2 tightening — Studio state readback submitted by tester

The tester submitted the on-chain read method `status()` result after polling the same pinned URL, now serving policy version 2. No upgrade or redeployment was reported.

| Field | V2 readback |
| --- | --- |
| `initialized` | `true` |
| `health` | `OK` |
| `policy_status` | `RESTRICTED` |
| `last_policy_version` | `2` |
| `revision` | `2` |
| `send_cents` | `5000` |
| `swap_cents` | `15000` |
| `bridge_cents` | `0` |
| `pending` | `false` |
| `evidence_fresh` | `true` at time of tester's readback |
| `last_source_hash` | `ad37adfe469be68acbce55e3bce8542be6664090e998142894463fd54b62f050` |
| `last_verified_at` | `1792207351` |
| `max_evidence_age_seconds` | `3600` |
| `agent` | `0x3333333333333333333333333333333333333333` |
| `owner` and `monitor` | `0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb` |

This is evidence that an externally changed policy activated a *tightening* state transition on the same contract; **the V2 TX hash was supplied, but Explorer FINALIZED status has not yet been verified**.

### V2 access readbacks submitted by tester

The tester was directed to retain `agent=0x3333333333333333333333333333333333333333` and `action=SEND`, then reported these two successive responses without reiterating the input fields:

| Assumed input | Reported Studio read result | Expected |
| --- | --- | --- |
| `can_execute(agent, "SEND", 8000)` | `false` | `false` |
| `can_execute(agent, "SEND", 4000)` | `true` | `true` |

**Qualification:** The messages gave amounts and response values but omitted the `who` and `action` inputs. These match the prescribed tests *assuming the agent and SEND action were unchanged*. Accepted-state readback is not a transaction FINALIZED receipt. V2 poll TX link and audit_at(1) received; finality verification still pending, then V3 staged widening.

### V2 audit_at(1) — tester readback (2026-10-17)

- V2 poll TX: https://explorer-studio.genlayer.com/tx/0x1c795d57bc357c98024c993424fd47a88b118a3ab3de2b5030f2754f37ff3df0
- actor: 0x4C7cb73aC8F8999af21cfc9fF4cF2333a9508Dcb
- kind: **TIGHTENED**; policy_version: **2**; revision: **2**
- send_cents: **5000**; send_quote: "Agents may SEND up to $50.00 per operation."
- swap_cents: **15000**; swap_quote: "Agents may SWAP up to $150.00 per operation."
- bridge_cents: **0**; bridge_quote: "BRIDGE is prohibited."
- source_sha256: ad37adfe469be68acbce55e3bce8542be6664090e998142894463fd54b62f050
- quote_sha256: b972dc7aa95303ee14fa397c589f75c5fb68b9d9cad19f2d87a735174d4f1134

**Assessment:** User-provided audit and status demonstrate expected effective tightening and full source quotes. Linked Explorer FINALIZED status cannot be independently verified from the available page response.

**Version-2 snapshot:** examples/archive/policy_v2_tightened_2026-10-17.txt, saved before preparing version 3.

### Version-3 widening source published (2026-10-17)

- Mutable monitored path: https://raw.githubusercontent.com/bearbaba/DRAIL/fix/security-hardening-v1/examples/policy_v1.txt
- Publish commit: d85c81d7018c0ac0d7cf441824b0407717baf2d4
- Version: 3. Proposed limits: SEND 20000 cents, SWAP 35000 cents, BRIDGE 2500 cents.
- Expected first poll return: `WIDENING_PENDING`; `policy_status=PENDING_WIDENING`, `pending=true`, `pending_policy_version=3`, `pending_caps=[20000,35000,2500]`.
- Expected **effective** limits before explicit owner approval: `[5000,15000,0]` unchanged; `revision=3`; `audit_at(2).kind=WIDENING_PENDING`.
- Expected blocked before approval: SEND 8000 (false), BRIDGE 100 (false). Permitted while evidence fresh: SEND 4000 (true).
- **Status: V3 state readback submitted, with expected PENDING_WIDENING and effective V2 limits preserved. V3 poll transaction hash, finality evidence and audit_at(2) still pending.**
- The V2 source was archived at `examples/archive/policy_v2_tightened_2026-10-17.txt` before this source edit.


### V3 widening state readback — tester submission

The tester submitted the result of `status()` after invoking the V3 `poll()` against the **same deployed contract**.

| Field | Tester readback |
| --- | --- |
| `last_policy_version` | `3` |
| `policy_status` | `PENDING_WIDENING` |
| `revision` | `3` |
| `health` | `OK` |
| `evidence_fresh` | `true` at time of read |
| `pending` | `true` |
| `pending_policy_version` | `3` |
| `pending_caps` | `[20000,35000,2500]` |
| `send_cents` (effective) | `5000` |
| `swap_cents` (effective) | `15000` |
| `bridge_cents` (effective) | `0` |
| `last_source_hash` | `9e655041844ee3255486b4094dbb5badb6235532497d5155daf84a2ccedfc2fb` |
| `pending_source_hash` | `9e655041844ee3255486b4094dbb5badb6235532497d5155daf84a2ccedfc2fb` |
| `last_verified_at` | `1792207878` |
| `authority_url` | `https://raw.githubusercontent.com/bearbaba/DRAIL/fix/security-hardening-v1/examples/policy_v1.txt` |

**Interpretation:** V3 proposes wider SEND ($200), SWAP ($350), and BRIDGE ($25) caps, but effective rights remain at V2 ($50, $150, $0). This passes the state-level widening-gate assertion and preserves denial-by-default for new permissions. The V3 transaction hash, FINALIZED receipt, and `audit_at(2)` have not yet been supplied; two provisional `can_execute` results during pending widening were supplied without reprinting the full `who`/`action` inputs. Do not count owner authorization as passed until tested.

**Next gate:** Capture V3 poll TX and `audit_at(2)`; test SEND 8000 => false, SEND 4000 => true, BRIDGE 100 => false using the configured agent before `approve_widening()`. Then test unauthorized approval with a different wallet, followed by owner approval against the unchanged same-source digest.

### V3 permission checks while widening pending — user-reported results

User reported these values after being instructed to keep agent `0x3333333333333333333333333333333333333333` and `action=SEND`:

| Test (assuming retained who/action) | User-reported read result | Expected |
| --- | --- | --- |
| `can_execute(agent, "SEND", 8000)` | `false` | `false` |
| `can_execute(agent, "SEND", 4000)` | `true` | `true` |

These match V2 effective limits held during `PENDING_WIDENING` despite V3 proposed SEND 20000 cents. Individual messages did not contain the `who` or `action` fields, so those inputs remain assumed. Outstanding before owner approval: `can_execute(agent, "BRIDGE", 100) == false`, V3 `poll()` TX + finality, `audit_at(2)` and a rejected approval attempt from a non-owner account.
