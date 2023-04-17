# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from typing import List


# ============================================================================
#  QLearning        by Hung1
# ----------------------------------------------------------------------------
#  使用QLearning來做學習，適用於魔塔環境。
#  V 1.0   2020/2/1
#  搭配Mota AI V0.2來使用。
# ============================================================================
class QLearning:
    # ------------------------------------------------------------------------
    #  常量
    # ------------------------------------------------------------------------
    DATA_TYPE = np.int16              # Q表的資料型態

    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self,
                 learning_rate: float = 0.01,
                 discount_factor: float = 0.9,
                 e_greedy: float = 0.1):
        self.alpha = learning_rate    # 學習速率
        self.gamma = discount_factor  # 折扣因子
        self.epsilon = e_greedy       # 隨機機率
        self.cost_capacity = 0        # 儲存格計數
        self.q_table = {}

    # ------------------------------------------------------------------------
    #  建立該狀態的Q表
    # ------------------------------------------------------------------------
    def create_state_qtable(self, state: str, actions: List[object]):
        self.q_table[state] = pd.Series(
            [0] * len(actions),
            index=actions,
            dtype=QLearning.DATA_TYPE
        )
        self.cost_capacity += len(actions)

    # ------------------------------------------------------------------------
    #  選擇下一步行動
    # ------------------------------------------------------------------------
    def choose_action(self, state: str) -> tuple:
        if np.random.rand() < self.epsilon:
            # 隨機選擇方向行動
            action = np.random.choice(self.q_table[state].index)
        else:
            # 依照最高分數行動，若有複數個最高值，從中隨機取一個
            state_action = self.q_table[state]
            action = np.random.choice(state_action[state_action == np.max(state_action)].index)
        return action

    # ------------------------------------------------------------------------
    #  學習，更新Q表的值 <s, a, r, s'>
    # ------------------------------------------------------------------------
    def learn(self, state: str, action: object, reward: int, next_state: str, terminal: bool):
        old_value = self.q_table[state][action]
        if terminal:
            self.q_table[state][action] = old_value + self.alpha * (reward - old_value)
        else:
            #  Q(S,A) ← (1-α)Q(S,A)+α[R+γ maxQ(S',α)]
            learned_value = reward + self.gamma * self.q_table[next_state].max()
            self.q_table[state][action] = (1 - self.alpha) * old_value + self.alpha * learned_value


# ============================================================================
#  QLearning v2        by Hung1
# ----------------------------------------------------------------------------
#  改良QLearning，去除不必要的選擇
#  V 1.0   2020/2/18
#  搭配Mota AI V0.3來使用。
# ============================================================================
class QLearning_v2(QLearning):
    # ------------------------------------------------------------------------
    #  建立該狀態的Q表
    # ------------------------------------------------------------------------
    def create_state_qtable(self, state: str, actions: List[object], rewards: List[int]):
        self.q_table[state] = pd.Series(
            rewards,
            index=actions,
            dtype=QLearning.DATA_TYPE
        )
        self.cost_capacity += len(actions)
