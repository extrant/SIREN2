import inspect #line:1
import typing #line:2
import imgui #line:3
from ff_draw .main import FFDraw #line:4
from ff_draw .mem .utils import bit_field_property #line:5
from nylib .utils .imgui import ctx as imgui_ctx #line:6
from nylib .utils .win32 import memory as ny_mem #line:7
from ff_draw .mem import XivMem #line:8
from ctypes import c_void_p ,CFUNCTYPE #line:10
if typing .TYPE_CHECKING :#line:11
    from .import Hacks #line:12
shell ='''
import ctypes #line:1
import threading #line:2
from nylib .hook import create_hook #line:3
def on_get_flag (OO0O0OOO0O000O00O ,OO0O0000OOOO000O0 ):#line:4
    OO00O0O0000OO0O00 =OO0O0OOO0O000O00O .original (OO0O0000OOOO000O0 )#line:5
    if OO00O0O0000OO0O00 &1 :#line:6
        OO00O0O0000OO0O00 =(OO00O0O0000OO0O00 &~1 )|2 #line:7
    else :#line:8
        threading .Thread (target =OO0O0OOO0O000O00O .uninstall ).start ()#line:9
    return OO00O0O0000OO0O00 #line:10
create_hook (args [0 ],ctypes .c_uint64 ,[ctypes .c_size_t ])(on_get_flag ).install_and_enable ()
'''#line:26
class fly :#line:29
    def __init__ (OO00OO0OO0O0OO0O0 ,OOO0O0000OO0OOOO0 :'Hacks'):#line:31
        OO00OO0OO0O0OO0O0 .main =OOO0O0000OO0OOOO0 #line:32
        OO00OO0OO0O0OO0O0 .mem =OOO0O0000OO0OOOO0 .main .mem #line:33
        OO00OO0OO0O0OO0O0 .me =OO00OO0OO0O0OO0O0 .main .mem .mem .actor_table .me #line:34
        OO00OO0OO0O0OO0O0 .handle =OO00OO0OO0O0OO0O0 .mem .handle #line:35
        OO00OO0OO0O0OO0O0 .set_fly =OO00OO0OO0O0OO0O0 .mem .scanner .find_point ("e8 * * * * ba ? ? ? ? 48 89 7c 24 ? 48 ? ? ? ? ? ? 45 ? ? 45")[0 ]#line:36
    def draw_panel (OO0O0OO0OOO00OOO0 ):#line:39
        OO0O0OO0OOO00OOO0 .me =OO0O0OO0OOO00OOO0 .main .mem .mem .actor_table .me #line:40
        global shell #line:41
        if imgui .button ("fly"):#line:42
            FFDraw .instance .mem .inject_handle .run (shell ,OO0O0OO0OOO00OOO0 .mem .scanner_v2 .find_val ("e8 * * * * f3 ? ? ? ? ? 33 ? 83")[0 ])#line:43
            OO0O0OO0OOO00OOO0 .mem .do_text_command (f'/#SirenPVPTPFly')#line:44
            OO0O0OO0OOO00OOO0 .mem .call_once_game_main (f'''
from ctypes import *                                          
CFUNCTYPE(c_void_p, c_void_p,)({OO0O0OO0OOO00OOO0.set_fly})({OO0O0OO0OOO00OOO0.me.address})
''')#line:49
