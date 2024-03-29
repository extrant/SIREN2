import struct
import typing

import imgui

import nylib.utils.win32.memory as ny_mem

if typing.TYPE_CHECKING:
    from . import Combat


class AutoQte:
    def __init__(self, combat: 'Combat', default_val):
        self.main = combat
        mem = combat.main.main.mem
        self.handle = mem.handle
        self.p_codes = mem.scanner.find_addresses("75 ? 48 ? ? 48 ? ? ? 48 ? ? ? ? ? ? 7c ? f6 82")
        assert len(self.p_codes) == 3, "auto qte pattern match failed"
        self.state = default_val

    @property
    def state(self):
        return ny_mem.read_ubyte(self.handle, self.p_codes[0]) == 0xeb

    @state.setter
    def state(self, value):
        for p_code in self.p_codes:
            ny_mem.write_ubyte(self.handle, p_code, 0xeb if value else 0x75)

    def render_edit(self):
        changed, new_val = imgui.checkbox("自动QTE", self.state)
        if changed: self.state = new_val
        return changed, new_val
