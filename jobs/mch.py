import imgui
from ..Vars import vars
import glm
from ff_draw.sniffer.utils.message import NetworkMessage
from ff_draw.sniffer.message_structs.zone_server import ActionEffect

me = None
#target_lb_id = "0"

def mch_test(m, is_pvp=True):
    global me
    vars.now_job = 31
    debuff_status_ids = {1345, 3022, 1348, 1343, 1347}
    me = m.me
    if vars.used_mode == 1: 
        if vars.be_target and vars.be_target.isdigit():
            vars.mch_player1 = m.main.main.mem.actor_table.get_actor_by_id(int(vars.be_target))
        else:
            vars.mch_player1 = None  
        if vars.be_target1 and vars.be_target1.isdigit():
            vars.mch_player2 = m.main.main.mem.actor_table.get_actor_by_id(int(vars.be_target1))
        else:
            vars.mch_player2 = None  
        if vars.be_target2 and vars.be_target2.isdigit():
            vars.mch_player3 = m.main.main.mem.actor_table.get_actor_by_id(int(vars.be_target2))
        else:
            vars.mch_player3 = None  
        if vars.mch_player1 is not None and me is not None:
            if glm.distance(me.pos, vars.mch_player1.pos) > 20:m.main.main.gui.add_line(me.pos, vars.mch_player1.pos, glm.vec4(1, 0, 0, .5), 5)
            else:m.main.main.gui.add_line(me.pos, vars.mch_player1.pos, glm.vec4(0, 1, 0, .5), 5)
        if vars.mch_player2 is not None and me is not None:
            if glm.distance(me.pos, vars.mch_player2.pos) > 20:m.main.main.gui.add_line(me.pos, vars.mch_player2.pos, glm.vec4(1, 0, 0, .5), 5)
            else:m.main.main.gui.add_line(me.pos, vars.mch_player2.pos, glm.vec4(0, 1, 0, .5), 5)
        if vars.mch_player3 is not None and me is not None:
            if glm.distance(me.pos, vars.mch_player3.pos) > 20:m.main.main.gui.add_line(me.pos, vars.mch_player3.pos, glm.vec4(1, 0, 0, .5), 5)
            else:m.main.main.gui.add_line(me.pos, vars.mch_player3.pos, glm.vec4(0, 1, 0, .5), 5)
        if me.target_id is not None:
            main_target = m.main.main.mem.actor_table.get_actor_by_id(int(me.target_id))
            if main_target is not None and me is not None:
                if vars.mch_player1 is not None and me is not None:
                    if glm.distance(me.pos, vars.mch_player1.pos) > 48:m.main.main.gui.add_line(main_target.pos, vars.mch_player1.pos, glm.vec4(1, 0, 0, .5), 5)
                    else:m.main.main.gui.add_line(main_target.pos, vars.mch_player1.pos, glm.vec4(0, 1, 0, .5), 5)
                if vars.mch_player2 is not None and me is not None:
                    if glm.distance(me.pos, vars.mch_player2.pos) > 48:m.main.main.gui.add_line(main_target.pos, vars.mch_player2.pos, glm.vec4(1, 0, 0, .5), 5)
                    else:m.main.main.gui.add_line(main_target.pos, vars.mch_player2.pos, glm.vec4(0, 1, 0, .5), 5)
                if vars.mch_player3 is not None and me is not None:
                    if glm.distance(me.pos, vars.mch_player3.pos) > 48:m.main.main.gui.add_line(main_target.pos, vars.mch_player3.pos, glm.vec4(1, 0, 0, .5), 5)
                    else:m.main.main.gui.add_line(main_target.pos, vars.mch_player3.pos, glm.vec4(0, 1, 0, .5), 5)       
    if vars.used_mode == 0:
        #imgui.text("1")
        if vars.main_target and vars.be_target.isdigit(): 
            vars.mch_main = m.main.main.mem.actor_table.get_actor_by_id(int(vars.main_target))
            #imgui.text("2")
        else:
            vars.mch_main = None  
            #imgui.text("21")
        if vars.mch_main is not None and me is not None:
            #imgui.text("3")
            if glm.distance(me.pos, vars.mch_main.pos) > 20:m.main.main.gui.add_line(me.pos, vars.mch_main.pos, glm.vec4(1, 0, 0, .5), 5)
            else:m.main.main.gui.add_line(me.pos, vars.mch_main.pos, glm.vec4(0, 1, 0, .5), 5)                
            main_target_player = m.main.main.mem.actor_table.get_actor_by_id(int(vars.mch_main.target_id))
            if main_target_player is not None:
                if glm.distance(me.pos, main_target_player.pos) > 48:
                    #m.main.main.gui.add_line(me.pos, main_target_player.pos, glm.vec4(1, 0, 0, .5), 5)
                    end = main_target_player.pos
                    start = me.pos
                    offset = 0.0
                    step_distance = 2  # 设置步长
                    scale = glm.mat4(1.1)  # 设置缩放矩阵                
                    norm_d = glm.normalize(end - start)
                    dis = glm.distance(start, end)
                    rot = glm.polar(norm_d).y
                    drawn = offset * step_distance
                    _surface_color = glm.vec4(1.0, 0.0, 0.0, .5)  # 设置表面颜色
                    _line_color = glm.vec4(1.0, 1.0, 1.0, 1.0)  # 设置线条颜色
                    surface_color = glm.vec4(_surface_color[0], _surface_color[1], _surface_color[2], _surface_color[3])
                    line_color = glm.vec4(_line_color[0], _line_color[1], _line_color[2], _line_color[3])
                    while drawn < dis:
                        m.main.main.gui.add_3d_shape(
                            shape=0x1010000,
                            transform=glm.translate(start + (norm_d * drawn)) * glm.rotate(rot, glm.vec3(0, 1, 0)) * scale,
                            surface_color=surface_color,
                            line_color=line_color,
                        )
                        drawn += step_distance                    
                else:
                    end = main_target_player.pos
                    start = me.pos
                    offset = 0.0
                    step_distance = 2  # 设置步长
                    scale = glm.mat4(1.1)  # 设置缩放矩阵                
                    norm_d = glm.normalize(end - start)
                    dis = glm.distance(start, end)
                    rot = glm.polar(norm_d).y
                    drawn = offset * step_distance
                    _surface_color = glm.vec4(0.0, 1.0, 0.0, .5)  # 设置表面颜色
                    _line_color = glm.vec4(1.0, 1.0, 1.0, 1.0)  # 设置线条颜色
                    surface_color = glm.vec4(_surface_color[0], _surface_color[1], _surface_color[2], _surface_color[3])
                    line_color = glm.vec4(_line_color[0], _line_color[1], _line_color[2], _line_color[3])
                    while drawn < dis:
                        m.main.main.gui.add_3d_shape(
                            shape=0x1010000,
                            transform=glm.translate(start + (norm_d * drawn)) * glm.rotate(rot, glm.vec3(0, 1, 0)) * scale,
                            surface_color=surface_color,
                            line_color=line_color,
                        )
                        drawn += step_distance                                 
    if vars.use_ip == True:
        if vars.used_mode == 0:
            if vars.target_lb_id == "0": return "无网络包接收"
            #if main_target == m.me.id
            get_ip_target_int = int( vars.target_lb_id)
            m.action_state.use_action(29415, get_ip_target_int)
            vars.target_lb_id = "0"


    else:
        return "非匹配条件目标"
    
def machinist_panel():
    global me
    交换显示 = ['接收模式', '发送模式'] 
    _, vars.used_mode = imgui.combo("Mode", vars.used_mode, 交换显示, len(交换显示))
    #imgui.same_line()
    imgui.text(f'MeID:{str(me.id)}')
    imgui.separator()
    if vars.used_mode == 1: 
        with imgui.begin_tab_bar("tabBar") as tab_bar:
            if tab_bar.opened:
                with imgui.begin_tab_item('输出') as item1: 
                    if item1.selected: 
                        imgui.text('被控端监视')    
                        if vars.mch_player1 is not None and me is not None:
                            imgui.text(f'1:{vars.mch_player1.name},距离:{str(int(glm.distance(me.pos, vars.mch_player1.pos)))},血量:{str(vars.mch_player1.current_hp)}')                            
                        else:imgui.text("1:未就绪")
                        if vars.mch_player2 is not None and me is not None:
                            imgui.text(f'2:{vars.mch_player2.name},距离:{str(int(glm.distance(me.pos, vars.mch_player2.pos)))},血量:{str(vars.mch_player2.current_hp)}')
                        else:imgui.text("2:未就绪")
                        if vars.mch_player3 is not None and me is not None:
                            imgui.text(f'3:{vars.mch_player3.name},距离:{str(int(glm.distance(me.pos, vars.mch_player3.pos)))},血量:{str(vars.mch_player3.current_hp)}')                                                        
                        else:imgui.text("3:未就绪")
                with imgui.begin_tab_item('输入') as item2: 
                    if item2.selected:       
                        imgui.text('测试版目前只支持控制3个用户')
                        _, vars.be_target = imgui.input_text("被控用户A ID:", str(vars.be_target), 100)   
                        _, vars.be_target1 = imgui.input_text("被控用户B ID:", str(vars.be_target1), 100)   
                        _, vars.be_target2 = imgui.input_text("被控用户C ID:", str(vars.be_target2), 100) 
                        #_, vars.be_target3 = imgui.input_text("被控用户A ID:", str(vars.be_target3), 100) 
    if vars.used_mode == 0:    
        imgui.text(str(vars.main_target))
        _, vars.main_target = imgui.input_text("输入主控 用户ID:", str(vars.main_target), 100)    