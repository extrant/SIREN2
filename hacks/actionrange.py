import typing
import glm
import json
import glfw
import imgui
from ff_draw.gui.text import TextPosition
from ff_draw.plugins import FFDrawPlugin
import nylib.utils.win32.memory as ny_mem
#from pynput import keyboard

from ff_draw.main import FFDraw

if typing.TYPE_CHECKING:
    from . import Hacks
from ..Vars import vars


shell_uninstall = '''
def uninstall(key):
    if hasattr(inject_server, key):
        getattr(inject_server, key).uninstall()
        delattr(inject_server, key)
'''


class GetActionRange:
    key = '__hacks_hook__get_action_range__'
    # shell param = key, address
    shell = '''
def install_get_action_range_hook():
    import ctypes
    if hasattr(inject_server, key):
        return ctypes.addressof(getattr(getattr(inject_server, key), 'val'))
    from nylib.hook import create_hook
    val = ctypes.c_float(0)
    hook = create_hook(
        address, ctypes.c_float, [ctypes.c_uint]
    )(
        lambda h, *a: (res := h.original(*a)) and max(res + val.value, 0)
    ).install_and_enable()
    setattr(hook, 'val', val)
    setattr(inject_server, key, hook)
    return ctypes.addressof(val)
res = install_get_action_range_hook()
'''

    def __init__(self, main: 'Hacks'):
        self.main = main
        self.mem = main.main.mem
        self.handle = self.mem.handle
        self.hook_addr, = self.mem.scanner.find_point("e8 * * * * f3 0f 11 43 ? 80 ? ?")
        self.val_addr = 0

        self.preset_data = main.data.setdefault('combat/get_action_range', {})
        if 'val' in self.preset_data:
            self.val = self.preset_data['val']
        else:
            self.preset_data['val'] = 0
            self.main.storage.save()

    @property
    def val(self):
        if self.val_addr:
            return ny_mem.read_float(self.handle, self.val_addr)
        return -1

    @val.setter
    def val(self, value):
        if value == -1:
            self.mem.inject_handle.run(f'key = {repr(self.key)};\n' + shell_uninstall)
            self.val_addr = 0
        else:
            if not self.val_addr:
                self.val_addr = self.mem.inject_handle.run(f'key = {repr(self.key)}; address = {hex(self.hook_addr)};\n' + self.shell)
            ny_mem.write_float(self.handle, self.val_addr, value)
        self.preset_data['val'] = value
        self.main.storage.save()

    def draw_panel(self):
        val = self.val
        vars.actionrange = self.val
        imgui.text("长臂猿")
        changed, new_val = imgui.checkbox("##Enabled", self.val != -1)
        if changed:
            self.val = 0 if val < 0 else -1
        if val != -1:
            #imgui.same_line()
            changed, new_val = imgui.slider_float("##Value", val, 0, 4, "%.2f", .1)
            if imgui.button("重置（默认值0）"):
                self.val = 0
            imgui.same_line()
            if imgui.button("1.0"):
                self.val = 1.0
            imgui.same_line()
            if imgui.button("1.5"):
                self.val = 1.5
            imgui.same_line()    
            if imgui.button("2"):
                self.val = 2.0               
            if changed: self.val = new_val                        
            if imgui.button("40"):
                self.val = 40.0               
            if changed: self.val = new_val