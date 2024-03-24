import typing
import imgui
from ff_draw.gui.text import TextPosition
from ff_draw.plugins import FFDrawPlugin
import nylib.utils.win32.memory as ny_mem
import pathlib
from fpt4.utils.sqpack import SqPack
from ff_draw.main import FFDraw

if typing.TYPE_CHECKING:
    from . import Hacks
from ..Vars import vars


sq_pack = SqPack.get()


if typing.TYPE_CHECKING:
    from . import Hacks

def make_shell(key='#__hacks_hooks__/move'):
    f = pathlib.Path(__file__).parent / 'shell.py'
    
    return f.read_text('utf-8') + f'''
def _install():
    if hasattr(inject_server, {key!r}):
        # return ctypes.addressof(getattr(inject_server, {key!r}).cfg)
        getattr(inject_server, {key!r}).uninstall()
        delattr(inject_server, {key!r})
    hook = MoveHook(args[0])
    setattr(inject_server, {key!r}, hook)
    return ctypes.addressof(hook.cfg)
__file__ = {str(f)!r}\n
res = _install()
''', str(f)




class Speed:
    key = '__hacks_hook__speed__'
    # shell param = key, address1, address2
    shell = '''
def install_speed_hook():
    import ctypes
    if hasattr(inject_server, key):
        hook1, hook2 = getattr(inject_server, key)
        return ctypes.addressof(getattr(hook1, 'accel')), ctypes.addressof(getattr(hook1, 'speed'))
    from nylib.hook import create_hook
    accel = ctypes.c_ubyte(0)
    speed = ctypes.c_float(1)

    def on_update_speed(h, a):
        current_speed = ctypes.c_float.from_address(a + 0x44)
        if accel.value:
            current_speed.value = 1e10
        res = h.original(a)
        if speed.value != 1:
            current_speed.value *= speed.value
        return res

    def on_get_fly_speed(h, a):
        return h.original(a) * speed.value

    hook1 = create_hook(
        address1, ctypes.c_void_p, [ctypes.c_size_t]
    )(on_update_speed).install_and_enable()

    hook2 = create_hook(
        address2, ctypes.c_float, [ctypes.c_size_t]
    )(on_get_fly_speed).install_and_enable()

    setattr(hook1, 'accel', accel)
    setattr(hook1, 'speed', speed)
    setattr(inject_server, key, (hook1, hook2))
    return ctypes.addressof(accel), ctypes.addressof(speed)
res = install_speed_hook()
'''

    def __init__(self, main: 'Hacks'):
        self.main = main
        self.mem = main.main.mem
        self.handle = self.mem.handle
        self.hook_addr_1 = self.mem.scanner.find_address("40 53 48 83 EC ? 80 79 ? ? 48 8B D9 0F 84 ? ? ? ? 48 89 7C 24 ?")
        self.hook_addr_2 = self.mem.scanner.find_address("40 ? 48 83 EC ? 48 8B ? 48 8B ? FF 90 ? ? ? ? 48 85 ? 75")
        self.hook_addr_3 = self.mem.scanner.find_address("40 ? 48 83 EC ? 48 8B ? 48 8B ? FF 90 ? ? ? ? 48 85 ? 75")
        self.max_accel_addr, self.speed_addr = self.mem.inject_handle.run(f'key = {repr(self.key)}; address1 = {hex(self.hook_addr_1)};address2 = {hex(self.hook_addr_2)};\n' + self.shell)
        self.main.main.command.on_command['SirenPVPSpeed'].append(self.cmd_speed) 
        self.preset_data = main.data.setdefault('combat/speed', {})
        if 'max_accel' in self.preset_data:
            self.max_accel = self.preset_data['max_accel']
        else:
            self.preset_data['max_accel'] = self.max_accel
            self.main.storage.save()

        if 'speed' in self.preset_data:
            self.speed = self.preset_data['speed']
        else:
            self.preset_data['speed'] = self.speed
            self.main.storage.save()
        self.speed = 1.00
    def cmd_speed(self, _, args):
        if len(args) < 1: return
        self.speed = float(args[0])
    @property
    def max_accel(self):
        return bool(ny_mem.read_ubyte(self.handle, self.max_accel_addr))

    @max_accel.setter
    def max_accel(self, value):
        ny_mem.write_ubyte(self.handle, self.max_accel_addr, int(value))
        self.preset_data['max_accel'] = value
        self.main.storage.save()

    @property
    def speed(self):
        return ny_mem.read_float(self.handle, self.speed_addr)

    @speed.setter
    def speed(self, value):
        ny_mem.write_float(self.handle, self.speed_addr, value)
        self.preset_data['speed'] = value
        self.main.storage.save()

    def draw_panel(self):
        changed, new_val = imgui.checkbox("Max Accel", self.max_accel)
        if changed: self.max_accel = new_val
        changed, new_val = imgui.slider_float("Speed", self.speed, 0, 3, "%.2f", .1)

        imgui.same_line()
        imgui.text(f"当前移速: {self.speed}")
        if imgui.button("重置（默认值1）"):
            self.speed = 1.00
        imgui.same_line()
        if imgui.button("1.05"):
            self.speed = 1.05
        imgui.same_line()
        if imgui.button("1.10"):
            self.speed = 1.10
        if changed: self.speed = new_val



class AfterImageAttack:
    shell='''
import ctypes
from nylib.hook import create_hook
from ctypes import c_int64, c_float, c_ubyte, c_uint,c_void_p,addressof
def create_knock_hook():
    if hasattr(inject_server, key):
        return addressof(getattr(getattr(inject_server, key), 'val'))
    val = c_float(0)
    def knock_hook(hook, a1):
        print(f"get_hooked_message {str(a1)} ")
        return a1#hook.original(a1)
    hook = create_hook(actorLBAdress1, ctypes.c_uint64, [ctypes.c_int64])(knock_hook).install_and_enable()
    setattr(hook, 'val', val)
    setattr(inject_server, key, hook)
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
        self.LBKnock=False
        self.actorLBAdress1 = self.mem.scanner_v2.find_val("E8 * * * * C6 83 ?? ?? ?? ?? ?? EB ?? 0F 57 C9")
        self.actorKnockKey1='__hacks_hook__AIAKnock__'
        main.main.command.on_command['SirenPVPAIA'].append(self.cmd_AFK) 
        
    def cmd_AFK(self, _, args):
        if len(args) < 1: return
        if args[0] == "On":
            self.actorKnockHook1=self.mem.inject_handle.run(f'key=\'{self.actorKnockKey1}\'\nactorLBAdress1 = {self.actorLBAdress1[0]}\n' + self.shell)
            self.LBKnock = True                            
        if args[0] == "Off":
            self.mem.inject_handle.run(f'key =\'{self.actorKnockKey1}\'\n' + self.shell_uninstall_mini) 
            self.LBKnock = False


    def draw_panel(self):


        if imgui.button('LB可位移') :
            if not self.LBKnock:
                self.actorKnockHook1=self.mem.inject_handle.run(f'key=\'{self.actorKnockKey1}\'\nactorLBAdress1 = {self.actorLBAdress1[0]}\n' + self.shell)
            else:
                self.mem.inject_handle.run(f'key =\'{self.actorKnockKey1}\'\n' + self.shell_uninstall_mini)   
            self.LBKnock=not self.LBKnock
        imgui.same_line()
        imgui.text(f'LB可位移状态：{"开启" if self.LBKnock else "关闭"}') 



class NoActionMove:
    def __init__(self, main: 'Hacks'):
        self.main = main
        self.mem = main.main.mem
        self.handle = self.mem.handle
        self.actionMove = False
        self.write_1 = self.mem.scanner.find_address("48 89 5C 24 ? 48 89 74 24 ? 57 48 83 EC ? 48 8B F1 0F 29 74 24 ? 48 8B 89 ? ? ? ? 0F 28 F3")
        #self.preset_data = main.main.mem.mem.data.setdefault('NoActionMove', {})
        self.actionNoMoveAdress = self.mem.scanner.find_address("48 89 5C 24 ? 48 89 74 24 ? 57 48 83 EC ? 48 8B F1 0F 29 74 24 ? 48 8B 89 ? ? ? ? 0F 28 F3")
        self.actionNoMoveRaw=self.mem.scanner.get_original_text(self.actionNoMoveAdress, 1)[0]
        self.original_value = ny_mem.read_ubyte(self.handle, self.write_1)  
        main.main.command.on_command['SirenPVPNoActionMove'].append(self.cmd_NAM) 
        #if 'enabled' in self.preset_data:
        #    self.is_enabled = self.preset_data['enabled']
        #else:
        #    self.preset_data['enabled'] = self.is_enabled
       # #

        #self.main.logger.debug(f'NoActionMove/write_1: {self.write_1:X}')


    def cmd_NAM(self, _, args):
        if len(args) < 1: return
        if args[0] == "On":
            ny_mem.write_ubyte(self.handle, self.write_1, 0xc3)
            self.actionMove = True                            
        if args[0] == "Off":
            ny_mem.write_ubyte(self.handle, self.write_1, self.actionNoMoveRaw)
            self.actionMove = False       

    def draw_panel(self):

            
            
        if imgui.button('无视突进') :
            if not self.actionMove:
                ny_mem.write_ubyte(self.handle, self.write_1, 0xc3)
                #self.actorKnockHook=self.mem.inject_handle.run(f'key=\'{self.actorKnockKey}\'\nactorKnockAdress = {self.actorKnockAdress}\n' + self.shell)
            else:
                ny_mem.write_ubyte(self.handle, self.write_1, self.actionNoMoveRaw)
                #self.mem.inject_handle.run(f'key =\'{self.actorKnockKey}\'\n' + shell_uninstall)   
            self.actionMove=not self.actionMove
        imgui.same_line()
        imgui.text(f'无视突进状态：{"开启" if self.actionMove else "关闭"}') 