# DRAIL Studionet evidence ledger

This ledger separates **observed state submitted by the tester**, **automated CI tests**, and **independently verified finality**. Never interpret the presence of a transaction hash as proof of `FINALIZED`.

## Deployment and initial policy activation — 2026-10-17

- Network: GenLayer Studionet (`chain_id=61999`)
- Contract: `0xC67f64634b603cF3fe62fD3447FEedb3E4707E56`
- Studio import: https://studio.genlayer.com/?import-contract=0xC67f64634b603cF3fe62fD3447FEedb3E4707E56
- Bootstrap `poll()` transaction (tester-provided): `0xbe88150877b36ce3c9b13b89b69340d606242b0c9e0b061c723a08d9ee23cdf2`
- Explorer link pattern (check finality in browser): https://explorer-studio.genlayer.com/tx/0xbe88150877b36ce3c9b13b89b69340d606242b0c9e0b061c723a08d9ee23cdf2
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

**Evidence level:** Human-submitted full `status()` result and transaction ID. These show the initial policy activation had committed to observable Studio contract state when read. Exact validator votes, the transaction's finality state, and immutable linkage to the deployed code commit have not yet been independently checked. Do not claim fully finalized consensus or production readiness from this ledger alone.

### Outstanding live cases

- [ ] Verify deployment and `poll` finality in Explorer.
- [ ] Record `audit_at(0)` (quote evidence, revision, provenance).
- [ ] `can_execute(agent, "SEND", 8000)` => true while policy verification remains fresh.
- [ ] `can_execute(agent, "SEND", 12000)` => false.
- [ ] `can_execute(agent, "BRIDGE", 100)` => false.
- [ ] Tighten version 2 **at the same pinned URL**; expected caps: 5000 / 15000 / 0; record tx and verify finality.
- [ ] Stage version 3; expected `PENDING_WIDENING`, no increases effective before owner approval.
- [ ] Reject unauthorized approval; approve by owner with fresh same-policy observation.
- [ ] Verify source rollback/failure/contradictions and consumer fixture, with transaction hashes and receipts.

**Do not change `examples/policy_v1.txt` in the connected branch until all V1 snapshots and `can_execute` checks have been recorded.** Updating that path is a live policy change for this deployed demo instance.
