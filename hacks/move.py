import typing
import imgui
import json
from pynput.keyboard import Controller, Key
from ff_draw.gui.text import TextPosition
from ff_draw.plugins import FFDrawPlugin
import nylib.utils.win32.memory as ny_mem
import pathlib
import glm
from fpt4.utils.sqpack import SqPack
from ff_draw.main import FFDraw
from .utils import ShellInject, struct2dict, dict2struct, Patch, Hack
from .shell import MoveHookConfig
if typing.TYPE_CHECKING:
    from . import Hacks
from ..Vars import vars
from nylib.utils.imgui import ctx as imgui_ctx
from ff_draw.main import FFDraw
import os
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
        changed, new_val = imgui.checkbox("最大加速度", self.max_accel)
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
        #print(f"get_hooked_message {str(a1)} ")
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




class NoFallDamage:
    def __init__(self, main: 'Hacks'):
        self.main = main
        self.mem = main.main.mem
        self.handle = self.mem.handle
        shell, script_file = make_shell()
        

        self.p_cfg = self.mem.inject_handle.run(shell, {
            'on_send_flag': self.mem.scanner_v2.find_val("e8 * * * * 48 ? ? c6 05 ? ? ? ? ? 48")[0],
            'on_send_normal_move': self.mem.scanner_v2.find_val("48 ? ? 45 ? ? 44 ? ? 41 ? ? ? e8 * * * *")[0],
            'on_send_combat_move': self.mem.scanner_v2.find_val("45 ? ? 44 ? ? 48 ? ? 41 ? ? ? e8 * * * * eb")[0],
        }, filename=script_file)

        self.data = self.main.data.setdefault('move', {})
        self.cfg = dict2struct(self.data.get('hook', {
            'speed_percent': 1,
        }), MoveHookConfig)
        self.safe_mode = False
    @property
    def cfg(self):
        return ny_mem.read_memory(self.handle, MoveHookConfig, self.p_cfg)

    @cfg.setter
    def cfg(self, value: MoveHookConfig):
        ny_mem.write_memory(self.handle, self.p_cfg, value)

    def draw_panel(self):
        cfg = self.cfg
        any_data_change = False
        any_hook_change = False

        if self.safe_mode is False:
            cfg.y_adjust = 0
            any_hook_change = True
            self.safe_mode = True
        change, new_val = imgui.checkbox('无视掉落伤害', cfg.no_fall_damage)
        if change:
            cfg.no_fall_damage = new_val
            any_hook_change = True



        y_adjust = cfg.y_adjust
        change, new_val = imgui.slider_float('y_adjust', cfg.y_adjust, -20, 20, '%.2f')
        if change:
            cfg.y_adjust = new_val
            any_hook_change = True

        if imgui.button("恢复成0"):
            cfg.y_adjust = 0
            any_hook_change = True
        imgui.same_line()
        if imgui.button("遁地-7"):
            cfg.y_adjust = -7
            any_hook_change = True
        imgui.same_line()
        if imgui.button("遁地-5"):
            cfg.y_adjust = -5  
            any_hook_change = True


        if any_hook_change:
            self.cfg = cfg
            self.data['hook'] = struct2dict(cfg)
            any_data_change = True
        if any_data_change:
            self.main.storage.save()
     
class MovePermission:
    def __init__(self, main: 'Hacks'):
        self.main = main
        self.mem = main.main.mem
        self.handle = self.mem.handle
        self.p_code, =self.mem.scanner_v2.find_val("e8 * * * * 84 ? 74 ? 48 c7 05")
        self.inject = ShellInject(self.p_code,)
        self.update_inject()
        self.state = False

    def update_inject(self):
        self.inject.disable()
        code = ''
        p_ids = list(range(96, 100)) + [int(0x3E9), int(0x3EE), int(0x3EF), int(0x3F0)]
        for p_id in p_ids:
            code += f'cmp edx, {p_id};je ret1;'
        code += 'jmp orig;ret1:mov al, 1;ret;orig:{taken};jmp {return_at:#X};'
        self.inject.shell_code = code
        self.inject.compile()

    def draw_panel(self):
        imgui.text("强制位移,会飞尸")
        changed, new_val = imgui.checkbox("强制位移", self.inject.state)
        if changed: self.inject.state = new_val
        return changed, new_val
    

class MoveStatus:
    def __init__(self, main: 'Hacks'):
        data  = {
            3023: False,
            3024: False,
        }
        self.main = main
        self.mem = main.main.mem
        self.inject = ShellInject(self.mem.scanner_v2.find_address("0f 84 ? ? ? ? 42 ? ? ? ? ? 45") + 12)
        self.data = {int(k): v for k, v in data.items()}
        self.update_inject()
        self.to_add_id = 0

    def update_inject(self):
        self.inject.disable()
        to_check = [k for k, v in self.data.items() if v]
        if not to_check: return
        code = ''
        for status_id in to_check:
            code += f'cmp ecx, {status_id};je clearEcx;'
        code += 'jmp orig;clearEcx:xor ecx, ecx;orig:{taken};jmp {return_at:#X};'
        self.inject.shell_code = code
        self.inject.compile()
        self.inject.enable()

    def draw_panel(self):
        any_change = False
        with imgui_ctx.ImguiId("MoveStatus"):
            for status_id, v in list(self.data.items()):
                changed, new_val = imgui.checkbox(f"##enable_{status_id}", v)
                if changed:
                    self.data[status_id] = new_val
                    any_change = True
                imgui.same_line()
                try:
                    imgui.text(f"{sq_pack.sheets.status_sheet[status_id][0]}#{status_id}")
                except KeyError:
                    imgui.text(f"Status#{status_id}")
                imgui.same_line()
                if imgui.button(f"X##remove_{status_id}"):
                    self.data.pop(status_id)
                    any_change = True
            _, self.to_add_id = imgui.input_int("##add_id", self.to_add_id)
            if self.to_add_id and self.to_add_id not in self.data:
                try:
                    btn_text = f"add {sq_pack.sheets.status_sheet[self.to_add_id][0]}"
                except KeyError:
                    pass
                else:
                    if imgui.button(btn_text):
                        self.data[self.to_add_id] = True
                        any_change = True
        if any_change:
            self.update_inject()
        return any_change, self.data    
    

shell_uninstall_mini = '''
def uninstall(key):
    if hasattr(inject_server, key):
        getattr(inject_server, key).uninstall()
        delattr(inject_server, key)
uninstall(key)
'''
class MiniHackUI:
    shell='''
from nylib.hook import create_hook
from ctypes import c_int64, c_float, c_ubyte, c_uint,c_void_p,addressof
def create_knock_hook():
    if hasattr(inject_server, key):
        return addressof(getattr(getattr(inject_server, key), 'val'))
    val = c_float(0)
    def knock_hook(hook, actor_ptr, angle, dis, knock_time, a5, a6):
        #print(f"get_hooked_message {str(actor_ptr)} ")
        return hook.original(actor_ptr, 0, 0, 0, a5, a6)
    hook = create_hook(actorKnockAdress, c_int64, [c_int64, c_float, c_float, c_int64, c_ubyte, c_uint])(knock_hook).install_and_enable()
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
    def __init__(self, main: 'Hacks'):
        self.show_imgui_window = True
        self.main = main
        self.mem = main.main.mem
        self.handle = self.mem.handle
        
        self.antiKnock=False
        self.actorKnockAdress = self.mem.scanner.find_address("48 8B C4 48 89 70 ? 57 48 81 EC ? ? ? ? 0F 29 70 ? 0F 28 C1")
        self.actorKnockKey='__hacks_hook__actorKnock__'
        main.main.command.on_command['SirenPVPAKA'].append(self.cmd_AFK) 
        
    def cmd_AFK(self, _, args):
        if len(args) < 1: return
        if args[0] == "On":
            self.actorKnockHook=self.mem.inject_handle.run(f'key=\'{self.actorKnockKey}\'\nactorKnockAdress = {self.actorKnockAdress}\n' + self.shell)
            self.antiKnock = True                            
        if args[0] == "Off":
            self.mem.inject_handle.run(f'key =\'{self.actorKnockKey}\'\n' + shell_uninstall_mini) 
            self.antiKnock = False


    def draw_panel(self):


        if imgui.button('防击退') :
            if not self.antiKnock:
                self.actorKnockHook=self.mem.inject_handle.run(f'key=\'{self.actorKnockKey}\'\nactorKnockAdress = {self.actorKnockAdress}\n' + self.shell)
            else:
                self.mem.inject_handle.run(f'key =\'{self.actorKnockKey}\'\n' + shell_uninstall_mini)   
            self.antiKnock=not self.antiKnock
        imgui.same_line()
        imgui.text(f'防击退状态：{"开启" if self.antiKnock else "关闭"}')  


tp_true = False
positions = []  
mapname = ""  
maps = []
clicked_coordinate = None
from pynput import keyboard
class MiniHackTP:


    


            
    shell='''
from nylib.hook import create_hook
from ctypes import c_int64, c_float, c_ubyte, c_uint,c_void_p,addressof
def create_knock_hook():
    if hasattr(inject_server, key):
        return addressof(getattr(getattr(inject_server, key), 'val'))
    val = c_float(0)
    def knock_hook(hook, actor_ptr, angle, dis, knock_time, a5, a6):
        #print(f"get_hooked_message {str(actor_ptr)} ")
        return hook.original(actor_ptr, 0, 0, 0, a5, a6)
    hook = create_hook(actorKnockAdress, c_int64, [c_int64, c_float, c_float, c_int64, c_ubyte, c_uint])(knock_hook).install_and_enable()
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

    def __init__(self, main):
        #super().__init__(main)
        #self.print_name = self.data.setdefault('print_name', True)
        self.show_imgui_window = True
        self.main= main
        self.mem = main.main.mem  #combat.mem
        self.me= self.main.mem.mem.actor_table.me        
        self.territory = ''
        self.collapsed_states = {}
        main.main.command.on_command['SirenPVPTP'].append(self.cmd_tp)         
        main.main.command.on_command['SirenPVPTPMo'].append(self.cmd_tp2)
        self.tp=False
        self.tid = -1
        self.me_pos_temp = None
        self.coordinates_data = {}
        self.selected_map_id_index = 0  # Initialize with an integer
        self.selected_coordinate_index = 0  # Initialize the coordinate index
        self.wait_to_teleport = False
        self.vfall = False
        self.vfall_enable = False
        self.temp_note = ""
        file_path = r'.\\plugins\\SIREN2\\warp_list.json'
        
        # 检查文件是否存在，如果不存在，则初始化坐标数据为一个空字典
        if not os.path.exists(file_path):
            self.coordinates_data = {}   
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.coordinates_data, file, indent=2)                 
    def load_coordinates(self):
        with open(r'.\\plugins\\SIREN2\\warp_list.json', 'r', encoding='utf-8') as file:
            self.coordinates_data = json.load(file)

    def delete_coordinate(self, map_id, coordinate_index):
        """从 JSON 数据中删除指定的坐标条目"""
        if map_id in self.coordinates_data and 0 <= coordinate_index < len(self.coordinates_data[map_id]):
            # 删除指定索引的坐标
            del self.coordinates_data[map_id][coordinate_index]
            # 如果此地图ID下没有更多坐标，可选择删除整个键
            if not self.coordinates_data[map_id]:
                del self.coordinates_data[map_id]
            # 保存更新后的数据
            file_path = r'.\\plugins\\SIREN2\\warp_list.json'
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.coordinates_data, file, indent=2)
            print(f"坐标已从地图 {map_id} 删除")
        else:
            print("未找到指定的地图 ID 或坐标索引超出范围")

    def save_coordinates(self, map_id, coordinates, note):
        
        """向现有 JSON 数据中追加新的坐标和注释，并保存。如果文件不存在，则创建一个新文件。"""
        # 定义文件路径
        file_path = r'.\\plugins\\SIREN2\\warp_list.json'
        if not os.path.exists(file_path):
            self.coordinates_data = {}
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.coordinates_data, file, indent=2)
        else:
            # 如果文件存在，从文件加载坐标数据
            self.load_coordinates()
        
        # 如果 map_id 存在，则追加数据；如果不存在，则创建新项
        if map_id in self.coordinates_data:
            self.coordinates_data[map_id].append({"coordinates": coordinates, "note": note})
        else:
            self.coordinates_data[map_id] = [{"coordinates": coordinates, "note": note}]

        # 将更新后的数据写回 JSON 文件
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(self.coordinates_data, file, indent=2)

        print(f"已保存新坐标到地图 {map_id}: {coordinates}, {note}")

    def cmd_tp(self, _, args):
        if len(args) < 1: return
        coordinates = args[0]  
        coordinate_list = coordinates.split(",")  # 使用逗号分割字符串
        if len(coordinate_list) != 3:
            print("输入格式错误，请使用 '111,111,111' 的格式输入坐标。")
            return

        try:
            x = float(coordinate_list[0])
            z = float(coordinate_list[1])
            y = float(coordinate_list[2])
        except ValueError:
            print("输入格式错误，请使用数字表示坐标。")
            return

        ooPos = glm.vec3(x, z, y)  # 将坐标转换为浮点数，并传递给 glm.vec3 函数

     
        self.testPos(ooPos)
    def cmd_tp2(self, _, args):
        if len(args) < 1: return
        if not (pos := self.mem.ray_cast.cursor_to_world()):
            return self.logger.warning('cursor_to_world failed')
        print(pos)     
        self.testPos(pos)


    def draw_panel(self):
        #if not self.show_imgui_window: return
        
                        
        if imgui.button('tp开关') :
            self.tp=not self.tp

        imgui.same_line()
        imgui.text(f'TP开关状态：{"开启" if self.tp else "关闭"}')      
        
        imgui.same_line()
        if imgui.button('Load Position'):
            self.load_coordinates()
        imgui.same_line()
        if imgui.button('糖豆人'):
            self.vfall_enable = not self.vfall_enable
        tid = self.mem.territory_info.territory_id
        imgui.text(str(tid))
        if tid != self.tid:
            self.tid = tid
            try:
                territory = self.mem.main.sq_pack.sheets.territory_type_sheet[tid]
            except KeyError:
                territory = 'N/A'
            else:
                self.territory = f'{territory.region.text_sgl}-{territory.sub_region.text_sgl}-{territory.area.text_sgl}'   
        imgui.same_line()
        imgui.text(str(self.territory))
        if tid in [1165, 1197]:
            self.tp = False
        if tid not in [1165, 1197]:
            if self.coordinates_data:
                #map_ids = list(self.coordinates_data.keys())
                map_ids = list(self.coordinates_data.keys())
                # 构建包含地图 ID 和地理区域信息的列表
                map_id_with_territory = []
                for map_id in map_ids:
                    try:
                        territory = self.mem.main.sq_pack.sheets.territory_type_sheet[int(map_id)]
                        territory_description = f'{territory.region.text_sgl}-{territory.sub_region.text_sgl}-{territory.area.text_sgl}'
                    except KeyError:
                        territory_description = 'N/A'
                    map_id_with_territory.append(f"{map_id} - {territory_description}")            
                #clicked, selected_map_id_index = imgui.combo("地图ID", self.selected_map_id_index, map_ids)
                clicked, selected_map_id_index = imgui.combo("地图ID", self.selected_map_id_index, map_id_with_territory)
                if clicked:
                    self.selected_map_id_index = selected_map_id_index

                if self.selected_map_id_index is not None:
                    selected_map_id = map_ids[self.selected_map_id_index]
                    coordinates = self.coordinates_data[selected_map_id]
                    coordinate_items = [f"{coord['coordinates']} - {coord['note']}" for coord in coordinates]
                    clicked, selected_coordinate_index = imgui.combo("选择TP节点", self.selected_coordinate_index, coordinate_items)
                    
                    if clicked:
                        self.selected_coordinate_index = selected_coordinate_index

                    if imgui.button("跨界传送"):
                        self.me_pos_temp = self.me.pos
                        self.wait_to_teleport = True
                        self.mem.do_text_command(f'/#SirenPVPSpeed 0')
                        self.mem.do_text_command(f'/e 移速已为0 <se.11><se.11><se.11><se.11>')
                        coord = coordinates[self.selected_coordinate_index]['coordinates']
                        self.mem.do_text_command(f'/e 你的TP位置{coord}')
                        self.mem.do_text_command(f'/e 跨界传送TP移速被锁为0后请进行对应地图区域传送。') 
                        self.mem.do_text_command(f'/e 只要是会被服务器移动的都可以使用这个TP(死亡复活)') 

                    if self.wait_to_teleport is True:
                        imgui.same_line()
                        if imgui.button("取消"):
                            self.me_pos_temp = self.me.pos
                            self.wait_to_teleport = False  
                            self.mem.do_text_command(f'/#SirenPVPSpeed 1')                

                        #self.teleport_to_coordinate(coord)
                        #print(coord)
                        if self.me.pos != self.me_pos_temp:
                            imgui.text(f'准备传送')
                            imgui.same_line()
                            imgui.text(f'{selected_map_id}==>{self.tid}')
                            coord = coordinates[self.selected_coordinate_index]['coordinates']
                            if str(selected_map_id) != str(self.tid):
                                self.mem.do_text_command(f'/e 地图id不符 <se.11><se.11><se.11><se.11>')
                                self.mem.do_text_command(f'/#SirenPVPSpeed 1')
                                self.mem.do_text_command(f'/e 移速已恢复 <se.6><se.6><se.6><se.6>')                            
                            else:
                                self.teleport_to_coordinate(coord)
                            #self.mem.do_text_command(f'/#SirenPVPSpeed 1')
                            #self.mem.do_text_command(f'/e 移速恢复')                        
                            self.wait_to_teleport = False
                    imgui.same_line()
            if imgui.button("保存新坐标"):
                self.save_coordinates(str(tid), f"{self.me.pos.x:.3f},{self.me.pos.y:.3f},{self.me.pos.z:.3f}", self.temp_note) 
            imgui.same_line()
            if imgui.button("删除选中坐标"):
                if self.selected_map_id_index is not None and self.selected_coordinate_index is not None:
                    selected_map_id = list(self.coordinates_data.keys())[self.selected_map_id_index]
                    self.delete_coordinate(selected_map_id, self.selected_coordinate_index)
                    imgui.same_line()
                    imgui.text("选中坐标已删除！")
                    # 删除坐标后重置选中的坐标索引
                    self.selected_coordinate_index = 0
                    self.load_coordinates()  # 重新加载坐标数据更新 GUI                    
            imgui.text("添加新坐标:")
            _, self.temp_note = imgui.input_text("注释:", str(self.temp_note), 100)   
        imgui.text(f'你自己最好知道你在干什么！') 
        if self.me is not None:
            for status_id, param, remain, source_id in self.me.status:
                if status_id == 3704:
                    imgui.text(str(param))
            imgui.text(f'{self.me.pos}！') 
        
        
    def addTeleportButton(self, coordinates):
        if imgui.button("传送"):
            ooPos = glm.vec3(coordinates)
            self.testPos(ooPos)
    def CommandTeleport(self, coordinates):
        ooPos = glm.vec3(coordinates)
        self.testPos(ooPos)
    def CommandTeleport2(self, coordinates):
        ooPos = coordinates
        self.testPos(ooPos)        
    def testPos(self, ooPos):
        #if self.vfall_enable is True:
        #self.keyboard.press(Key.space)
        #self.keyboard.release(Key.space)        
        if self.tp:
            ny_mem.write_bytes(self.me.handle, self.me.address + self.me.offsets.pos, ooPos.to_bytes())

            
    def writePos(self,toPos:glm.vec3)  :    
        if self.tp:    
            ny_mem.write_bytes(self.me.handle, self.me.address + self.me.offsets.pos, toPos.to_bytes())
    def moveoo(self,value=1):
        ooPos=glm.vec3(3.71959,-7,-1.17685 )  
        self.testPos(ooPos)       
    def movefly(self):
        ooPos= me.pos + glm.vec3(0, 1, 0)
        ny_mem.write_bytes(self.me.handle, self.me.address + self.me.offsets.pos, ooPos.to_bytes())
          
      
    def teleport_to_coordinate(self, coordinates):
        self.mem.do_text_command(f'/#SirenPVPSpeed 1')
        self.mem.do_text_command(f'/e TP成功，移速已恢复 <se.4><se.4><se.4><se.4>')
        self.wait_to_teleport = False
        x, y, z = map(float, coordinates.split(','))
        pos = glm.vec3(x, y, z)
        self.testPos(pos)
    
    def getPos(self):
        return bytes(ny_mem.read_bytes(self.me.handle, self.me.address + self.me.offsets.pos, 0xc))

    def update(self, main):
        meAdress=self.me.address + self.me.offsets.pos