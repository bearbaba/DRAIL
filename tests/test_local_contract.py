"""Deterministic harness for state invariants, NOT a substitute for live gltest.

A GenLayer shim exercises consensus OUTPUT handling and all state transitions.
It does not simulate validator voting, web snapshots across nodes or finality.
"""
import importlib.util
import json
import pathlib
import sys
import types

import pytest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'contracts' / 'drail.py'
OWNER = '0x' + '1'*40
WATCHER = '0x' + '2'*40
AGENT = '0x' + '3'*40
STRANGER = '0x' + '4'*40


class Address(str):
    @property
    def as_hex(self):
        return str(self)


class FakeStorageBase:
    def __getattr__(self, key):
        if key == 'audit':
            self.audit = []
            return self.audit
        raise AttributeError(key)


class FakePrinciple:
    def __init__(self, svc):
        self.svc = svc

    def prompt_comparative(self, leader, principle):
        assert 'THREE' in principle
        assert 'independently fetches' in principle
        self.svc.rounds += 1
        return leader()


class FakeSvc:
    def __init__(self):
        self.page = ''
        self.response = None
        self.rounds = 0

    def render(self, url, mode='text'):
        assert url == 'https://policy.example.org/current'
        assert mode == 'text'
        if self.page is None:
            raise OSError('fetch unavailable')
        return self.page

    def exec_prompt(self, prompt):
        assert 'SOURCE (' in prompt
        if self.response is None:
            raise ValueError('no model answer')
        return json.dumps(self.response)


def fixture_doc(send=100, swap=250, bridge=None, version=1, agent=AGENT, chain=61999):
    clauses = [
        ('SEND is prohibited.' if send == 0 else f'Agents may SEND up to ${send:.2f} per operation.'),
        ('SWAP is prohibited.' if swap == 0 else f'Agents may SWAP up to ${swap:.2f} per operation.'),
        ('BRIDGE is prohibited.' if bridge is None else
         f'Agents may BRIDGE up to ${bridge:.2f} per operation.'),
    ]
    caps = [int(send*100), int(swap*100), 0 if bridge is None else int(bridge*100)]
    model = dict(result='VALID', send_cents=caps[0], swap_cents=caps[1],
                 bridge_cents=caps[2], send_quote=clauses[0],
                 swap_quote=clauses[1], bridge_quote=clauses[2])
    header = ["DRAIL_POLICY_V1", f"POLICY_VERSION: {version}",
              f"AGENT: {agent}", f"CHAIN_ID: {chain}",
              "CURRENCY: USD", "STATUS: EFFECTIVE", ""]
    return '\n'.join(header + clauses), model


@pytest.fixture
def ctx(monkeypatch):
    svc = FakeSvc()
    gl = types.SimpleNamespace()
    gl.Contract = FakeStorageBase
    gl.vm = types.SimpleNamespace(UserError=ValueError)
    gl.message = types.SimpleNamespace(sender_address=Address(OWNER), chain_id=61999)
    gl.public = types.SimpleNamespace(write=lambda fn: fn, view=lambda fn: fn)
    gl.nondet = types.SimpleNamespace(web=types.SimpleNamespace(render=svc.render),
                                     exec_prompt=svc.exec_prompt)
    gl.eq_principle = FakePrinciple(svc)
    mod = types.ModuleType('genlayer')
    mod.gl = gl
    mod.Address = Address
    mod.u256 = int
    mod.DynArray = list
    mod.TreeMap = dict
    mod.allow_storage = lambda obj: obj
    monkeypatch.setitem(sys.modules, 'genlayer', mod)
    spec = importlib.util.spec_from_file_location('drail_test_module', SOURCE)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, 'drail_test_module', module)
    spec.loader.exec_module(module)
    contract = module.Drail('https://policy.example.org/current', Address(AGENT), Address(WATCHER))
    def actor(addr):
        gl.message.sender_address = Address(addr)
    def set_document(send=100, swap=250, bridge=None, version=1):
        svc.page, svc.response = fixture_doc(send, swap, bridge, version=version)
    return contract, svc, actor, set_document


def test_initially_locked_and_owner_only_bootstrap(ctx):
    c, svc, actor, set_doc = ctx
    assert c.can_execute(Address(AGENT), 'SEND', 100) is False
    set_doc()
    actor(WATCHER)
    with pytest.raises(ValueError, match='owner must activate'):
        c.poll()
    actor(OWNER)
    assert c.poll() == 'INITIALIZED'
    assert c.can_execute(Address(AGENT), 'SEND', 8000)
    assert not c.can_execute(Address(AGENT), 'SEND', 10001)
    assert not c.can_execute(Address(AGENT), 'BRIDGE', 1)
    assert not c.can_execute(Address(STRANGER), 'SEND', 100)
    assert not c.can_execute(Address(AGENT), 'HACK', 1)
    assert c.audit_count() == 1


def test_tightening_is_immediate_and_poll_idempotent(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    actor(WATCHER)
    set_doc(send=50, swap=150, version=2)
    assert c.poll() == 'RESTRICTED'
    assert not c.can_execute(Address(AGENT), 'SEND', 8000)
    assert c.can_execute(Address(AGENT), 'SEND', 3000)
    assert c.audit_count() == 2
    assert c.poll() == 'RESTRICTED'
    assert c.audit_count() == 2


def test_widening_requires_owner_plus_fresh_source(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    actor(WATCHER)
    set_doc(send=200, swap=350, bridge=25, version=2)
    assert c.poll() == 'WIDENING_PENDING'
    assert not c.can_execute(Address(AGENT), 'SEND', 15000)
    assert not c.can_execute(Address(AGENT), 'BRIDGE', 100)
    with pytest.raises(ValueError, match='owner only'):
        c.approve_widening()
    actor(OWNER)
    assert c.approve_widening() == 'ACTIVE'
    assert c.can_execute(Address(AGENT), 'SEND', 15000)
    assert c.can_execute(Address(AGENT), 'BRIDGE', 100)
    with pytest.raises(ValueError, match='no valid staged widening'):
        c.approve_widening()


def test_stale_pending_revision_cannot_be_approved(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    set_doc(send=200, version=2)
    c.poll()
    set_doc(send=300, version=3)
    with pytest.raises(ValueError, match='source changed'):
        c.approve_widening()
    assert not c.can_execute(Address(AGENT), 'SEND', 15000)


def test_mixed_revision_tightens_even_when_other_cap_widens(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    actor(WATCHER)
    set_doc(send=50, swap=500, version=2)
    assert c.poll() == 'WIDENING_PENDING'
    assert not c.can_execute(Address(AGENT), 'SEND', 8000)
    assert not c.can_execute(Address(AGENT), 'SWAP', 45000)
    assert c.can_execute(Address(AGENT), 'SWAP', 20000)


def test_fetch_failure_freezes_but_preserves_baseline(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    original = json.loads(c.status())
    svc.page = None
    actor(WATCHER)
    assert c.poll() == 'UNRESOLVED'
    assert not c.can_execute(Address(AGENT), 'SEND', 10)
    frozen = json.loads(c.status())
    assert frozen['send_cents'] == original['send_cents']
    assert frozen['last_source_hash'] == original['last_source_hash']
    assert c.poll() == 'UNRESOLVED'
    assert c.audit_count() == 2  # no repeated freeze spam
    set_doc()
    assert c.poll() == 'ACTIVE'
    assert c.can_execute(Address(AGENT), 'SEND', 10)


def test_invalid_citation_fails_closed(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    svc.response['send_quote'] = 'fabricated from another website'
    assert c.poll() == 'UNRESOLVED'
    assert not c.can_execute(Address(AGENT), 'SEND', 100)


def test_missing_action_fails_closed(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    svc.page = 'Only SEND is permitted; no other rules.'
    svc.response = {'result': 'UNCLEAR'}
    assert c.poll() == 'UNRESOLVED'
    assert not c.can_execute(Address(AGENT), 'SEND', 100)


def test_revocation_and_owner_only_monitor_change(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    actor(STRANGER)
    with pytest.raises(ValueError, match='owner or monitor'):
        c.poll()
    with pytest.raises(ValueError, match='owner only'):
        c.change_monitor(Address(STRANGER))
    actor(WATCHER)
    set_doc(send=0, swap=0, version=2)
    assert c.poll() == 'REVOKED'
    assert not c.can_execute(Address(AGENT), 'SEND', 1)
    actor(OWNER)
    c.change_monitor(Address(STRANGER))
    assert c.monitor == Address(STRANGER)


def test_multiple_actions_and_invalid_amounts(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    assert c.can_execute(Address(AGENT), 'swap', 20000)
    for bad in (0, -1, True, 10**15):
        assert not c.can_execute(Address(AGENT), 'SEND', bad)


def test_outage_invalidates_pending_widening(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    set_doc(send=200, version=2)
    assert c.poll() == 'WIDENING_PENDING'
    svc.page = None
    assert c.poll() == 'UNRESOLVED'
    with pytest.raises(ValueError, match='no valid staged widening'):
        c.approve_widening()
    assert not c.can_execute(Address(AGENT), 'SEND', 1)


def test_emergency_pause_can_freeze_after_failed_consensus(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    actor(STRANGER)
    with pytest.raises(ValueError, match='owner or monitor'):
        c.emergency_pause()
    actor(WATCHER)
    c.emergency_pause()
    assert not c.can_execute(Address(AGENT), 'SEND', 10)
    count = c.audit_count()
    c.emergency_pause()
    assert c.audit_count() == count
    set_doc()
    assert c.poll() == 'ACTIVE'
    assert c.can_execute(Address(AGENT), 'SEND', 10)


def test_audit_preserves_verbatim_quotes_and_actor(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    audit = json.loads(c.audit_at(0))
    assert audit['actor'] == OWNER
    assert 'SEND up to $100.00' in audit['send_quote']
    assert len(audit['quote_sha256']) == 64
    with pytest.raises(ValueError, match='missing audit'):
        c.audit_at(999)


# Security regression tests: DO NOT remove to "fix" a failing contract.
def test_forged_numeric_cap_is_not_authorized(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    svc.response["send_cents"] = 99999999  # quote still says $100
    assert c.poll() == "UNRESOLVED"
    assert not c.initialized
    assert not c.can_execute(Address(AGENT), "SEND", 8000)


def test_full_document_is_not_silently_truncated(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    before = c.audit_count()
    old_hash = json.loads(c.status())["last_source_hash"]
    # A >8192-byte page with late revocation MUST NEVER be accepted as valid.
    svc.page += "\n" + ("Z" * 9000) + "\nSEND is prohibited."
    assert c.poll() == "UNRESOLVED"
    assert json.loads(c.status())["health"] == "UNRESOLVED"
    assert c.audit_count() == before + 1
    assert json.loads(c.status())["last_source_hash"] == old_hash
    assert not c.can_execute(Address(AGENT), "SEND", 100)


def test_same_version_edit_freezes_instead_of_applying(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    set_doc(send=50, version=1)
    assert c.poll() == "UNRESOLVED"
    assert c.send_cents == 10000  # preserved but no execution allowed
    assert not c.can_execute(Address(AGENT), "SEND", 100)
    assert json.loads(c.status())["last_policy_version"] == 1


def test_old_version_cannot_widen_after_tightening(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    set_doc(send=50, version=2)
    assert c.poll() == "RESTRICTED"
    set_doc(send=100, version=1)
    assert c.poll() == "UNRESOLVED"
    assert c.send_cents == 5000
    assert not c.can_execute(Address(AGENT), "SEND", 8000)


def test_wrong_agent_and_chain_fail_closed(ctx):
    c, svc, actor, set_doc = ctx
    doc, answer = fixture_doc(agent=STRANGER)
    svc.page, svc.response = doc, answer
    assert c.poll() == "UNRESOLVED"
    doc, answer = fixture_doc(chain=100)
    svc.page, svc.response = doc, answer
    assert c.poll() == "UNRESOLVED"


def test_wrong_currency_and_missing_version_fail_closed(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    svc.page = svc.page.replace("CURRENCY: USD", "CURRENCY: EUR")
    assert c.poll() == "UNRESOLVED"
    set_doc()
    svc.page = svc.page.replace("POLICY_VERSION: 1", "POLICY_VERSION: unknown")
    assert c.poll() == "UNRESOLVED"


def test_wrong_quote_scope_rejected(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    svc.response["send_quote"] = svc.response["swap_quote"]
    assert c.poll() == "UNRESOLVED"
    assert not c.initialized


def test_multiple_usd_values_are_ambiguous(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    additional = "Agents may SEND up to $100.00 per operation, not $10000.00."
    svc.page += "\n" + additional
    svc.response["send_quote"] = additional
    assert c.poll() == "UNRESOLVED"


def test_quote_claiming_zero_without_prohibition_rejected(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    svc.response["send_cents"] = 0
    assert c.poll() == "UNRESOLVED"


def test_new_version_valid_recovery_after_rollback(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    set_doc(send=50, version=2)
    c.poll()
    set_doc(version=1)
    c.poll()
    set_doc(send=40, version=3)
    assert c.poll() == "RESTRICTED"
    assert c.can_execute(Address(AGENT), "SEND", 3000)
    assert not c.can_execute(Address(AGENT), "SEND", 8000)
    assert json.loads(c.status())["last_policy_version"] == 3


def test_strict_positive_quote_parses_USD_cents(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    assert c.can_execute(Address(AGENT), "SEND", 10000)
    assert not c.can_execute(Address(AGENT), "SEND", 10001)
    entry = json.loads(c.audit_at(0))
    assert entry["policy_version"] == 1


def test_duplicate_action_clause_is_ambiguous(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    # A later restriction must not be ignored even if the model quotes the old rule.
    svc.page += "\nSEND is prohibited."
    assert c.poll() == "UNRESOLVED"
    assert not c.initialized


def test_positive_amount_with_extra_decimal_digit_is_invalid(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    bad = "Agents may SEND up to $100.000 per operation."
    svc.page = svc.page.replace(svc.response["send_quote"], bad)
    svc.response["send_quote"] = bad
    assert c.poll() == "UNRESOLVED"


def test_replay_version_zero_is_invalid(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    svc.page = svc.page.replace("POLICY_VERSION: 1", "POLICY_VERSION: 0")
    assert c.poll() == "UNRESOLVED"


def test_widening_source_version_and_hash_are_both_pinned(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    c.poll()
    set_doc(send=200, version=2)
    assert c.poll() == "WIDENING_PENDING"
    assert json.loads(c.status())["pending_policy_version"] == 2
    set_doc(send=200, version=3)  # same caps but a new edition
    with pytest.raises(ValueError, match="source changed"):
        c.approve_widening()
    assert not c.can_execute(Address(AGENT), "SEND", 15000)


def test_more_exact_amount_quote_rejected(ctx):
    c, svc, actor, set_doc = ctx
    set_doc()
    svc.response["send_cents"] = 10001
    assert c.poll() == "UNRESOLVED"


def test_invalid_constructor_url_is_rejected(ctx):
    c, svc, actor, set_doc = ctx
    module = sys.modules['drail_test_module']
    for url in ('https://', 'http://policy.example.org/current',
                'https://policy.example.org/current?x=1',
                'https://user@policy.example.org/current'):
        with pytest.raises(ValueError):
            module.Drail(url, Address(AGENT), Address(WATCHER))


def test_consumer_rejects_invalid_guard_and_invalid_inputs(ctx):
    c, svc, actor, set_doc = ctx
    from importlib.util import spec_from_file_location, module_from_spec
    path = pathlib.Path(__file__).resolve().parents[1] / 'contracts' / 'consumer_fixture.py'
    spec = spec_from_file_location('drail_consumer_test_module', path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    zero = Address('0x' + '0'*40)
    with pytest.raises(ValueError, match='guard must be'):
        module.DrailConsumerFixture(zero)
    fixture = module.DrailConsumerFixture(Address(WATCHER))
    for a, amount in [('BOGUS', 1), ('SEND', 0), ('SEND', True), ('SEND', -3)]:
        with pytest.raises(ValueError):
            fixture.execute(a, amount)
    assert fixture.count() == 0


def test_consumer_uses_real_guard_result_and_agent_binding(ctx):
    c, svc, actor, set_doc = ctx
    import importlib.util
    path = pathlib.Path(__file__).resolve().parents[1] / 'contracts' / 'consumer_fixture.py'
    spec = importlib.util.spec_from_file_location('drail_consumer_test_module2', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    genlayer_mod = sys.modules['genlayer']
    class Proxy:
        def view(self):
            return c
    genlayer_mod.gl.get_contract_at = lambda addr: Proxy()
    consumer = module.DrailConsumerFixture(Address(WATCHER))
    set_doc()
    c.poll()
    actor(AGENT)
    assert consumer.execute('SEND', 9000) is True
    assert consumer.count() == 1
    with pytest.raises(ValueError, match='permission denied'):
        consumer.execute('BRIDGE', 1)
    assert consumer.count() == 1
    actor(STRANGER)
    with pytest.raises(ValueError, match='permission denied'):
        consumer.execute('SEND', 1)
    assert consumer.count() == 1
