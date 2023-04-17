# -*- coding: utf-8 -*-
import random
import numpy as np
from util.lzw import LZW


# ============================================================================
#  Go-Explore
# ----------------------------------------------------------------------------
#  根據論文所提到的核心演算法來設計。
# ============================================================================
class GoExplore:
    # ------------------------------------------------------------------------
    #  初始化
    #  sample_size:        存檔取樣次數
    #  score_weights:      分數的評價指標權重
    #  visits_weights:     走訪次數的評價指標權重
    #  high_level_weights: 更高關卡的評價指標權重
    # ------------------------------------------------------------------------
    def __init__(self,
                 sample_size=50,
                 score_weights=1,
                 visits_weights=-1,
                 high_level_weights=0):
        self.lzw = LZW()
        self.archive = {}
        self.sample_size = sample_size
        self.evaluate_weights = {
            'score': score_weights,
            'visits': visits_weights,
            'high_level': high_level_weights}

    # ------------------------------------------------------------------------
    #  從存檔中選擇狀態
    # ------------------------------------------------------------------------
    def select_state_from_archive(self):
        # 從存檔集中從中抽出數個存檔，並根據評價指標選擇存檔
        if len(self.archive) > self.sample_size:
            keys = random.sample(self.archive.keys(), self.sample_size)
        elif self.archive:
            keys = self.archive.keys()
        else:
            return []
        data = {
            'score': np.zeros(len(keys)),
            'visits': np.zeros(len(keys)),
            'high_level': np.zeros(len(keys))}
        for i, key in enumerate(keys):
            arch = self.archive[key]
            data['score'][i] = arch['score']
            data['visits'][i] = arch['visits']
            data['high_level'][i] = len(arch['action_list'])
        # 歸一化(Normalization)
        data['score'] = data['score'] / np.linalg.norm(data['score'])
        data['visits'] = data['visits'] / np.linalg.norm(data['visits'])
        data['high_level'] = data['high_level'] / np.linalg.norm(data['high_level'])
        # 計算評價指標
        values = data['score'] * self.evaluate_weights['score']
        values += data['visits'] * self.evaluate_weights['visits']
        values += data['high_level'] * self.evaluate_weights['high_level']
        bast_index = np.where(values == np.max(values))[0][0]
        # 返回行動軌跡
        return self.archive[list(keys)[bast_index]]['action_list']

    # ------------------------------------------------------------------------
    #  更新存檔
    # ------------------------------------------------------------------------
    def update_archive(self, action_list, score):
        key = self.lzw.compress(action_list)
        if key in self.archive:
            self.archive[key]['visits'] += 1
        else:
            self.archive[key] = {
                'action_list': action_list,
                'score': score,
                'visits': 1}


# 測試
if __name__ == '__main__':
    from env.environment import Mota

    # 環境建立
    env = Mota()
    env.build_env('map_01')
    env.create_nodes()
    # Go-Explore演算法
    agent = GoExplore()
    # 訓練迴圈
    rounds = 10000
    for episode in range(1, rounds + 1):
        # 重置環境
        env.reset()
        # 1.從存檔中選擇狀態
        action_list_ = agent.select_state_from_archive()
        # 2.前往該狀態
        for action in action_list_:
            env.step(action)
        ending = 'continue'
        # 3.從這個狀態進行探索
        while ending == 'continue':
            actions = env.get_feasible_actions()
            if actions:
                action = random.choice(actions)
                ending = env.step(action)
                # 4.更新存檔
                score_ = env.player.hp
                action_list_ = env.observation[1:]
                agent.update_archive(action_list_, score_)
            else:
                ending = 'stop'
        # 顯示成績
        if ending == 'clear':
            score_ = env.player.hp
        else:
            score_ = 0
        print('round:', episode, 'score', score_)
