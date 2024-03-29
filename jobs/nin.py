from ..mem import CombatMem
from ..Vars import vars
from typing import Optional
from ff_draw.mem.actor import Actor
from nylib.utils.win32 import memory as ny_mem
import glm
import imgui

result_list = []
id_name = "无"
忍者无视距离的大刀 = False

limit_break_gauge_gauge = 0
limit_break_gauge_gauge_one = 0


def nin_command(_, args):
    if len(args) < 1: return
    if vars.ninja_select_mode == 0:
        if args[0] == "AUTO" and args[1] == "On":
            vars.ninja_use_lb = True                            
        if args[0] == "AUTO" and args[1] == "Off":
            vars.ninja_use_lb = False  
    if vars.ninja_select_mode == 1:
        if args[0] == "MANUAL":
            vars.ninja_use_lb = True        
#忍者选择器
def select_closest_enemy_with_real_hp(m: CombatMem) -> Optional[Actor]:    #忍者选择器  LB选人阶段
    me = m.me
    if not me : return None
    me_pos = me.pos

    inv_status_ids = {3039, 2413, 1302, 1301, 1420}

    def target_validator(a: Actor) -> bool:
        global id_name, id_name_bak, result_list
        id_name = a.name
        if id_name not in result_list:  # 检查结果是否已经存在于列表中
            result_list.append(id_name)
        if not m.is_enemy(me, a): return False
        real_hp = a.current_hp
        if real_hp >= a.max_hp * 0.5: return False
        if me.current_hp <= me.max_hp * 0.1: return False

        has_select_target = False
        for status_id, param, remain, source_id in a.status:
            if status_id in inv_status_ids: return False
            if real_hp <= a.max_hp * 0.47 and real_hp >= a.max_hp * 0.1:
                has_select_target = True
        return has_select_target

    it = (actor for actor in m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor)) #m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor))

    k = lambda a: glm.distance(me_pos, a.pos)
    selected = min(it, key=k, default=None)
    imgui.text(f'{str(selected)}')
    if not selected or glm.distance(me_pos, selected.pos) > 20 + vars.actionrange: return None
    return selected
#忍者选择器
def ninja_pvp(m: CombatMem, is_pvp=True):
    global limit_break_gauge_gauge_one, limit_break_gauge_gauge
    vars.now_job = 30     
    debuff_status_ids = {1345, 3022, 1348, 1343, 1347}
    target = m.targets.current
    if (me := m.me) is None: return 4
    if vars.is_mount != 0: return "坐骑状态中"  
    #if (target := m.targets.current) is None: return "无目标！"
    if not m.is_enemy(me, target): return "非敌对目标"
    #if m.action_state.stack_has_action: return "动作执行中"
    gcd_remain = m.action_state.get_cool_down_by_action(2248).remain
    gcd_remain_jinhua = m.action_state.get_cool_down_by_action(29056).remain    
    if gcd_remain > .5: return 8
    
    if vars.ninja_select_mode == 1:
        if vars.ninja_use_lb is True:
            #imgui.text("这一步说明模式识别是正确的")
            target_enemy = select_closest_enemy_with_real_hp(m)
            #imgui.text("这一步说明选择器是正确的")
            if target_enemy:
                #imgui.text("这一步说明已经找到了符合的敌人")
                m.targets.current = target_enemy
                #imgui.text("这一步说明已经选择符合的敌人")
                real_hp = target_enemy.current_hp
                if m.limit_break_gauge.gauge == m.limit_break_gauge.gauge_one:
                    #imgui.text("这一步说明你的LB槽慢了")
                    m.action_state.use_action(29515, target_enemy.id)
                    #imgui.text("这一步正在执行LB")
                    vars.ninja_use_lb = False
                if any(status_id in me.status for status_id in debuff_status_ids) and me.status.has_status(status_id=3192) and gcd_remain_jinhua ==0:
                    #imgui.text("这一步正在执行净化")
                    m.action_state.use_action(29056)
                if me.status.has_status(status_id=3192):    #星遁天诛预备
                    #imgui.text("斩杀中")
                    m.action_state.use_action(29516, target_enemy.id) 
                    vars.ninja_use_lb = False            
    if vars.ninja_use_lb is True and vars.ninja_select_mode == 0:
        #imgui.text("这一步说明模式识别是正确的")
        target_enemy = select_closest_enemy_with_real_hp(m)
        #imgui.text("这一步说明选择器是正确的")
        if target_enemy :
            #imgui.text("这一步说明已经找到了符合的敌人")
            m.targets.current = target_enemy
            #imgui.text("这一步说明已经选择符合的敌人")
            real_hp = target_enemy.current_hp
            if m.limit_break_gauge.gauge == m.limit_break_gauge.gauge_one:
                #imgui.text("这一步说明你的LB槽慢了")
                m.action_state.use_action(29515, target_enemy.id)
                #imgui.text("这一步正在执行LB")
            if any(status_id in me.status for status_id in debuff_status_ids) and me.status.has_status(status_id=3192) and gcd_remain_jinhua ==0:
                #imgui.text("这一步正在执行净化")
                m.action_state.use_action(29056)
            if me.status.has_status(status_id=3192):    #星遁天诛预备
                #imgui.text("斩杀中")
                m.action_state.use_action(29516, target_enemy.id)           
def ninja_panel():
    交换显示 = ['自动斩模式', '手动斩模式']
    imgui.text("NinJa V2024.03.28 (多斩暂时不可用)")
    imgui.same_line()
    imgui.text(f'KO:{vars.ninja_now_counts}') 
    imgui.text(str(vars.ninja_select_mode))   
    _, vars.ninja_select_mode = imgui.combo("Mode", vars.ninja_select_mode, 交换显示, len(交换显示))
    
    #_, vars.jinhua_quanju_sa = imgui.checkbox('武士LB净化', vars.jinhua_quanju_sa )
    imgui.text(f'当前状态:{str(vars.ninja_use_lb)}')
    imgui.same_line()    
    if vars.ninja_select_mode == 0:
        if imgui.button("自动斩开关"):
            vars.ninja_use_lb = not vars.ninja_use_lb
        
    #_, vars.ninja_select_disten = imgui.slider_float(f"忍者LB距离 +{vars.ninja_select_disten}", vars.ninja_select_disten, 0, 2, "%.0f")