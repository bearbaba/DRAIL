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
        if isinstance(guard, Address):
            addr = guard
        elif type(guard) is int:
            if not 0 <= guard < (1 << 160):
                raise gl.vm.UserError("invalid guard address")
            addr = Address("0x" + format(guard, "040x"))
        elif isinstance(guard, str) and len(guard) == 42 and guard.startswith("0x"):
            addr = Address(guard)
        else:
            raise gl.vm.UserError("invalid guard address")
        if addr == Address("0x0000000000000000000000000000000000000000"):
            raise gl.vm.UserError("guard must be deployed and nonzero")
        self.guard = addr
        self.executed = u256(0)

    @gl.public.write
    def execute(self, action: str, amount_cents: int) -> bool:
        if not isinstance(action, str) or action.upper() not in ("SEND", "SWAP", "BRIDGE"):
            raise gl.vm.UserError("invalid action")
        if type(amount_cents) is not int or amount_cents <= 0 or amount_cents > 10 ** 12:
            raise gl.vm.UserError("invalid amount")
        contract = gl.get_contract_at(self.guard)
        allowed = contract.view().can_execute(
            gl.message.sender_address, action, amount_cents)
        if allowed is not True:
            raise gl.vm.UserError("DRAIL permission denied")
        self.executed = u256(int(self.executed) + 1)
        return True

    @gl.public.view
    def count(self) -> int:
        return int(self.executed)
