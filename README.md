![Mota AI](pictures/text_logo.png)

# Mota AI（魔塔 AI）
<details>
<summary>什麼是魔塔？</summary>

> 魔塔是一種類型的電子角色扮演遊戲（RPG），在中國大陸、臺灣、香港等地區非常受歡迎，也是許多玩家最初接觸的 RPG 之一。魔塔最初由日本的一些業餘程序員和愛好者所開發，最早的版本於 1983 年問世，而現在已經有許多不同版本的魔塔遊戲可供選擇。
> 
> 魔塔的遊戲玩法通常包括探索多層迷宮、戰鬥敵人、收集寶物、升級角色等元素。玩家需要通過在迷宮中探索和戰鬥來逐漸提高自己的實力，解開故事情節中的謎團，最終擊敗遊戲中的頭目。遊戲畫面通常使用像素風格的圖像，並且具有簡潔而易於操作的介面。
>
> 在中國大陸、臺灣、香港等地區，魔塔被廣泛認為是一種經典的 RPG 遊戲，有很多玩家通過魔塔遊戲體驗到了 RPG 的樂趣，同時也影響了許多後來的 RPG 遊戲開發者。
> 
> -- 來源：ChatGPT
</details>

提供魔塔遊戲環境和學習演算法（強化學習、啟發式搜尋、暴力搜尋）的圖形使用者介面（GUI），可用於遊玩魔塔、訓練模型、觀看代理（Agent）在環境中的學習過程。

設計的初衷是讓不曾接觸過機器學習的使用者也能夠輕鬆使用，享受學習樂趣。

Mota AI 想要達成的目標是「讓 AI 遊玩魔塔，並且超越人類成績」。

- 作者：Hung1
- 版本：1.0（2020 / 08 / 18）
- GUI 是使用 Tkinter 製作

---
<details>
<summary>What is a Magic Tower (Mota)?</summary>

> The "Magic Tower" (魔塔, hereinafter referred to as "Mota") is a type of electronic role-playing game (RPG) that is very popular in mainland China, Taiwan, Hong Kong, and other regions. It is also one of the RPGs that many players first come into contact with. Mota was originally developed by some amateur programmers and enthusiasts in Japan. The earliest version was released in 1983, and now there are many different versions of the Mota game to choose from.
> 
> The gameplay of Mota usually includes exploring multi-level mazes, fighting enemies, collecting treasures, and upgrading characters. Players need to gradually improve their strength by exploring and fighting in the maze, unlocking the mysteries in the story, and finally defeating the bosses in the game. The game screen usually uses pixel-style images and has a simple and easy-to-operate interface.
>
> In mainland China, Taiwan, Hong Kong, and other regions, Mota is widely regarded as a classic RPG game, and many players have experienced the fun of RPG through the Mota game. At the same time, it has also influenced many RPG game developers in the future.
> 
> -- Source: ChatGPT
</details>

The graphical user interface (GUI) provides a game environment for Mota and learning algorithms (reinforcement learning, heuristic search, brute force search) that can be used to play Mota, train models, and observe the learning process of agents in the environment.

The design intent is to enable users who have never had any experience with machine learning to easily use it and enjoy the pleasure of learning.

The goal of Mota AI is to "let AI play Mota and surpass human performance".

- Author: Hung1
- Version: 1.0 (2020/08/18)
- GUI was created using Tkinter.

## 目錄結構 Directory Structure
```
├── algorithms                    # 存放各種學習演算法
│   └── *.py
├── env
│   ├── database.py               # 魔塔環境資料庫
│   └── environment.py            # 創建可用於學習的魔塔環境
├── model                         # 存放機器學習訓練出來的模型
│   ├── *.pkl                     # 模型資料
│   └── *.npy                     # 模型設定檔
├── output                        # 存放機器學習的學習曲線圖片
│   └── *.png
├── paper                         # 專題報告書
│   └── *.pdf
├── path                          # 存放機器學習訓練出來的最好通關路線
│   └── *
│       └── *
│           └── *.npy
├── pictures                      # GUI 會用到的各種圖片
│   └── demo                      # README.md 會用到的圖片
│       └── *.png
│   ├── *.png
│   ├── *.jpg
│   └── *.ico
├── translation
│   ├── Strings.py                # GUI 文本
│   └── ui_text.py
├── util
│   ├── lzw.py                    # 串列(列表)壓縮
│   ├── model.py                  # 使用監督式學習產生模型
│   └── results_plot.py           # 繪製折線圖
├── video                         # 演示影片
│   └── *.mp4
├── widget                        # GUI 窗口的各種小部件
│   ├── advanced_form.py          # 高級表格
│   ├── animation_environment.py  # 顯示代理在環境中行動的過程動畫
│   ├── combobox.py               # 根據文字寬度更改下拉列表框的寬度
│   ├── frame_scrollbar.py        # 根據框架大小產生滾動條
│   ├── label_image.py            # 隨窗口縮放改變圖片尺寸
│   └── tooltip.py                # 工具提示
├── .gitignore
├── calculation.py                # 各個學習演算法的主函式方法
├── picture_source.txt            # 網路圖片來源
├── README.md
├── requirements.txt              # 列出 Python 相依套件
├── run_this.py                   # GUI 的進入點
└── window.py                     # 使用者操作視窗
```

- database.py  
內建一些小型地圖和經典魔塔「24層魔塔」，此外還可以在此檔案添加新的自訂義地圖。  
在HTML5魔塔 (https://h5mota.com/) 可以獲取人類玩家的排行榜，能作為判斷學習演算法表現好壞的依據。


- environment.py  
提供類似 Gym (https://www.gymlibrary.dev/) 的 API，例如 step、reset。  
另外提供更為實用的方法，例如 back_step，不需重置環境即可退回到之前的狀態，方便實現探路功能。


- paper  
本作者大學時的專題報告書，包含魔塔研究和遊戲創作兩個獨立領域。若想深入了解 Mota AI 背後的設計，只需閱讀第 2 章、第 3 章和第 4.2 節。第 4.2.4 小節所介紹的 Mota AI 與此版本不同，請依此自述文件為主。

## 相依套件 Dependencies
- 本程式開發時所使用的 Python 版本為 3.7
- 推薦 IDE：Spyder (Anaconda 3) 或是 PyCharm
- 安裝相依套件可在根目錄下使用指令：
```bash
pip install -r requirements.txt
```
- 下面列出相依套件的版本：
```
psutil~=5.9.4
numpy~=1.21.6
Pillow~=9.5.0
matplotlib~=3.5.3
pandas~=1.3.5
joblib~=1.2.0
scikit-learn~=1.0.2
```

## 操作介紹 Instruction
### 1. 如何啟動GUI
安裝好 Python 環境後，直接運行 `run_this.py` 即可開啟視窗。
```bash
python run_this.py
```
### 2. 產生通關路線 - 代理自我學習
#### Demo
https://user-images.githubusercontent.com/55278574/232440139-ef318948-113b-49bb-86cc-641793e3c059.mp4  

使用學習演算法來產生一條通關路線。  
選擇一張遊戲地圖，您可以在右下角的 Information 中查看您的電腦配置和環境建立資訊。  
點擊 ![line_visible](pictures/line_visible.png) 可開啟/開閉事件節點之間的連線。  
地圖下方顯示勇者（代理）當前的狀態資訊，點擊「顯示屬性」可以切換顯示當前樓層資訊。  
接下來您可以開始選擇一種學習演算法來搜尋通關路線，輸入訓練回數之後，您可以開始看到代理正在探索環境的過程。  
如果想暫停訓練，請將滑動條移至 ![pause](pictures/pause.png) 最右側；如果想關閉動畫，全速訓練，請將滑動條移至 ![fast](pictures/fast.png) 最左側。
您隨時都能透過按下 ![stop](pictures/stop.png) 中止按鈕來提前結束訓練。  
在暫停訓練或訓練結束時，都可以點擊「顯示屬性」切換至「訓練結果」標籤來查看當前的訓練曲線。  
若是在暫停訓練中查看訓練結果，請先手動點擊「刷新當前結果」按鈕。  
如果想儲存訓練曲線，請點擊「列印」按鈕。  
訓練完成後，依您自身需求可以選擇「重新選擇遊戲地圖」和「選擇其他演算法」，亦或是「返回主選單」。

- 遊戲地圖  
內建 5 張地圖，「[迷你魔塔](https://h5mota.com/tower/?name=minimota)」和「[24層魔塔](https://h5mota.com/tower/?name=24)」皆從 HTML5魔塔 (https://h5mota.com/) 取得。

| 名稱            | 層數  | 事件節點 | 單向連接 | 描述                            |
|---------------|-----|------|------|-------------------------------|
| map_01        | 1   | 65   | 177  | 標準難度的魔塔，含商店。因為鑰匙有限，所以有可能無法通關。 |
| map_02        | 3   | 50   | 140  | 簡單難度的魔塔，不含商店。                 |
| map_03        | 1   | 19   | 64   | 最低難度的魔塔，不含商店且路線簡單，生命足夠必定通關。   |
| 迷你魔塔 (html5)  | 4   | 281  | 798  | 公開的低層數魔塔，用來試試水溫。              |
| 24層魔塔 (html5) | 27  | 848  | 2473 | 公開的經典魔塔，作為測量AI是否能突破人類成績的基準魔塔。 |

- 學習演算法  

| 名稱                | 分類    | 描述                                                                                           |
|-------------------|-------|----------------------------------------------------------------------------------------------|
| Backtracking      | 暴力搜尋  | 基於深度優先搜尋 (Depth-First Search, DFS) 所實現的演算法，沒有任何的學習能力。                                        |
| Stochastic Search | 隨機搜尋  | 隨機選擇動作。沒有任何的學習能力。                                                                            |
| Q-Learning        | 強化學習  | 一種知名的強化學習演算法。                                                                                |
| Sarsa             | 強化學習  | 全名 State-Action-Reward-State-Action，一種強化學習演算法。                                               |
| Q-Learning v2     | 強化學習  | 基於 Q-Learning 的改良版本，設置初始 Q 值，並修改選擇行動策略。                                                      |
| MCTS              | 啟發式搜尋 | 在電腦圍棋上有卓越的表現，例如：AlphaGo。                                                                     |
| MCTS v2           | 啟發式搜尋 | 基於 MCTS 的改良版本，共享相同事件節點的學習經驗，並修改選擇行動策略。                                                       |
| Go-Explore        | 強化學習  | 基於 [Go-Explore](https://arxiv.org/abs/1901.10995) 核心概念所實現的演算法，沒有使用神經網路。<br/>_該演算法目前僅做為實驗用途。_ |

- 樓層資訊  
  - 怪物：  
  怪物事件包含名稱 (id)、生命 (hp)、攻擊 (atk)、防禦 (def)、金幣 (money)、經驗 (exp)、能力 (special) 等資訊。  
  能力目前有 3 種：

    | 編號  | 名稱  | 影響參數   | 描述                             |
    |-----|-----|--------|--------------------------------|
    | 1   | 先攻  |        | 怪物首先攻擊。                        |
    | 11  | 吸血  | value  | 戰鬥前，怪物首先吸取角色的 {value} %生命作為傷害。 |
    | 22  | 固傷  | damage | 戰鬥前，怪物對角色造成 {damage} 點傷害。      |

  - 道具：  
  可以增加主角各項數值的道具事件。  
  一些事件的數值並非是常數，則會使用 `function` 來計算。

  - 角色：  
  可提供一些特殊指令 `command` 的事件。「商店」屬於角色的一種。  
  若一些角色具有多個連續的特殊指令，`order` 則代表特殊指令的執行順序。  
  `position` 代表(樓層、Y座標、X座標、事件選項)，多個事件選項常見於商店。  
  以下為 command 種類：
    
    | type           | 描述                             |
    |----------------|--------------------------------|
    | if             | 當 {condition} 未成立時，無法觸發該事件。    |
    | addItem        | 獲得 {value} 個 {name} 的道具。       |
    | addValue       | 獲得 {value} 點 {name} 的數值。       |
    | not_activated  | 該事件可以重複執行。                     |
    | open           | 啟用座標位於 {loc} 的事件。              |
    | enable         | 禁用座標位於 {loc} 的事件。              |
    | update_enemies | 將現有的 {*key} 怪物替換成 {*value} 怪物。 |

  - 事件後：  
  在當前事件節點處理完之後，才會觸發特殊指令 `command` ，常見於一些怪物事件。
  



### 3. 產生通關路線 - 手動輸入路線
#### Demo
https://user-images.githubusercontent.com/55278574/232440869-0e57125d-0c9d-48ba-b235-ed89a7889e9f.mp4

可以用人工手動的方式輸入通關路線。  
點擊「可行動列表」中的事件時，會自動填入行動索引值，並且地圖上會顯示紅色圈圈 ![cursor](pictures/cursor.png) 來標示您所選擇的事件。  
確認後即可按下確認 ![ok](pictures/ok.png) 按鈕以執行事件。  
如果選擇錯誤的行動，您可以按下退回 ![ok](pictures/back.png) 按鈕以回到前一個事件。

### 4. 產生通關路線 - 以模型產生路線
#### Demo
https://user-images.githubusercontent.com/55278574/232440953-d3568473-c0f9-4c37-b0c4-da02c4311cb5.mp4

將已經訓練好的模型用來預測其他魔塔，這也適用於未曾見過的魔塔。
- 模型結合學習演算法  
  目前只提供 MCTSfD (Monte Carlo tree search from demonstration) 演算法，是將 MCTS 與模型預測做結合的演算法，能夠在模型產生的路線下，進一步的去探索新的狀態，以達到更好的成績。
- 一般模型預測  
  對於已經訓練好的模型，產生同一張地圖的路線將會是固定的，因此不存在訓練回數。

### 5. 訓練模型 - 使用通關路線訓練
#### Demo
https://user-images.githubusercontent.com/55278574/232441048-23ad8dd5-1347-4f82-9ac2-3c06eb068c5b.mp4

可以使用多條已生成的通關路線來訓練出一個模型，這是達成泛化 (Generalization) 的必要方式。  
在列表中按住 Shift 鍵可以一次選取多條通關路線。  
模型是使用「監視式學習」的方式訓練，可使用的演算法有：Random Forest 和 Gradient Boosting。
- 特化  
僅能使用同一張地圖的路線來訓練模型。已訓練好的模型建議用在同一張地圖的預測上。  
- 泛化  
通關路線不限定於同一張地圖，你可以把所有至今為止的路線全部拿來訓練。  
「特化」與「泛化」的差異在於訓練模型時所使用的特徵不同，這會影響模型的預測能力。

### 6. 演示路線 - 使用現有資料庫
#### Demo
https://user-images.githubusercontent.com/55278574/232441113-f611c13c-7198-4088-9041-3a346bec7b93.mp4

可以回放已存在的通關路線動畫。  
您可以通過滑動條來決定動畫撥放速度。  
若想查看特定狀態的行動，可以通過單步 ![cursor](pictures/play.png) 和退回 ![cursor](pictures/back.png) 來移動到你想要的位置上。

## 其他 Other
- 將滑鼠移至 ![tooltip](pictures/tooltip.png) 圖示上，就會出現相關的工具提示。
- 點擊表格欄位可排序。
- 若 Animation Map 的視窗尺寸大於地圖尺寸，你可以用滑鼠移動它的位置。
  - Demo  
  
  https://user-images.githubusercontent.com/55278574/232441176-20eb813c-e575-43a9-96bc-e24f57da1662.mp4

## 本地化翻譯 Localized Translation
- 默認語言使用「繁體中文」，文本放置於 `translation\Strings.py`，如果需要進行本地化翻譯，請聯繫作者Email: hung61601@gmail.com
