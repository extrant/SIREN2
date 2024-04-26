from ..mem import CombatMem
from ..Vars import vars
from typing import Optional
from ff_draw.mem.actor import Actor
from nylib.utils.win32 import memory as ny_mem
import glm
import imgui



#学者毒先决条件
def select_du_enemy(m: CombatMem, select_status_id: int) -> Optional[Actor]:
    me = m.me
    if not me : return None
    me_pos = me.pos

    inv_status_ids = {1302, 3054}
    def target_validator(a: Actor) -> bool:
        if not m.is_enemy(me, a): return False
        real_hp = a.shield * a.max_hp / 100 + a.current_hp
        if real_hp < a.max_hp * 0.7: return False
        if me.current_hp <= me.max_hp * 0.05: return False
        has_select_status = False
        for status_id, param, remain, source_id in a.status:
            if status_id in inv_status_ids: return False  
            if select_status_id != status_id:
                has_select_status = True
        return has_select_status  

    k = lambda a: glm.distance(me_pos, a.pos)
    t = [actor for actor in m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor) and k(actor) <= 25]

    if not t:return None


    actor_counts = {}
    for actor in t:
        actor_counts[actor] = len([other_actor for other_actor in t if glm.distance(actor.pos, other_actor.pos) <= 15])

    vars.sch_enemy = len(x for x in actor_counts if actor_counts[x])
    filtered_actors = list(filter(lambda x: actor_counts[x] >= vars.select_most_du_value, actor_counts.keys()))
    if filtered_actors:
        target = max(actor_counts, key=actor_counts.get)
        return target
    else:
        return None




#学者扩毒后手
def select_du_kuosan_enemy(m: CombatMem, select_status_id: int) -> Optional[Actor]:  # 斩铁剑选择器
    me = m.me
    if not me : return None
    me_pos = me.pos  

    inv_status_ids = {1302, 3054}  
    def target_validator(a: Actor) -> bool:  # 目标验证器
        if not m.is_enemy(me, a): return False
        real_hp = a.shield * a.max_hp / 100 + a.current_hp
        if real_hp < a.max_hp * 0.3: return False
        if me.current_hp <= me.max_hp * 0.05: return False
        has_select_status = False
        for status_id, param, remain, source_id in a.status:  
            if status_id in inv_status_ids: return False 
            if status_id == select_status_id and source_id == me.id:  
                has_select_status = True
        return has_select_status 
    
    actor_temp = m.mem.actor_table.iter_actor_by_type(1)
    k = lambda a: glm.distance(me_pos, a.pos) 
    t = [actor for actor in actor_temp if target_validator(actor)  and k(actor) <= 30]
    t2 = [actor for actor in actor_temp]

    if not t: return None
    actor_counts = {}
    for actor in t:
        actor_counts[actor] = len([other_actor for other_actor in t2 if glm.distance(actor.pos, other_actor.pos) <= 15])

    vars.sch_enemy_a = len(x for x in actor_counts if actor_counts[x])
    filtered_actors = list(filter(lambda x: actor_counts[x] >= vars.select_most_du_value, actor_counts.keys()))
    if filtered_actors:
        target = max(actor_counts, key=actor_counts.get)
        return target
    else:
        return None

#学者扩毒后手再判断
def select_du_kuosan_enemy_double(m: CombatMem, select_status_id: int) -> Optional[Actor]:
    me = m.me
    if not me : return None
    me_pos = me.pos

    inv_status_ids = {1302, 3054}
    def target_validator(a: Actor) -> bool:
        if not m.is_enemy(me, a): return False
        real_hp = a.shield * a.max_hp / 100 + a.current_hp
        if real_hp < a.max_hp * 0.3: return False
        if me.current_hp <= me.max_hp * 0.05: return False
        has_select_status = False
        for status_id, param, remain, source_id in a.status:
            if status_id in inv_status_ids: return False
            if status_id == select_status_id and source_id == me.id:
                has_select_status = True
        return has_select_status

    actor_temp = m.mem.actor_table.iter_actor_by_type(1)
    k = lambda a: glm.distance(me_pos, a.pos)
    t = [actor for actor in actor_temp if target_validator(actor)  and k(actor) <= 30]
    t2 = [actor for actor in actor_temp]

    if not t:return None
    actor_counts = {}
    for actor in t:
        actor_counts[actor] = len([other_actor for other_actor in t2 if glm.distance(actor.pos, other_actor.pos) <= 15])

    vars.sch_enemy_b = len(x for x in actor_counts if actor_counts[x])
    filtered_actors = list(filter(lambda x: actor_counts[x] >= vars.select_most_du_value, actor_counts.keys()))
    if filtered_actors:
        target = max(actor_counts, key=actor_counts.get)
        return target
    else:
        return None
    


def sch_test(m, is_pvp=True):
    target = m.targets.current
    vars.now_job = 28
    if (me := m.me) is None: return 4
    if vars.is_mount != 0: return "坐骑状态中"    
    #if (target := m.targets.current) is None: return "无目标！"
    if not m.is_enemy(me, target): return 6
    if me.status.has_status(status_id=3054): return "防御状态中"
    if m.action_state.stack_has_action: return "动作执行中"
    jipao_remain = m.action_state.get_cool_down_by_action(29236).remain
    du_remain = m.action_state.get_cool_down_by_action(29233).remain
    kuosan_remain = m.action_state.get_cool_down_by_action(29234).remain
    debuff_status_ids = {1345, 3022, 1348, 1343, 1347}
    heal_jinhua = m.action_state.get_cool_down_by_action(29056).remain
    target_enemy = select_du_enemy(m, 1240)
    target_kuosan = select_du_kuosan_enemy(m, 3089)
    target_kuosan_double = select_du_kuosan_enemy_double(m, 3089)
    if du_remain == 0 and kuosan_remain < 15:
        if target_enemy:
            if me.status.has_status(status_id=3094) and du_remain == 0 and kuosan_remain < 15:
                m.targets.current = target_enemy
                m.action_state.use_action(29233, target_enemy.id)

            if not me.status.has_status(status_id=3094) and du_remain < 5:
                if jipao_remain == 0 and not m.limit_break_gauge.gauge == m.limit_break_gauge.gauge_one:m.action_state.use_action(29236)
                if jipao_remain > 0 and m.limit_break_gauge.gauge      == m.limit_break_gauge.gauge_one:m.use_action_pos(29237, me.pos)
                if jipao_remain == 0 and m.limit_break_gauge.gauge     == m.limit_break_gauge.gauge_one:m.action_state.use_action(29236)

    if du_remain > 0 and kuosan_remain < 15:
        if target_kuosan and kuosan_remain == 0:
            m.targets.current = target_kuosan
            m.action_state.use_action(29234, target_kuosan.id)
            #m.action_state.use_action(29234, target_kuosan.id)
        if target_kuosan_double and kuosan_remain < 15 and kuosan_remain > 0:
            m.targets.current = target_kuosan_double
            m.action_state.use_action(29234, target_kuosan_double.id)
    if any(status_id in me.status for status_id in debuff_status_ids) and heal_jinhua == 0:
        m.action_state.use_action(29056)
    if me.current_hp < me.max_hp * 0.5 and me.current_mp > me.max_mp * 0.25:
        m.action_state.use_action(29711)


def sch_panel():
    imgui.same_line()
    imgui.text("当前职业：苗疆毒妇")
    _, vars.select_most_du_value = imgui.slider_float("苗疆扩毒人数", vars.select_most_du_value, 1, 20, "%.0f")
    imgui.text("debug")
    imgui.text(f"起始上毒人数:{vars.sch_enemy}")
    imgui.text(f"起手扩毒人数:{vars.sch_enemy_a}")
    imgui.text(f"后手扩毒人数:{vars.sch_enemy_b}")