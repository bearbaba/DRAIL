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
    initial = json.loads(c.status().call())
    assert initial['health'] == 'UNRESOLVED'
    assert initial['initialized'] is False
    assert c.can_execute(args=[agent, 'SEND', 100]).call() is False

    # Only the deployer is allowed to initialize the initial policy.
    forbidden = c.connect(account=monitor).poll().transact()
    assert not tx_execution_succeeded(forbidden)
    assert json.loads(c.status().call())['initialized'] is False

    live = c.poll().transact()  # genuine multi-validator observation
    assert tx_execution_succeeded(live)
    result = json.loads(c.status().call())
    assert result['initialized'] is True
    assert result['health'] == 'OK'
    assert result['revision'] >= 1
    assert c.audit_count().call() >= 1
    assert result['last_policy_version'] >= 1
    assert result['agent'].lower() == agent.lower()
    for action in ('SEND', 'SWAP', 'BRIDGE'):
        cap = int(result[action.lower() + '_cents'])
        assert c.can_execute(args=[agent, action, 1]).call() == (cap >= 1)
