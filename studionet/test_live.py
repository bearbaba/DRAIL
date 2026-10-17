"""Optional actual Studionet integration — requires installed GenLayer SDK.

Set DRAIL_AUTHORITY_URL and DRAIL_AGENT_ADDRESS to values that MATCH the
published DRAIL_POLICY_V1 metadata, then run:
  gltest --network studionet studionet/test_live.py -v
No fake receipt/status claims are made in this file.
"""
import json
import os
import pytest
from gltest import create_account, get_contract_factory
from gltest.assertions import tx_execution_succeeded


@pytest.mark.skipif(not (os.getenv('DRAIL_AUTHORITY_URL') and
                         os.getenv('DRAIL_AGENT_ADDRESS')),
                    reason='Set DRAIL_AUTHORITY_URL and DRAIL_AGENT_ADDRESS')
def test_deploy_and_live_consensus():
    agent = os.environ['DRAIL_AGENT_ADDRESS']
    monitor = create_account()
    url = os.environ['DRAIL_AUTHORITY_URL']
    c = get_contract_factory('Drail').deploy(args=[url, agent, monitor.address])
    print(f'DRAIL_DEPLOYED_ADDRESS={c.address}', flush=True)
    initial = json.loads(c.status().call())
    assert initial['health'] == 'UNRESOLVED'
    assert initial['initialized'] is False
    assert c.can_execute(args=[agent, 'SEND', 100]).call() is False

    # Only the deployer is allowed to initialize the initial policy.
    forbidden = c.connect(account=monitor).poll().transact()
    assert not tx_execution_succeeded(forbidden)
    assert json.loads(c.status().call())['initialized'] is False

    live = c.poll().transact()  # genuine multi-validator observation
    print(f'DRAIL_POLL_RECEIPT={str(live)[:2000]}', flush=True)
    assert tx_execution_succeeded(live)
    result = json.loads(c.status().call())
    print(f'DRAIL_CONFIRMED_STATUS={json.dumps(result, sort_keys=True)}', flush=True)
    assert result['initialized'] is True
    assert result['health'] == 'OK'
    assert result['revision'] >= 1
    assert c.audit_count().call() >= 1
    assert result['last_policy_version'] >= 1
    assert result['last_verified_at'] > 0
    assert result['max_evidence_age_seconds'] == 3600
    assert result['evidence_fresh'] is True
    assert result['agent'].lower() == agent.lower()
    for action in ('SEND', 'SWAP', 'BRIDGE'):
        cap = int(result[action.lower() + '_cents'])
        assert c.can_execute(args=[agent, action, 1]).call() == (cap >= 1)


def test_studio_integer_constructor_compatibility():
    agent_int = int('0x3333333333333333333333333333333333333333', 16)
    monitor_int = int('0x0000000000000000000000000000000000001234', 16)
    url = os.environ.get('DRAIL_AUTHORITY_URL',
       'https://raw.githubusercontent.com/bearbaba/DRAIL/fix/security-hardening-v1/examples/policy_v1.txt')
    contract = get_contract_factory('Drail').deploy(args=[url, agent_int, monitor_int])
    state = json.loads(contract.status().call())
    assert state['agent'].lower() == '0x3333333333333333333333333333333333333333'
    assert state['monitor'].lower() == '0x0000000000000000000000000000000000001234'
    assert state['initialized'] is False
