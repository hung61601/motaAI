# -*- coding: utf-8 -*-
import time
import random
from util.results_plot import SaveFile
from util.lzw import LZW
from algorithms.QLearning import QLearning, QLearning_v2
from algorithms.Sarsa import Sarsa
from algorithms.mcts import MCTS
from algorithms.mcts2 import MCTS_v2
from algorithms.GoExplore import GoExplore
from util.model import MotaModel

# ----------------------------------------------------------------------------
#  常數
# ----------------------------------------------------------------------------
SELF_ALGORITHM = ['Backtracking', 'Stochastic Search', 'Q-Learning', 'Sarsa', 'Q-Learning v2', 'MCTS', 'MCTS v2',
                  'Go-Explore']
# MODEL_ALGORITHM = ['QLfD', 'MCTSfD', 'MCTSv2fD']  # TODO: 此演算法僅用於開發時使用
MODEL_ALGORITHM = ['MCTSfD']
MODEL_PREDICT = ['Model Prediction']


# ============================================================================
#  calculation 計算  V2.0    by Hung1    2020/6/22
# ----------------------------------------------------------------------------
#  各個學習演算法的主函式操作，對環境進行學習。
#  refresh_function為外部傳入的方法。每隔一段時間，會調用這個方法進行自訂義刷新。
#  V2.0 將每個演算法的主函式更明確
# ============================================================================
class Calculation:
    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self, scale_time=0.02):
        self.start_time = 0
        self.next_refresh_time = 0
        self.env = None
        self.algorithm = None
        self.refresh_function = None
        self.save_file = None
        self.rounds = 0
        self.model = MotaModel()
        self.scale_time = scale_time  # 最小刷新間隔時間
        self.interval_time = 0        # 動畫每一幀間隔時間
        self.best_success_path = None
        self.highest_score = 0
        self.now_round = 0
        self.show_frame = True
        self.pause_flag = False
        self.stop_flag = True

    # ------------------------------------------------------------------------
    #  設定參數
    # ------------------------------------------------------------------------
    def set_parameters(self, env, algorithm, rounds, model_path=None, refresh_function=None):
        self.env = env
        self.algorithm = algorithm
        self.rounds = rounds
        if model_path:
            self.model.load_model(model_path)
        self.refresh_function = refresh_function
        del self.save_file
        self.save_file = SaveFile(env.env_name, algorithm)
        self.stop_flag = False
        self.best_success_path = None
        self.highest_score = 0
        self.now_round = 0
        self.start_time = time.perf_counter()
        self.next_refresh_time = self.start_time + self.scale_time

    # ------------------------------------------------------------------------
    #  執行學習演算法
    # ------------------------------------------------------------------------
    def run(self):
        # 演算法函式
        if self.algorithm == 'Backtracking':
            function = self.backtracking
        elif self.algorithm == 'Stochastic Search':
            function = self.stochastic_search
        elif self.algorithm == 'Q-Learning':
            function = self.q_learning
        elif self.algorithm == 'Sarsa':
            function = self.sarsa
        elif self.algorithm == 'Q-Learning v2':
            function = self.q_learning_v2
        elif self.algorithm == 'MCTS':
            function = self.mcts
        elif self.algorithm == 'MCTS v2':
            function = self.mcts_v2
        elif self.algorithm == 'Go-Explore':
            function = self.go_explore
        elif self.algorithm == 'QLfD':
            function = self.qlfd
        elif self.algorithm == 'MCTSfD':
            function = self.mctsfd
        elif self.algorithm == 'MCTSv2fD':
            function = self.mctsv2fd
        elif self.algorithm == 'Model Prediction':
            function = self.model_prediction
        else:
            raise RuntimeError('algorithm does not exist.')
        # 迭代運行
        for _ in function():
            self.wait_time()
            # 中止旗標
            if self.stop_flag:
                break
        self.env.reset(refresh_frame=self.show_frame)
        self.env.update_frame()
        self.stop_flag = True

    # ------------------------------------------------------------------------
    #  動畫等待時間
    # ------------------------------------------------------------------------
    def wait_time(self):
        if self.show_frame:
            self.env.update_frame()
            if self.interval_time < self.scale_time:
                time.sleep(self.interval_time)
            else:
                quo, rem = divmod(self.interval_time, self.scale_time)
                for i in range(int(quo)):
                    # 有中止旗標時，立即停止等待
                    if self.stop_flag:
                        return
                    time.sleep(self.scale_time)
                    self.refresh()
                time.sleep(rem)
            # 暫停處理
            while self.pause_flag and not self.stop_flag:
                time.sleep(self.scale_time)
                self.refresh()
        self.refresh()

    # ------------------------------------------------------------------------
    #  刷新
    # ------------------------------------------------------------------------
    def refresh(self):
        now_time = time.perf_counter()
        # 一定時間刷新窗口
        if now_time >= self.next_refresh_time:
            self.next_refresh_time = now_time + self.scale_time
            if self.refresh_function:
                self.refresh_function()

    # ------------------------------------------------------------------------
    #  結局更新
    # ------------------------------------------------------------------------
    def ending_update(self, ending):
        if ending == 'clear':
            # 紀錄成績
            self.save_file.sampling(self.env.player.hp)
            if self.env.player.hp > self.highest_score:
                # 更新最好通關路線
                self.best_success_path = self.env.observation.copy()
                # 更新最高成績
                self.highest_score = self.env.player.hp
        else:
            # 紀錄成績
            self.save_file.sampling(0)
        # 回數增加
        self.now_round += 1

    # ------------------------------------------------------------------------
    #  獲得訓練紀錄資料
    # ------------------------------------------------------------------------
    def get_train_data(self):
        return self.save_file.get_data()

    # ------------------------------------------------------------------------
    #  快轉(關閉動畫)
    # ------------------------------------------------------------------------
    def fast(self):
        if self.show_frame:
            self.show_frame = False
            self.env.frame_reset()
            # self.env.update_frame()  # 更新畫面由之後wait_time()中處理，以避免卡頓

    # ------------------------------------------------------------------------
    #  暫停
    # ------------------------------------------------------------------------
    def pause(self):
        self.pause_flag = True

    # ------------------------------------------------------------------------
    #  恢復
    # ------------------------------------------------------------------------
    def resume(self):
        if not self.show_frame:
            self.env.frame_recover()
            self.show_frame = True
            # self.env.update_frame()  # 更新畫面由之後wait_time()中處理，以避免卡頓
        self.pause_flag = False

    # ------------------------------------------------------------------------
    #  中止
    # ------------------------------------------------------------------------
    def stop(self):
        self.stop_flag = True

    '''=======================以下是各個演算法的主函式======================='''

    # ------------------------------------------------------------------------
    #  Backtracking演算法
    # ------------------------------------------------------------------------
    def backtracking(self):
        # 建立初始狀態
        unvisited = self.env.get_actions()[::-1]
        pop_times = [0] * len(unvisited)
        for _ in range(self.rounds):
            while True:
                action = unvisited.pop()
                ending = self.env.step(action, refresh_frame=self.show_frame)
                yield
                # top數值+1
                pop_times[-1] += 1
                # 如果走到終點
                if ending != 'continue':
                    break
                # 添加可選擇的節點
                actions = self.env.get_actions()
                unvisited += actions[::-1]  # 反向添加(不影響結果，只改變搜尋順序)
                pop_times += [0] * (len(actions) - 1)
            # 已經全部探索完時
            if not unvisited:
                break
            # 結局更新
            self.ending_update(ending)
            # 退回路徑
            if self.show_frame:
                for _ in range(pop_times.pop()):
                    self.env.back_step(1, refresh_frame=True)
            else:
                self.env.back_step(pop_times.pop())
            yield

    # ------------------------------------------------------------------------
    #  Stochastic Search演算法
    # ------------------------------------------------------------------------
    def stochastic_search(self):
        for _ in range(self.rounds):
            # 重置環境
            self.env.reset(refresh_frame=self.show_frame)
            yield
            # 遊戲開始
            actions = self.env.get_feasible_actions()
            ending = 'continue'
            while actions:
                action = random.choice(actions)
                ending = self.env.step(action, refresh_frame=self.show_frame)
                yield
                if ending != 'continue':
                    break
                actions = self.env.get_feasible_actions()
            # 結局更新
            self.ending_update(ending)

    # ------------------------------------------------------------------------
    #  Q-learning演算法
    # ------------------------------------------------------------------------
    def q_learning(self):
        agent = QLearning()
        # 字串壓縮工具
        lzw = LZW()
        # 建立初始Q表
        state = lzw.compress(self.env.observation)
        agent.create_state_qtable(state, self.env.get_actions())
        # 訓練迴圈
        for _ in range(self.rounds):
            # 重置環境
            self.env.reset(refresh_frame=self.show_frame)
            yield
            # 初始化觀測值
            state = lzw.compress(self.env.observation)
            while True:
                # 選擇下一步位置
                action = agent.choose_action(state)
                # 採取行動並獲得觀測和獎勵值
                ending, reward = self.env.step(action, return_reward=True, refresh_frame=self.show_frame)
                yield
                state_ = lzw.compress(self.env.observation)
                if ending == 'continue':
                    done = False
                    # 檢查下一狀態的Q表是否存在
                    if state_ not in agent.q_table:
                        agent.create_state_qtable(state_, self.env.get_actions())
                else:
                    done = True
                # 從過程中學習
                agent.learn(state, action, reward, state_, done)
                # 將狀態傳到下一次循環
                state = state_
                # 如果走到終點，結束本回合
                if done:
                    break
            # 結局更新
            self.ending_update(ending)

    # ------------------------------------------------------------------------
    #  Sarsa演算法
    # ------------------------------------------------------------------------
    def sarsa(self):
        agent = Sarsa()
        # 字串壓縮工具
        lzw = LZW()
        # 建立初始狀態
        state = lzw.compress(self.env.observation)
        agent.create_state_qtable(state, self.env.get_actions())
        # 訓練迴圈
        for _ in range(self.rounds):
            # 重置環境
            self.env.reset(refresh_frame=self.show_frame)
            yield
            # 根據觀察選擇行動
            state = lzw.compress(self.env.observation)
            action = agent.choose_action(state)
            while True:
                # 採取行動並獲得觀測和獎勵值
                ending, reward = self.env.step(action, return_reward=True, refresh_frame=self.show_frame)
                yield
                state_ = lzw.compress(self.env.observation)
                if ending == 'continue':
                    done = False
                    # 檢查下一狀態的Q表是否存在
                    if state_ not in agent.q_table:
                        agent.create_state_qtable(state_, self.env.get_actions())
                    # 根據下次觀察選擇行動
                    action_ = agent.choose_action(state_)
                else:
                    done = True
                    action_ = None
                # 從過程中學習
                agent.learn(state, action, reward, state_, action_, done)
                # 更新狀態和行動
                state = state_
                action = action_
                # 如果走到終點，結束本回合
                if done:
                    break
            # 結局更新
            self.ending_update(ending)

    # ------------------------------------------------------------------------
    #  Q-Learning v2演算法
    # ------------------------------------------------------------------------
    def q_learning_v2(self):
        agent = QLearning_v2()
        # 字串壓縮工具
        lzw = LZW()
        # 建立初始Q表
        state = lzw.compress(self.env.observation)
        actions = self.env.get_feasible_actions()
        agent.create_state_qtable(state, actions, [0] * len(actions))
        # 訓練迴圈
        for _ in range(self.rounds):
            # 重置環境
            self.env.reset(refresh_frame=self.show_frame)
            yield
            # 初始化觀測值
            state = lzw.compress(self.env.observation)
            while True:
                # 選擇下一步位置
                action = agent.choose_action(state)
                # 採取行動並獲得觀測和獎勵值
                ending, reward = self.env.step(action, return_reward=True, refresh_frame=self.show_frame)
                yield
                state_ = lzw.compress(self.env.observation)
                if ending == 'continue':
                    done = False
                    # 檢查下一狀態的Q表是否存在
                    if state_ not in agent.q_table:
                        actions, rewards = self.env.get_feasible_actions(return_reward=True)
                        if actions:
                            # 建立Q表
                            agent.create_state_qtable(state_, actions, rewards)
                        else:
                            # 刪除前次狀態的行動
                            agent.q_table[state].drop(action)
                            ending = 'stop'
                            done = True
                else:
                    done = True
                # 從過程中學習
                agent.learn(state, action, reward, state_, done)
                # 將狀態傳到下一次循環
                state = state_
                # 如果走到終點，結束本回合
                if done:
                    break
            # 結局更新
            self.ending_update(ending)

    # ------------------------------------------------------------------------
    #  MCTS演算法
    # ------------------------------------------------------------------------
    def mcts(self):
        # 建立蒙特卡洛搜尋樹(UCT)
        actions = self.env.get_feasible_actions()
        agent = MCTS(actions)
        # 訓練迴圈
        for _ in range(self.rounds):
            # 重置環境
            self.env.reset(refresh_frame=self.show_frame)
            yield
            # 1.選擇
            ending = 'continue'
            actions_path = agent.select()
            for action in actions_path:
                ending = self.env.step(action, refresh_frame=self.show_frame)
                yield
            # 2.擴展
            actions = self.env.get_feasible_actions()
            if ending == 'continue' and actions:
                expand_action, expand_index = agent.choose_expansion_node()
                ending = self.env.step(expand_action, refresh_frame=self.show_frame)
                yield
                actions = self.env.get_feasible_actions()
                agent.expand(expand_index, actions)
            # 3.模擬
            while ending == 'continue' and actions:
                action = random.choice(actions)
                ending = self.env.step(action, refresh_frame=self.show_frame)
                yield
                actions = self.env.get_feasible_actions()
            # 4.反向傳播
            if ending == 'clear':
                score = self.env.player.hp
            else:
                score = 0
            agent.backpropagate(score)
            # 結局更新
            self.ending_update(ending)

    # ------------------------------------------------------------------------
    #  MCTS v2演算法
    # ------------------------------------------------------------------------
    def mcts_v2(self):
        agent = MCTS_v2()
        # 訓練迴圈
        for _ in range(self.rounds):
            # 重置環境
            self.env.reset(refresh_frame=self.show_frame)
            yield
            while True:
                actions = self.env.get_feasible_actions()
                # 選擇行動
                if actions:
                    pos = self.env.n2p[self.env.observation[-1]]
                    action = agent.choose_action(pos, actions, select_type='ucb_select')
                    ending = self.env.step(action, refresh_frame=self.show_frame)
                    yield
                else:
                    ending = 'stop'
                if ending != 'continue':
                    break
            # 反向傳播
            if ending == 'clear':
                score = self.env.player.hp
            else:
                score = 0
            # 反向傳播
            agent.backpropagate(score, max_update=True)
            # 結局更新
            self.ending_update(ending)

    # ------------------------------------------------------------------------
    #  Go-Explore演算法
    # ------------------------------------------------------------------------
    def go_explore(self):
        agent = GoExplore()
        # 訓練迴圈
        for _ in range(self.rounds):
            # 重置環境
            self.env.reset(refresh_frame=self.show_frame)
            yield
            # 1.從存檔中選擇狀態
            action_list = agent.select_state_from_archive()
            # 2.前往該狀態
            for action in action_list:
                self.env.step(action, refresh_frame=self.show_frame)
                yield
            ending = 'continue'
            # 3.從這個狀態進行探索
            while ending == 'continue':
                actions = self.env.get_feasible_actions()
                if actions:
                    action = random.choice(actions)
                    ending = self.env.step(action, refresh_frame=self.show_frame)
                    yield
                    # 4.更新存檔
                    action_list = self.env.observation[1:]
                    agent.update_archive(action_list, self.env.player.hp)
                else:
                    ending = 'stop'
            # 結局更新
            self.ending_update(ending)

    # ------------------------------------------------------------------------
    #  QLfD演算法
    # ------------------------------------------------------------------------
    def qlfd(self):
        agent = QLearning()
        cache = {}
        # 字串壓縮工具
        lzw = LZW()
        # 建立初始Q表
        state = lzw.compress(self.env.observation)
        agent.create_state_qtable(state, self.env.get_actions())
        # 訓練迴圈
        for _ in range(self.rounds):
            # 重置環境
            self.env.reset(refresh_frame=self.show_frame)
            yield
            # 初始化觀測值
            state = lzw.compress(self.env.observation)
            while True:
                # 選擇下一步位置
                action = agent.choose_action(state)
                if state in cache:
                    true_action = cache[state]
                else:
                    true_action = self.model.predict(self.env, self.env.get_actions())
                    cache[state] = true_action
                # 採取行動並獲得觀測和獎勵值
                ending = self.env.step(action, refresh_frame=self.show_frame)
                reward = 100 if action == true_action else 0
                yield
                state_ = lzw.compress(self.env.observation)
                if ending == 'continue':
                    done = False
                    # 檢查下一狀態的Q表是否存在
                    if state_ not in agent.q_table:
                        agent.create_state_qtable(state_, self.env.get_actions())
                else:
                    done = True
                # 從過程中學習
                agent.learn(state, action, reward, state_, done)
                # 將狀態傳到下一次循環
                state = state_
                # 如果走到終點，結束本回合
                if done:
                    break
            # 結局更新
            self.ending_update(ending)

    # ------------------------------------------------------------------------
    #  MCTSfD演算法
    # ------------------------------------------------------------------------
    def mctsfd(self):
        cache = {}
        lzw = LZW()
        # 建立蒙特卡洛搜尋樹(UCT)
        actions = self.env.get_feasible_actions()
        agent = MCTS(actions)
        # 訓練迴圈
        for _ in range(self.rounds):
            # 重置環境
            self.env.reset(refresh_frame=self.show_frame)
            yield
            # 1.選擇
            ending = 'continue'
            actions_path = agent.select()
            for action in actions_path:
                ending = self.env.step(action, refresh_frame=self.show_frame)
                yield
            # 2.擴展
            actions = self.env.get_feasible_actions()
            if ending == 'continue' and actions:
                expand_action, expand_index = agent.choose_expansion_node()
                ending = self.env.step(expand_action, refresh_frame=self.show_frame)
                yield
                actions = self.env.get_feasible_actions()
                agent.expand(expand_index, actions)
            # 3.使用模型預測進行模擬
            while ending == 'continue' and actions:
                state = lzw.compress(self.env.observation)
                if state in cache:
                    action = cache[state]
                else:
                    action = self.model.predict(self.env, actions)
                    cache[state] = action
                ending = self.env.step(action, refresh_frame=self.show_frame)
                yield
                actions = self.env.get_feasible_actions()
            # 4.反向傳播
            if ending == 'clear':
                score = self.env.player.hp
            else:
                score = 0
            agent.backpropagate(score)
            # 結局更新
            self.ending_update(ending)

    # ------------------------------------------------------------------------
    #  MCTSv2fD演算法
    # ------------------------------------------------------------------------
    def mctsv2fd(self):
        agent = MCTS_v2()
        cache = {}
        lzw = LZW()
        # 訓練迴圈
        for _ in range(self.rounds):
            # 重置環境
            self.env.reset(refresh_frame=self.show_frame)
            yield
            ending = 'continue'
            while ending == 'continue':
                actions = self.env.get_feasible_actions()
                # 選擇行動
                if actions:
                    # 10%機率使用模型來預測
                    if random.randint(1, 10) == 1:
                        state = lzw.compress(self.env.observation)
                        if state in cache:
                            action = cache[state]
                        else:
                            action = self.model.predict(self.env, actions)
                            cache[state] = action
                    else:
                        pos = self.env.n2p[self.env.observation[-1]]
                        action = agent.choose_action(pos, actions, select_type='ucb_select')
                    ending = self.env.step(action, refresh_frame=self.show_frame)
                    yield
                else:
                    ending = 'stop'
            # 反向傳播
            if ending == 'clear':
                score = self.env.player.hp
            else:
                score = 0
            # 反向傳播
            agent.backpropagate(score, max_update=True)
            # 結局更新
            self.ending_update(ending)

    # ------------------------------------------------------------------------
    #  模型預測
    # ------------------------------------------------------------------------
    def model_prediction(self):
        cache = {}
        lzw = LZW()
        # 訓練迴圈
        for _ in range(self.rounds):
            # 重置環境
            self.env.reset(refresh_frame=self.show_frame)
            yield
            ending = 'continue'
            while ending == 'continue':
                actions = self.env.get_feasible_actions()
                # 選擇行動
                if actions:
                    state = lzw.compress(self.env.observation)
                    if state in cache:
                        action = cache[state]
                    else:
                        action = self.model.predict(self.env, actions)
                        cache[state] = action
                    ending = self.env.step(action, refresh_frame=self.show_frame)
                    yield
                else:
                    ending = 'stop'
            # 結局更新
            self.ending_update(ending)


# 測試
if __name__ == '__main__':
    # 前置處理
    from widget.animation_environment import Mota
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    winWidth = 806
    winHeight = 499
    x = (root.winfo_screenwidth() - winWidth) // 2
    y = (root.winfo_screenheight() - winHeight) // 3
    root.geometry('%sx%s+%s+%s' % (winWidth, winHeight, x, y))
    frm = ttk.LabelFrame(text='Animation Map')
    frm.place(relwidth=0.6, relheight=1.0)
    test_env = Mota(frm)
    test_env.build_env('24層魔塔 (html5)')
    test_env.create_map()
    test_env.create_nodes()
    test_env.build_anima_frame()
    # 建立程序
    cal = Calculation()
    cal.set_parameters(test_env, 'Q-Learning', 100,
                       refresh_function=lambda: print('當前回合:', cal.now_round, '當前步數:', cal.env.get_step_count()))
    cal.interval_time = 0.05
    cal.run()
    root.mainloop()
