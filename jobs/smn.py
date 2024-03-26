from ..mem import CombatMem
from ..Vars import vars
from typing import Optional
from ff_draw.mem.actor import Actor
from nylib.utils.win32 import memory as ny_mem
import glm
import imgui


me = None
#target_lb_id = "0"
def smn_command(_, args):
    vars.smn_fire = True
    print("111111")

def smn_test(m, is_pvp=True):
    global me
    vars.now_job = 27
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
                distance_xzme = ((main_target.pos.x - me.pos.x) ** 2 + (main_target.pos.z - me.pos.z) ** 2) ** 0.5
                if (main_target.pos.y - me.pos.y) > vars.a29537_high or distance_xzme >= 30:m.main.main.gui.add_line(main_target.pos, me.pos, glm.vec4(1, 0, 0, .5), 5)
                else:m.main.main.gui.add_line(main_target.pos, me.pos, glm.vec4(0, 1, 0, .5), 5)  
                vars.smn_textdis = f'高度差：{str(int(main_target.pos.y - me.pos.y + 5))} 平面距离 {str(int(distance_xzme))}'         
                if vars.mch_player1 is not None and me is not None:
                    distance_xz1 = ((main_target.pos.x - vars.mch_player1.pos.x) ** 2 + (main_target.pos.z - vars.mch_player1.pos.z) ** 2) ** 0.5
                    if int(main_target.pos.y - vars.mch_player1.pos.y) + 5> vars.a29537_high or distance_xz1 >= 30:m.main.main.gui.add_line(main_target.pos, vars.mch_player1.pos, glm.vec4(1, 0, 0, .5), 5)
                    else:m.main.main.gui.add_line(main_target.pos, vars.mch_player1.pos, glm.vec4(0, 1, 0, .5), 5)
                if vars.mch_player2 is not None and me is not None:
                    distance_xz2 = ((main_target.pos.x - vars.mch_player2.pos.x) ** 2 + (main_target.pos.z - vars.mch_player2.pos.z) ** 2) ** 0.5
                    if int(main_target.pos.y - vars.mch_player2.pos.y) + 5 > vars.a29537_high or distance_xz2 >= 30:m.main.main.gui.add_line(main_target.pos, vars.mch_player2.pos, glm.vec4(1, 0, 0, .5), 5)
                    else:m.main.main.gui.add_line(main_target.pos, vars.mch_player2.pos, glm.vec4(0, 1, 0, .5), 5)
                if vars.mch_player3 is not None and me is not None:
                    distance_xz3 = ((main_target.pos.x - vars.mch_player3.pos.x) ** 2 + (main_target.pos.z - vars.mch_player3.pos.z) ** 2) ** 0.5
                    if int(main_target.pos.y - vars.mch_player3.pos.y) + 5 > vars.a29537_high or distance_xz3 >= 30:m.main.main.gui.add_line(main_target.pos, vars.mch_player3.pos, glm.vec4(1, 0, 0, .5), 5)
                    else:m.main.main.gui.add_line(main_target.pos, vars.mch_player3.pos, glm.vec4(0, 1, 0, .5), 5)  
                if vars.smn_fire is True and m.limit_break_gauge.gauge == m.limit_break_gauge.gauge_one:
                    if main_target.pos.y - me.pos.y > 0:
                        fix_high = main_target.pos.y - me.pos.y
                        m.use_action_pos(29673, glm.vec3(main_target.pos.x, main_target.pos.y + (vars.a29537_high - fix_high), main_target.pos.z))
                    else: m.use_action_pos(29673, glm.vec3(main_target.pos.x, me.pos.y + vars.a29537_high, main_target.pos.z))  
                    vars.smn_fire = False
                if m.limit_break_gauge.gauge != m.limit_break_gauge.gauge_one:
                    vars.smn_fire = False
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
                distance_xz = ((main_target_player.pos.x - me.pos.x) ** 2 + (main_target_player.pos.z - me.pos.z) ** 2) ** 0.5
                #m.targets.current = main_target_player
                vars.a29537_pos = main_target_player.pos
                #imgui.text(f'{str(main_target_player.pos.y - me.pos.y)} + {str(distance_xz)}')
                if int(main_target_player.pos.y - me.pos.y)  + 5>= vars.a29537_high or distance_xz >= 30:
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
                if vars.target_lb_id == 1:
                    if vars.a29537_pos.y - me.pos.y > 0:
                        fix_high = vars.a29537_pos.y - me.pos.y
                        m.use_action_pos(29673, glm.vec3(vars.a29537_pos.x, vars.a29537_pos.y + (vars.a29537_high - fix_high), vars.a29537_pos.z))
                    else: m.use_action_pos(29673, glm.vec3(vars.a29537_pos.x, me.pos.y + vars.a29537_high, vars.a29537_pos.z))                    
                vars.target_lb_id = "0"




#@register_strategy(27) #召唤
def smn_test_old(m, is_pvp=True):
    target = m.targets.current
    me_target = m.me.target_id
    if me_target is not None:
        main_target = m.main.main.mem.actor_table.get_actor_by_id(int(me_target))
    vars.now_job = 27
    if (me := m.me) is None: return 4
    #if (target := m.targets.current) is None: return "无目标！"
    if not m.is_enemy(me, target): return 6
    if m.action_state.stack_has_action: return "动作执行中"
    gcd_remain = m.action_state.get_cool_down_by_action(3617).remain
    if gcd_remain > .5: return 8
    #if m.limit_break_gauge.gauge == m.limit_break_gauge.gauge_one:m.use_action_pos(29673, glm.vec3(me.pos.x + 50, me.pos.y + vars.a29537_high, me.pos.z))
    if m.limit_break_gauge.gauge == m.limit_break_gauge.gauge_one and main_target is not None:
        if main_target.pos.y - me.pos.y > 0:
            fix_high = main_target.pos.y - me.pos.y
            #m.use_action_pos(29673, glm.vec3(main_target.pos.x, main_target.pos.y + (vars.a29537_high - fix_high), main_target.pos.z))
            m.use_action_pos(29673, glm.vec3(main_target.pos.x, me.pos.y + (vars.a29537_high - fix_high), main_target.pos.z))
        else: m.use_action_pos(29673, glm.vec3(main_target.pos.x, me.pos.y + vars.a29537_high, main_target.pos.z))
        
        return "龙神！"
    else:
        return "极限槽未满"
    #else:
    #    return "非匹配条件目标"
    #    pass
    

def smn_panel():
    global me
    imgui.same_line()
    imgui.text("Summon V2")
    _, vars.a29537_high = imgui.slider_float("龙神空中高度", vars.a29537_high, -1, 30, "%.0f")    
    
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
                        imgui.text('目标距离') 
                        imgui.same_line()
                        imgui.text(vars.smn_textdis)
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