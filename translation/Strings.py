# 字型設定
FONT = {
    'TkDefaultFont'      : {'family': 'Microsoft JhengHei UI', 'size': 9, 'weight': 'normal', 'slant': 'roman',
                            'underline': 0, 'overstrike': 0},
    'TkTextFont'         : {'family': 'Microsoft JhengHei UI', 'size': 9, 'weight': 'normal', 'slant': 'roman',
                            'underline': 0, 'overstrike': 0},
    'TkFixedFont'        : {'family': '細明體', 'size': 10, 'weight': 'normal', 'slant': 'roman',
                            'underline': 0, 'overstrike': 0},
    'menu_normal'        : ('DFKai-SB', 16),
    'menu_active'        : ('DFKai-SB', 16, 'bold'),
    'menu_label'         : ('DFKai-SB', 16, 'bold'),
    'sub_menu'           : ('DFKai-SB', 14),
    'state_table'        : ('Times New Roman', 11),
    'dataset_title'      : ('Microsoft JhengHei', 14, 'bold'),
    'dataset_tips'       : ('Microsoft JhengHei', 10, 'italic'),
    'version'            : ('Arial', 14),
    'information'        : ('Consolas', 10),
    'attribute_title'    : ('Calibri', 12, 'italic'),
    'attribute_null'     : ('Calibri', 10, 'italic'),
    'result_label'       : ('Calibri', 12, 'italic'),
    'chart_print_info'   : ('Calibri', 10),
}
# 後綴為 widths 的屬性為表格欄位的寬度參數，可依文本長度進行調整
TABLE = {
    'path_file1_columns' : ['檔案名稱'],
    'path_file1_widths'  : [10],
    'path_file2_columns' : ['遊戲地圖', '演算法', '檔案名稱'],
    'path_file2_widths'  : [10, 10, 10],
    'action_list_columns': ['索引', '座標', '類別', '名稱'],
    'action_list_widths' : [10, 50, 30, 70],
    'state_columns'      : ['hp', 'atk', 'def', 'mdef', 'money', 'exp', 'yellowKey', 'blueKey', 'redKey'],
    'state_widths'       : [55, 32, 32, 30, 35, 30, 50, 40, 35],
    'enemies_columns'    : ['id', 'hp', 'atk', 'def', 'money', 'exp', 'special', 'damage', 'value'],
    'enemies_widths'     : [100, 70, 50, 50, 50, 50, 50, 60, 40],
    'items_columns'      : ['id', 'hp', 'atk', 'def', 'money', 'exp', 'yKey', 'bKey', 'rKey', 'function'],
    'items_widths'       : [100, 50, 40, 40, 50, 40, 40, 40, 40, 250],
    'npcs_columns'       : ['position', 'order', 'command'],
    'npcs_widths'        : [100, 50, 400],
    'afterEvent_columns' : ['position', 'order', 'command'],
    'afterEvent_widths'  : [100, 50, 400],
}
FRAME = {
    'animation_map': 'Animation Map',
    'information': 'Information',
    'dataset': 'Data Set Selection',
    'tab1': '樓層資訊',
    'tab2': '訓練結果',
}
LABEL = {
    'version': 'Ver 1.0',
    'window_title': 'Mota AI',
    'author_msg': '作者：Hung1    版本：V1.0 (2020.8.18)',
    'menu_lab1': '產生通關路線',
    'menu_lab2': '訓練模型',
    'menu_lab3': '演示路線',
    'game_map': '遊戲地圖：',
    'algorithm': '學習演算法：',
    'round': '訓練回數：',
    'dataset': '通關路線資料庫',
    'dataset_lab1': '遊戲地圖：',
    'dataset_lab2': '演算法：',
    'dataset_lab3': '添加列表：',
    'dataset_lab4': '用來訓練模型的通關路線：',
    'dataset_tips': '提示：鼠標點擊列表即可添加或移除檔案',
    'speed_scale': '動畫每幀間隔（毫秒）：',
    'floor_info1': '第 %d 層',
    'floor_info2': '該樓層有 %d 個事件節點。',
    'enemies': '怪物  Enemies:',
    'items': '道具  Items:',
    'npcs': '角色  NPC:',
    'afterEvent': '事件後  AfterEvent:',
    'no_data': '無資料',
    'print_chart': '已成功列印圖片：%s',
    'training_result1': '花費時間：%d 時% 02d 分 %02d 秒',
    'training_result2': '【訓練中】',
    'training_result3': '【訓練完成】',
    'training_result4': '已完成訓練回數：%d',
    'training_result5': '最高成績：%d 分',
    'action_index': '行動索引值',
    'action_list': '可行動列表',
    'model': '模型：',
    'train_model': '模型訓練方向',
    'model_architecture': '模型架構：',
    'replay_algorithm': '演算法：',
    'clear_path': '通關路線：',
}
BUTTON = {
    'menu_btn1': ' 產生通關路線 ',
    'menu_btn2': '   訓練模型   ',
    'menu_btn3': '   演示路線   ',
    'menu_sub1': '代理自我學習',
    'menu_sub2': '手動輸入路線',
    'menu_sub3': '以模型產生路線',
    'menu_sub4': '使用通關路線訓練',
    'menu_sub5': '使用現有資料庫',
    'menu_back': '返回',
    'down': '下一層',
    'attribute_disable': '顯示屬性',
    'attribute': '顯示屬性(%dF)',
    'map': '顯示地圖(%dF)',
    'up': '上一層',
    'back': ' 退回 ',
    'play': ' 單步 ',
    'enter': ' 確認 ',
    'stop': ' 中止 ',
    'home': '  返回主選單',
    'manual_start': '開始手動輸入路線',
    'specialization': '特化  Specialization',
    'generalization': ' 泛化  Generalization',
    'restart1': '重新選擇遊戲地圖',
    'restart2': '選擇其他演算法',
    'restart3': '重新選擇模型方式',
    'restart4': '選擇其他模型',
    'restart5': '重新選擇資料集',
    'restart6': '選擇其他模型架構',
    'restart7': '再次演示路線',
    'refresh': '刷新當前結果',
    'print': '列印',
    'model_learn': '模型結合學習演算法',
    'model_predict': '一般模型預測',
}
INFO = {
    'pc_info1': '\n【您的電腦配置】\n',
    'pc_info2': '%s\n',  # CPU
    'pc_info3': '總內存﹍﹍﹍： %10.1f GB\n',
    'pc_info4': '内存使用量﹍： %10.1f GB\n',
    'pc_info5': '總內存使用率： %10s %%\n',
    'pc_info6': 'ＣＰＵ邏輯核心數： %6d 個\n',
    'pc_info7': 'ＣＰＵ物理核心數： %6d 個\n',
    'build_env1': '\n遊戲地圖：  %s\n',
    'build_env2': '建立環境完成。　　　　花費時間：%7.4f 秒\n',
    'build_env3': '繪製地圖完成。　　　　花費時間：%7.4f 秒\n',
    'build_env4': '本塔共有 %d 層。\n',
    'build_env5': '總共建立 %4d 個事件節點。\n',
    'build_env6': '總共產生 %4d 條單向連接。\n',
    'speed_scale1': '已關閉動畫。全速進行訓練。\n',
    'speed_scale2': '訓練已暫停。可移動滑動條來恢復訓練。\n',
    'time1': '第 %d 回訓練結束。\n',
    'time2': '學習經過時間：%d時%02d分%06.3f秒\n',
    'time3': '目前最高成績：%d\n',
    'warning1': '請輸入正確的訓練回數...\n',
    'warning2': '請輸入數值1以上訓練回數...\n',
    'warning3': '請輸入正確的索引值。',
    'tips': '提示：\n',
    'start1': '請選擇一個遊戲地圖來開始進行學習。\n',
    'start2': '請選擇一個遊戲地圖來進行下一步。\n',
    'start3': '請選擇一個行動來讓主角前進。',
    'start4': '請選擇一個方式來產生通關路線。\n\n',
    'start5': '請在左側選擇要用來訓練模型的資料集（通關路線），然後接著在上面選擇一種模型訓練方向。\n',
    'start6': '請選擇一個遊戲地圖來開始進行路線演示。\n',
    'replay': '\n開始進行路線演示，請操作按鈕進行播放。\n',
    'model_info': (
        '1.【模型結合學習演算法】\n'
        '使用模型以及學習演算法來讓代理進行遊戲。\n\n'
        '2.【一般模型預測】\n'
        '單純使用模型來預測行動。\n'),
    'train_model_info': (
        '【特化模型】\n對於單一資料集具有較高準度的預測能力。\n'
        '【泛化模型】\n對於未知資料集具有一定預測能力。\n'),
    'train1': '\n學習演算法：%s\n',
    'train2': '訓練回數：%d\n',
    'train3': '開始訓練...\n',
    'train4': '\n用來訓練的通關路線數量：%d 條\n',
    'train5': '\n模型架構：%s\n',
    'train6': '正在建立訓練集...\n',
    'train7': '完成度：%d/%d\n',
    'train8': '正在訓練模型...\n',
    'train_model_time': '經過時間： %6.3f 秒\n',
    'create_model1': '建立訓練集完成。　　　花費時間：%7.4f 秒\n',
    'create_model2': '總共建立 %d 筆資料。\n',
    'create_model3': '訓練模型完成。　　　　花費時間：%7.4f 秒\n',
    'create_model4': '訓練集準確率：%7.3f%%\n',
    'use_model': '模型使用方式：%s\n',
    'step1': '主角已經行動了 %d 步。',
    'step2': '主角已退回起始位置。',
    'step3': '你已經沒有任何可選擇的行動，請按「退回」以選擇其他行動。',
    'end1': '本次訓練沒有任何通關路線。\n',
    'end2': '訓練完成！可以點選「顯示屬性」觀看訓練結果。\n',
    'end3': '產生通關路線檔：%s\n',
    'end4': '恭喜通關！你的分數是：%d\n',
    'end5': '產生模型：%s\n',
    'end6': '訓練完成！回到主選單以使用你的模型。\n',
    'replay_finish': '路線演示結束。\n',
}
TOOLTIP = {
    'picture': '卡哇伊～',
    'event_link_btn': '開啟/關閉事件節點之間的連線。',
    'game_map': (
        '【遊戲地圖】\n'
        '讓代理(AI Agent)進行學習的遊戲環境。'),
    'animation_map': (
        '【Animation Map】\n'
        '該地圖能顯示代理在遊戲中選擇行動的過程。\n\n'
        '●當窗口尺寸與地圖大小不同時，您可以透過鼠標拖曳的方式來移動地圖位置。\n\n'
        '●建立完成的遊戲環境會變成四維空間的網路拓樸(z,y,x,e)，由於動畫只能表示二維空間資訊，故動畫中節點之間的連線將會有所省略。'),
    'self_algorithm': (
        '【學習演算法】\n'
        '代理學習遊戲的方法。可以想成在遊戲中進行決策的大腦。\n'
        '能供使用者選擇的演算法有暴力搜尋（如backtracking）、強化學習（如Q-Learning）以及啟發式搜尋（如MCTS）。\n\n'
        '【訓練回數】\n'
        '給予足夠的訓練回數，就能讓代理得到較好的表現，理論上時間越長越好，但也需要衡量時間與效率之間的平衡。\n'
        '當經過足夠訓練，會使代理的成績得到收斂，這之後成績將不會再提升。\n'),
    'speed_scale': (
        '【滑動條】\n'
        '可以調整動畫的撥放速度。'
        '將滑動條移到最左邊可以關閉訓練過程動畫，以全速的方式進行訓練。將滑動條移到最右邊可以讓動畫暫停，定格在同一個畫面。\n\n'
        '【中止】\n'
        '會停止當前訓練，並結算已訓練的結果。\n\n'
        '【最高成績】\n'
        '以通關時主角剩餘的血量做計算，分數比1:1。\n'),
    'floor_information': (
        '【樓層資訊】\n'
        '顯示該一樓層的所有事件資訊。\n'
        '點擊表格的標題列欄位，可以依降序或升序的方式對內容進行排列。'),
    'training_result': (
        '【訓練結果】\n'
        '將每一回訓練所得到的成績繪製成折線圖。\n'
        '若目前正在訓練中，你可以按下「刷新當前結果」來更新折線圖資訊。訓練完成後，可以按下「列印」將圖片保存起來。'),
    'action_index': (
        '【行動索引值】\n'
        '可以輸入行動列表中的「索引」值。按下「確認」按鈕後主角會去觸發這個行動事件。\n'
        '【可行動列表】\n'
        '可觸發的事件都會列在清單中。鼠標點擊列表可以填上索引值。座標最多有四軸，從左到右依序是樓層(z軸)、'
        '縱坐標(y軸)、橫坐標(x軸)、事件選項(e軸)。詳細事件屬性可在「顯示屬性」中查詢。\n'
        '【退回】\n'
        '若走錯路或是卡關時，可以點擊此按紐來退回一步行動。\n'
        '★ 在24層魔塔(html5)中，你可能會在操作時對於地圖的顯示感到困惑，'
        '尤其是在上下樓的時候。但請記住，最終結果和原遊戲是相同的。'
        '會讓你感到困惑是因為地圖被轉換成網路拓樸結構，這使主角選擇行動的方式略有不同。'),
    'model_learn': (
        '【模型】\n'
        '可以在遊戲中對行動做出預測。\n'
        '建議選擇對應遊戲地圖的模型，以提升代理學習的效率和成績。\n\n'
        '【學習演算法】\n'
        '代理學習遊戲的方法。可以想成在遊戲中進行決策的大腦。\n'
        '結合了模型的學習演算法，會受到模型的好壞而影響學習的成果。不好的模型反而會讓成績下降。'),
    'model_predict': (
        '【模型】\n'
        '可以在遊戲中對行動做出預測。\n'
        '你可以選擇具有泛化性高的模型(名稱帶有字母g的標示)進行預測，即使是沒有學習過的地圖也能夠有一定程度的表現。'
        '但要注意一點，每張地圖之間都存在著差異，通關策略也不盡相同，模型的訓練集不夠豐富會侷限模型的泛化性。'),
    'train_model': (
        '【模型訓練方向】\n'
        '至少選擇一條通關路線才能選擇模型訓練方向。\n'
        '要選擇特化模型，則資料集必須全部選擇出自於同一個遊戲地圖的通關路線。而泛化模型則沒有限制。'),
    'model_architecture': (
        '【模型架構】\n'
        '表示模型進行預測的運作方式。\n'
        '針對魔塔的特性，這裡提供sklearn的兩種分類演算法供使用者選擇。'),
    'replay': (
        '【演算法】\n'
        '演算法必須存在至少一個通關路線檔案(或有目錄)，才會出現在下拉式選單中。\n\n'
        '【通關路線】\n'
        '選擇演算法後，才會出現該演算法的通關路線列表。'),
    'replay_scale': (
        '【滑動條】\n'
        '可以調整動畫的撥放速度。\n'
        '若要使用自動撥放，請移動滑動條來使用自動撥放。'
        '若要單步撥放，請將滑動條移到最右邊，方可操作「單步」與「退回」按扭。'),
}
