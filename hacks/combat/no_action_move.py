import struct
import typing

import imgui

import nylib.utils.win32.memory as ny_mem

if typing.TYPE_CHECKING:
    from . import Combat


class NoActionMove:
    def __init__(self, combat: 'Combat', default_val):
        mem = combat.main.main.mem
        self.handle = mem.handle
        self.p_code = mem.scanner.find_address("48 89 5C 24 ? 48 89 74 24 ? 57 48 83 EC ? 48 8B F1 0F 29 74 24 ? 48 8B 89 ? ? ? ? 0F 28 F3")
        self.state = default_val

    @property
    def state(self):
        return ny_mem.read_ubyte(self.handle, self.p_code) == 0xc3

    @state.setter
    def state(self, value):
        ny_mem.write_ubyte(self.handle, self.p_code, 0xc3 if value else 0x48)

    def render_edit(self):
        changed, new_val = imgui.checkbox("无突进", self.state)
        if changed: self.state = new_val
        return changed, new_val
