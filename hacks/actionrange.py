import typing
import glm
import json
import struct
import imgui
import pathlib
from ff_draw.gui.text import TextPosition
from ff_draw.plugins import FFDrawPlugin
import nylib.utils.win32.memory as ny_mem
#from pynput import keyboard
from nylib.utils import imgui as ny_imgui


from fpt4.utils.sqpack import SqPack
from ff_draw.main import FFDraw
import nylib.utils.imgui.ctx as imgui_ctx
from .utils import ShellInject, struct2dict, dict2struct, Patch, Hack
if typing.TYPE_CHECKING:
    from . import Hacks
from ..Vars import vars

def make_shell(key='#__hacks_hooks__/combat'):
    f = pathlib.Path(__file__).parent / 'hook_shell.py'
    return f.read_text('utf-8') + f'''
def _install():
    if hasattr(inject_server, {key!r}):
        # return ctypes.addressof(getattr(inject_server, {key!r}).cfg)
        getattr(inject_server, {key!r}).uninstall()
        delattr(inject_server, {key!r})
    hook = CombatHook(args[0])
    setattr(inject_server, {key!r}, hook)
    return ctypes.addressof(hook.cfg)
res = _install()
''', str(f)


action_sheet = SqPack.get().sheets.action_sheet


def make_action_timeline_names():
    mapping = {}
    for action in action_sheet:
        if (timeline := getattr(action.timeline, 'key', 0)) and (name := action[0]) and action.action_timeline_move != 0:
            mapping.setdefault(timeline, set()).add(name)
    return {k: '/'.join(sorted(v)) for k, v in mapping.items()}


action_timeline_names = make_action_timeline_names()




shell_uninstall = '''
def uninstall(key):
    if hasattr(inject_server, key):
        getattr(inject_server, key).uninstall()
        delattr(inject_server, key)
'''
class CurrentMinMax:
    def __init__(self, handle, address):
        self.handle = handle
        self.address = address

    current = property(
        lambda self: ny_mem.read_float(self.handle, self.address),
        lambda self, value: ny_mem.write_float(self.handle, self.address, value)
    )

    min = property(
        lambda self: ny_mem.read_float(self.handle, self.address + 4),
        lambda self, value: ny_mem.write_float(self.handle, self.address + 4, value)
    )

    max = property(
        lambda self: ny_mem.read_float(self.handle, self.address + 8),
        lambda self, value: ny_mem.write_float(self.handle, self.address + 8, value)
    )


class Cam:
    def __init__(self, main: 'Hacks'):
        self.main = main
        mem = main.main.mem
        self.handle = mem.handle
        self._cam_base, = mem.scanner.find_point("48 8D 0D * * * * E8 ? ? ? ? 48 83 3D ? ? ? ? ? 74 ? E8 ? ? ? ?")
        self._zoom_offset, = mem.scanner.find_val("F3 0F ? ? * * * * 48 8B ? ? ? ? ? 48 85 ? 74 ? F3 0F ? ? ? ? ? ? 48 83 C1")
        self._fov_offset, = mem.scanner.find_val("F3 0F ? ? * * * * 0F 2F ? ? ? ? ? 72 ? F3 0F ? ? ? ? ? ? 48 8B")
        self._angle_offset, = mem.scanner.find_val("F3 0F 10 B3 * * * * 48 8D ? ? ? F3 44 ? ? ? ? ? ? ? F3 44")
        self.preset_data = main.data.setdefault('cam_preset', {})
        if 'zoom' in self.preset_data:
            self.cam_zoom.min, self.cam_zoom.max = self.preset_data['zoom']['min'], self.preset_data['zoom']['max']
        else:
            self.preset_data['zoom'] = {'min': self.cam_zoom.min, 'max': self.cam_zoom.max}

        if 'fov' in self.preset_data:
            self.cam_fov.min, self.cam_fov.max = self.preset_data['fov']['min'], self.preset_data['fov']['max']
        else:
            self.preset_data['fov'] = {'min': self.cam_fov.min, 'max': self.cam_fov.max}

        if 'angle' in self.preset_data:
            self.cam_angle.min, self.cam_angle.max = self.preset_data['angle']['min'], self.preset_data['angle']['max']
        else:
            self.preset_data['angle'] = {'min': self.cam_angle.min, 'max': self.cam_angle.max}

        main.storage.save()
        self.main.logger.debug(f'cam/cam_base: {self._cam_base:X}')
        self.main.logger.debug(f'cam/zoom_offset: {self._zoom_offset:X}')
        self.main.logger.debug(f'cam/fov_offset: {self._fov_offset:X}')
        self.main.logger.debug(f'cam/angle_offset: {self._angle_offset:X}')

    @property
    def cam_zoom(self):
        return CurrentMinMax(self.handle, ny_mem.read_address(self.handle, self._cam_base) + self._zoom_offset)

    @property
    def cam_fov(self):
        return CurrentMinMax(self.handle, ny_mem.read_address(self.handle, self._cam_base) + self._fov_offset)

    @property
    def cam_angle(self):
        return CurrentMinMax(self.handle, ny_mem.read_address(self.handle, self._cam_base) + self._angle_offset)

    def draw_panel(self):
        imgui.columns(4)
        imgui.next_column()
        imgui.text("Current")
        imgui.next_column()
        imgui.text("Min")
        imgui.next_column()
        imgui.text("Max")
        imgui.next_column()
        imgui.separator()

        zoom = self.cam_zoom
        imgui.text("Zoom")
        imgui.next_column()
        changed, new_zoom_current = imgui.drag_float("##zoom_current", zoom.current, 0.1, zoom.min, zoom.max, "%.1f")
        if changed: zoom.current = new_zoom_current
        imgui.next_column()
        changed, new_zoom_min = imgui.input_float('##zoom_min', zoom.min, .5, 5, "%.1f")
        if changed:
            zoom.min = new_zoom_min
            self.preset_data['zoom']['min'] = new_zoom_min
            self.main.storage.save()
        imgui.next_column()
        changed, new_zoom_max = imgui.input_float('##zoom_max', zoom.max, .5, 5, "%.1f")
        if changed:
            zoom.max = new_zoom_max
            self.preset_data['zoom']['max'] = new_zoom_max
            self.main.storage.save()
        imgui.next_column()


        imgui.columns(1)



        


class NoActionMove:
    def __init__(self, combat: 'Hacks'):
        mem = combat.main.mem
        self.handle = mem.handle
        self.p_code = mem.scanner.find_address("48 89 5C 24 ? 48 89 74 24 ? 57 48 83 EC ? 48 8B F1 0F 29 74 24 ? 48 8B 89 ? ? ? ? 0F 28 F3")
        self.state = False#default_val

    @property
    def state(self):
        return ny_mem.read_ubyte(self.handle, self.p_code) == 0xc3

    @state.setter
    def state(self, value):
        ny_mem.write_ubyte(self.handle, self.p_code, 0xc3 if value else 0x48)

    def draw_panel(self):
        changed, new_val = imgui.checkbox("无突进", self.state)
        if changed: self.state = new_val
        return changed, new_val
    

class AniLock:
    def __init__(self, main: 'Hacks'):
        self.main = main
        mem = main.main.mem
        self.handle = mem.handle
        self.local_lock = mem.scanner.find_address("41 C7 45 08 ? ? ? ? EB ? 41 C7 45 08")
        if struct.unpack('f', mem.scanner.get_original_text(self.local_lock + 4, 4)) == .5:
            self.normal_lock_addr = self.local_lock + 4
            self.seal_lock_addr = self.local_lock + 14
        else:
            self.normal_lock_addr = self.local_lock + 14
            self.seal_lock_addr = self.local_lock + 4
        self.original_seal_val, = struct.unpack('f', mem.scanner.get_original_text(self.seal_lock_addr, 4))
        self.original_normal_val, = struct.unpack('f', mem.scanner.get_original_text(self.normal_lock_addr, 4))

        self.main.logger.debug(f'ani_lock/local_lock: {self.normal_lock_addr:X} (original: {self.original_normal_val:.2f})')
        self.main.logger.debug(f'ani_lock/seal_lock: {self.seal_lock_addr:X} (original: {self.original_seal_val:.2f})')

        self.sync_normal_addr = mem.scanner.find_address("41 f6 44 24 ? ? 74 ? f3") + 0xf
        self.sync_normal_original = mem.scanner.get_original_text(self.sync_normal_addr, 8)
        self.main.logger.debug(f'ani_lock/sync_normal: {self.sync_normal_addr:X}')

        # sync seal not impl

        self.preset_data = main.data.setdefault('anilock', {})
        if 'state' in self.preset_data:
            self.state = self.preset_data['state']
        else:
            self.preset_data['state'] = self.state

    def set_local(self, val):
        if val == -1:
            ny_mem.write_float(self.handle, self.normal_lock_addr, self.original_normal_val)
            ny_mem.write_float(self.handle, self.seal_lock_addr, self.original_seal_val)
        else:
            ny_mem.write_float(self.handle, self.normal_lock_addr, min(val, self.original_normal_val))
            ny_mem.write_float(self.handle, self.seal_lock_addr, min(val, self.original_seal_val))

    def set_sync(self, mode):
        if mode:
            ny_mem.write_bytes(self.handle, self.sync_normal_addr, b'\x90' * 8)
        else:
            ny_mem.write_bytes(self.handle, self.sync_normal_addr, self.sync_normal_original)

    @property
    def state(self):
        if ny_mem.read_ubyte(self.handle, self.sync_normal_addr) == 0x90:
            return ny_mem.read_float(self.handle, self.normal_lock_addr)
        return -1

    @state.setter
    def state(self, value):
        self.set_local(value)
        self.set_sync(value != -1)

    def draw_panel(self):
        state = self.state
        imgui.text("动画锁 建议0.2")
        changed, new_val = imgui.checkbox("##Enabled", state != -1)
        imgui.same_line()
        if changed:
            if state < 0:
                self.state = .2
            else:
                self.state = -1
        if state != -1:
            changed, new_val = imgui.slider_float("##Value", state, 0, .5, "%.2f", .01)
            if changed:
                self.state = new_val




class GetRadius:
    key = '__hacks_hook__get_radius__'
    # shell param = key, address
    shell = '''
def install_get_radius_hook():
    import ctypes
    if hasattr(inject_server, key):
        return ctypes.addressof(getattr(getattr(inject_server, key), 'val'))
    from nylib.hook import create_hook
    val = ctypes.c_float(0)
    hook = create_hook(
        address, ctypes.c_float, [ctypes.c_void_p, ctypes.c_ubyte]
    )(
        lambda h, *a: max(h.original(*a) + val.value, 0)
    ).install_and_enable()
    setattr(hook, 'val', val)
    setattr(inject_server, key, hook)
    return ctypes.addressof(val)
res = install_get_radius_hook()
'''

    def __init__(self, main: 'Hacks'):
        self.main = main
        self.mem = main.main.mem
        self.handle = self.mem.handle
        self.hook_addr, = self.mem.scanner.find_point("E8 * * * * F3 0F 58 F0 F3 0F 10 05 ? ? ? ?")
        self.val_addr = 0

        self.preset_data = main.data.setdefault('combat/get_radius', {})
        if 'val' in self.preset_data:
            self.val = self.preset_data['val']
        else:
            self.preset_data['val'] = -1
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
        changed, new_val = imgui.checkbox("##Enabled", self.val != -1)
        if changed:
            self.val = 0 if val < 0 else -1
        if val != -1:
            imgui.same_line()
            imgui.text("目标圈大小")
            changed, new_val = imgui.slider_float("##Value", self.val, 0, 4, "%.2f", .1)
            if imgui.button("重置（默认值0）"):
                self.val = 0
            imgui.same_line()
            if imgui.button("1.0"):
                self.val = 1.0
            imgui.same_line()
            if imgui.button("1.5"):
                self.val = 1.5
            if changed: self.val = new_val




class Recast:

    key = '__hacks_hook__recast__'
    shell='''
import ctypes
#from ..Vars import vars
from nylib.hook import create_hook
from ctypes import c_int64, c_float, c_ubyte, c_uint,c_void_p,addressof
def create_knock_hook():
    if hasattr(inject_server, key):
        return addressof(getattr(getattr(inject_server, key), 'val'))
    val = ctypes.c_float(0)
    def knock_hook(hook, type_, key, extra):
        res = hook.original(type_, key, extra)
        if res and type_ == 1:
            if key in (18805, 18806, 18807, 2259, 2261, 2263):
                return 0        
            return int(max(res - val.value * 1000, 0))
        return res
    def knock_hook2(hook, a1, type_, key, time_max):
        if time_max and type_ == 1:
            if key in (18805, 18806, 18807, 2259, 2261, 2263):
                time_max = 0
            else:
                time_max = max(time_max - val.value, 0)
        return hook.original(a1, type_, key, time_max)   
    hook = create_hook(address, ctypes.c_int, [ctypes.c_uint, ctypes.c_uint, ctypes.c_ubyte])(knock_hook).install_and_enable()
    hook2 = create_hook(address, ctypes.c_float, [ctypes.c_uint64, ctypes.c_uint, ctypes.c_uint, ctypes.c_float])(knock_hook2).install_and_enable()
    setattr(hook, 'val', val)
    setattr(hook2, 'val', val)
    setattr(inject_server, key, hook)
    setattr(inject_server, key, hook2)
    return addressof(val)
res=create_knock_hook()
'''

    shell_uninstall = '''
def uninstall(key):
    if hasattr(inject_server, key):
        getattr(inject_server, key).uninstall()
        delattr(inject_server, key)
uninstall(key)
'''
    shell_uninstall_multi = '''
def uninstall_multi(key):
    if hasattr(inject_server, key):
        for hook in getattr(inject_server, key):
            hook.uninstall()
        delattr(inject_server, key)
'''

    shell_uninstall_mini = '''
def uninstall(key):
    if hasattr(inject_server, key):
        getattr(inject_server, key).uninstall()
        delattr(inject_server, key)
uninstall(key)
'''
    def __init__(self, main: 'Hacks'):
        self.show_imgui_window = True
        self.main=main
        self.mem = main.main.mem 
        self.handle = self.mem.handle      
        self.LBKnock=False
        self.actorCastAdress1 = self.mem.scanner.find_point('e8 * * * * 8b ? 44 ? ? ? 49 ? ? e8 ? ? ? ? 45')[0]
        self.actorKnockKey1='__hacks_hook__Recast__'
        self.val_addr = 0      
        self.preset_data = main.data.setdefault('combat/recasttimereduce', {})
        self.val = -1
        if 'val' in self.preset_data:
            self.val = self.preset_data['val']
        else:
            self.preset_data['val'] = -1
            self.main.storage.save()

    @property
    def val(self):
        if self.val_addr:
            return ny_mem.read_float(self.handle, self.val_addr)
        return -1

    @val.setter
    def val(self, value):
        if value == -1:
            self.mem.inject_handle.run(f'key =\'{self.actorKnockKey1}\'\n' + self.shell_uninstall_mini) 
            self.val_addr = 0
        else:
            if not self.val_addr:
                self.val_addr = self.mem.inject_handle.run(f'key=\'{self.actorKnockKey1}\'\naddress = {self.actorCastAdress1}\n' + self.shell)
            ny_mem.write_float(self.handle, self.val_addr, value)
        self.preset_data['val'] = value
        self.main.storage.save()


    def draw_panel(self):
        val = self.val
        changed, new_val = imgui.checkbox("##Enabled", self.val != -1)
        if changed:
            self.val = 0 if val < 0 else -1
        if val != -1:
            imgui.same_line()
            imgui.text("复唱时间")
            changed, new_val = imgui.slider_float("##Value", self.val, 0, 1, "%.3f", .1)
            if changed: self.val = new_val




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




