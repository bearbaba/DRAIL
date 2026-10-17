"""Official GenLayer direct-mode checks; run via `pytest tests/test_direct_genvm.py`.

Unlike test_local_contract.py, this uses the real genlayer-test DirectVM.
The network/validator consensus path still needs separate Studionet tests.
"""
import json
import pytest


@pytest.fixture
def guard(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.check_pickling = True
    return direct_deploy(
        "contracts/drail.py",
        "https://policy.example.org/current",
        direct_alice,
        direct_bob,
    )


def test_real_sdk_constructor_is_locked(guard, direct_alice):
    state = json.loads(guard.status())
    assert state["initialized"] is False
    assert state["health"] == "UNRESOLVED"
    assert state["last_policy_version"] == 0
    assert guard.can_execute(direct_alice, "SEND", 1) is False


def test_real_sdk_rejects_bad_actions(guard, direct_alice):
    for action, amount in (("SEND", 0), ("SEND", -10), ("BRIDGE", True),
                           ("UNKNOWN", 1), ("SWAP", 10**13)):
        assert guard.can_execute(direct_alice, action, amount) is False


def test_real_sdk_rejects_non_owner_update(guard, direct_vm, direct_alice, direct_bob):
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("owner only"):
            guard.change_monitor(direct_bob)


def test_real_sdk_studio_integer_address_constructor(direct_deploy):
    agent_int = int('0x3333333333333333333333333333333333333333', 16)
    monitor_int = int('0x0000000000000000000000000000000000001234', 16)
    guard = direct_deploy('contracts/drail.py', 'https://policy.example.org/current',
                          agent_int, monitor_int)
    state = json.loads(guard.status())
    assert state['agent'].lower() == '0x3333333333333333333333333333333333333333'
    assert state['monitor'].lower() == '0x0000000000000000000000000000000000001234'
    assert guard.can_execute(agent_int, 'SEND', 1) is False
