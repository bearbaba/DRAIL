# Studionet Demo Protocol (not yet executed)

1. Serve `examples/policy_v1.txt` as plain text at a stable publicly reachable
   `https://.../current-policy.txt`. GenVM needs to fetch it reliably. No login,
   JS render-dependent app shell, URL fragments, tracking query strings, or
   changing banners. Keep a record of the initial content and source commit.
2. Update each published policy's `AGENT` and `CHAIN_ID` header to match
   the selected test wallet / target chain. Increase `POLICY_VERSION` for each
   new edition; NEVER edit the bytes of an already-observed version.
   Deploy `contracts/drail.py` in GenLayer Studio with:
   - `authority_url`: the exact stable HTTPS source (never changes)
   - `agent`: a test wallet that will call the consumer fixture
   - `monitor`: a second test address or the owner for the first run
3. Before initialization, call `can_execute(agent,"SEND",8000)`: false.
   The owner then calls `poll()`. Wait for finality. Record transaction and
   call `status()` and `audit_at(0)`. Expect `SEND=10000`, `SWAP=25000`,
   `BRIDGE=0` (USD cents) if validators interpret source exactly as expected.
4. `can_execute(agent,"SEND",8000)` should now be true;
   `can_execute(agent,"SEND",12000)` false, BRIDGE false, strangers false.
5. Replace content at the SAME source URL with `examples/policy_v2.txt`.
   The authorized monitor polls after source propagation; expect SEND=5000,
   SWAP=15000, BRIDGE=0, with no owner approval call.
6. Replace content with `examples/policy_v3.txt`. The monitor polls; expect
   `PENDING_WIDENING`; the approved effective limits MUST NOT increase.
   Non-owner `approve_widening()` must fail. Owner then calls it; validators
   must re-fetch the current content and confirm identical hash and cents.
7. Negative experiment: stage a new expansion and replace the source again
   BEFORE approval. Owner approval must revert due to stale source digest.
8. Fetch-failure scenario: make the pinned URL return an unavailable response.
   If the comparative transaction FINALIZES with `FETCH_FAILED`, `health` should
   become `UNRESOLVED` and permissions deny. If consensus or RPC instead
   fails, owner/monitor calls `emergency_pause()` and confirms authorization
   is blocked. Restore source, owner/monitor polls to recover.
9. Verify failure cases: oversized source, duplicate SEND clause, wrong
   AGENT/CHAIN_ID, rollback to older policy version, and a forged cap/quote
   mismatch. All must deny new execution if the `poll` finalizes as unresolved.
10. Deploy `contracts/consumer_fixture.py` with DRAIL address, then invoke
   `execute()` with the configured agent. Record accepted/denied execution
   and the consumer's `count()` readback. The fixture DOES NOT move funds.

## Evidence to collect (do not fill with invented links)

| Evidence | URL / receipt |
|---|---|
| Main contract deployment | TODO: actual Explorer URL |
| Initial owner poll transaction | TODO |
| Monitor-driven tightening | TODO |
| Pending widening transaction | TODO |
| Unauthorized approval rejected | TODO |
| Owner recheck + approval | TODO |
| Stale proposal rejected | TODO |
| Outage/freeze test | TODO |
| Consumer deployment and cross-contract call | TODO |
| Test run report and exact revision | TODO |
| Oversized/duplicate/rollback adversarial tx | TODO |
| Publisher identity and signed-version verification | NOT IMPLEMENTED (known V1 limitation) |

Until these are completed, describe the project as a **prototype**, not a
verified mainnet escrow/agent security product.
