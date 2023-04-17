# -*- coding: utf-8 -*-
from algorithms.QLearning import QLearning


# ============================================================================
#  Sarsa
# ----------------------------------------------------------------------------
#  使用Sarsa來做學習，適用於魔塔環境。
#  V 1.0   2020/2/2  by hung1
#  搭配Mota AI V0.2來使用。
# ============================================================================
class Sarsa(QLearning):
    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self,
                 learning_rate: float = 0.01,
                 discount_factor: float = 0.9,
                 e_greedy: float = 0.1):
        super(Sarsa, self).__init__(learning_rate, discount_factor, e_greedy)

    # ------------------------------------------------------------------------
    #  學習，更新Q表的值 <s, a, r, s', a'>
    # ------------------------------------------------------------------------
    def learn(self, state: str, action: object, reward: int, next_state: str,
              next_action: object, terminal: bool):
        old_value = self.q_table[state][action]
        if terminal:
            self.q_table[state][action] = old_value + self.alpha * (reward - old_value)
        else:
            # 與Q-Learning差別在於 q[s'].max 改成 q[s'][a']
            learned_value = reward + self.gamma * self.q_table[next_state][next_action]
            self.q_table[state][action] = (1 - self.alpha) * old_value + self.alpha * learned_value
