# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""Minimal DRAIL consumer: actual cross-contract permission gate, no transfers.

Deploy after Drail. In the Drail constructor, `agent` must be the wallet
account that calls execute. Do NOT rely on an unfinalized Drail policy for
irreversible value transfers.
"""
from genlayer import *


class DrailConsumerFixture(gl.Contract):
    guard: Address
    executed: u256

    def __init__(self, guard: Address):
        self.guard = guard if isinstance(guard, Address) else Address(guard)
        self.executed = u256(0)

    @gl.public.write
    def execute(self, action: str, amount_cents: int) -> bool:
        contract = gl.get_contract_at(self.guard)
        allowed = contract.view().can_execute(
            gl.message.sender_address, action, amount_cents)
        if not allowed:
            raise gl.vm.UserError("DRAIL permission denied")
        self.executed = u256(int(self.executed) + 1)
        return True

    @gl.public.view
    def count(self) -> int:
        return int(self.executed)
