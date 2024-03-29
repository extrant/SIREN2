import struct
import typing

import imgui

import nylib.utils.win32.memory as ny_mem

if typing.TYPE_CHECKING:
    from . import Combat


class AniLock:
    def __init__(self, combat: 'Combat', default_val=-1):
        self.main = combat
        mem = combat.main.main.mem
        self.handle = mem.handle

        p_code = mem.scanner.find_address("41 C7 45 08 ? ? ? ? EB ? 41 C7 45 08")
        self.normal_lock_addr, self.seal_lock_addr = (
            p_code + 4, p_code + 14
        ) if struct.unpack('f', mem.scanner.get_original_text(p_code + 4, 4))[0] == .5 else (
            p_code + 14, p_code + 4
        )
        self.sync_normal_addr = mem.scanner.find_address("41 f6 44 24 ? ? 74 ? f3") + 0xf

        self.original_seal_val, = struct.unpack('f', mem.scanner.get_original_text(self.seal_lock_addr, 4))
        self.original_normal_val, = struct.unpack('f', mem.scanner.get_original_text(self.normal_lock_addr, 4))
        self.sync_normal_original = mem.scanner.get_original_text(self.sync_normal_addr, 8)
        self.state = default_val

    @property
    def state(self):
        if ny_mem.read_ubyte(self.handle, self.sync_normal_addr) == 0x90:
            return ny_mem.read_float(self.handle, self.normal_lock_addr)
        return -1

    @state.setter
    def state(self, value):
        if value == -1:
            ny_mem.write_float(self.handle, self.normal_lock_addr, self.original_normal_val)
            ny_mem.write_float(self.handle, self.seal_lock_addr, self.original_seal_val)
        else:
            ny_mem.write_float(self.handle, self.normal_lock_addr, min(value, self.original_normal_val))
            ny_mem.write_float(self.handle, self.seal_lock_addr, min(value, self.original_seal_val))
        ny_mem.write_bytes(self.handle, self.sync_normal_addr, (b'\x90' * 8) if value != -1 else self.sync_normal_original)

    def render_edit(self):
        state = self.state
        any_change = False
        changed, _ = imgui.checkbox("##anilock enabled", state >= 0)
        if changed:
            self.state = -1 if state >= 0 else .5
            any_change = True

        if state >= 0:
            imgui.same_line()
            changed, state = imgui.slider_float("##anilock val", state, 0, .5, "%.2f", .01)
            if changed:
                self.state = state
                any_change = True
        imgui.same_line()
        imgui.text("动画锁")
        return any_change, state
