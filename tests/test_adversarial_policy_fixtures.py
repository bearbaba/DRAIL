"""Static checks for isolated Studionet adversarial policy snapshots.

These validate fixture data and prevent accidental edits, not live GenLayer
consensus or on-chain security. The lab must still be exercised on Studionet.
"""
from pathlib import Path
import hashlib
import re

BASE = Path(__file__).resolve().parents[1] / "examples" / "adversarial"
SNAP = BASE / "snapshots"
AGENT = "0x4c7cb73ac8f8999af21cfc9ff4cf2333a9508dcb"


def read(name: str) -> str:
    return (SNAP / name).read_text(encoding="utf-8")


def test_initial_current_policy_identical_to_v1_baseline():
    baseline = read("01_baseline_v1.txt")
    current = (BASE / "current_policy.txt").read_text(encoding="utf-8")
    assert current == baseline
    assert "POLICY_VERSION: 1" in current


def test_positive_snapshots_are_bound_to_correct_agent_and_chain():
    candidates = [
        ("01_baseline_v1.txt", 1, 10000, 25000, 0),
        ("02_same_version_mutation_v1.txt", 1, 9000, 25000, 0),
        ("03_tightened_v2.txt", 2, 5000, 15000, 0),
        ("04_rollback_v1.txt", 1, 10000, 25000, 0),
        ("09_widening_v3.txt", 3, 20000, 35000, 2500),
        ("10_stale_widening_v3.txt", 3, 20000, 34000, 2500),
    ]
    for name, version, send, swap, bridge in candidates:
        document = read(name)
        lines = document.splitlines()
        assert lines[:7] == [
            "DRAIL_POLICY_V1",
            f"POLICY_VERSION: {version}",
            f"AGENT: {AGENT}",
            "CHAIN_ID: 61999",
            "CURRENCY: USD",
            "STATUS: EFFECTIVE",
            "",
        ]
        assert len(document.encode("utf-8")) <= 8192
        for action, cap in [("SEND", send), ("SWAP", swap), ("BRIDGE", bridge)]:
            expected = f"Agents may {action} up to \${cap/100:.2f} per operation."
            if cap == 0:
                assert f"{action} is prohibited." in document
            else:
                assert expected.replace("\\$", "$") in document


def test_adversarial_snapshot_differences_are_intentional():
    v1 = read("01_baseline_v1.txt")
    v1edit = read("02_same_version_mutation_v1.txt")
    assert "POLICY_VERSION: 1" in v1edit
    assert hashlib.sha256(v1.encode()).digest() != hashlib.sha256(v1edit.encode()).digest()
    assert read("04_rollback_v1.txt") == v1
    v3 = read("09_widening_v3.txt")
    v3edit = read("10_stale_widening_v3.txt")
    assert "POLICY_VERSION: 3" in v3edit
    assert "SWAP up to $340.00" in v3edit
    assert hashlib.sha256(v3.encode()).digest() != hashlib.sha256(v3edit.encode()).digest()


def test_invalid_fixtures_target_distinct_envelope_failures():
    bad_agent = read("05_wrong_agent_v2.txt")
    assert f"AGENT: {AGENT}" not in bad_agent
    assert "CHAIN_ID: 61999" in bad_agent
    wrong_chain = read("06_wrong_chain_v2.txt")
    assert "CHAIN_ID: 1" in wrong_chain
    assert f"AGENT: {AGENT}" in wrong_chain
    duplicate = read("07_duplicate_send_v2.txt")
    assert len(re.findall(r"\\bSEND\\b", duplicate.split("STATUS: EFFECTIVE", 1)[1], re.I)) == 2
    oversize = read("08_oversized_v2.txt")
    assert len(oversize.encode("utf-8")) > 8192
