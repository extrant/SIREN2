from ..mem import CombatMem
from ..Vars import vars
from typing import Optional
from ff_draw.mem.actor import Actor
from nylib.utils.win32 import memory as ny_mem
import glm
import imgui

result_list = []
id_name = "无"

用过净化了 = False

def sam_command(_, args):
    if len(args) < 1: return
    if args[0] == "AUTO" and args[1] == "On":
        vars.sam_able = True                            
    if args[0] == "AUTO" and args[1] == "Off":
        vars.sam_able = False  
  


#武士最近
def select_closest_enemy_with_status(m: CombatMem, select_status_id: int) -> Optional[Actor]:  # 斩铁剑选择器
    me = m.me
    if not me : return None
    me_pos = me.pos  # 对位置进行缓存，每一次调用actor.pos都会进行一次内存读取，因此一帧内的逻辑中尽量缓存重复使用的数据

    inv_status_ids = {3039, 2413, 1302, 1301, 1420}  # 使用set查找“是否包括数据”比list更快
    def target_validator(a: Actor) -> bool:  # 目标验证器
        global id_name, result_list
        id_name = a.name
        if id_name not in result_list:  # 检查结果是否已经存在于列表中
            result_list.append(id_name)
        if not m.is_enemy(me, a): return False  # 如果不是敌人，直接返回False
        real_hp = a.shield * a.max_hp / 100 + a.current_hp  # 先计算护盾，因为内存读取量比遍历status小
        if real_hp >= a.max_hp: return False
        if me.current_hp <= me.max_hp * 0.1: return False
        has_select_status = False  # 这里要做两件事，一是判断是否有自己施加的斩铁剑的状态，二是判断有没有无敌状态
        for status_id, param, remain, source_id in a.status:  # 遍历status
            if status_id in inv_status_ids: return False  # 如果status_id在无敌状态列表中，直接返回False
            if status_id == select_status_id and source_id == me.id:  # 如果status_id是斩铁剑，且来源是自己，就设置has_select_status为True；不直接返回True是为了遍历完整个status确定没有无敌
                has_select_status = True
        return has_select_status  # 如果遍历完整个status，has_select_status还是False，就返回False（如果存在无敌就在上面 返回false）
    #imgui.text("T1")
    it = (actor for actor in m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor) and glm.distance(me_pos, actor.pos) <= 20 + vars.actionrange) #m.mem.actor_table.iter_actor_by_type(1) if target_validator(actor))
    k = lambda a: glm.distance(me_pos, a.pos)  # 用于排序的key，这里是计算actor和自己的距离
    selected = min(it, key=k, default=None)  # 从迭代器中选出一个距离最近的actor，如果迭代器为空，就返回None

    if not selected or glm.distance(me_pos, selected.pos) > 20 + vars.actionrange: return None  # 如果没有选中，或者选中的actor距离自己太远，就返回None
    return selected
    
def select_closest_enemy_with_status_most(m: CombatMem, select_status_id: int) -> Optional[Actor]:  # 斩铁剑选择器
    me = m.me
    if not me : return None
    me_pos = me.pos  # 对位置进行缓存，每一次调用actor.pos都会进行一次内存读取，因此一帧内的逻辑中尽量缓存重复使用的数据
    valid_targets = []
    inv_status_ids = {3039, 2413, 1302, 1301, 1420}  # 使用set查找“是否包括数据”比list更快
    def target_validator(a: Actor) -> bool:  # 目标验证器
        global id_name, result_list
        id_name = a.name
        if id_name not in result_list:  # 检查结果是否已经存在于列表中
            result_list.append(id_name)
        if not m.is_enemy(me, a): return False  # 如果不是敌人，直接返回False
        real_hp = a.shield * a.max_hp / 100 + a.current_hp  # 先计算护盾，因为内存读取量比遍历status小
        if real_hp >= a.max_hp: return False
        if me.current_hp <= me.max_hp * 0.1: return False
        has_select_status = False  # 这里要做两件事，一是判断是否有自己施加的斩铁剑的状态，二是判断有没有无敌状态
        for status_id, param, remain, source_id in a.status:  # 遍历status
            if status_id in inv_status_ids: return False  # 如果status_id在无敌状态列表中，直接返回False
            if status_id == select_status_id and source_id == me.id:  # 如果status_id是斩铁剑，且来源是自己，就设置has_select_status为True；不直接返回True是为了遍历完整个status确定没有无敌
                has_select_status = True
        return has_select_status  # 如果遍历完整个status，has_select_status还是False，就返回False（如果存在无敌就在上面 返回false）
    #imgui.text("T2")
    # 筛选在指定范围内的符合条件的敌人
    for actor in m.mem.actor_table.iter_actor_by_type(1):
        if target_validator(actor) and glm.distance(me_pos, actor.pos) <= 20 + vars.actionrange:
            valid_targets.append(actor)

    #vars.sam_select_counts = 0
    best_target = None
    for target in valid_targets:
        # 对每个目标计算以其为中心，半径为aoe_radius的圆内有多少符合条件的敌人
        count = sum(1 for other in valid_targets if glm.distance(target.pos, other.pos) <= 5)
        if count >= vars.sam_select_counts:
            #max_target_count = count
            best_target = target

    return best_target  


def samurai_pvp(m, is_pvp=True):
    #actor_table = m.mem.actor_table
    target = m.targets.current
    global 用过净化了
    vars.now_job = 34
    if (me := m.me) is None: return 4
    vars.sam_me = me.id
    #if (target := m.targets.current) is None: return "无目标！"
    if vars.is_mount != 0: return "坐骑状态中"    
    if not m.is_enemy(me, target): return 6
    #if m.action_state.stack_has_action: return "动作执行中"
    gcd_remain = m.action_state.get_cool_down_by_action(29537).remain
    if gcd_remain > .5: return 8
    debuff_status_ids = {1345, 3022, 1348, 1343, 1347}
    if vars.jinhua_quanju_sa is False:gcd_remain_jinhua = 1
    if vars.jinhua_quanju_sa is True:gcd_remain_jinhua = m.action_state.get_cool_down_by_action(29056).remain
    gcd_remain_mjing = m.action_state.get_cool_down_by_action(29536).remain

    if vars.use_mjing is True and gcd_remain_mjing == 0:
        if me.status.has_status(status_id=1240): 
            m.action_state.use_action(29536) 
            m.main.main.gui.add_3d_shape(
                0x10000,
                #(0x10000,
                glm.translate(me.pos),
                point_color=glm.vec4(0, 1, 0, 0.3),
                line_color=glm.vec4(0, 1, 0, 0.3),
                surface_color=glm.vec4(0, 1, 0, 0.3),
                line_width=float(10.0),
            )
    if m.limit_break_gauge.gauge != m.limit_break_gauge.gauge_one:用过净化了 = False
    if vars.san_sanlianbing is False:vars.sam_used_bing = False
    if vars.sam_used_bing is True and vars.san_sanlianbing is True:
        m.action_state.use_action(29523)
        imgui.text('操作你')
    if vars.sam_select_mode == 0:target_enemy = select_closest_enemy_with_status(m, 3202)
    if vars.sam_select_mode == 1:target_enemy = select_closest_enemy_with_status_most(m, 3202)
    if target_enemy:
        m.targets.current = target_enemy  #选择目标
        if m.limit_break_gauge.gauge == m.limit_break_gauge.gauge_one: 
            start = target_enemy.pos
            end = me.pos
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
            if 用过净化了 is True:
                m.action_state.use_action(29537, target_enemy.id)
                #用过净化了 = False              
            if any(status_id in me.status for status_id in debuff_status_ids) and gcd_remain_jinhua == 0:
                m.action_state.use_action(29056)  
                if 用过净化了 is True:
                    m.action_state.use_action(29537, target_enemy.id)
                    #用过净化了 = False                        
            else:
                m.action_state.use_action(29537, target_enemy.id)
                用过净化了 = False
            return "斩！"
        else:
            return "极限槽未满"

    else:
        return "非匹配条件目标"
        pass


def sam_panel():
    imgui.same_line()
    imgui.text("Samurai V2")
    交换显示 = ['空游无所依', '多斩']
    _, vars.sam_select_mode = imgui.combo("Mode", vars.sam_select_mode, 交换显示, len(交换显示))
    _, vars.jinhua_quanju_sa = imgui.checkbox('武士LB净化', vars.jinhua_quanju_sa )
    imgui.same_line()
    _, vars.use_mjing = imgui.checkbox('武士地天自动明镜', vars.use_mjing )
    _, vars.san_sanlianbing = imgui.checkbox('早天自动强制冰雪', vars.san_sanlianbing )
    imgui.text(f'当前状态:{str(vars.sam_able)}')
    imgui.same_line()
    if imgui.button("自动斩开关"):
        vars.sam_able = not vars.sam_able
    if vars.sam_select_mode == 1:
        _, vars.sam_select_counts = imgui.slider_float("多斩人数", vars.sam_select_counts, 0, 10, "%.0f")
    