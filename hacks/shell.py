import ctypes
from nylib.hook import create_hook


class MoveHookConfig(ctypes.Structure):
    _fields_ = [
        ('speed_percent', ctypes.c_float),
        ('y_adjust', ctypes.c_float),
        ('max_acceleration', ctypes.c_bool),
        ('no_fall_damage', ctypes.c_bool),
        ('fly_hack', ctypes.c_bool),
        ('anti_knock', ctypes.c_bool),
        ('move_permission', ctypes.c_bool),
    ]


class MoveHook:
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.cfg = MoveHookConfig()
        self.hooks = {}
        set_hook = lambda name, rt, ats: self.hooks.__setitem__(name, create_hook(self.kwargs[name], rt, ats)(getattr(self, name)))
        set_hook('on_send_normal_move', ctypes.c_void_p, [ctypes.c_size_t, ctypes.POINTER(ctypes.c_float), ctypes.c_uint])
        set_hook('on_send_combat_move', ctypes.c_void_p, [ctypes.c_size_t, ctypes.POINTER(ctypes.c_float), ctypes.c_uint])
        set_hook('on_send_flag', ctypes.c_void_p, [ctypes.c_size_t, ctypes.c_uint])

        for hook in self.hooks.values(): hook.install_and_enable()


    def on_send_normal_move(self, hook, a1, p_data, a3):
        if p_data and self.cfg.y_adjust:
            p_data[3] += self.cfg.y_adjust
        return hook.original(a1, p_data, a3)

    def on_send_combat_move(self, hook, a1, p_data, a3):
        if p_data and self.cfg.y_adjust:
            p_data[4] += self.cfg.y_adjust
            p_data[7] += self.cfg.y_adjust
        return hook.original(a1, p_data, a3)

    def on_send_flag(self, hook, a1, flag):
        if self.cfg.no_fall_damage and flag & 0b11100000000:
            flag = (flag & (~0b11100000000)) | 2
        return hook.original(a1, flag)

    def uninstall(self):
        for hook in self.hooks.values(): hook.uninstall()





