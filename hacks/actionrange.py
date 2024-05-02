import typing #line:1
import glm #line:2
import json #line:3
import struct #line:4
import imgui #line:5
import pathlib #line:6
from ff_draw .gui .text import TextPosition #line:7
from ff_draw .plugins import FFDrawPlugin #line:8
import nylib .utils .win32 .memory as ny_mem #line:9
from nylib .utils import imgui as ny_imgui #line:11
from ..mem import CombatMem #line:12
from fpt4 .utils .sqpack import SqPack #line:14
from ff_draw .main import FFDraw #line:15
import nylib .utils .imgui .ctx as imgui_ctx #line:16
from .utils import ShellInject ,struct2dict ,dict2struct ,Patch ,Hack #line:17
if typing .TYPE_CHECKING :#line:18
    from .import Hacks #line:19
from ..Vars import vars #line:20
from .shell2 import CombatHookConfig #line:21
if typing .TYPE_CHECKING :#line:23
    from .import Hacks #line:24
def make_shell (key ='#__hacks_hooks__/actionrange'):#line:27
    O000OO0O0OO0OOO0O =pathlib .Path (__file__ ).parent /'shell2.py'#line:28
    return O000OO0O0OO0OOO0O .read_text ('utf-8')+f'''
def _install():
    if hasattr(inject_server, {key!r}):
        # return ctypes.addressof(getattr(inject_server, {key!r}).cfg)
        getattr(inject_server, {key!r}).uninstall()
        delattr(inject_server, {key!r})
    hook = CombatHook(args[0])
    setattr(inject_server, {key!r}, hook)
    return ctypes.addressof(hook.cfg)
res = _install()
''',str (O000OO0O0OO0OOO0O )#line:39
shell_uninstall ='''
def uninstall(key):
    if hasattr(inject_server, key):
        getattr(inject_server, key).uninstall()
        delattr(inject_server, key)
'''#line:51
class CurrentMinMax :#line:52
    def __init__ (self ,handle ,address ):#line:53
        self .handle =handle #line:54
        self .address =address #line:55
    current =property (lambda self :ny_mem .read_float (self .handle ,self .address ),lambda self ,value :ny_mem .write_float (self .handle ,self .address ,value ))#line:60
    min =property (lambda self :ny_mem .read_float (self .handle ,self .address +4 ),lambda self ,value :ny_mem .write_float (self .handle ,self .address +4 ,value ))#line:65
    max =property (lambda self :ny_mem .read_float (self .handle ,self .address +8 ),lambda self ,value :ny_mem .write_float (self .handle ,self .address +8 ,value ))#line:70
class Cam :#line:73
    def __init__ (self ,main :'Hacks'):#line:74
        self .main =main #line:75
        OOOO00O00OO0OOOOO =main .main .mem #line:76
        self .handle =OOOO00O00OO0OOOOO .handle #line:77
        self ._cam_base ,=OOOO00O00OO0OOOOO .scanner .find_point ("48 8D 0D * * * * E8 ? ? ? ? 48 83 3D ? ? ? ? ? 74 ? E8 ? ? ? ?")#line:78
        self ._zoom_offset ,=OOOO00O00OO0OOOOO .scanner .find_val ("F3 0F ? ? * * * * 48 8B ? ? ? ? ? 48 85 ? 74 ? F3 0F ? ? ? ? ? ? 48 83 C1")#line:79
        self ._fov_offset ,=OOOO00O00OO0OOOOO .scanner .find_val ("F3 0F ? ? * * * * 0F 2F ? ? ? ? ? 72 ? F3 0F ? ? ? ? ? ? 48 8B")#line:80
        self ._angle_offset ,=OOOO00O00OO0OOOOO .scanner .find_val ("F3 0F 10 B3 * * * * 48 8D ? ? ? F3 44 ? ? ? ? ? ? ? F3 44")#line:81
        self .preset_data =main .data .setdefault ('cam_preset',{})#line:82
        if 'zoom'in self .preset_data :#line:83
            self .cam_zoom .min ,self .cam_zoom .max =self .preset_data ['zoom']['min'],self .preset_data ['zoom']['max']#line:84
        else :#line:85
            self .preset_data ['zoom']={'min':self .cam_zoom .min ,'max':self .cam_zoom .max }#line:86
        if 'fov'in self .preset_data :#line:88
            self .cam_fov .min ,self .cam_fov .max =self .preset_data ['fov']['min'],self .preset_data ['fov']['max']#line:89
        else :#line:90
            self .preset_data ['fov']={'min':self .cam_fov .min ,'max':self .cam_fov .max }#line:91
        if 'angle'in self .preset_data :#line:93
            self .cam_angle .min ,self .cam_angle .max =self .preset_data ['angle']['min'],self .preset_data ['angle']['max']#line:94
        else :#line:95
            self .preset_data ['angle']={'min':self .cam_angle .min ,'max':self .cam_angle .max }#line:96
        main .storage .save ()#line:98
        self .main .logger .debug (f'cam/cam_base: {self._cam_base:X}')#line:99
        self .main .logger .debug (f'cam/zoom_offset: {self._zoom_offset:X}')#line:100
        self .main .logger .debug (f'cam/fov_offset: {self._fov_offset:X}')#line:101
        self .main .logger .debug (f'cam/angle_offset: {self._angle_offset:X}')#line:102
    @property #line:104
    def cam_zoom (self ):#line:105
        return CurrentMinMax (self .handle ,ny_mem .read_address (self .handle ,self ._cam_base )+self ._zoom_offset )#line:106
    @property #line:108
    def cam_fov (self ):#line:109
        return CurrentMinMax (self .handle ,ny_mem .read_address (self .handle ,self ._cam_base )+self ._fov_offset )#line:110
    @property #line:112
    def cam_angle (self ):#line:113
        return CurrentMinMax (self .handle ,ny_mem .read_address (self .handle ,self ._cam_base )+self ._angle_offset )#line:114
    def draw_panel (self ):#line:116
        imgui .columns (4 )#line:117
        imgui .next_column ()#line:118
        imgui .text ("Current")#line:119
        imgui .next_column ()#line:120
        imgui .text ("Min")#line:121
        imgui .next_column ()#line:122
        imgui .text ("Max")#line:123
        imgui .next_column ()#line:124
        imgui .separator ()#line:125
        OOOOOO0O00000OO0O =self .cam_zoom #line:127
        imgui .text ("Zoom")#line:128
        imgui .next_column ()#line:129
        OO000OO00O0OOO00O ,O0000OOOOO0OOO0O0 =imgui .drag_float ("##zoom_current",OOOOOO0O00000OO0O .current ,0.1 ,OOOOOO0O00000OO0O .min ,OOOOOO0O00000OO0O .max ,"%.1f")#line:130
        if OO000OO00O0OOO00O :OOOOOO0O00000OO0O .current =O0000OOOOO0OOO0O0 #line:131
        imgui .next_column ()#line:132
        OO000OO00O0OOO00O ,O0O0OOO0OO000O0OO =imgui .input_float ('##zoom_min',OOOOOO0O00000OO0O .min ,.5 ,5 ,"%.1f")#line:133
        if OO000OO00O0OOO00O :#line:134
            OOOOOO0O00000OO0O .min =O0O0OOO0OO000O0OO #line:135
            self .preset_data ['zoom']['min']=O0O0OOO0OO000O0OO #line:136
            self .main .storage .save ()#line:137
        imgui .next_column ()#line:138
        OO000OO00O0OOO00O ,O00O0OO0OOOOO0OOO =imgui .input_float ('##zoom_max',OOOOOO0O00000OO0O .max ,.5 ,5 ,"%.1f")#line:139
        if OO000OO00O0OOO00O :#line:140
            OOOOOO0O00000OO0O .max =O00O0OO0OOOOO0OOO #line:141
            self .preset_data ['zoom']['max']=O00O0OO0OOOOO0OOO #line:142
            self .main .storage .save ()#line:143
        imgui .next_column ()#line:144
        imgui .columns (1 )#line:147
class GrandCompany :#line:153
    shell ='''
import ctypes
from nylib.hook import create_hook
from ctypes import c_int64, c_float, c_ubyte, c_uint,c_void_p,addressof
def create_knock_hook():
    if hasattr(inject_server, key):
        return addressof(getattr(getattr(inject_server, key), 'val'))
    val = c_int64(0)
    def knock_hook(hook, a1):
        #print(f"get_hooked_message {str(a1)} ")
        return 17#hook.original(a1)
    hook = create_hook(actorLBAdress1, ctypes.c_uint64, [ctypes.c_int64])(knock_hook).install_and_enable()
    setattr(hook, 'val', val)
    setattr(inject_server, key, hook)
    return addressof(val)
res=create_knock_hook()
'''#line:170
    shell_uninstall ='''
def uninstall(key):
    if hasattr(inject_server, key):
        getattr(inject_server, key).uninstall()
        delattr(inject_server, key)
uninstall(key)
'''#line:178
    shell_uninstall_mini ='''
def uninstall(key):
    if hasattr(inject_server, key):
        getattr(inject_server, key).uninstall()
        delattr(inject_server, key)
uninstall(key)
'''#line:186
    def __init__ (self ,main :'Hacks'):#line:187
        self .show_imgui_window =True #line:188
        self .main =main #line:189
        self .mem =main .main .mem #line:190
        self .LBKnock =False #line:191
        self .actorLBAdress1 =self .mem .scanner .find_address ("0F B6 81 ?? ?? ?? ?? FF C8 83 F8 ?? 73")#line:192
        self .actorKnockKey1 ='__hacks_hook__GrandCompany__'#line:193
    def draw_panel (self ):#line:196
        if imgui .button ('无视军衔交军票'):#line:199
            if not self .LBKnock :#line:200
                self .actorKnockHook1 =self .mem .inject_handle .run (f'key=\'{self.actorKnockKey1}\'\nactorLBAdress1 = {self.actorLBAdress1}\n'+self .shell )#line:201
            else :#line:202
                self .mem .inject_handle .run (f'key =\'{self.actorKnockKey1}\'\n'+self .shell_uninstall_mini )#line:203
            self .LBKnock =not self .LBKnock #line:204
        imgui .same_line ()#line:205
        imgui .text (f'无视军衔交军票：{"开启" if self.LBKnock else "关闭"}')#line:206
class Afk :#line:208
    def __init__ (self ,main :'Hacks'):#line:209
        self .main =main #line:210
        O00OOOOO0OO0O0O00 =main .main .mem #line:211
        self .handle =O00OOOOO0OO0O0O00 .handle #line:212
        self .write_1 =O00OOOOO0OO0O0O00 .scanner .find_address ("75 ? 0F 28 C7 0F 28 CF")#line:213
        self .write_2 =O00OOOOO0OO0O0O00 .scanner .find_address ("F3 0F 11 51 ? 33 C9")#line:214
        self .write_2_original =O00OOOOO0OO0O0O00 .scanner .get_original_text (self .write_2 ,5 )#line:215
        self .preset_data =main .data .setdefault ('afk',{})#line:216
        if 'enabled'in self .preset_data :#line:217
            self .is_enabled =self .preset_data ['enabled']#line:218
        else :#line:219
            self .preset_data ['enabled']=self .is_enabled #line:220
        self .main .logger .debug (f'afk/write_1: {self.write_1:X}')#line:222
        self .main .logger .debug (f'afk/write_2: {self.write_2:X}')#line:223
    @property #line:225
    def is_enabled (self ):#line:226
        return ny_mem .read_ubyte (self .handle ,self .write_1 )==0xeb #line:227
    @is_enabled .setter #line:229
    def is_enabled (self ,value ):#line:230
        ny_mem .write_ubyte (self .handle ,self .write_1 ,0xeb if value else 0x75 )#line:231
        ny_mem .write_bytes (self .handle ,self .write_2 ,bytearray (b'\x90'*5 if value else self .write_2_original ))#line:232
        self .preset_data ['enabled']=value #line:233
        self .main .storage .save ()#line:234
    def draw_panel (self ):#line:236
        OO0O0OOO0OO0O00O0 ,O0O00OO00OO0OO00O =imgui .checkbox ("Enabled 挂机防踢",self .is_enabled )#line:237
        if OO0O0OOO0OO0O00O0 :#line:238
            self .is_enabled =O0O00OO00OO0OO00O #line:239
class ShopQuantity :#line:244
    def __init__ (self ,combat :'Hacks'):#line:245
        O0OO000OO000OOO00 =combat .main .mem #line:246
        self .handle =O0OO000OO000OOO00 .handle #line:247
        self .p_code =O0OO000OO000OOO00 .scanner_v2 .find_address ("41 ?? 63 00 00 00 41 ?? ?? 44 ?? ?? ?? 41")+0x2 #line:248
        self .p_code5 =O0OO000OO000OOO00 .scanner_v2 .find_address ('83 ? ? 76 ? bb ? ? ? ? eb')+0x2 #line:249
        self .p_code6 =O0OO000OO000OOO00 .scanner_v2 .find_address ('bb ? ? ? ? eb ? 85 ? 41 ? ? ?')+0x1 #line:251
        self .p_code1 =int ("7FF7F15626FC",16 )#line:252
        self .p_code2 =int ("7FF7F1562700",16 )#line:253
        self .p_code3 =int ("7FF7F1562704",16 )#line:254
        self .p_code4 =int ("7FF7F1562708",16 )#line:255
        self .raw =ny_mem .read_uint (self .handle ,self .p_code )#line:257
        self .raw5 =ny_mem .read_ubyte (self .handle ,self .p_code5 )#line:258
        self .raw6 =ny_mem .read_uint (self .handle ,self .p_code6 )#line:259
        self .raw1 =0 #line:260
        self .raw2 =0 #line:261
        self .raw3 =0 #line:262
        self .raw4 =0 #line:263
        self ._state =False #line:265
    @property #line:267
    def state (self ):#line:268
        OOO00O000OO00000O =ny_mem .read_uint (self .handle ,self .p_code )#line:269
        return OOO00O000OO00000O ==999 #line:270
    @state .setter #line:272
    def state (self ,value ):#line:273
        O00OOOOO0O0O00O00 =999 if value else 99 #line:274
        O0O00O0O00OOOOO00 =255 if value else 99 #line:275
        ny_mem .write_uint (self .handle ,self .p_code ,O00OOOOO0O0O00O00 )#line:276
        ny_mem .write_ubyte (self .handle ,self .p_code6 ,O0O00O0O00OOOOO00 )#line:277
        self ._state =value #line:278
    def draw_panel (self ):#line:280
        imgui .text (f'当前购买最高{self.raw}')#line:281
        OO0O0O00OOO00OO0O ,OO0O00O00OO0OO000 =imgui .checkbox ("去除购买限制",self .state )#line:282
        imgui .text ('部队战绩交易量最高为255,交易数量突破99都属于异常封包 \n请酌情开启')#line:283
        if OO0O0O00OOO00OO0O :#line:284
            self .state =OO0O00O00OO0OO000 #line:286
        return OO0O0O00OOO00OO0O ,OO0O00O00OO0OO000 #line:287
    def draw_2 (self ):#line:289
        imgui .text ("FAKE CN6.51 ONLY")#line:290
        _O0OOOO000OOOO0OOO ,self .raw1 =imgui .input_text ("参战次数:",str (self .raw1 ),100 )#line:291
        _O0OOOO000OOOO0OOO ,self .raw2 =imgui .input_text ("冠军次数:",str (self .raw2 ),100 )#line:292
        _O0OOOO000OOOO0OOO ,self .raw3 =imgui .input_text ("亚军次数:",str (self .raw3 ),100 )#line:293
        _O0OOOO000OOOO0OOO ,self .raw4 =imgui .input_text ("季军次数:",str (self .raw4 ),100 )#line:294
        if imgui .button ("确定"):#line:295
            ny_mem .write_uint (self .handle ,self .p_code1 ,int (self .raw1 ))#line:296
            ny_mem .write_uint (self .handle ,self .p_code2 ,int (self .raw2 ))#line:297
            ny_mem .write_uint (self .handle ,self .p_code3 ,int (self .raw3 ))#line:298
            ny_mem .write_uint (self .handle ,self .p_code4 ,int (self .raw4 ))#line:299
class NoActionMove :#line:301
    def __init__ (self ,combat :'Hacks'):#line:302
        O0O0O0O0OOOOOO0O0 =combat .main .mem #line:303
        self .handle =O0O0O0O0OOOOOO0O0 .handle #line:304
        self .p_code =O0O0O0O0OOOOOO0O0 .scanner .find_address ("48 89 5C 24 ? 48 89 74 24 ? 57 48 83 EC ? 48 8B F1 0F 29 74 24 ? 48 8B 89 ? ? ? ? 0F 28 F3")#line:305
        self .state =False #line:306
    @property #line:308
    def state (self ):#line:309
        return ny_mem .read_ubyte (self .handle ,self .p_code )==0xc3 #line:310
    @state .setter #line:312
    def state (self ,value ):#line:313
        ny_mem .write_ubyte (self .handle ,self .p_code ,0xc3 if value else 0x48 )#line:314
    def draw_panel (self ):#line:316
        OOOO0O00000000O00 ,OO00OO00O0O0OO0O0 =imgui .checkbox ("无突进",self .state )#line:317
        if OOOO0O00000000O00 :self .state =OO00OO00O0O0OO0O0 #line:318
        return OOOO0O00000000O00 ,OO00OO00O0O0OO0O0 #line:319
class AniLock :#line:322
    def __init__ (self ,main :'Hacks'):#line:323
        self .main =main #line:324
        O00O0O0O00O000OOO =main .main .mem #line:325
        self .handle =O00O0O0O00O000OOO .handle #line:326
        self .local_lock =O00O0O0O00O000OOO .scanner .find_address ("41 C7 45 08 ? ? ? ? EB ? 41 C7 45 08")#line:327
        if struct .unpack ('f',O00O0O0O00O000OOO .scanner .get_original_text (self .local_lock +4 ,4 ))==.5 :#line:328
            self .normal_lock_addr =self .local_lock +4 #line:329
            self .seal_lock_addr =self .local_lock +14 #line:330
        else :#line:331
            self .normal_lock_addr =self .local_lock +14 #line:332
            self .seal_lock_addr =self .local_lock +4 #line:333
        self .original_seal_val ,=struct .unpack ('f',O00O0O0O00O000OOO .scanner .get_original_text (self .seal_lock_addr ,4 ))#line:334
        self .original_normal_val ,=struct .unpack ('f',O00O0O0O00O000OOO .scanner .get_original_text (self .normal_lock_addr ,4 ))#line:335
        self .main .logger .debug (f'ani_lock/local_lock: {self.normal_lock_addr:X} (original: {self.original_normal_val:.2f})')#line:337
        self .main .logger .debug (f'ani_lock/seal_lock: {self.seal_lock_addr:X} (original: {self.original_seal_val:.2f})')#line:338
        self .sync_normal_addr =O00O0O0O00O000OOO .scanner .find_address ("41 f6 44 24 ? ? 74 ? f3")+0xf #line:340
        self .sync_normal_original =O00O0O0O00O000OOO .scanner .get_original_text (self .sync_normal_addr ,8 )#line:341
        self .main .logger .debug (f'ani_lock/sync_normal: {self.sync_normal_addr:X}')#line:342
        self .preset_data =main .data .setdefault ('anilock',{})#line:346
        if 'state'in self .preset_data :#line:347
            self .state =self .preset_data ['state']#line:348
        else :#line:349
            self .preset_data ['state']=self .state #line:350
    def set_local (self ,val ):#line:352
        if val ==-1 :#line:353
            ny_mem .write_float (self .handle ,self .normal_lock_addr ,self .original_normal_val )#line:354
            ny_mem .write_float (self .handle ,self .seal_lock_addr ,self .original_seal_val )#line:355
        else :#line:356
            ny_mem .write_float (self .handle ,self .normal_lock_addr ,min (val ,self .original_normal_val ))#line:357
            ny_mem .write_float (self .handle ,self .seal_lock_addr ,min (val ,self .original_seal_val ))#line:358
    def set_sync (self ,mode ):#line:360
        if mode :#line:361
            ny_mem .write_bytes (self .handle ,self .sync_normal_addr ,b'\x90'*8 )#line:362
        else :#line:363
            ny_mem .write_bytes (self .handle ,self .sync_normal_addr ,self .sync_normal_original )#line:364
    @property #line:366
    def state (self ):#line:367
        if ny_mem .read_ubyte (self .handle ,self .sync_normal_addr )==0x90 :#line:368
            return ny_mem .read_float (self .handle ,self .normal_lock_addr )#line:369
        return -1 #line:370
    @state .setter #line:372
    def state (self ,value ):#line:373
        self .set_local (value )#line:374
        self .set_sync (value !=-1 )#line:375
    def draw_panel (self ):#line:377
        OOO00OO0OO0OOO0OO =self .state #line:378
        imgui .text ("动画锁 建议0.2")#line:379
        O0O00OOO0O0O00OO0 ,OOO0OO00OOO0OO0OO =imgui .checkbox ("##Enabled",OOO00OO0OO0OOO0OO !=-1 )#line:380
        imgui .same_line ()#line:381
        if O0O00OOO0O0O00OO0 :#line:382
            if OOO00OO0OO0OOO0OO <0 :#line:383
                self .state =.2 #line:384
            else :#line:385
                self .state =-1 #line:386
        if OOO00OO0OO0OOO0OO !=-1 :#line:387
            O0O00OOO0O0O00OO0 ,OOO0OO00OOO0OO0OO =imgui .slider_float ("##Value",OOO00OO0OO0OOO0OO ,0 ,.5 ,"%.2f",.01 )#line:388
            if O0O00OOO0O0O00OO0 :#line:389
                self .state =OOO0OO00OOO0OO0OO #line:390
class GetRadius :#line:395
    key ='__hacks_hook__get_radius__'#line:396
    shell ='''
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
'''#line:414
    def __init__ (self ,main :'Hacks'):#line:416
        self .main =main #line:417
        self .mem =main .main .mem #line:418
        self .handle =self .mem .handle #line:419
        self .hook_addr ,=self .mem .scanner .find_point ("E8 * * * * F3 0F 58 F0 F3 0F 10 05 ? ? ? ?")#line:420
        self .val_addr =0 #line:421
        self .preset_data =main .data .setdefault ('combat/get_radius',{})#line:423
        if 'val'in self .preset_data :#line:424
            self .val =self .preset_data ['val']#line:425
        else :#line:426
            self .preset_data ['val']=-1 #line:427
            self .main .storage .save ()#line:428
    @property #line:430
    def val (self ):#line:431
        if self .val_addr :#line:432
            return ny_mem .read_float (self .handle ,self .val_addr )#line:433
        return -1 #line:434
    @val .setter #line:436
    def val (self ,value ):#line:437
        if value ==-1 :#line:438
            self .mem .inject_handle .run (f'key = {repr(self.key)};\n'+shell_uninstall )#line:439
            self .val_addr =0 #line:440
        else :#line:441
            if not self .val_addr :#line:442
                self .val_addr =self .mem .inject_handle .run (f'key = {repr(self.key)}; address = {hex(self.hook_addr)};\n'+self .shell )#line:443
            ny_mem .write_float (self .handle ,self .val_addr ,value )#line:444
        self .preset_data ['val']=value #line:445
        self .main .storage .save ()#line:446
    def draw_panel (self ):#line:448
        OO0OOO0OO0OO00OOO =self .val #line:449
        O0OO0O0O00O0O0000 ,OOOOOOO00O000O0OO =imgui .checkbox ("##Enabled",self .val !=-1 )#line:450
        if O0OO0O0O00O0O0000 :#line:451
            self .val =0 if OO0OOO0OO0OO00OOO <0 else -1 #line:452
        if OO0OOO0OO0OO00OOO !=-1 :#line:453
            imgui .same_line ()#line:454
            imgui .text ("目标圈大小")#line:455
            O0OO0O0O00O0O0000 ,OOOOOOO00O000O0OO =imgui .slider_float ("##Value",self .val ,0 ,4 ,"%.2f",.1 )#line:456
            if imgui .button ("重置（默认值0）"):#line:457
                self .val =0 #line:458
            imgui .same_line ()#line:459
            if imgui .button ("1.0"):#line:460
                self .val =1.0 #line:461
            imgui .same_line ()#line:462
            if imgui .button ("1.5"):#line:463
                self .val =1.5 #line:464
            if O0OO0O0O00O0O0000 :self .val =OOOOOOO00O000O0OO #line:465
class Recast :#line:468
    def __init__ (self ,main :'Hacks'):#line:469
        self .main =main #line:470
        self .mem =main .main .mem #line:471
        self .handle =self .mem .handle #line:472
        OOO0OOO0O0OO00000 ,O000OOOOOOOOOO00O =make_shell ()#line:473
        self .p_cfg =self .mem .inject_handle .run (OOO0OOO0O0OO00000 ,{'on_get_recast_time':self .mem .scanner .find_point ('e8 * * * * 8b ? 44 ? ? ? 49 ? ? e8 ? ? ? ? 45')[0 ],'on_sync_recast_time':self .mem .scanner .find_address ('40 ? 48 ? ? ? 0f 29 74 24 ? 41 ? ? 0f')},filename =O000OOOOOOOOOO00O )#line:477
        self .data =main .data .setdefault ('combat',{})#line:478
        self .cfg =dict2struct (self .data .get ('hook',{}),CombatHookConfig )#line:479
    @property #line:481
    def cfg (self ):#line:482
        return ny_mem .read_memory (self .handle ,CombatHookConfig ,self .p_cfg )#line:483
    @cfg .setter #line:485
    def cfg (self ,value ):#line:486
        ny_mem .write_memory (self .handle ,self .p_cfg ,value )#line:487
    def draw_panel (self ):#line:489
        OOOO0O00O0OOOO00O =self .cfg #line:490
        O000OOOOO00O00000 =False #line:491
        OO00O0OOO000O00OO =False #line:492
        OO000OOOOO00O00O0 ,O0O0OO00000OO000O =imgui .slider_float ("Recast time reduce",OOOO0O00O0OOOO00O .recast_time_reduce ,0 ,3 )#line:494
        if OO000OOOOO00O00O0 :#line:495
            OOOO0O00O0OOOO00O .recast_time_reduce =O0O0OO00000OO000O #line:496
            OO00O0OOO000O00OO =True #line:497
        OO000OOOOO00O00O0 ,O0O0OO00000OO000O =imgui .checkbox ("Mudra no recast",OOOO0O00O0OOOO00O .mudra_no_recast )#line:498
        if OO000OOOOO00O00O0 :#line:499
            OOOO0O00O0OOOO00O .mudra_no_recast =O0O0OO00000OO000O #line:500
            OO00O0OOO000O00OO =True #line:501
        if OO00O0OOO000O00OO :#line:504
            self .cfg =OOOO0O00O0OOOO00O #line:505
            self .data ['hook']=struct2dict (OOOO0O00O0OOOO00O )#line:506
            O000OOOOO00O00000 =True #line:507
        if O000OOOOO00O00000 :#line:508
            self .main .storage .save ()#line:509
class GetActionRange :#line:512
    key ='__hacks_hook__get_action_range__'#line:513
    shell ='''
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
'''#line:531
    def __init__ (self ,main :'Hacks'):#line:533
        self .main =main #line:534
        self .mem =main .main .mem #line:535
        self .handle =self .mem .handle #line:536
        self .hook_addr ,=self .mem .scanner .find_point ("e8 * * * * f3 0f 11 43 ? 80 ? ?")#line:537
        self .val_addr =0 #line:538
        self .preset_data =main .data .setdefault ('combat/get_action_range',{})#line:540
        if 'val'in self .preset_data :#line:541
            self .val =self .preset_data ['val']#line:542
        else :#line:543
            self .preset_data ['val']=0 #line:544
            self .main .storage .save ()#line:545
    @property #line:547
    def val (self ):#line:548
        if self .val_addr :#line:549
            return ny_mem .read_float (self .handle ,self .val_addr )#line:550
        return -1 #line:551
    @val .setter #line:553
    def val (self ,value ):#line:554
        if value ==-1 :#line:555
            self .mem .inject_handle .run (f'key = {repr(self.key)};\n'+shell_uninstall )#line:556
            self .val_addr =0 #line:557
        else :#line:558
            if not self .val_addr :#line:559
                self .val_addr =self .mem .inject_handle .run (f'key = {repr(self.key)}; address = {hex(self.hook_addr)};\n'+self .shell )#line:560
            ny_mem .write_float (self .handle ,self .val_addr ,value )#line:561
        self .preset_data ['val']=value #line:562
        self .main .storage .save ()#line:563
    def draw_panel (self ):#line:565
        O000OO0OOO0O00OOO =self .val #line:566
        vars .actionrange =self .val #line:567
        imgui .text ("长臂猿")#line:568
        OO00000OOOO00O000 ,OO000O0O0OO0O0O00 =imgui .checkbox ("##Enabled",self .val !=-1 )#line:569
        if OO00000OOOO00O000 :#line:570
            self .val =0 if O000OO0OOO0O00OOO <0 else -1 #line:571
        if O000OO0OOO0O00OOO !=-1 :#line:572
            OO00000OOOO00O000 ,OO000O0O0OO0O0O00 =imgui .slider_float ("##Value",O000OO0OOO0O00OOO ,0 ,4 ,"%.2f",.1 )#line:574
            if imgui .button ("重置（默认值0）"):#line:575
                self .val =0 #line:576
            imgui .same_line ()#line:577
            if imgui .button ("1.0"):#line:578
                self .val =1.0 #line:579
            imgui .same_line ()#line:580
            if imgui .button ("1.5"):#line:581
                self .val =1.5 #line:582
            imgui .same_line ()#line:583
            if imgui .button ("2"):#line:584
                self .val =2.0 #line:585
            if OO00000OOOO00O000 :self .val =OO000O0O0OO0O0O00 #line:586
            if imgui .button ("40"):#line:587
                self .val =40.0 #line:588
            if OO00000OOOO00O000 :self .val =OO000O0O0OO0O0O00 #line:589
