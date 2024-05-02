import ctypes
from nylib.hook import create_hook

class CombatHookConfig(ctypes.Structure):
    _fields_ = [
        ('extra_actor_radius', ctypes.c_float),
        ('extra_action_range', ctypes.c_float),
        ('recast_time_reduce', ctypes.c_float),
        ('mudra_no_recast', ctypes.c_bool),
        ('anti_knock', ctypes.c_bool),
        ('move_permission', ctypes.c_bool),
        ('no_action_move', ctypes.c_bool),
        ('action_move_white_list', ctypes.c_uint16 * 0x50),
    ]


class CombatHook:
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.cfg = CombatHookConfig()
        self.hooks = {}
        set_hook = lambda name, rt, ats: self.hooks.__setitem__(name, create_hook(self.kwargs[name], rt, ats)(getattr(self, name)))
        set_hook('on_get_recast_time', ctypes.c_int, [ctypes.c_uint, ctypes.c_uint, ctypes.c_ubyte])
        set_hook('on_sync_recast_time', ctypes.c_float, [ctypes.c_uint64, ctypes.c_uint, ctypes.c_uint, ctypes.c_float])        
        for hook in self.hooks.values():
            hook.install_and_enable()

    def uninstall(self):
        for hook in self.hooks.values():
            hook.uninstall()

    def on_get_recast_time(self, hook, type_, key, extra):
        res = hook.original(type_, key, extra)
        if res and type_ == 1:
            if self.cfg.mudra_no_recast and key in (18805, 18806, 18807, 2259, 2261, 2263):
                return 0
            return int(max(res - self.cfg.recast_time_reduce * 1000, 0))
        return res

    def on_sync_recast_time(self, hook, a1, type_, key, time_max):
        if time_max :
            if self.cfg.mudra_no_recast and key in (18805, 18806, 18807, 2259, 2261, 2263):
                time_max = 0
            else:
                time_max = max(time_max - self.cfg.recast_time_reduce, 0)
        return hook.original(a1, type_, key, time_max)