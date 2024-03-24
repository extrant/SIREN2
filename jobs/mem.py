import ctypes
import typing
import nylib.utils.win32.memory as ny_mem

from ff_draw.mem.actor import Actor
from ff_draw.mem.utils import direct_mem_property

if typing.TYPE_CHECKING:
    from . import CombatDemo
    from raid_helper import RaidHelper


# patch direct_mem_property to support write memory
def direct_mem_property_set(self, instance, value):
    if instance is None: return
    if not (addr := instance.address): return
    try:
        return ny_mem.write_bytes(instance.handle, addr + getattr(instance.offsets, self.offset_key), bytearray(self.type(value)))
    except Exception:
        return


direct_mem_property.__set__ = direct_mem_property_set


class CoolDown:
    class offsets:
        used = 0x0
        action_id = 0x4
        timer = 0x8
        timer_max = 0xc
        last_state = 0x10

    def __init__(self, handle, address):
        self.handle = handle
        self.address = address

    used = direct_mem_property(ctypes.c_ubyte)
    action_id = direct_mem_property(ctypes.c_uint)
    timer = direct_mem_property(ctypes.c_float)
    timer_max = direct_mem_property(ctypes.c_float)
    last_state = direct_mem_property(ctypes.c_byte)

    @property
    def remain(self):
        return (self.timer_max - self.timer) if self.used else 0


class ActionState:
    class offsets:
        combo_remain = 0x0
        combo_action = 0x4
        stack_has_action = 0x8
        stack_action_type = 0xc
        stack_action_id = 0x10
        stack_target_id = 0x18
        cd_arr = 0x100

    def __init__(self, main: 'CombatMem'):
        self.main = main
        self.handle = main.handle
        self.address, = main.mem.scanner.find_point("F3 0F 11 05 * * * * 48 83 C7 ?")
        self._action_sheet = self.main.main.main.sq_pack.sheets.action_sheet
        self.main.main.logger.debug(f"ActionState address: {hex(self.address)}")

    combo_remain = direct_mem_property(ctypes.c_float)
    combo_action = direct_mem_property(ctypes.c_uint)
    stack_has_action = direct_mem_property(ctypes.c_ubyte)
    stack_action_type = direct_mem_property(ctypes.c_uint)
    stack_action_id = direct_mem_property(ctypes.c_uint)
    stack_target_id = direct_mem_property(ctypes.c_ulonglong)

    def use_action(self, action_id, target_id=None, action_type=1):
        if target_id is None:
            try:
                target_id = self.main.me.id
            except:
                target_id = 0xe0000000
        self.stack_has_action = 1
        self.stack_action_id = action_id
        self.stack_target_id = target_id
        self.stack_action_type = action_type

    def get_cool_down_by_action(self, action_id):
        return self.get_cool_down_by_idx(self._action_sheet[action_id].recast_group)

    def get_cool_down_by_idx(self, idx):
        return CoolDown(self.handle, self.address + self.offsets.cd_arr + 0x14 * idx)


class Targets:
    def __init__(self, main: 'CombatMem'):
        self.main = main
        self.mem = main.mem
        self.handle = main.handle
        self.address, = self.mem.scanner.find_point("48 8B 05 * * * * 48 8D 0D ? ? ? ? FF 50 ? 48 85 DB")
        self.main.main.logger.debug(f"Targets address: {hex(self.address)}")

    @property
    def current(self):
        if actor_ptr := ny_mem.read_ulonglong(self.handle, self.address + 0x80):
            return Actor(self.handle, actor_ptr)

    @current.setter
    def current(self, actor: Actor):
        ny_mem.write_ulonglong(self.handle, self.address + 0x80, actor.address)

    @property
    def mouse_over(self):
        if actor_ptr := ny_mem.read_ulonglong(self.handle, self.address + 0xD0):
            return Actor(self.handle, actor_ptr)

    @mouse_over.setter
    def mouse_over(self, actor: Actor):
        ny_mem.write_ulonglong(self.handle, self.address + 0xD0, actor.address)

    @property
    def focus(self):
        if actor_ptr := ny_mem.read_ulonglong(self.handle, self.address + 0xF8):
            return Actor(self.handle, actor_ptr)

    @focus.setter
    def focus(self, actor: Actor):
        ny_mem.write_ulonglong(self.handle, self.address + 0xF8, actor.address)


class UseActionPos:
    def __init__(self, main: 'CombatMem'):
        self.main = main
        self.mem = main.mem
        self.address = self.mem.scanner.find_address("44 89 44 24 ? 89 54 24 ? 55 53 57")
        self.p_action_manager, = self.mem.scanner.find_point("48 ? ? * * * * 89 5c 24 ? 4c ? ? 44")
        self.main.main.logger.debug(f"UseActionPos address: {hex(self.address)}")
        self.main.main.logger.debug(f"p_action_manager address: {hex(self.p_action_manager)}")

    def __call__(self, action_id, pos, action_type=1):
        # should return 1 if success
        return self.mem.call_once_game_main(
            f'from ctypes import *\n'
            f'vec=(c_float * 3)({pos.x},{pos.y},{pos.z})\n'
            f'res=CFUNCTYPE(c_uint8,c_void_p,c_uint,c_uint,c_uint64,c_uint64,c_uint)({self.address})({self.p_action_manager},{action_type},{action_id},0xe0000000,addressof(vec),0)'
        )


class LimitBreakGauge:
    class offsets:
        level_cap = 0x0
        gauge = 0xa
        gauge_one = 0xc
        fine_play = 0xe
        type = 0xf

    def __init__(self, main: 'CombatMem'):
        self.handle = main.handle
        self.address, = main.mem.scanner.find_point("48 ? ? * * * * e8 ? ? ? ? 44 ? ? 85 ? 75 ? f3")

    level_cap = direct_mem_property(ctypes.c_ubyte)
    gauge = direct_mem_property(ctypes.c_ushort)
    gauge_one = direct_mem_property(ctypes.c_ushort)
    fine_play = direct_mem_property(ctypes.c_ubyte)
    type = direct_mem_property(ctypes.c_ubyte)


class CombatMem:
    _gauges = {}

    def __init__(self, main: 'CombatDemo'):
        self.main = main
        self.mem = main.main.mem
        self.handle = main.main.mem.handle
        self._territory_type_sheet = self.main.main.sq_pack.sheets.territory_type_sheet
        self._battalion_sheet = self.main.main.sq_pack.sheets.battalion_sheet
        self.action_state = ActionState(self)
        self.targets = Targets(self)
        self.use_action_pos = UseActionPos(self)
        self.limit_break_gauge = LimitBreakGauge(self)

    @property
    def me(self):
        return self.mem.actor_table.me

    @property
    def is_pvp(self):
        return self._territory_type_sheet[self.mem.territory_info.territory_id].is_pvp_action

    def is_enemy(self, a1: Actor | None, a2: Actor | None):
        plugin: 'RaidHelper | None'
        if plugin := self.main.main.plugins.get("raid_helper/RaidHelper"):
            return plugin.is_enemy(a1, a2)
        return True  # fallback
