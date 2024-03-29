import struct
import typing

import imgui

import nylib.utils.win32.memory as ny_mem

if typing.TYPE_CHECKING:
    from . import Combat


class MoveForbiddenClip:
    def __init__(self, combat: 'Combat', default_val):
        self.main = combat
        mem = combat.main.main.mem
        self.handle = mem.handle
        self.p_code, = mem.scanner.find_point("E8 * * * * C6 83 ? ? ? ? ? EB ? 0F 57 C9")
        self.original_code = mem.scanner.get_original_text(self.p_code, 1)[0]
        self.state = default_val

    @property
    def state(self):
        return ny_mem.read_ubyte(self.handle, self.p_code) == 0xc3

    @state.setter
    def state(self, value):
        ny_mem.write_ubyte(self.handle, self.p_code, 0xc3 if value else self.original_code)

    def render_edit(self):
        changed, new_val = imgui.checkbox("move forbidden clip", self.state)
        if changed: self.state = new_val
        return changed, new_val
