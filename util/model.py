# -*- coding: utf-8 -*-
import random
import numpy as np
import pandas as pd
from env.environment import Mota
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import joblib


# ----------------------------------------------------------------------------
#  取得權重最大值和索引
# ----------------------------------------------------------------------------
def max_weight(array):
    value = np.max(array)
    indexes = np.where(array == value)[0]
    return value, indexes


# ============================================================================
#  MotaModel  魔塔模型        by Hung1    2020/7/21
# ----------------------------------------------------------------------------
#  由通關路線經過特徵工程轉換成資料集，再將其餵進模型做訓練。
# ============================================================================
class MotaModel:
    # ------------------------------------------------------------------------
    #  常數
    # ------------------------------------------------------------------------
    MODEL_TYPE = ['Random Forest', 'Gradient Boosting']
    # 特徵
    LABEL = ['p_hp', 'p_atk', 'p_def', 'p_mdef', 'p_money', 'p_exp',
             'p_yellowKey', 'p_blueKey', 'p_redKey',
             'class', 'hp', 'atk', 'def', 'mdef', 'money', 'exp',
             'yellowKey', 'blueKey', 'redKey', 'special',
             'z', 'y', 'x', 'e']
    # 資料映射表
    LABEL_ASSIGN = {'flag': 1, 'items': 2, 'terrains': 3, 'npcs': 4, 'enemies': 5}

    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self):
        self.df = None
        self.env = None
        self.model = None
        self.train_accuracy = 0
        self.generalization = False
        self.use_cache = False
        self.cache = {}
        self._build_df_dict()

    # ------------------------------------------------------------------------
    #  建立空表格
    # ------------------------------------------------------------------------
    def _build_df_dict(self):
        self.df_dict = {label: [] for label in MotaModel.LABEL}
        self.df_dict['choose'] = []

    # ------------------------------------------------------------------------
    #  建立訓練集
    #  一次只能訓練一個遊戲地圖環境和路線。該方法可以呼叫多次。
    #  同一張地圖訓練完再換另一張地圖會較有效率。
    # ------------------------------------------------------------------------
    def create_dataset(self, env_name, action_index):
        # 重新建立環境
        if not self.env or self.env.env_name != env_name:
            del self.env
            self.env = Mota()
            self.env.build_env(env_name)
            self.env.create_nodes()
        # 產生資料集(包含不可行之行動)
        for index in action_index:
            actions = self.env.get_actions()
            true_action = actions[index]
            before_state = self.env.get_player_state()
            # 添加資料
            for action in actions:
                self.df_dict['p_hp'].append(self.env.player.hp)
                self.df_dict['p_atk'].append(self.env.player.atk)
                self.df_dict['p_def'].append(self.env.player.def_)
                self.df_dict['p_mdef'].append(self.env.player.mdef)
                self.df_dict['p_money'].append(self.env.player.money)
                self.df_dict['p_exp'].append(self.env.player.exp)
                self.df_dict['p_yellowKey'].append(self.env.player.items['yellowKey'])
                self.df_dict['p_blueKey'].append(self.env.player.items['blueKey'])
                self.df_dict['p_redKey'].append(self.env.player.items['redKey'])
                self.env.step(action)
                state_diff = self.env.get_player_state() - before_state
                self.df_dict['class'].append(action.class_)
                self.df_dict['hp'].append(state_diff[0])
                self.df_dict['atk'].append(state_diff[1])
                self.df_dict['def'].append(state_diff[2])
                self.df_dict['mdef'].append(state_diff[3])
                self.df_dict['money'].append(state_diff[4])
                self.df_dict['exp'].append(state_diff[5])
                self.df_dict['yellowKey'].append(state_diff[6])
                self.df_dict['blueKey'].append(state_diff[7])
                self.df_dict['redKey'].append(state_diff[8])
                self.df_dict['special'].append(action.special if action.class_ == 'enemies' else 0)
                pos = self.env.n2p[action]
                self.df_dict['z'].append(pos[0])
                self.df_dict['y'].append(pos[1])
                self.df_dict['x'].append(pos[2])
                self.df_dict['e'].append(0 if len(pos) == 3 else pos[3])
                self.df_dict['choose'].append(1 if action == true_action else 0)
                self.env.back_step(1)
            self.env.step(true_action)
        self.env.reset()

    # ------------------------------------------------------------------------
    #  輸出訓練集成檔案
    # ------------------------------------------------------------------------
    def output_dataset(self, file_path):
        df = pd.DataFrame(self.df_dict)
        df.to_excel(file_path, index=False)

    # ------------------------------------------------------------------------
    #  資料預處理
    # ------------------------------------------------------------------------
    def preprocess(self):
        self.df = pd.DataFrame(self.df_dict)
        # 刪除特徵
        if self.generalization:
            self.df = self.df.drop(['z', 'y', 'x', 'e'], axis=1)
        # 將class這項特徵轉換成數字
        self.df['class'] = self.df['class'].map(lambda x: MotaModel.LABEL_ASSIGN[x])

    # ------------------------------------------------------------------------
    #  訓練模型
    # ------------------------------------------------------------------------
    def train(self, model_type, n_estimators=500, **kwargs):
        y_train = self.df.choose
        x_train = self.df.drop(['choose'], axis=1)
        if model_type == 'Random Forest':
            self.model = RandomForestClassifier(n_estimators=n_estimators, **kwargs)
        elif model_type == 'Gradient Boosting':
            self.model = GradientBoostingClassifier(n_estimators=n_estimators, **kwargs)
        else:
            raise RuntimeError('model_type does not exist.')
        self.model.fit(x_train.values, y_train)
        self.train_accuracy = self.model.score(x_train.values, y_train)

    # ------------------------------------------------------------------------
    #  儲存模型
    # ------------------------------------------------------------------------
    def save_model(self, file_path):
        if file_path[-4:] == '.pkl':
            np.save(file_path[:-4] + '_config.npy', self.generalization)
        else:
            np.save(file_path + '_config.npy', self.generalization)
            file_path += '.pkl'
        joblib.dump(self.model, file_path)

    # ------------------------------------------------------------------------
    #  載入模型
    # ------------------------------------------------------------------------
    def load_model(self, file_path):
        self.generalization = np.load(file_path[:-4] + '_config.npy')
        self.model = joblib.load(file_path)
        self.cache.clear()

    # ----------------------------------------------------------------------------
    #  特徵工程
    #  將行動列表轉換成可輸入模型的資料集。
    # ----------------------------------------------------------------------------
    def feature_engineering(self, env, actions):
        cols = []
        before_state = env.get_player_state()
        for action in actions:
            env.step(action)
            state_diff = env.get_player_state() - before_state
            class_ = MotaModel.LABEL_ASSIGN[action.class_]
            special = action.special if action.class_ == 'enemies' else 0
            if self.generalization:
                col = np.hstack((before_state, class_, state_diff, special))
            else:
                pos = env.n2p[action]
                if len(pos) == 3:
                    pos = pos + (0,)
                col = np.hstack((before_state, class_, state_diff, special, pos))
            cols.append(col)
            env.back_step(1)
        if self.use_cache:
            return cols
        else:
            return np.vstack(cols)

    # ------------------------------------------------------------------------
    #  使用模型進行預測
    #  e_greedy:  隨機概率，範圍0到1，值為1時完全隨機行動
    # ------------------------------------------------------------------------
    def predict(self, env, actions, e_greedy=0.0):
        if np.random.rand() < e_greedy:
            # 隨機行動
            return np.random.choice(actions)
        else:
            # 取得最大權重索引
            _, best_index = self._predict_weight(env, actions)
            # 若索引有數個，則進行行動未來價值預測
            if len(best_index) == 1:
                best_index = best_index[0]
            else:
                # best_index = self.future_predict(env, actions, best_index)  # 棄用
                best_index = self.limit_future_predict(env, actions, best_index)
            # 回傳最好行動
            return actions[best_index]

    # ------------------------------------------------------------------------
    #  預測最大權重和索引
    # ------------------------------------------------------------------------
    def _predict_weight(self, env, actions):
        if self.use_cache:
            # 特徵工程
            cols = self.feature_engineering(env, actions)
            # 預測權重
            weights = []
            for col in cols:
                t_col = tuple(col)
                if t_col in self.cache:
                    weights.append(self.cache[t_col])
                else:
                    w = self.model.predict_proba(np.expand_dims(col, axis=0))
                    w = w[0, 1]
                    self.cache[t_col] = w
                    weights.append(w)
            # 取得最大權重索引
            return max_weight(np.array(weights))
        else:
            # 特徵工程
            data = self.feature_engineering(env, actions)
            # 預測權重
            weights = self.model.predict_proba(data)
            # 取得最大權重索引
            return max_weight(weights[:, 1])

    # ----------------------------------------------------------------------------
    #  對行動的未來價值進行預測 (已廢棄)
    #  prediction_horizon:  預測視野，表示要預測未來多少步行動(深度)
    # ----------------------------------------------------------------------------
    def future_predict(self, env, actions, best_index, prediction_horizon=6):
        best_root_index = 0  # 最好行動的索引
        path = []  # 當前探索路線
        path_value = []  # 當前探索路線價值
        best_path_value = 0  # 最好的路線價值
        unvisited = list(best_index)[::-1]  # 未探索節點
        pop_times = [0] * len(unvisited)  # 用於回溯法探索
        while unvisited:
            index = unvisited.pop()
            path.append(index)
            pop_times[-1] += 1
            env.step(actions[index])
            actions = env.get_feasible_actions()
            # 行動不為空時
            if actions:
                best_value, best_index = self._predict_weight(env, actions)
                path_value.append(best_value)
            # 還沒到達預測視野深度時
            if actions and len(path) < prediction_horizon:
                unvisited += list(best_index)[::-1]
                pop_times += [0] * (len(best_index) - 1)
            else:
                # 紀錄最好行動
                if sum(path_value) > best_path_value:
                    best_path_value = sum(path_value)
                    best_root_index = path[0]
                pop_time = pop_times.pop()
                env.back_step(pop_time)
                actions = env.get_feasible_actions()
                path_value = path_value[:-pop_time]
                path = path[:-pop_time]
        return best_root_index

    # ----------------------------------------------------------------------------
    #  對行動的未來價值進行預測，具有限制搜索廣度的參數
    #  prediction_horizon:  預測視野，表示要預測未來多少步行動(深度)
    #  max_search_size:     最大搜尋路線數量
    # ----------------------------------------------------------------------------
    def limit_future_predict(self, env, actions, best_index,
                             prediction_horizon=6, max_search_size=100):
        # 獲得每條分支的搜尋路線數量
        # 該寫法取代math.ceil()
        quota = max_search_size // len(best_index) + (max_search_size % len(best_index) != 0)
        best_root_index = 0
        best_value = 0
        for index in best_index:
            env.step(actions[index])
            value = self._limit_search(env, prediction_horizon, quota)
            if value >= best_value:  # TODO: 當視野越深時，效率會變得很差，需要尋找更好作法
                best_value = value
                best_root_index = index
            env.back_step(1)
        return best_root_index

    # ----------------------------------------------------------------------------
    #  依照預測視野計算根節點的行動最大價值
    # ----------------------------------------------------------------------------
    def _limit_search(self, env, prediction_horizon, max_search_size):
        actions = env.get_feasible_actions()
        # 若行動為空則返回0
        if not actions:
            return 0
        best_value, best_index = self._predict_weight(env, actions)
        paths = {tuple([i]): best_value for i in best_index}
        for horizon in range(1, prediction_horizon):
            # 縮減搜索廣度
            if len(paths) > max_search_size:
                keys = random.sample(paths.keys(), max_search_size)
                paths = {key: paths[key] for key in keys}
            new_paths = {}
            # 探索節點
            for path, value in paths.items():
                for index in path:
                    actions = env.get_feasible_actions()
                    env.step(actions[index])
                actions = env.get_feasible_actions()
                if actions:
                    best_value, best_index = self._predict_weight(env, actions)
                    for index in best_index:
                        p = path + (index,)
                        new_paths[p] = value + best_value
                env.back_step(len(path))
            # 重新下一輪路徑
            paths = new_paths
        # 返回最高價值
        if paths:
            return max(paths.values())
        else:
            return 0


# 測試
if __name__ == '__main__':
    import time
    from util.lzw import LZW
    # ---------------- example 1 ----------------
    test_env_name = 'map_01'
    # choose_index_list = [
    #     2, 1, 0, 0, 2, 3, 1, 0, 0, 0, 0, 1, 0, 3, 0, 0, 0, 1, 1, 0, 0, 1, 3, 0, 6,
    #     0, 0, 3, 5, 2, 0, 0, 5, 0, 0, 5, 2, 0, 0, 0, 5, 0, 0, 1, 2, 6, 3, 0, 4, 0,
    #     0, 3, 3, 0, 5, 3, 4, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    choose_index_list = [
        3, 3, 0, 0, 3, 3, 1, 0, 0, 0, 0, 1, 0, 4, 1, 0, 0, 1, 2, 0, 0, 9, 0, 0, 0,
        7, 0, 0, 8, 0, 0, 7, 0, 0, 0, 7, 1, 1, 2, 6, 6, 0, 6, 0, 0, 0, 0, 1, 5, 3,
        4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 5, 5, 0, 0, 5]

    # ---------------- example 2 ----------------
    # test_env_name = '迷你魔塔 (html5)'
    # choose_index_list = [
    #  0, 0, 2, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 3,
    #  0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 4,
    #  1, 1, 0, 0, 0, 0, 0, 1, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 6,
    #  0, 7, 0, 0, 0, 0,10, 1, 0, 0, 1,10, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 5, 0,
    #  0, 5,11, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,16, 5, 0, 0, 0, 6, 0, 0, 0,
    #  0, 0, 0, 0, 0, 0, 0, 0, 0,16, 0, 0, 0,14, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0,
    #  0,21, 0, 0,15, 0, 0, 0, 0, 0, 0, 0, 1, 6, 0, 0, 7, 0, 0, 0, 1, 7, 0, 0, 0,
    #  0, 0, 0,15, 0, 0,13, 0, 0, 0, 0,13, 0, 0, 0,16, 0, 0, 0, 0,11, 0, 1,11, 0,
    #  0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0,13,12, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
    #  0, 0, 0, 0, 4, 0, 0, 8, 0, 0, 0, 0, 0, 2, 0, 7, 1, 0, 0, 3, 0,10, 0, 3, 0,
    #  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #  0, 0, 0, 5, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0,13, 0, 0, 0, 0, 0, 0, 0,
    # 10, 2, 0, 0, 0]
    # choose_index_list = [
    #  1, 0, 2, 0, 0, 1, 4, 0, 0, 1, 0, 1, 0, 5, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 3,
    #  0, 0, 0, 0, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 8,
    #  3, 2, 0, 0, 0, 0, 0, 1, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,10,
    #  0,13, 0, 0, 0, 0,18, 1, 0, 1, 1,22, 0, 0, 0, 1, 0, 0, 1, 0, 7, 3, 3,19, 0,
    #  0, 7,17, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,22, 7, 0, 0, 0,19, 0, 0, 0,
    #  0, 0, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0,15, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0,
    #  0,21, 0, 0,19, 0, 0, 0, 0, 0, 0, 0, 1, 6, 0, 0, 7, 0, 0, 0, 1, 7, 0, 0, 0,
    #  0, 0, 0,15, 0, 0,13, 0, 0, 0, 0,13, 0, 0, 0,16, 0, 0, 0, 0,15, 0, 1,14, 0,
    #  0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0,15,14, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
    #  0, 3, 0, 0, 5, 0, 0,12, 0, 0, 0, 0, 0, 2, 0, 9, 3, 0, 0, 7, 0,14, 0, 3, 0,
    #  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #  0, 0, 1, 5, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0,17, 0, 0, 0, 0, 4, 0, 0,
    # 14, 5, 0, 0,11]

    mota_env = Mota()
    lzw = LZW()
    cache = {}
    test_model_type = 'Random Forest'
    mota_env.build_env(test_env_name)
    mota_env.create_nodes()
    print('model:', test_model_type)
    model = MotaModel()
    model.generalization = True
    model.create_dataset(test_env_name, choose_index_list)
    model.preprocess()
    model.train(test_model_type)
    # model.save_model('000s_test_model')
    print('train accuracy:', model.train_accuracy)
    print('\nenv name:', test_env_name)
    for rounds in range(1):
        print('rounds:', rounds + 1)
        startTime = time.perf_counter()
        ending = 'continue'
        while ending == 'continue':
            actions_list = mota_env.get_feasible_actions()
            if actions_list:
                state = lzw.compress(mota_env.observation)
                if state in cache:
                    select_action = cache[state]
                else:
                    select_action = model.predict(mota_env, actions_list)
                    cache[state] = select_action
                ending = mota_env.step(select_action)
                print('第 %d 步' % mota_env.get_step_count(), '執行', select_action)
            else:
                ending = 'no actions'
        endTime = time.perf_counter()
        print('ending:', ending)
        if ending == 'clear':
            print('score:', mota_env.player.hp)
        else:
            print('共前進了 %d 步' % mota_env.get_step_count())
        print('play game time:', endTime - startTime)
        mota_env.reset()
