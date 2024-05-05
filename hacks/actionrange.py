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
    OOOO00000O0OO00OO =pathlib .Path (__file__ ).parent /'shell2.py'#line:28
    return OOOO00000O0OO00OO .read_text ('utf-8')+f'''
def _install():
    if hasattr(inject_server, {key!r}):
        # return ctypes.addressof(getattr(inject_server, {key!r}).cfg)
        getattr(inject_server, {key!r}).uninstall()
        delattr(inject_server, {key!r})
    hook = CombatHook(args[0])
    setattr(inject_server, {key!r}, hook)
    return ctypes.addressof(hook.cfg)
res = _install()
''',str (OOOO00000O0OO00OO )#line:39
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
        O0OO0O000OO00OO0O =main .main .mem #line:76
        self .handle =O0OO0O000OO00OO0O .handle #line:77
        self ._cam_base ,=O0OO0O000OO00OO0O .scanner .find_point ("48 8D 0D * * * * E8 ? ? ? ? 48 83 3D ? ? ? ? ? 74 ? E8 ? ? ? ?")#line:78
        self ._zoom_offset ,=O0OO0O000OO00OO0O .scanner .find_val ("F3 0F ? ? * * * * 48 8B ? ? ? ? ? 48 85 ? 74 ? F3 0F ? ? ? ? ? ? 48 83 C1")#line:79
        self ._fov_offset ,=O0OO0O000OO00OO0O .scanner .find_val ("F3 0F ? ? * * * * 0F 2F ? ? ? ? ? 72 ? F3 0F ? ? ? ? ? ? 48 8B")#line:80
        self ._angle_offset ,=O0OO0O000OO00OO0O .scanner .find_val ("F3 0F 10 B3 * * * * 48 8D ? ? ? F3 44 ? ? ? ? ? ? ? F3 44")#line:81
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
        O0000000OOOOOO0O0 =self .cam_zoom #line:127
        imgui .text ("Zoom")#line:128
        imgui .next_column ()#line:129
        O00OOO000O0000OOO ,O0OOOOO00O000O0OO =imgui .drag_float ("##zoom_current",O0000000OOOOOO0O0 .current ,0.1 ,O0000000OOOOOO0O0 .min ,O0000000OOOOOO0O0 .max ,"%.1f")#line:130
        if O00OOO000O0000OOO :O0000000OOOOOO0O0 .current =O0OOOOO00O000O0OO #line:131
        imgui .next_column ()#line:132
        O00OOO000O0000OOO ,O0O0O0OOOO0OO0OOO =imgui .input_float ('##zoom_min',O0000000OOOOOO0O0 .min ,.5 ,5 ,"%.1f")#line:133
        if O00OOO000O0000OOO :#line:134
            O0000000OOOOOO0O0 .min =O0O0O0OOOO0OO0OOO #line:135
            self .preset_data ['zoom']['min']=O0O0O0OOOO0OO0OOO #line:136
            self .main .storage .save ()#line:137
        imgui .next_column ()#line:138
        O00OOO000O0000OOO ,OO000OOOOOOO000OO =imgui .input_float ('##zoom_max',O0000000OOOOOO0O0 .max ,.5 ,5 ,"%.1f")#line:139
        if O00OOO000O0000OOO :#line:140
            O0000000OOOOOO0O0 .max =OO000OOOOOOO000OO #line:141
            self .preset_data ['zoom']['max']=OO000OOOOOOO000OO #line:142
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
        OO000OO00O0OO0000 =main .main .mem #line:211
        self .handle =OO000OO00O0OO0000 .handle #line:212
        self .write_1 =OO000OO00O0OO0000 .scanner .find_address ("75 ? 0F 28 C7 0F 28 CF")#line:213
        self .write_2 =OO000OO00O0OO0000 .scanner .find_address ("F3 0F 11 51 ? 33 C9")#line:214
        self .write_2_original =OO000OO00O0OO0000 .scanner .get_original_text (self .write_2 ,5 )#line:215
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
        O000OOO00OO00O0OO ,OO0000O0O0OOO00O0 =imgui .checkbox ("Enabled 挂机防踢",self .is_enabled )#line:237
        if O000OOO00OO00O0OO :#line:238
            self .is_enabled =OO0000O0O0OOO00O0 #line:239
class ShopQuantity :#line:244
    def __init__ (self ,combat :'Hacks'):#line:245
        O0O00OO0O00000O0O =combat .main .mem #line:246
        self .handle =O0O00OO0O00000O0O .handle #line:247
        self .p_code =O0O00OO0O00000O0O .scanner_v2 .find_address ("41 ?? 63 00 00 00 41 ?? ?? 44 ?? ?? ?? 41")+0x2 #line:248
        self .p_code5 =O0O00OO0O00000O0O .scanner_v2 .find_address ('83 ? ? 76 ? bb ? ? ? ? eb')+0x2 #line:249
        self .p_code6 =O0O00OO0O00000O0O .scanner_v2 .find_address ('bb ? ? ? ? eb ? 85 ? 41 ? ? ?')+0x1 #line:251
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
        OOOO0OO00000O0OO0 =ny_mem .read_uint (self .handle ,self .p_code )#line:269
        return OOOO0OO00000O0OO0 ==999 #line:270
    @state .setter #line:272
    def state (self ,value ):#line:273
        OOO0OO0OOOO0O0000 =999 if value else 99 #line:274
        O0O0OOOOOO00O000O =255 if value else 99 #line:275
        ny_mem .write_uint (self .handle ,self .p_code ,OOO0OO0OOOO0O0000 )#line:276
        ny_mem .write_ubyte (self .handle ,self .p_code6 ,O0O0OOOOOO00O000O )#line:277
        self ._state =value #line:278
    def draw_panel (self ):#line:280
        imgui .text (f'当前购买最高{self.raw}')#line:281
        OO00OO0OOO0000O00 ,OOOO000OOO00O0O0O =imgui .checkbox ("去除购买限制",self .state )#line:282
        imgui .text ('部队战绩交易量最高为255,交易数量突破99都属于异常封包 \n请酌情开启')#line:283
        if OO00OO0OOO0000O00 :#line:284
            self .state =OOOO000OOO00O0O0O #line:286
        return OO00OO0OOO0000O00 ,OOOO000OOO00O0O0O #line:287
    def draw_2 (self ):#line:289
        imgui .text ("FAKE CN6.51 ONLY")#line:290
        _OO00000O00000000O ,self .raw1 =imgui .input_text ("参战次数:",str (self .raw1 ),100 )#line:291
        _OO00000O00000000O ,self .raw2 =imgui .input_text ("冠军次数:",str (self .raw2 ),100 )#line:292
        _OO00000O00000000O ,self .raw3 =imgui .input_text ("亚军次数:",str (self .raw3 ),100 )#line:293
        _OO00000O00000000O ,self .raw4 =imgui .input_text ("季军次数:",str (self .raw4 ),100 )#line:294
        if imgui .button ("确定"):#line:295
            ny_mem .write_uint (self .handle ,self .p_code1 ,int (self .raw1 ))#line:296
            ny_mem .write_uint (self .handle ,self .p_code2 ,int (self .raw2 ))#line:297
            ny_mem .write_uint (self .handle ,self .p_code3 ,int (self .raw3 ))#line:298
            ny_mem .write_uint (self .handle ,self .p_code4 ,int (self .raw4 ))#line:299
class NoActionMove :#line:301
    def __init__ (self ,combat :'Hacks'):#line:302
        OO000OOO0O0O000O0 =combat .main .mem #line:303
        self .handle =OO000OOO0O0O000O0 .handle #line:304
        self .p_code =OO000OOO0O0O000O0 .scanner .find_address ("48 89 5C 24 ? 48 89 74 24 ? 57 48 83 EC ? 48 8B F1 0F 29 74 24 ? 48 8B 89 ? ? ? ? 0F 28 F3")#line:305
        self .state =False #line:306
        combat .main .command .on_command ['SIRENNoActionMove'].append (self .cmd_AFK )#line:307
    @property #line:310
    def state (self ):#line:311
        return ny_mem .read_ubyte (self .handle ,self .p_code )==0xc3 #line:312
    @state .setter #line:314
    def state (self ,value ):#line:315
        ny_mem .write_ubyte (self .handle ,self .p_code ,0xc3 if value else 0x48 )#line:316
    def cmd_AFK (self ,_ ,args ):#line:318
        if len (args )<1 :return #line:319
        if args [0 ]=="On":#line:320
            self .state =True #line:321
        if args [0 ]=="Off":#line:322
            self .state =False #line:323
    def draw_panel (self ):#line:325
        OO0OOOOOO00OO0000 ,O00OO00O0O0OO000O =imgui .checkbox ("无突进",self .state )#line:326
        if OO0OOOOOO00OO0000 :self .state =O00OO00O0O0OO000O #line:327
        return OO0OOOOOO00OO0000 ,O00OO00O0O0OO000O #line:328
class AniLock :#line:331
    def __init__ (self ,main :'Hacks'):#line:332
        self .main =main #line:333
        OO00OOOO00OO000O0 =main .main .mem #line:334
        self .handle =OO00OOOO00OO000O0 .handle #line:335
        self .local_lock =OO00OOOO00OO000O0 .scanner .find_address ("41 C7 45 08 ? ? ? ? EB ? 41 C7 45 08")#line:336
        if struct .unpack ('f',OO00OOOO00OO000O0 .scanner .get_original_text (self .local_lock +4 ,4 ))==.5 :#line:337
            self .normal_lock_addr =self .local_lock +4 #line:338
            self .seal_lock_addr =self .local_lock +14 #line:339
        else :#line:340
            self .normal_lock_addr =self .local_lock +14 #line:341
            self .seal_lock_addr =self .local_lock +4 #line:342
        self .original_seal_val ,=struct .unpack ('f',OO00OOOO00OO000O0 .scanner .get_original_text (self .seal_lock_addr ,4 ))#line:343
        self .original_normal_val ,=struct .unpack ('f',OO00OOOO00OO000O0 .scanner .get_original_text (self .normal_lock_addr ,4 ))#line:344
        self .main .logger .debug (f'ani_lock/local_lock: {self.normal_lock_addr:X} (original: {self.original_normal_val:.2f})')#line:346
        self .main .logger .debug (f'ani_lock/seal_lock: {self.seal_lock_addr:X} (original: {self.original_seal_val:.2f})')#line:347
        self .sync_normal_addr =OO00OOOO00OO000O0 .scanner .find_address ("41 f6 44 24 ? ? 74 ? f3")+0xf #line:349
        self .sync_normal_original =OO00OOOO00OO000O0 .scanner .get_original_text (self .sync_normal_addr ,8 )#line:350
        self .main .logger .debug (f'ani_lock/sync_normal: {self.sync_normal_addr:X}')#line:351
        self .preset_data =main .data .setdefault ('anilock',{})#line:355
        if 'state'in self .preset_data :#line:356
            self .state =self .preset_data ['state']#line:357
        else :#line:358
            self .preset_data ['state']=self .state #line:359
    def set_local (self ,val ):#line:361
        if val ==-1 :#line:362
            ny_mem .write_float (self .handle ,self .normal_lock_addr ,self .original_normal_val )#line:363
            ny_mem .write_float (self .handle ,self .seal_lock_addr ,self .original_seal_val )#line:364
        else :#line:365
            ny_mem .write_float (self .handle ,self .normal_lock_addr ,min (val ,self .original_normal_val ))#line:366
            ny_mem .write_float (self .handle ,self .seal_lock_addr ,min (val ,self .original_seal_val ))#line:367
    def set_sync (self ,mode ):#line:369
        if mode :#line:370
            ny_mem .write_bytes (self .handle ,self .sync_normal_addr ,b'\x90'*8 )#line:371
        else :#line:372
            ny_mem .write_bytes (self .handle ,self .sync_normal_addr ,self .sync_normal_original )#line:373
    @property #line:375
    def state (self ):#line:376
        if ny_mem .read_ubyte (self .handle ,self .sync_normal_addr )==0x90 :#line:377
            return ny_mem .read_float (self .handle ,self .normal_lock_addr )#line:378
        return -1 #line:379
    @state .setter #line:381
    def state (self ,value ):#line:382
        self .set_local (value )#line:383
        self .set_sync (value !=-1 )#line:384
    def draw_panel (self ):#line:386
        OOO0OO0000OOOO0O0 =self .state #line:387
        imgui .text ("动画锁 建议0.2")#line:388
        OO00O00O00OO00O00 ,O0O00OOOO00OO0OO0 =imgui .checkbox ("##Enabled",OOO0OO0000OOOO0O0 !=-1 )#line:389
        imgui .same_line ()#line:390
        if OO00O00O00OO00O00 :#line:391
            if OOO0OO0000OOOO0O0 <0 :#line:392
                self .state =.2 #line:393
            else :#line:394
                self .state =-1 #line:395
        if OOO0OO0000OOOO0O0 !=-1 :#line:396
            OO00O00O00OO00O00 ,O0O00OOOO00OO0OO0 =imgui .slider_float ("##Value",OOO0OO0000OOOO0O0 ,0 ,.5 ,"%.2f",.01 )#line:397
            if OO00O00O00OO00O00 :#line:398
                self .state =O0O00OOOO00OO0OO0 #line:399
class GetRadius :#line:404
    key ='__hacks_hook__get_radius__'#line:405
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
'''#line:423
    def __init__ (self ,main :'Hacks'):#line:425
        self .main =main #line:426
        self .mem =main .main .mem #line:427
        self .handle =self .mem .handle #line:428
        self .hook_addr ,=self .mem .scanner .find_point ("E8 * * * * F3 0F 58 F0 F3 0F 10 05 ? ? ? ?")#line:429
        self .val_addr =0 #line:430
        self .preset_data =main .data .setdefault ('combat/get_radius',{})#line:432
        if 'val'in self .preset_data :#line:433
            self .val =self .preset_data ['val']#line:434
        else :#line:435
            self .preset_data ['val']=-1 #line:436
            self .main .storage .save ()#line:437
    @property #line:439
    def val (self ):#line:440
        if self .val_addr :#line:441
            return ny_mem .read_float (self .handle ,self .val_addr )#line:442
        return -1 #line:443
    @val .setter #line:445
    def val (self ,value ):#line:446
        if value ==-1 :#line:447
            self .mem .inject_handle .run (f'key = {repr(self.key)};\n'+shell_uninstall )#line:448
            self .val_addr =0 #line:449
        else :#line:450
            if not self .val_addr :#line:451
                self .val_addr =self .mem .inject_handle .run (f'key = {repr(self.key)}; address = {hex(self.hook_addr)};\n'+self .shell )#line:452
            ny_mem .write_float (self .handle ,self .val_addr ,value )#line:453
        self .preset_data ['val']=value #line:454
        self .main .storage .save ()#line:455
    def draw_panel (self ):#line:457
        OOOO0O0O000O0000O =self .val #line:458
        O0O00O00O00OOO000 ,O000O0O00OO0OOO0O =imgui .checkbox ("##Enabled",self .val !=-1 )#line:459
        if O0O00O00O00OOO000 :#line:460
            self .val =0 if OOOO0O0O000O0000O <0 else -1 #line:461
        if OOOO0O0O000O0000O !=-1 :#line:462
            imgui .same_line ()#line:463
            imgui .text ("目标圈大小")#line:464
            O0O00O00O00OOO000 ,O000O0O00OO0OOO0O =imgui .slider_float ("##Value",self .val ,0 ,4 ,"%.2f",.1 )#line:465
            if imgui .button ("重置（默认值0）"):#line:466
                self .val =0 #line:467
            imgui .same_line ()#line:468
            if imgui .button ("1.0"):#line:469
                self .val =1.0 #line:470
            imgui .same_line ()#line:471
            if imgui .button ("1.5"):#line:472
                self .val =1.5 #line:473
            if O0O00O00O00OOO000 :self .val =O000O0O00OO0OOO0O #line:474
class Recast :#line:477
    def __init__ (self ,main :'Hacks'):#line:478
        self .main =main #line:479
        self .mem =main .main .mem #line:480
        self .handle =self .mem .handle #line:481
        O0000OO0O0O0O0000 ,OO0O0OOOOO00OOOO0 =make_shell ()#line:482
        self .p_cfg =self .mem .inject_handle .run (O0000OO0O0O0O0000 ,{'on_get_recast_time':self .mem .scanner .find_point ('e8 * * * * 8b ? 44 ? ? ? 49 ? ? e8 ? ? ? ? 45')[0 ],'on_sync_recast_time':self .mem .scanner .find_address ('40 ? 48 ? ? ? 0f 29 74 24 ? 41 ? ? 0f')},filename =OO0O0OOOOO00OOOO0 )#line:486
        self .data =main .data .setdefault ('combat',{})#line:487
        self .cfg =dict2struct (self .data .get ('hook',{}),CombatHookConfig )#line:488
    @property #line:490
    def cfg (self ):#line:491
        return ny_mem .read_memory (self .handle ,CombatHookConfig ,self .p_cfg )#line:492
    @cfg .setter #line:494
    def cfg (self ,value ):#line:495
        ny_mem .write_memory (self .handle ,self .p_cfg ,value )#line:496
    def draw_panel (self ):#line:498
        OO000000OO00O0OO0 =self .cfg #line:499
        OO00000O000OOOOO0 =False #line:500
        O0O0O0O000000O0O0 =False #line:501
        O00O00O0O0O00OO00 ,O0OO0O000OOOOO0O0 =imgui .slider_float ("Recast time reduce",OO000000OO00O0OO0 .recast_time_reduce ,0 ,3 )#line:503
        if O00O00O0O0O00OO00 :#line:504
            OO000000OO00O0OO0 .recast_time_reduce =O0OO0O000OOOOO0O0 #line:505
            O0O0O0O000000O0O0 =True #line:506
        O00O00O0O0O00OO00 ,O0OO0O000OOOOO0O0 =imgui .checkbox ("Mudra no recast",OO000000OO00O0OO0 .mudra_no_recast )#line:507
        if O00O00O0O0O00OO00 :#line:508
            OO000000OO00O0OO0 .mudra_no_recast =O0OO0O000OOOOO0O0 #line:509
            O0O0O0O000000O0O0 =True #line:510
        if O0O0O0O000000O0O0 :#line:513
            self .cfg =OO000000OO00O0OO0 #line:514
            self .data ['hook']=struct2dict (OO000000OO00O0OO0 )#line:515
            OO00000O000OOOOO0 =True #line:516
        if OO00000O000OOOOO0 :#line:517
            self .main .storage .save ()#line:518
class GetActionRange :#line:521
    key ='__hacks_hook__get_action_range__'#line:522
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
'''#line:540
    def __init__ (self ,main :'Hacks'):#line:542
        self .main =main #line:543
        self .mem =main .main .mem #line:544
        self .handle =self .mem .handle #line:545
        self .hook_addr ,=self .mem .scanner .find_point ("e8 * * * * f3 0f 11 43 ? 80 ? ?")#line:546
        self .val_addr =0 #line:547
        self .preset_data =main .data .setdefault ('combat/get_action_range',{})#line:549
        if 'val'in self .preset_data :#line:550
            self .val =self .preset_data ['val']#line:551
        else :#line:552
            self .preset_data ['val']=0 #line:553
            self .main .storage .save ()#line:554
        main .main .command .on_command ['SIRENGetActionRange'].append (self .cmd_AFK )#line:555
    def cmd_AFK (self ,_ ,args ):#line:557
        if len (args )<1 :return #line:558
        if args [0 ]:#line:559
            self .val =int (args [0 ])#line:560
    @property #line:562
    def val (self ):#line:563
        if self .val_addr :#line:564
            return ny_mem .read_float (self .handle ,self .val_addr )#line:565
        return -1 #line:566
    @val .setter #line:568
    def val (self ,value ):#line:569
        if value ==-1 :#line:570
            self .mem .inject_handle .run (f'key = {repr(self.key)};\n'+shell_uninstall )#line:571
            self .val_addr =0 #line:572
        else :#line:573
            if not self .val_addr :#line:574
                self .val_addr =self .mem .inject_handle .run (f'key = {repr(self.key)}; address = {hex(self.hook_addr)};\n'+self .shell )#line:575
            ny_mem .write_float (self .handle ,self .val_addr ,value )#line:576
        self .preset_data ['val']=value #line:577
        self .main .storage .save ()#line:578
    def draw_panel (self ):#line:580
        OOOO0O0000OO00O0O =self .val #line:581
        vars .actionrange =self .val #line:582
        imgui .text ("长臂猿")#line:583
        OO00OO000OOO0O00O ,O0OOO00OO0O000OOO =imgui .checkbox ("##Enabled",self .val !=-1 )#line:584
        if OO00OO000OOO0O00O :#line:585
            self .val =0 if OOOO0O0000OO00O0O <0 else -1 #line:586
        if OOOO0O0000OO00O0O !=-1 :#line:587
            OO00OO000OOO0O00O ,O0OOO00OO0O000OOO =imgui .slider_float ("##Value",OOOO0O0000OO00O0O ,0 ,4 ,"%.2f",.1 )#line:589
            if imgui .button ("重置（默认值0）"):#line:590
                self .val =0 #line:591
            imgui .same_line ()#line:592
            if imgui .button ("1.0"):#line:593
                self .val =1.0 #line:594
            imgui .same_line ()#line:595
            if imgui .button ("1.5"):#line:596
                self .val =1.5 #line:597
            imgui .same_line ()#line:598
            if imgui .button ("2"):#line:599
                self .val =2.0 #line:600
            if OO00OO000OOO0O00O :self .val =O0OOO00OO0O000OOO #line:601
            if imgui .button ("40"):#line:602
                self .val =40.0 #line:603
            if OO00OO000OOO0O00O :self .val =O0OOO00OO0O000OOO #line:604
