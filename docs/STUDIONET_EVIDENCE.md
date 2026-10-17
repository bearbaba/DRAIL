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
- [ ] Record `audit_at(0)` (quote evidence, revision, provenance).
- [ ] `can_execute(agent, "SEND", 8000)` => true while policy verification remains fresh.
- [ ] `can_execute(agent, "SEND", 12000)` => false.
- [ ] `can_execute(agent, "BRIDGE", 100)` => false.
- [ ] Tighten version 2 **at the same pinned URL**; expected caps: 5000 / 15000 / 0; record tx and verify finality.
- [ ] Stage version 3; expected `PENDING_WIDENING`, no increases effective before owner approval.
- [ ] Reject unauthorized approval; approve by owner with fresh same-policy observation.
- [ ] Verify source rollback/failure/contradictions and consumer fixture, with transaction hashes and receipts.

**Do not change `examples/policy_v1.txt` in the connected branch until all V1 snapshots and `can_execute` checks have been recorded.** Updating that path is a live policy change for this deployed demo instance.
