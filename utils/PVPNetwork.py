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

    if vars.now_job == 27:
        #print(evt.header.source_id)
        if vars.use_ip is True and vars.main_target == "": return "无目标"
        if vars.use_ip is True and vars.main_target == "0": return "无目标"
        if vars.use_ip is True and vars.main_target != "0":
            data = evt.message
            #print(evt.header.source_id)
            if data.action_id == 29673 and evt.header.source_id == int(vars.main_target):
                vars.target_lb_id = 1
                print(data.main_target_id)

    if vars.now_job == 34:
        data = evt.message
        if vars.sam_me is not None:
            if data.action_id == 29532 and evt.header.source_id == int(vars.sam_me):
                vars.sam_used_bing = True
            if data.action_id == 29526 and evt.header.source_id == int(vars.sam_me):
                vars.sam_used_bing = False              
    if vars.now_job == 24:
    
        if vars.a29228_remain > 0: vars.target_bianzhu_id = None        
        if vars.a29228_remain == 0:
        
            data = evt.message

            if data.action_id == 29537:    #LB武士
                vars.target_bianzhu_id = evt.header.source_id
                
            if data.action_id == 29497:    #龙骑下葬
                vars.target_bianzhu_id = evt.header.source_id
        
            if data.action_id == 29092:    #跳斩
                vars.target_bianzhu_id = evt.header.source_id            

            if data.action_id == 29097:    #夜昏
                vars.target_bianzhu_id = evt.header.source_id   

            if data.action_id == 29550:    #地狱入境
                vars.target_bianzhu_id = evt.header.source_id  

            if data.action_id == 29485:    #LB武僧
                vars.target_bianzhu_id = evt.header.source_id 