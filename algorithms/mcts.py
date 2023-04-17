# -*- coding: utf-8 -*-
import numpy as np


# ============================================================================
#  TreeNode
# ----------------------------------------------------------------------------
#  蒙特卡洛樹的節點。
# ============================================================================
class TreeNode:
    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self, actions: list):
        self.score = 0                    # 獲勝次數
        self.visits = 0                   # 訪問次數
        self.actions = np.array(actions)  # 所有行動選項
        self.children = np.zeros(         # 子節點的列表
            len(actions), dtype=object)
        self.all_visit = False            # 是否每個子節點都走訪過

    # ------------------------------------------------------------------------
    #  選擇
    # ------------------------------------------------------------------------
    def select(self, c: float) -> object:
        # 根據UCB公式選擇子節點
        ucb_base = self.get_ucb_base()
        ucb_bonus = np.array(
            [c * np.sqrt(np.log(self.visits) / node.visits) for node in self.children],
            dtype=np.float16)
        index = np.argmax(ucb_base + ucb_bonus)
        # 返回選擇的行動
        return self.actions[index], self.children[index], index

    # ------------------------------------------------------------------------
    #  獲取UCB基礎值
    # ------------------------------------------------------------------------
    def get_ucb_base(self):
        scores = np.array([node.score for node in self.children])
        # 將重複分數取出
        scores, indices = np.unique(scores, return_inverse=True)
        length = len(scores)
        # 依照分數進行排序，並對數值做正規化
        bonus = np.array([1 - i / length for i in range(length, 0, -1)],
                         dtype=np.float16)
        return bonus[indices]


# ============================================================================
#  MCTS
# ----------------------------------------------------------------------------
#  使用蒙特卡洛樹搜索來做學習，適用於魔塔環境。
# ============================================================================
class MCTS:
    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self, actions: list, c: float = np.sqrt(2)):
        self.root = TreeNode(actions)  # 根節點
        self.visit_path = []           # 行動序列
        self.c = c                     # UCB加權係數

    # ------------------------------------------------------------------------
    #  選擇
    # ------------------------------------------------------------------------
    def select(self) -> list:
        node = self.root
        # 清除行動序列
        self.visit_path.clear()
        steps = []
        self.visit_path.append(node)
        # 從根節點開始，遞迴選擇子節點，直到達到葉子節點
        while node.all_visit:
            action, node, index = node.select(self.c)
            steps.append(action)
            self.visit_path.append(node)
        return steps

    # ------------------------------------------------------------------------
    #  選擇擴展節點
    # ------------------------------------------------------------------------
    def choose_expansion_node(self) -> object:
        node = self.visit_path[-1]
        # 探索沒走過的子節點
        unvisited = np.where(node.children == 0)[0]
        expand_index = unvisited[0]
        # 檢查所有子節點是否都走訪過
        if len(unvisited) == 1:
            node.all_visit = True
        return node.actions[expand_index], expand_index

    # ------------------------------------------------------------------------
    #  擴展
    # ------------------------------------------------------------------------
    def expand(self, expand_index: int, expand_actions: list):
        # 創建一個子節點
        expand_node = TreeNode(expand_actions)
        # 與父節點連結
        node = self.visit_path[-1]
        node.children[expand_index] = expand_node
        # 添加至行動序列
        self.visit_path.append(expand_node)

    # ------------------------------------------------------------------------
    #  反向傳播
    # ------------------------------------------------------------------------
    def backpropagate(self, score: int):
        # 用模擬的結果輸出，更新當前行動序列
        for node in self.visit_path[::-1]:
            node.visits += 1
            if score > node.score:
                node.score = score


# 測試
if __name__ == '__main__':
    import time
    from env.environment import Mota

    # 環境建立
    env = Mota()
    env.build_env('map_01')
    env.create_nodes()
    # 蒙特卡洛搜尋樹建立(UCT)
    _actions = env.get_feasible_actions()
    mcts = MCTS(_actions)
    # 訓練迴圈
    rounds = 10000
    highest_score = 0
    highest_round = 0
    startTime = time.perf_counter()
    for episode in range(1, rounds + 1):
        ending = 'continue'
        # 1.選擇
        actions_path = mcts.select()
        for _action in actions_path:
            ending = env.step(_action)
        # 2.擴展
        _actions = env.get_feasible_actions()  # 效能降低---
        if ending == 'continue' and _actions:
            expand_action, _expand_index = mcts.choose_expansion_node()
            ending = env.step(expand_action)
            _actions = env.get_feasible_actions()
            mcts.expand(_expand_index, _actions)
        # 3.模擬
        while ending == 'continue' and _actions:
            _action = np.random.choice(_actions)
            ending = env.step(_action)
            _actions = env.get_feasible_actions()
        # 4.反向傳播
        if ending == 'clear':
            _score = env.player.hp
        else:
            print(ending, len(env.observation))
            _score = 0
        mcts.backpropagate(_score)
        # 反饋本次成績
        if highest_score < _score:
            highest_score = _score
            highest_round = episode
        # 進度顯示
        print('round: %d    score: %d    max_score: %d    max_round: %d    time: %0.4f' %
              (episode, _score, highest_score, highest_round, time.perf_counter() - startTime))
        if episode % 100 == 0:
            print('action list:', [[env.n2p[n] for n in env.observation]])
        env.reset()
