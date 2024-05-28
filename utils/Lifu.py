import collections
import ctypes
import struct
import time
import typing
import imgui
import threading
from ff_draw.sniffer.enums import ZoneServer
from ff_draw.sniffer.message_structs import zone_server, TypeMap, ZoneClient
from ff_draw.sniffer.utils.message import NetworkMessage
from ff_draw.plugins import FFDrawPlugin
from ff_draw.main import FFDraw
from ff_draw.sniffer.sniffer_main import Sniffer
from ff_draw.sniffer.message_structs import zone_server, zone_client, chat_server, chat_client
from ffd_plus.api.pkt_work import PktWorks
from ffd_plus.api.pkt_work.utils import build_event_start, build_event_action, build_event_finish, build_client_trigger, build_inventory_handler
from nylib.utils import ResEvent, wait_until
from nylib.utils.imgui.window_mgr import Window
from ffd_plus.api.pkt_work.utils import packet_builder
import nylib.utils.win32.memory as ny_mem
from ff_draw.mem import XivMem
from nylib.struct import set_fields_from_annotations, fctypes
zone_proto_no = Sniffer.instance.zone_client_pno
chat_proto_no = Sniffer.instance.chat_client_pno        
GlobalRun = False       
Running =False    
PostTrue = False
GetTrue = False   
type_map = TypeMap()


@type_map.set(ZoneClient.InventoryModifyHandler)
@set_fields_from_annotations
class InventoryModifyHandler():
    _size_ = 0X30
    context_id: 'fctypes.c_uint32' = eval('0X0')
    operation_type: 'fctypes.c_uint32' = eval('0X4')
    src_entity: 'fctypes.c_uint32' = eval('0X8')
    src_storage_id: 'fctypes.c_uint32' = eval('0XC')
    src_container_index: 'fctypes.c_int16' = eval('0X10')
    src_cnt: 'fctypes.c_uint32' = eval('0X14')
    src_item_id: 'fctypes.c_uint32' = eval('0X18')
    dst_entity: 'fctypes.c_uint32' = eval('0X1C')
    dst_storage_id: 'fctypes.c_uint32' = eval('0X20')
    dst_container_index: 'fctypes.c_int16' = eval('0X24')
    dst_cnt: 'fctypes.c_uint32' = eval('0X28')
    dst_item_id: 'fctypes.c_uint32' = eval('0X2C')

 
class LifuHelper():
    def __init__(self, main):
        #self.target_id = Control.instance.control_character_id
        self.scene_id = -1
        self.scene_arg = []
        self.delay = 1.0
        
        
        self.main = main
        mem = main.main.mem   
        self.handle = mem.handle
        self.actionMove = False
        self.write_1, = mem.scanner.find_point("44 89 6c 24 ? e8 * * * * e9 ? ? ? ?")
        self.write_2, = mem.scanner.find_point("4c 89 44 24 ? 45 ? ? ? e8 * * * *")
        self.on_push_event_state = ny_mem.read_ubyte(self.handle, self.write_1)  
        self.on_play_event = ny_mem.read_ubyte(self.handle, self.write_2)         
       
        self.run_count = 0  # 初始化计数器
        self.total_runs = 0  # 总次数，初始为0
        self.context_id = "0x10000010"
        self.operation_type = "0x2b0"

        
    def find_item(self, item_id):
        for storage in XivMem.instance.storage:
            #print(ContainerGroup.Inventory)
            #print(storage.container_idx)
            #if storage.storage_id not in ContainerGroup.Inventory: continue
            for item in storage:
                if item.item_id == item_id:
                    #print(item.quantity)
                    return item        
    def send_event_action(self, scene_id=None, res=0, results=None) -> NetworkMessage[zone_server.EventActionResultN]:
        results = results or []
        if scene_id is None: scene_id = self.scene_id
        return PktWorks.instance.zone.send(
            build_event_action(self.id, scene_id, res, *results),
            route=Sniffer.instance.on_zone_server_message[ZoneServer.EventActionResultN],
        )

    def run_code2(self, delay):
        global Running
        PktWorks.instance.zone.send(
            build_event_start(0x60023, 0x10087342a),
            route=Sniffer.instance.on_zone_server_message[ZoneServer.EventStart],
        )   
        time.sleep(delay)  # 使用传入的延时时间
        args1 = [0x663]
        PktWorks.instance.zone.send(
            build_event_action(0x60023, 0x0, 0x1, *args1),
            route=Sniffer.instance.on_zone_server_message[ZoneServer.EventActionResultN],
        )
        time.sleep(delay)  # 使用传入的延时时间
        args2 = []
        PktWorks.instance.zone.send(
            build_event_finish(0x60023, 0x0, 0x0, *args2),
            route=(
                Sniffer.instance.on_zone_server_message[ZoneServer.EventPlayN],
                Sniffer.instance.on_zone_server_message[ZoneServer.EventFinish],
            ),
        )  
        self.run_count += 1
        PktWorks.instance.zone.send(build_event_start(0xe0000, 0x10087342b))
        PktWorks.instance.zone.send(
            build_inventory_handler(0x10000010, 0x2b0, 0x0, 0x1, self.find_item(36115).container_idx, self.find_item(36115).quantity, 0x0, 0x0, 0x7d5, 0x0, 0x0, 0x0),
            route=Sniffer.instance.on_zone_server_message[ZoneServer.InventoryActionAck],
        )   
        args3 = [0x8d13, 0x3, 0x1, 0x663]
        PktWorks.instance.zone.send(
            build_event_action(0xe0000, 0x0, 0x0, *args3),
            route=Sniffer.instance.on_zone_server_message[ZoneServer.EventActionResultN],
        )  
        args4 = [0x663, 0x1]
        PktWorks.instance.zone.send(
            build_event_action(0xe0000, 0x0, 0x1, *args4),
            route=Sniffer.instance.on_zone_server_message[ZoneServer.EventActionResultN],
        )            
        args5 = []
        PktWorks.instance.zone.send(
            build_event_finish(0xe0000, 0x0, 0x0, *args5),
            route=(
                Sniffer.instance.on_zone_server_message[ZoneServer.EventPlayN],
                Sniffer.instance.on_zone_server_message[ZoneServer.EventFinish],
            ),
        )          
        Running = False        
    def draw_panel(self):
        global GlobalRun, Running


        if imgui.button('EventHook(MUST)') :
            if not self.actionMove:
                ny_mem.write_ubyte(self.handle, self.write_1, 0xc3)
                ny_mem.write_ubyte(self.handle, self.write_2, 0xc3)

            else:
                ny_mem.write_ubyte(self.handle, self.write_1, self.on_push_event_state)
                ny_mem.write_ubyte(self.handle, self.write_2, self.on_play_event)

            self.actionMove=not self.actionMove
        imgui.same_line()
        imgui.text(f'Hook：{"开启" if self.actionMove else "关闭"}')  
        imgui.same_line()
        if self.find_item(36115) is not None:
            imgui.text(f'巨匠药酒:DEC:{self.find_item(36115).quantity} HEX:{hex(self.find_item(36115).quantity)}')
        changed, self.delay = imgui.slider_float("Delay", self.delay, 0.1, 2.0, "%.1f", 1)
                        
        imgui.separator()
        if self.actionMove is True:
            changed, self.total_runs = imgui.input_int(f"运行次数{self.run_count}", self.total_runs)
            if imgui.button('Start Loop'):
                GlobalRun = True
            imgui.same_line()
            if imgui.button('Stop Loop'):
                GlobalRun = False
                Running = False
            imgui.same_line()
            if imgui.button('Clear'):
                self.run_count = 0
            imgui.same_line()
            if imgui.button('Test'):
                thread = threading.Thread(target=self.run_code2, args=(self.delay,))
                thread.start() 
            if GlobalRun is True and self.run_count < self.total_runs:
                if Running is False:
                    Running = True
                    thread = threading.Thread(target=self.run_code2, args=(self.delay,))
                    thread.start() 



#"""
#How TO USE?
    
#Modify: FFDraw\ff_draw\sniffer\message_structs\zone_client.py    
#Add this code inside:

#@type_map.set(ZoneClient.InventoryModifyHandler)
#@set_fields_from_annotations
#class InventoryModifyHandler(Structure):
#    _size_ = 0X30
#    context_id: 'fctypes.c_uint32' = eval('0X0')
#    operation_type: 'fctypes.c_uint32' = eval('0X4')
#    src_entity: 'fctypes.c_uint32' = eval('0X8')
#    src_storage_id: 'fctypes.c_uint32' = eval('0XC')
#    src_container_index: 'fctypes.c_int16' = eval('0X10')
#    src_cnt: 'fctypes.c_uint32' = eval('0X14')
#    src_item_id: 'fctypes.c_uint32' = eval('0X18')
#    dst_entity: 'fctypes.c_uint32' = eval('0X1C')
#    dst_storage_id: 'fctypes.c_uint32' = eval('0X20')
#    dst_container_index: 'fctypes.c_int16' = eval('0X24')
#    dst_cnt: 'fctypes.c_uint32' = eval('0X28')
#    dst_item_id: 'fctypes.c_uint32' = eval('0X2C')



    
#Modify: FFDraw\plugins\ffd_bot\api\pkt_work\utils.py   
#Add this code inside:    
    
#def build_inventory_handler(context_id, operation_type, src_entity, src_storage_id, src_container_index, src_cnt, src_item_id, dst_entity, dst_storage_id, dst_container_index, dst_cnt, dst_item_id):
#    pkt = zone_client.InventoryModifyHandler()
#    pkt.context_id = context_id
#    pkt.operation_type = operation_type
#    pkt.src_entity = src_entity
#    pkt.src_storage_id = src_storage_id
#    pkt.src_container_index = src_container_index
#    pkt.src_cnt = src_cnt
#    pkt.src_item_id = src_item_id
#    pkt.dst_entity = dst_entity
#    pkt.dst_storage_id = dst_storage_id
#    pkt.dst_container_index = dst_container_index
#    pkt.dst_cnt = dst_cnt
#    pkt.dst_item_id = dst_item_id
#    return packet_builder(zone_proto_no['InventoryModifyHandler'][0], pkt)
    
#"""