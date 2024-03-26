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
    if not selected or glm.distance(me_pos, selected.pos) > 20 + vars.actionrange: return None
    return selected
#忍者选择器
def select_closest_enemy_with_real_hp2222222222222(m: CombatMem) -> Optional[Actor]:    #忍者选择器  LB选人阶段
    global limit_break_gauge_gauge, limit_break_gauge_gauge_one
    me = m.me
    if not me : return None
    me_pos = me.pos

    inv_status_ids = {3039, 2413, 1302, 1301, 1420}

    def target_validator(a: Actor) -> bool:
        global id_name, result_list

        if not m.is_enemy(me, a): return False
        real_hp = a.current_hp
        if real_hp >= a.max_hp * 0.5: return False
        if me.current_hp <= me.max_hp * 0.1: return False

        has_select_target = False
        for status_id, param, remain, source_id in a.status:
            if status_id in inv_status_ids: return False
            if real_hp <= a.max_hp * 0.49 and real_hp >= a.max_hp * 0.1:
                has_select_target = True
        return has_select_target
    def target_validator_kkk(a: Actor) -> bool:
        global id_name, result_list

        if not m.is_enemy(me, a): return False
        real_hp = a.current_hp
        #if real_hp >= a.max_hp * 0.5: return False
        #if me.current_hp <= me.max_hp * 0.1: return False

        has_select_target = False
        for status_id, param, remain, source_id in a.status:
            if status_id in inv_status_ids: return False
            if real_hp <= a.max_hp * 0.47 and real_hp >= a.max_hp * 0.1:
                has_select_target = True
        return has_select_target    
    if vars.ninja_select_mode == 0:
        if me.status.has_status(status_id=3192):
            k = lambda a: glm.distance(me_pos, a.pos)
            it = (actor for actor in m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor)) #m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor))

            for actor in it:
                m.main.main.gui.add_line(me_pos, actor.pos, glm.vec4(1, 0, 0, .8), 5.0)             
            selected = min(it, key=k, default=None)
            if not selected or glm.distance(me_pos, selected.pos) > 20 + vars.actionrange: return None
            #if 忍者无视距离的大刀 is True:
            #    if not selected or glm.distance(me_pos, selected.pos) > select_nin_lb_value: return None
            return selected
        if limit_break_gauge_gauge == limit_break_gauge_gauge_one:
            k = lambda a: glm.distance(me_pos, a.pos)

            # 筛选出距离自己20以内的所有敌人
            t = [actor for actor in m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor) and k(actor) <= 20 + vars.actionrange]

            if not t:
                return None
            #if limit_break_gauge_gauge == limit_break_gauge_gauge_one:
            for actor in t:
                m.main.main.gui.add_line(me_pos, actor.pos, glm.vec4(0, 1, 0, .8), 5.0)               
            
            vars.ninja_now_counts = len(t)
            if len(t) >= vars.ninja_select_counts:
                closest_enemy = min(t, key=k)
                return closest_enemy
            else:
                return None


    if vars.ninja_select_mode == 1:
        k = lambda a: glm.distance(me_pos, a.pos)
        it = (actor for actor in m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor)) #m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor))
        if limit_break_gauge_gauge == limit_break_gauge_gauge_one or me.status.has_status(status_id=3192):
            for actor in it:
                m.main.main.gui.add_line(me_pos, actor.pos, glm.vec4(1, 0, 0, .8), 5.0) 
        selected = min(it, key=k, default=None)
        if not selected or glm.distance(me_pos, selected.pos) > 20 + vars.actionrange: return None
        return selected        

    if vars.ninja_select_mode == 2:
        k = lambda a: glm.distance(me_pos, a.pos)
        it = (actor for actor in m.mem.actor_table.iter_actor_by_type(1) if target_validator_kkk(actor)) #m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor))
        if limit_break_gauge_gauge == limit_break_gauge_gauge_one or me.status.has_status(status_id=3192):
            for actor in it:
                m.main.main.gui.add_line(me_pos, actor.pos, glm.vec4(1, 0, 0, .8), 5.0) 
        selected = min(it, key=k, default=None)
        if not selected or glm.distance(me_pos, selected.pos) > 20 + vars.actionrange: return None
        return selected  


def ninja_pvp99999999(m, is_pvp=True):
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
    if vars.ninja_select_mode != 2:
        if gcd_remain > .5: return 8
    target_enemy = select_closest_enemy_with_real_hp(m)
    limit_break_gauge_gauge_one = m.limit_break_gauge.gauge_one
    limit_break_gauge_gauge = m.limit_break_gauge.gauge
    #if target_enemy and limit_break_gauge_gauge == limit_break_gauge_gauge_one and gcd_remain_jinhua == 0:m.action_state.use_action(29056)
   
    if target_enemy:
        m.targets.current = target_enemy
        real_hp = target_enemy.current_hp
        if real_hp < target_enemy.max_hp * 0.47 and m.limit_break_gauge.gauge == m.limit_break_gauge.gauge_one:
        #last_target_time = current_time
        #if m.limit_break_gauge.gauge == m.limit_break_gauge.gauge_one:
            m.action_state.use_action(29515, target_enemy.id)

        if any(status_id in me.status for status_id in debuff_status_ids) and me.status.has_status(status_id=3192) and gcd_remain_jinhua ==0:
            m.action_state.use_action(29056)
        if me.status.has_status(status_id=3192):    #星遁天诛预备
            imgui.text("斩杀中")
            m.action_state.use_action(29516, target_enemy.id) 
            return "遍历更新中"


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
    target_enemy = select_closest_enemy_with_real_hp(m)
    if gcd_remain > .5: return 8
    if target_enemy:
        m.targets.current = target_enemy
        real_hp = target_enemy.current_hp
        if real_hp < target_enemy.max_hp * 0.47 and m.limit_break_gauge.gauge == m.limit_break_gauge.gauge_one:
        #last_target_time = current_time
        #if m.limit_break_gauge.gauge == m.limit_break_gauge.gauge_one:
            m.action_state.use_action(29515, target_enemy.id)

        if any(status_id in me.status for status_id in debuff_status_ids) and me.status.has_status(status_id=3192) and gcd_remain_jinhua ==0:
            m.action_state.use_action(29056)
        if me.status.has_status(status_id=3192):    #星遁天诛预备
            imgui.text("斩杀中")
            m.action_state.use_action(29516, target_enemy.id)           
def ninja_panel():
    交换显示 = ['多条件符合自动斩', '视情况手动开启斩', '释放自我']
    imgui.text("NinJa V2")
    imgui.same_line()
    imgui.text(f'KO:{vars.ninja_now_counts}') 
    imgui.text(str(vars.ninja_select_mode))   
    _, vars.ninja_select_mode = imgui.combo("Mode", vars.ninja_select_mode, 交换显示, len(交换显示))
    #_, vars.jinhua_quanju_sa = imgui.checkbox('武士LB净化', vars.jinhua_quanju_sa )
    if vars.ninja_select_mode == 0:
        _, vars.ninja_select_counts = imgui.slider_float("多斩人数", vars.ninja_select_counts, 1, 10, "%.0f")
        
    #_, vars.ninja_select_disten = imgui.slider_float(f"忍者LB距离 +{vars.ninja_select_disten}", vars.ninja_select_disten, 0, 2, "%.0f")