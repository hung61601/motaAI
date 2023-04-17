# -*- coding: utf-8 -*-
import numpy as np


# ============================================================================
#  Node
# ----------------------------------------------------------------------------
#  節點(集)
# ============================================================================
class Node:
    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self):
        self.children = set()         # 子節點的列表
        self.child_scores = {}        # 子節點的期望分數
        self.child_visits = {}        # 子節點的訪問次數

    # ------------------------------------------------------------------------
    #  ★獲取權重係數，這裡可以自己訂立規則！
    # ------------------------------------------------------------------------
    def get_weights_coefficient(self, visits):
        n = np.min(visits)
        if n <= 1:
            return 1
        else:
            return np.log2(n)

    # ------------------------------------------------------------------------
    #  獲取分數和走訪次數
    # ------------------------------------------------------------------------
    def get_scores_and_visits(self, actions):
        scores = []
        visits = []
        for action in actions:
            if action not in self.children:
                self.add_action(action)
            scores.append(self.child_scores[action])
            visits.append(self.child_visits[action])
        return scores, visits

    # ------------------------------------------------------------------------
    #  添加行動
    # ------------------------------------------------------------------------
    def add_action(self, action):
        self.children.add(action)
        self.child_scores[action] = 0
        self.child_visits[action] = 0

    # ------------------------------------------------------------------------
    #  選擇
    # ------------------------------------------------------------------------
    def select(self, actions):
        scores, visits = self.get_scores_and_visits(actions)
        # 權重參數c
        c = self.get_weights_coefficient(visits)
        # 權重
        _, indices = np.unique(scores, return_inverse=True)
        weights = np.power(c, indices)
        # 將權重轉成機率
        probability = weights / np.sum(weights)
        # 依機率選擇行動
        index = np.random.choice(len(weights), p=probability)
        return actions[index]

    # ------------------------------------------------------------------------
    #  UCB權重選擇
    # ------------------------------------------------------------------------
    def ucb_select(self, actions, c=np.sqrt(2)):
        scores, visits = self.get_scores_and_visits(actions)
        ucb_bonus_list = []
        # UCB基礎值
        scores, indices = np.unique(scores, return_inverse=True)
        length = len(scores)
        ucb_base = np.array([1 - i / length for i in range(length, 0, -1)],
                            dtype=np.float16)
        ucb_base = ucb_base[indices]
        # UCB追加值
        sum_visit = sum(visits)
        if sum_visit <= 0:
            sum_visit = 1  # 最低探索次數為1
        for visit in visits:
            if visit <= 0:
                visit = 1
            ucb_bonus_list.append(c * np.sqrt(np.log(sum_visit) / visit))
        ucb_bonus = np.array(ucb_bonus_list, dtype=np.float16)
        # 根據UCB公式選擇行動
        index = np.argmax(ucb_base + ucb_bonus)
        return actions[index]

    # ------------------------------------------------------------------------
    #  最高分數選擇
    # ------------------------------------------------------------------------
    def max_select(self, actions):
        scores, _ = self.get_scores_and_visits(actions)
        x = np.max(scores)
        index = np.random.choice(np.where(scores == x)[0])
        return actions[index]

    # ------------------------------------------------------------------------
    #  更新，r=學習率
    # ------------------------------------------------------------------------
    def update(self, action, score, r=0.1):
        self.child_scores[action] = self.child_scores[action] * (1 - r) + score * r
        self.child_visits[action] += 1

    # ------------------------------------------------------------------------
    #  最大更新
    # ------------------------------------------------------------------------
    def max_update(self, action, score):
        if score >= self.child_scores[action]:
            self.child_scores[action] = score
        self.child_visits[action] += 1


# ============================================================================
#  MCTS_v2
# ----------------------------------------------------------------------------
#  基於MCTS改良的演算法，適用於魔塔環境。
#  特色為節點共享學習經驗，大幅減少資料儲存空間。
# ============================================================================
class MCTS_v2:
    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self):
        self.data_set = {}            # 資料集
        self.visit_node = {}          # 走訪過的節點
        self.enter_num = {}           # 觀測值進入次數

    # ------------------------------------------------------------------------
    #  選擇行動
    # ------------------------------------------------------------------------
    def choose_action(self, observation, actions, select_type='select'):
        # 不重複觀測值
        if observation not in self.enter_num:
            self.enter_num[observation] = 0
        else:
            self.enter_num[observation] += 1
            observation = observation + (self.enter_num[observation],)
        # 建立資料集
        if observation not in self.data_set:
            self.data_set[observation] = Node()
        node = self.data_set[observation]
        # 動作選擇
        if select_type == 'select':
            action = node.select(actions)
        elif select_type == 'ucb_select':
            action = node.ucb_select(actions)
        elif select_type == 'max_select':
            action = node.max_select(actions)
        else:
            raise ValueError('select_type not found')
        # 添加進已行動序列
        self.visit_node[node] = action
        return action

    # ------------------------------------------------------------------------
    #  反向傳播
    # ------------------------------------------------------------------------
    def backpropagate(self, score, r=0.1, max_update=False):
        if max_update:
            for node, action in self.visit_node.items():
                node.max_update(action, score)
        else:
            for node, action in self.visit_node.items():
                node.update(action, score, r)
        # 重置
        self.visit_node.clear()
        self.enter_num.clear()


# 測試
if __name__ == '__main__':
    import time
    from env.environment import Mota

    # 環境建立
    env = Mota()
    env.build_env('map_01')
    env.create_nodes()
    agent = MCTS_v2()
    # 訓練迴圈
    rounds = 10000
    highest_score = 0
    startTime = time.perf_counter()
    for episode in range(1, rounds + 1):
        while True:
            actions_ = env.get_feasible_actions()
            # 選擇行動
            if actions_:
                action_ = agent.choose_action(env.n2p[env.observation[-1]], actions_)
                ending = env.step(action_)
            else:
                ending = 'stop'
            if ending != 'continue':
                break
        # 結局成績
        score_ = 0
        if ending == 'clear':
            score_ = env.player.hp
        # 反向傳播
        f = np.max([env.n2p[n][0] for n in env.observation])
        li = len(env.observation)
        agent.backpropagate(score_ + f + 0.001 * li)
        # 最高成績
        if highest_score < score_:
            highest_score = score_
        # 進度顯示
        print('round:', episode, '   score:', score_, '   time:', time.perf_counter() - startTime)
        # 環境重置
        env.reset()
