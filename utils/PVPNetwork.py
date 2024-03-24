from ..Vars import vars
from ff_draw.sniffer.utils.message import NetworkMessage
from ff_draw.sniffer.message_structs.zone_server import ActionEffect

def on_effect(evt: NetworkMessage[ActionEffect]):  #网络包相关
    #global target_lb_id
    #print(evt.header.source_id)
    if vars.now_job == 31:
        if vars.use_ip is True and vars.main_target == "": return "无目标"
        if vars.use_ip is True and vars.main_target == "0": return "无目标"
        if vars.use_ip is True and vars.main_target != "0":
            data = evt.message
            #print(evt.header.source_id)
            if data.action_id == 29415 and evt.header.source_id == int(vars.main_target):
                vars.target_lb_id = data.main_target_id
                print(data.main_target_id)