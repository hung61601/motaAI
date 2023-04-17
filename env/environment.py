# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from env import database as db
import collections
from PIL import Image


# ============================================================================
#  Node 節點
# ----------------------------------------------------------------------------
#  紀錄節點事件與狀態。
# ============================================================================
class Node:
    # ------------------------------------------------------------------------
    #  初始化[Python] *args 和**kwargs
    # ------------------------------------------------------------------------
    def __init__(self, kw: dict):
        self.links = []  # 與其他相鄰的節點
        self.class_ = kw['cls']  # 事件類別
        self.id = kw['id']  # 文字標籤
        self.activated = False  # 該事件是否被觸發過
        self.disabled = False  # 該事件是否被禁用

    # ------------------------------------------------------------------------
    #  觸發事件，在子類實作
    # ------------------------------------------------------------------------
    def activate(self):
        pass

    # ------------------------------------------------------------------------
    #  還原觸發事件，在子類實作
    # ------------------------------------------------------------------------
    def re_activate(self):
        pass


# ============================================================================
#  Player 玩家
# ----------------------------------------------------------------------------
#  作為活耀節點在拓樸圖形中移動。繼承Node
# ============================================================================
class Player(Node):
    # ------------------------------------------------------------------------
    #  設定初始狀態
    # ------------------------------------------------------------------------
    def reset(self, skw: dict):
        self.activated = True
        self.lv = skw['lv']
        self.maxhp = skw['maxhp']
        self.hp = skw['hp']
        self.atk = skw['atk']
        self.def_ = skw['def']
        self.mdef = skw['mdef']
        self.money = skw['money']
        self.exp = skw['exp']
        # 由於items對象是字典，必須使用copy複製一份新狀態
        self.items = skw['items'].copy()
        self.cum_damage = 0


# ============================================================================
#  Enemy 敵人
# ----------------------------------------------------------------------------
#  紀錄怪物的能力與計算傷害。繼承Node
# ============================================================================
class Enemy(Node):
    # ------------------------------------------------------------------------
    #  設定初始狀態
    # ------------------------------------------------------------------------
    def reset(self, skw: dict, new_id: str = None):
        if new_id:
            self.id = new_id
        self.hp = skw['hp']
        self.atk = skw['atk']
        self.def_ = skw['def']
        self.money = skw['money']
        self.exp = skw['exp']
        self.special = skw['special']
        self.skw = skw

    # ------------------------------------------------------------------------
    #  觸發事件
    # ------------------------------------------------------------------------
    def activate(self, player: Player) -> str:
        if self.activated:
            raise RuntimeError('This node has been activated')
        self.activated = True
        # 戰鬥計算
        p_damage = player.atk - self.def_
        if p_damage <= 0:
            ending = 'death'
            damage = 999999
        else:
            # 主角自帶先攻一次
            rounds = self.hp // p_damage - (self.hp % p_damage == 0)  # 該寫法取代math.ceil()
            e_damage = max(self.atk - player.def_, 0)
            damage = e_damage * rounds
            if self.special == 0:
                pass
            elif self.special == 1:  # 先攻屬性
                damage += e_damage
            elif self.special == 11:  # 吸血屬性
                damage += player.hp // self.skw['value']
            elif self.special == 22:  # 固傷屬性
                damage += self.skw['damage']
            # 魔防減傷
            damage -= player.mdef
            # 計算結局
            ending = 'continue' if player.hp > damage else 'death'
        # 傷害上限(生命不會被扣到0以下)
        if damage > player.hp:
            damage = player.hp
        elif damage < 0:
            damage = 0
        # 戰鬥處理
        player.hp -= damage
        player.cum_damage -= damage
        player.money += self.money
        player.exp += self.exp
        # 用於還原處理
        self.re_damage = damage
        return ending

    # ------------------------------------------------------------------------
    #  還原觸發事件
    # ------------------------------------------------------------------------
    def re_activate(self, player: Player):
        if self.activated:
            self.activated = False
            player.hp += self.re_damage
            player.cum_damage += self.re_damage
            player.money -= self.money
            player.exp -= self.exp
        else:
            raise RuntimeError('This node has not been activated')


# ============================================================================
#  Item 道具
# ----------------------------------------------------------------------------
#  紀錄道具的資訊。繼承Node
# ============================================================================
class Item(Node):
    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self, kw: dict, skw: dict):
        super().__init__(kw)
        self.effects = skw.copy()
        self.cls_ = self.effects.pop('cls')

    # ------------------------------------------------------------------------
    #  觸發事件
    # ------------------------------------------------------------------------
    def activate(self, player: Player) -> str:
        if self.activated:
            raise RuntimeError('This node has been activated')
        self.activated = True
        # 道具處理
        ending = 'continue'
        if self.cls_ == 'item':
            if self.id in player.items:
                player.items[self.id] += 1
            else:
                player.items[self.id] = 1
        elif self.cls_ == 'items':
            for k, v in self.effects.items():
                if k in player.items:
                    player.items[k] += v
                else:
                    player.items[k] = v
        else:
            for effect, value in self.effects.items():
                if effect == 'hp':
                    self.re_hp = min(value, player.maxhp - player.hp)  # 溢血
                    player.hp += self.re_hp
                elif effect == 'atk':
                    player.atk += value
                elif effect == 'def':
                    player.def_ += value
                elif effect == 'money':
                    player.money += value
                elif effect == 'lv':
                    player.lv += value
                elif effect == 'function':
                    self.re_function = []
                    for team in value:
                        value = eval(team['value'])
                        if team['name'] == 'player.hp':
                            # 使用function的hp不會受到溢血影響
                            self.re_function.append(value - player.hp)
                            player.hp = value
                        elif team['name'] == 'player.atk':
                            self.re_function.append(value - player.atk)
                            player.atk = value
                        elif team['name'] == 'player.def':
                            self.re_function.append(value - player.def_)
                            player.def_ = value
        return ending

    # ------------------------------------------------------------------------
    #  還原觸發事件
    # ------------------------------------------------------------------------
    def re_activate(self, player: Player):
        if self.activated:
            self.activated = False
            if self.cls_ == 'item':
                player.items[self.id] -= 1
            elif self.cls_ == 'items':
                for k, v in self.effects.items():
                    player.items[k] -= v
            else:
                for effect, value in self.effects.items():
                    if effect == 'hp':
                        player.hp -= self.re_hp
                    elif effect == 'atk':
                        player.atk -= value
                    elif effect == 'def':
                        player.def_ -= value
                    elif effect == 'money':
                        player.money -= value
                    elif effect == 'lv':
                        player.lv -= value
                    elif effect == 'function':
                        for team, val in zip(value, self.re_function):
                            if team['name'] == 'player.hp':
                                player.hp -= val
                            elif team['name'] == 'player.atk':
                                player.atk -= val
                            elif team['name'] == 'player.def':
                                player.def_ -= val
        else:
            raise RuntimeError('This node has not been activated')


# ============================================================================
#  NPC 人物
# ----------------------------------------------------------------------------
#  紀錄人物的資訊。繼承Node
# ============================================================================
class NPC(Node):
    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self, kw: dict, commands: list):
        super().__init__(kw)
        self.commands = commands

    # ------------------------------------------------------------------------
    #  觸發事件
    # ------------------------------------------------------------------------
    def activate(self, player: Player) -> str:
        if self.activated:
            raise RuntimeError('This node has been activated')
        self.activated = True
        ending = 'continue'
        for command in self.commands:
            # 條件句
            if command['type'] == 'if':
                if not eval(command['condition']):
                    ending = 'stop'
            # 增加數值
            elif command['type'] == 'addValue':
                if command['name'] == 'player.money':
                    player.money += command['value']
                elif command['name'] == 'player.hp':
                    player.hp += command['value']
                elif command['name'] == 'player.atk':
                    player.atk += command['value']
                elif command['name'] == 'player.def':
                    player.def_ += command['value']
                elif command['name'] == 'player.exp':
                    player.exp += command['value']
                elif command['name'] == 'player.lv':
                    player.lv += command['value']
            # 增加道具
            elif command['type'] == 'addItem':
                if command['name'] in player.items:
                    player.items[command['name']] += command['value']
                else:
                    player.items[command['name']] = command['value']
            # 可重複觸發
            elif command['type'] == 'not_activated':
                self.activated = False
        return ending

    # ------------------------------------------------------------------------
    #  還原觸發事件
    # ------------------------------------------------------------------------
    def re_activate(self, player: Player):
        self.activated = False
        for command in self.commands[::-1]:  # 反向迭代
            # 數值
            if command['type'] == 'addValue':
                if command['name'] == 'player.money':
                    player.money -= command['value']
                elif command['name'] == 'player.hp':
                    player.hp -= command['value']
                elif command['name'] == 'player.atk':
                    player.atk -= command['value']
                elif command['name'] == 'player.def':
                    player.def_ -= command['value']
                elif command['name'] == 'player.exp':
                    player.exp -= command['value']
                elif command['name'] == 'player.lv':
                    player.lv -= command['value']
            # 道具
            elif command['type'] == 'addItem':
                player.items[command['name']] -= command['value']


# ============================================================================
#  Terrain 地形
# ----------------------------------------------------------------------------
#  紀錄地形的資訊。繼承Node
# ============================================================================
class Terrain(Node):
    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self, kw: dict):
        super().__init__(kw)
        self.no_pass = kw.get('noPass', True)

    # ------------------------------------------------------------------------
    #  觸發事件
    # ------------------------------------------------------------------------
    def activate(self, player: Player) -> str:
        if self.activated:
            raise RuntimeError('This node has been activated')
        self.activated = True
        # 地形處理
        if self.no_pass:
            ending = 'stop'
            self.re_num = 0
            if self.id == 'yellowDoor':
                player.items['yellowKey'] -= 1
                self.re_num = 1
                if player.items['yellowKey'] >= 0:
                    ending = 'continue'
            elif self.id == 'blueDoor':
                player.items['blueKey'] -= 1
                self.re_num = 1
                if player.items['blueKey'] >= 0:
                    ending = 'continue'
            elif self.id == 'redDoor':
                player.items['redKey'] -= 1
                self.re_num = 1
                if player.items['redKey'] >= 0:
                    ending = 'continue'
            elif self.id == 'greenDoor' and 'greenKey' in player.items:
                player.items['greenKey'] -= 1
                self.re_num = 1
                if player.items['greenKey'] >= 0:
                    ending = 'continue'
        else:  # 樓梯之類的地形
            ending = 'continue'
        return ending

    # ------------------------------------------------------------------------
    #  還原觸發事件
    # ------------------------------------------------------------------------
    def re_activate(self, player: Player):
        if self.activated:
            self.activated = False
            if self.no_pass:
                if self.id == 'yellowDoor':
                    player.items['yellowKey'] += self.re_num
                elif self.id == 'blueDoor':
                    player.items['blueKey'] += self.re_num
                elif self.id == 'redDoor':
                    player.items['redKey'] += self.re_num
                elif self.id == 'greenDoor' and 'greenKey' in player.items:
                    player.items['greenKey'] += self.re_num
        else:
            raise RuntimeError('This node has not been activated')


# ============================================================================
#  EndFlag 結束標誌
# ----------------------------------------------------------------------------
#  終點節點的處理。繼承Node
# ============================================================================
class EndFlag(Node):
    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self, kw: dict):
        super().__init__(kw)

    # ------------------------------------------------------------------------
    #  觸發事件
    # ------------------------------------------------------------------------
    def activate(self, player: Player) -> str:
        if self.activated:
            raise RuntimeError('This node has been activated')
        self.activated = True
        ending = 'clear'
        return ending

    # ------------------------------------------------------------------------
    #  還原觸發事件
    # ------------------------------------------------------------------------
    def re_activate(self, player: Player):
        if self.activated:
            self.activated = False
        else:
            raise RuntimeError('This node has not been activated')


# ============================================================================
#  Mota 魔塔  V2.0    by Hung1    2020/6/22
# ----------------------------------------------------------------------------
#  模擬魔塔環境，當給予動作時做出回饋。
#  事件節點定義：比如怪物、道具、商店等觸發後會改變主角狀態，狀態數值發生變化。
#  V1.1
#  可以支援24層魔塔，增加npc的類別，優化一些函式
#  V1.2    2020/04/24
#  將reward變為可選參數回傳
#  V2.0    2020/06/22
#  調整部分方法的參數與回傳值，可使用於Mota AI V0.4版本
# ============================================================================
class Mota:
    # ------------------------------------------------------------------------
    #  常數
    # ------------------------------------------------------------------------
    # 主角狀態的獎勵值比率(生命、攻擊、防禦、魔防、金幣、經驗、黃鑰匙、藍鑰匙、紅鑰匙)
    REWARD_RATE = np.array([1, 200, 200, 100, 20, 20, 10, 10, 10])

    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self):
        self.env_data = None  # 環境數據庫
        self.env_name = ''  # 環境名稱
        self.n2p = collections.OrderedDict()  # 以有序的方式儲存每個節點物件 (node_to_pos)
        self.p2n = {}  # 座標到節點的對應字典 (pos_to_node)
        self.observation = []  # 當前state的觀測值
        self.player = None  # 儲存玩家對象
        self.re_update_enemies = {}  # 用於還原怪物數據
        self.tile_path = 'pictures/baseTile.png'

    # ------------------------------------------------------------------------
    #  獲取數據庫所有檔案名稱
    # ------------------------------------------------------------------------
    @staticmethod
    def get_file_name() -> list:
        return db.FILE_NAME

    # ------------------------------------------------------------------------
    #  獲取主角狀態的數組
    # ------------------------------------------------------------------------
    def get_player_state(self) -> np.array:
        p = self.player
        return np.array([p.hp, p.atk, p.def_, p.mdef, p.money, p.exp,
                         p.items['yellowKey'], p.items['blueKey'], p.items['redKey']])

    # ------------------------------------------------------------------------
    #  獲取地圖層數
    # ------------------------------------------------------------------------
    def get_layer(self) -> int:
        return self.env_data['floors']['layer']

    # ------------------------------------------------------------------------
    #  主角已行動步數
    # ------------------------------------------------------------------------
    def get_step_count(self) -> int:
        return len(self.observation) - 1

    # ------------------------------------------------------------------------
    #  環境是否為初始狀態
    # ------------------------------------------------------------------------
    def is_initial(self) -> bool:
        return len(self.observation) == 1

    # ------------------------------------------------------------------------
    #  返回地圖的每個座標的迭代器
    # ------------------------------------------------------------------------
    def pos_iter(self) -> iter:
        floors = self.env_data['floors']
        for z in range(0, floors['layer']):
            for y in range(0, floors['height']):
                for x in range(0, floors['width']):
                    yield z, y, x

    # ------------------------------------------------------------------------
    #  建立環境
    # ------------------------------------------------------------------------
    def build_env(self, env_name: str) -> int:
        self.env_name = env_name
        self.env_data = db.load_data(env_name)  # 載入數據庫
        map_ = self.env_data['floors']['map']
        disable = self.env_data['floors']['disable']
        maps = self.env_data['maps']
        enemies = self.env_data['enemies']
        items = self.env_data['items']
        npcs = self.env_data['npcs']
        for z, y, x in self.pos_iter():
            pos = (z, y, x)
            kw = maps[map_[z][y][x]]
            if kw['cls'] != 'except':  # 非事件id不須建立成節點物件
                if kw['cls'] == 'enemies':  # 敵人類別
                    node = Enemy(kw)
                    node.reset(enemies[kw['id']])
                elif kw['cls'] == 'items':  # 道具類別
                    node = Item(kw, items[kw['id']])
                elif kw['cls'] == 'terrains':  # 地形類別
                    node = Terrain(kw)
                elif kw['cls'] == 'npcs':  # 人物類別
                    if pos not in npcs:
                        node = NPC(kw, [])
                    elif npcs[pos] == 'shop':
                        node = NPC(kw, [])
                        i = 1
                        # 4 維座標
                        while pos + (i,) in npcs:
                            snode = NPC(kw, npcs[pos + (i,)])
                            self.n2p[snode] = pos + (i,)
                            self.p2n[pos + (i,)] = snode
                            i += 1
                    else:
                        node = NPC(kw, npcs[pos])
                elif kw['id'] == 'player':  # 玩家類別
                    node = Player(kw)
                    node.reset(self.env_data['player'])
                    self.player = node
                elif kw['id'] == 'end':  # 結束標誌類別
                    node = EndFlag(kw)
                else:
                    raise TypeError(f'When creating a node, the {kw["cls"]} class is not defined')
                # 事件禁用(無法觸發)
                if pos in disable:
                    node.disabled = True
                self.n2p[node] = pos
                self.p2n[pos] = node
        # 設置觀測值
        self.observation.append(self.player)
        return len(self.n2p)

    # ------------------------------------------------------------------------
    #  繪製地圖
    # ------------------------------------------------------------------------
    def draw_map(self, picture_name: str) -> int:
        layer = self.env_data['floors']['layer']
        width = self.env_data['floors']['width']
        height = self.env_data['floors']['height']
        map_ = self.env_data['floors']['map']
        maps = self.env_data['maps']
        tile = self.env_data['icons']
        tile_image = Image.open(self.tile_path)
        # 地板平鋪式背景
        bg = Image.new('RGBA', (width * 32, height * 32))
        bf = tile_image.crop((0, 0, 32, 32))
        for i in range(0, width * 32, 32):
            for j in range(0, height * 32, 32):
                bg.paste(bf, (i, j))
        # 依序畫出每一樓層
        for f in range(0, layer):
            fin = bg.copy()
            for i in range(0, width):
                for j in range(0, height):
                    # 獲取圖塊
                    n = map_[f][j][i]
                    if n == 0:
                        continue
                    tile_id = tile[maps[n]['id']]
                    local = (tile_id % 16 * 32, tile_id // 16 * 32, tile_id % 16 * 32 + 32, tile_id // 16 * 32 + 32)
                    et = tile_image.crop(local)
                    # 分離通道並進行透明度拼貼
                    r, g, b, a = et.split()
                    fin.paste(et, (i * 32, j * 32), mask=a)
            fin.save(picture_name + str(f) + '.png')
        return layer

    # ------------------------------------------------------------------------
    #  節點建圖
    # ------------------------------------------------------------------------
    def create_nodes(self) -> int:
        width = self.env_data['floors']['width']
        height = self.env_data['floors']['height']
        map_ = self.env_data['floors']['map']
        change_floor = self.env_data['floors']['changeFloor']
        npcs = self.env_data['npcs']
        direction = [(0, 0, 1), (0, 1, 0), (0, 0, -1), (0, -1, 0)]  # 四個方向，右下左上
        count = 0
        for node in self.n2p:
            # 以BFS方式來尋找相鄰的節點
            q = collections.deque()  # 高效雙端佇列，時間複雜度O(1)
            node_pos = self.n2p[node]
            # 如果是商店，則鏈結交易選項
            if npcs.get(node_pos) == 'shop':
                i = 1
                while node_pos + (i,) in self.p2n:
                    node.links.append(self.p2n[node_pos + (i,)])
                    count += 1
                    i += 1
            # 如果是傳送點，則從傳送位置開始搜尋
            if node_pos in change_floor:
                node_pos = change_floor[node_pos]
            q.append(node_pos)
            visited = {node_pos}  # 走訪過的地板
            while q:
                search_pos = q.popleft()
                # 尋找周圍有路是否可以走
                for d in direction:
                    pos = tuple(map(lambda x, y: x + y, search_pos, d))
                    # 如果已走訪過地點 (過濾最多)
                    if pos in visited:
                        continue
                    # 如果不是事件節點 (判斷最快)
                    elif pos not in self.p2n:
                        # 如果在地圖範圍內
                        if 0 <= pos[1] < height and 0 <= pos[2] < width:
                            # 如果是普通地板 (判斷最慢)
                            if map_[pos[0]][pos[1]][pos[2]] == 0:
                                q.append(pos)
                        visited.add(pos)
                    # 與該事件節點建立鏈結
                    else:
                        node.links.append(self.p2n[pos])
                        visited.add(pos)
                        count += 1
        return count

    # ------------------------------------------------------------------------
    #  獲取樓層的所有事件位置
    # ------------------------------------------------------------------------
    def get_floor_pos(self, floor: int) -> list:
        pos_list = [pos for pos in self.p2n if pos[0] == floor]
        return pos_list

    # ------------------------------------------------------------------------
    #  獲得樓層的所有事件數據
    # ------------------------------------------------------------------------
    def get_floor_data(self, floor: int, id_class: chr) -> list:
        if id_class == 'enemies' or id_class == 'items':
            if id_class == 'enemies':
                columns = ['id', 'hp', 'atk', 'def', 'money', 'exp', 'special', 'damage', 'value']
            else:
                columns = ['id', 'hp', 'atk', 'def', 'money', 'exp', 'yellowKey', 'blueKey', 'redKey', 'function']
            map_ = self.env_data['floors']['map'][floor]
            maps = self.env_data['maps']
            target = self.env_data[id_class]
            # 取樓層中不重複ID
            show_num = {i for li in map_ for i in li}
            # 選擇符合類別的事件
            show_num = sorted([k for k in show_num if maps[k]['cls'] == id_class])
            show_list = [{**maps[k], **target[maps[k]['id']]} for k in show_num]
            data = []
            for d in show_list:
                row = []
                for c in columns:
                    row.append(str(d.get(c, '')))
                data.append(row)
        elif id_class == 'npcs' or id_class == 'afterEvent':
            if id_class == 'npcs':
                target = self.env_data[id_class]
            else:
                target = self.env_data['floors'][id_class]
            data = []
            for k, v in target.items():
                if k[0] == floor:
                    if isinstance(v, list):
                        for order, command in enumerate(v, 1):
                            data.append([str(k), str(order), str(command)])
                    else:
                        data.append([str(k), '', str(v)])
        else:
            raise ValueError('No id_class name found.')
        return data

    # ------------------------------------------------------------------------
    #  重置環境
    # ------------------------------------------------------------------------
    def reset(self):
        disable = self.env_data['floors']['disable']
        self.observation.clear()
        for node, pos in self.n2p.items():
            node.activated = False
            if pos in disable:
                node.disabled = True
            if pos in self.re_update_enemies:  # 怪物數據重置
                re_id = self.re_update_enemies[pos]
                node.reset(self.env_data['enemies'][re_id], re_id)
        self.re_update_enemies.clear()
        self.player.reset(self.env_data['player'])  # 這行必須放在上面兩行之下，否則activated會被設為False
        self.observation.append(self.player)

    # ------------------------------------------------------------------------
    #  輸入行動，回饋狀態
    # ------------------------------------------------------------------------
    def step(self, action: Node, return_reward: bool = False) -> (str, int):
        # 觸發事件處理
        reward = 0
        if return_reward:
            before = self.get_player_state()
            ending = action.activate(self.player)
            # 計算獎勵值
            if ending == 'stop':
                reward = -999999
            else:
                after = self.get_player_state()
                reward = np.sum((after - before) * Mota.REWARD_RATE)
        else:
            ending = action.activate(self.player)

        # 事件後處理(全局處理)
        if self.n2p[action] in self.env_data['floors']['afterEvent']:
            for command in self.env_data['floors']['afterEvent'][self.n2p[action]]:
                if command['type'] == 'open':
                    self.p2n[command['loc']].activated = True
                elif command['type'] == 'enable':
                    self.p2n[command['loc']].disabled = False
                elif command['type'] == 'update_enemies':
                    enemy_id = command.copy()
                    enemy_id.pop('type')
                    for node in self.n2p:
                        if node.id in enemy_id:
                            # 紀錄最原始的怪物id
                            if self.n2p[node] not in self.re_update_enemies:
                                self.re_update_enemies[self.n2p[node]] = node.id
                            new_id = enemy_id[node.id]
                            node.reset(self.env_data['enemies'][new_id], new_id)
        # 更新觀測值
        self.observation.append(action)
        # 回傳值
        if return_reward:
            return ending, reward
        else:
            return ending

    # ------------------------------------------------------------------------
    #  退回行動
    # ------------------------------------------------------------------------
    def back_step(self, times: int):
        if times <= 0:
            return
        for action in self.observation[:-times - 1:-1]:  # 反向迭代，該方法比reversed()還快
            # 事件後處理(全局處理)
            if self.n2p[action] in self.env_data['floors']['afterEvent']:
                for command in self.env_data['floors']['afterEvent'][self.n2p[action]][::-1]:
                    if command['type'] == 'open':
                        self.p2n[command['loc']].activated = False
                    elif command['type'] == 'enable':
                        self.p2n[command['loc']].disabled = True
                    elif command['type'] == 'update_enemies':
                        enemy_id = {v: k for k, v in command.items() if k != 'type'}
                        for node in self.n2p:
                            if node.id in enemy_id:
                                new_id = enemy_id[node.id]
                                node.reset(self.env_data['enemies'][new_id], new_id)
            # 觸發事件處理
            action.re_activate(self.player)
        # 更新觀測值
        self.observation = self.observation[:-times]  # 利用切片的方式節省迭代pop花費的時間

    # ------------------------------------------------------------------------
    #  獲取所有可選擇的行動
    # ------------------------------------------------------------------------
    def get_actions(self) -> list:
        visited = set()  # 已經參訪過的節點
        q = collections.deque()  # 待搜索的節點
        actions = []  # 行動列表
        # 判斷目前位置節點是否可選擇
        node = self.observation[-1]
        if not node.activated:
            actions.append(node)
        # 添加目前位置
        visited.add(node)
        q.append(node)
        while q:
            node = q.pop()
            for _node in node.links:
                # 如果事件節點未觸發但已參訪則放入待搜索
                # 如果事件節點未觸發且未參訪則放入行動列表
                if _node not in visited:
                    visited.add(_node)
                    if _node.activated:
                        q.append(_node)
                    elif not _node.disabled:
                        actions.append(_node)
        return actions

    # ------------------------------------------------------------------------
    #  獲取所有可行的行動(不含死亡和卡住)
    #  return_reward: 回傳獎勵值，默認為False
    # ------------------------------------------------------------------------
    def get_feasible_actions(self, return_reward: bool = False) -> list:
        exclude = {'death', 'stop'}
        new_actions = []
        if return_reward:
            new_rewards = []
            for action in self.get_actions():
                ending, reward = self.step(action, return_reward=True)
                if ending not in exclude:
                    new_actions.append(action)
                    new_rewards.append(reward)
                self.back_step(1)
            return new_actions, new_rewards
        else:
            for action in self.get_actions():
                ending = self.step(action)
                if ending not in exclude:
                    new_actions.append(action)
                self.back_step(1)
            return new_actions

    # ------------------------------------------------------------------------
    #  轉換通關路線(行動物件序列)變為行動索引
    #  請注意先reset()再調用該方法。
    # ------------------------------------------------------------------------
    def convert_action_index(self, observation: list) -> list:
        path = []
        for action in observation[len(self.observation):]:
            path.append(self.get_actions().index(action))
            self.step(action)
        # 重置環境
        self.reset()
        return path


# 測試
if __name__ == '__main__':
    mota = Mota()
    print('節點數：', mota.build_env('24層魔塔 (html5)'))
    print('連結數：', mota.create_nodes())
    # 使用者操作行動
    print('★ =========歡迎使用文字版魔塔環境========= ★')
    index = ['hp', 'atk', 'def', 'money', 'exp', 'yellowKey', 'blueKey', 'redKey']
    playerDf = pd.DataFrame([0] * len(index), index=index, columns=['value'])
    choose_index_list = []
    p_ = mota.player
    ending_ = 'start'
    while ending_ != 'clear':
        print('主角狀態：')
        playerDf.value = [p_.hp, p_.atk, p_.def_, p_.money, p_.exp,
                          p_.items['yellowKey'], p_.items['blueKey'], p_.items['redKey']]
        print(playerDf.T)
        print('已前進步數：', len(mota.observation) - 1)
        print('全部選擇數：', len(mota.get_actions()))
        actions_ = mota.get_feasible_actions()
        print('可行選擇數：', len(actions_))
        print('可選擇節點資訊：')
        data_ = [[mota.n2p[action], action.class_, action.id] for action in actions_]
        print(pd.DataFrame(data_, columns=['loc', 'class', 'id']))
        index = int(input('請輸入行動index(-1退回/-2結束)：'))
        if index == -1:
            choose_index_list.pop()
            mota.back_step(1)
        elif index == -2:
            break
        else:
            choose_index_list.append(index)
            ending_ = mota.step(actions_[index])
    else:
        print('你的通關分數為(生命)：', mota.player.hp)
        print('恭喜通關！你的總扣血量為：', p_.cum_damage)
    print('已行動選項順序：', choose_index_list)
