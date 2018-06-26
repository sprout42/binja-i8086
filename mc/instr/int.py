from binaryninja.enums import BranchType

from ..helpers import *
from ..tables import *
from . import *


__all__ = ['Int3', 'IntImm']


class Int(Instruction):
    def name(self):
        return 'int'

    def analyze(self, info, addr):
        Instruction.analyze(self, info, addr)
        info.add_branch(BranchType.SystemCall, 4 * self.number)

    def render(self, addr):
        tokens = Instruction.render(self, addr)
        tokens += asm(
            ('int', fmt_dec(self.number), self.number)
        )
        return tokens

    def lift(self, il, addr):
        if self.number == 3:
            il.append(il.breakpoint())
        else:
            # This *is* a trap, but if we lift it as a trap, BN assumes that execution
            # will not continue afterwards. So, to aid analysis, we add an explicit call
            # to the vector.
            # Not quite semantically correct, but good enough and useful.
            # TODO: represent this as a system call
            cs_ip = il.load(4, il.const_pointer(2, self.number * 4))
            cs    = il.logical_shift_right(2, cs_ip, il.const(1, 16))
            ip    = il.low_part(2, cs_ip)
            il.append(il.call(self._lift_addr(il, cs, ip)))

class Int3(Int):
    number = 3


class IntImm(Int):
    def length(self):
        return 2

    def decode(self, decoder, addr):
        Int.decode(self, decoder, addr)
        self.number = decoder.unsigned_byte()

    def encode(self, encoder, addr):
        Int.encode(self, encoder, addr)
        encoder.unsigned_byte(self.number)
