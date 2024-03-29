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
        # set_hook('on_get_actor_radius', ctypes.c_float, [ctypes.c_uint64, ctypes.c_ubyte])
        # set_hook('on_get_action_range', ctypes.c_float, [ctypes.c_uint])
        # set_hook('on_get_recast_time', ctypes.c_int, [ctypes.c_uint, ctypes.c_uint, ctypes.c_ubyte])
        # set_hook('on_sync_recast_time', ctypes.c_float, [ctypes.c_uint64, ctypes.c_uint, ctypes.c_uint, ctypes.c_float])
        # set_hook('on_knock_back', ctypes.c_uint64, [ctypes.c_uint64, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_ubyte, ctypes.c_uint])
        # set_hook('on_permission_check', ctypes.c_ubyte, [ctypes.c_uint64, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint])
        # set_hook('on_action_move', ctypes.c_uint64, [ctypes.c_uint64, ctypes.c_uint8, ctypes.c_uint64, ctypes.c_float, ctypes.POINTER(ctypes.c_uint16)])
        for hook in self.hooks.values():
            hook.install_and_enable()

    def uninstall(self):
        for hook in self.hooks.values():
            hook.uninstall()

    def on_get_actor_radius(self, hook, p_actor, straight):
        return max(hook.original(p_actor, straight) + self.cfg.extra_actor_radius, 0)

    def on_get_action_range(self, hook, action_id):
        return (res := hook.original(action_id)) and max(res + self.cfg.extra_action_range, 0)

    def on_get_recast_time(self, hook, type_, key, extra):
        res = hook.original(type_, key, extra)
        if res and type_ == 1:
            if self.cfg.mudra_no_recast and key in (18805, 18806, 18807, 2259, 2261, 2263):
                return 0
            return int(max(res - self.cfg.recast_time_reduce * 1000, 0))
        return res

    def on_sync_recast_time(self, hook, a1, type_, key, time_max):
        if time_max and type_ == 1:
            if self.cfg.mudra_no_recast and key in (18805, 18806, 18807, 2259, 2261, 2263):
                time_max = 0
            else:
                time_max = max(time_max - self.cfg.recast_time_reduce, 0)
        return hook.original(a1, type_, key, time_max)

    def on_knock_back(self, hook, actor_ptr, rotation, distance, duration, is_no_motion, knock_back_type):
        if self.cfg.anti_knock:
            return hook.original(actor_ptr, 0, 0, 0, 1, 0)
        else:
            return hook.original(actor_ptr, rotation, distance, duration, is_no_motion, knock_back_type)

    def on_permission_check(self, hook, cond_manager, permission_id, ignore, ignore2):
        if 96 <= permission_id <= 99 and self.cfg.move_permission: return 1
        return hook.original(cond_manager, permission_id, ignore, ignore2)

    def on_action_move(self, hook, a1, action_timeline_move_id, target_id, facing, p_action_timeline):
        if self.cfg.no_action_move:
            timeline = p_action_timeline.contents.value
            block = True
            for white in self.cfg.action_move_white_list:
                if white == 0:
                    break
                if white == timeline:
                    block = False
                    break
            if block:
                return
        return hook.original(a1, action_timeline_move_id, target_id, facing, p_action_timeline)
