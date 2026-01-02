import os
import requests
from datetime import datetime
from pydantic import BaseModel, Field


class Tools:
    def __init__(self):
        pass

    # --- 既有工具 (User Info) ---
    def get_user_name_and_email_and_id(self, __user__: dict = {}) -> str:
        """
        Get the user name, Email and ID from the user object.
        """
        print(__user__)
        result = ""
        if "name" in __user__:
            result += f"User: {__user__['name']}"
        if "id" in __user__:
            result += f" (ID: {__user__['id']})"
        if "email" in __user__:
            result += f" (Email: {__user__['email']})"
        if result == "":
            result = "User: Unknown"
        return result

    # --- 既有工具 (Time) ---
    def get_current_time(self) -> str:
        """
        Get the current time in a more human-readable format.
        """
        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")
        current_date = now.strftime("%A, %B %d, %Y")
        return f"Current Date and Time = {current_date}, {current_time}"

    #   新增/修改的健身工具組 (拆分為：飲食、課表、詳細動作)

    # --- 工具 1: 專注於熱量與營養素計算 (修正防呆版) ---
    def calculate_daily_macros(
        self,
        #  修改點 1: 改回 None，並在描述中加入嚴格警語，防止模型亂編數字
        weight_kg: float = Field(
            None,
            description="體重(kg)。⚠️注意：若用戶對話中未提供具體數字，請務必傳入 None，切勿自行填寫預設值。",
        ),
        height_cm: float = Field(
            None, description="身高(cm)。⚠️注意：若用戶未提供，請務必傳入 None。"
        ),
        age: int = Field(
            None, description="年齡。⚠️注意：若用戶未提供，請務必傳入 None。"
        ),
        gender: str = Field("M", description="性別: M(男) / F(女)"),
        activity_level: str = Field(
            "light", description="活動量: sedentary, light, moderate, active"
        ),
        goal: str = Field(
            "recomp", description="目標: cut(減脂), bulk(增肌), recomp(重組)"
        ),
        force_estimate: bool = Field(
            False,
            description="只有當用戶明確說「我不知道」、「直接幫我算」時，才設為 True。",
        ),
    ) -> str:
        """
        計算基礎代謝(BMR)、每日總消耗(TDEE)及營養素建議。
        若用戶未提供身高體重，此工具會回傳提示，請 AI 進行詢問。
        """

        # --- 數據清洗 ---
        def clean_numeric(val):
            # 增加對 'None' 字串的過濾
            if val is None or str(val).strip().lower() in [
                "none",
                "null",
                "unknown",
                "nan",
            ]:
                return None
            try:
                s = (
                    str(val)
                    .lower()
                    .replace("kg", "")
                    .replace("cm", "")
                    .replace("歲", "")
                    .strip()
                )
                return float(s)
            except:
                return None

        w_val = clean_numeric(weight_kg)
        h_val = clean_numeric(height_cm)
        a_val = clean_numeric(age)

        missing_fields = []
        if w_val is None:
            missing_fields.append("體重")
        if h_val is None:
            missing_fields.append("身高")
        if a_val is None:
            missing_fields.append("年齡")

        # --- 互動邏輯: 缺資料且非強制估算 -> 提示 AI 詢問 ---
        if missing_fields and not force_estimate:
            m_str = "、".join(missing_fields)
            return f"""
            SYSTEM_INSTRUCTION:
            缺少必要數據：【{m_str}】。
            請勿自己假設數值。
            請回覆用戶：「為了計算您的增重熱量，請問您的{m_str}是多少？」
            """

        # --- 填入數值 (只有當 force_estimate=True 才使用預設值) ---
        w = w_val if w_val else 70.0
        h = h_val if h_val else 173.0
        a = int(a_val) if a_val else 25
        if h < 3:
            h *= 100

        # --- BMR & TDEE 計算 ---
        g = str(gender).upper()
        if "F" in g or "女" in g:
            bmr = (10 * w) + (6.25 * h) - (5 * a) - 161
            gender_desc = "女性"
        else:
            bmr = (10 * w) + (6.25 * h) - (5 * a) + 5
            gender_desc = "男性"

        act_map = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}
        multiplier = act_map.get(activity_level.lower(), 1.375)
        tdee = int(bmr * multiplier)

        # --- 目標熱量計算 ---
        goal_lower = goal.lower()
        if "cut" in goal_lower or "減脂" in goal_lower:
            target_calories = tdee - 500
            protein = int(w * 2.2)
            goal_desc = "減脂 (Fat Loss)"
        elif "bulk" in goal_lower or "增肌" in goal_lower or "增重" in goal_lower:
            target_calories = tdee + 300
            protein = int(w * 1.8)
            goal_desc = "增肌/增重 (Bulk)"
        else:
            target_calories = tdee
            protein = int(w * 2.0)
            goal_desc = "身體重組 (Recomp)"

        # 標記是否為估算，讓 AI 知道要不要加上免責聲明
        est_tag = ""
        if force_estimate and missing_fields:
            est_tag = " (基於預設值 70kg/173cm/25歲 計算)"

        return f"""
        【營養素計算結果 ({gender_desc}){est_tag}】
        -----------------------------------
        您的基礎代謝 (BMR): {int(bmr)} kcal
        每日總消耗 (TDEE): {tdee} kcal
        當前目標: {goal_desc}
        
         **每日建議攝取**:
        - 熱量: {int(target_calories)} kcal
        - 蛋白質: {protein} g
        - 碳水與脂肪: 剩餘熱量自由分配，建議碳水佔比 40-50%
        """

    # --- 工具 2: 提供每週簡單課表 (分化安排) - 防跳針版 ---
    def get_weekly_workout_schedule(
        self,
        goal: str = Field(
            "general", description="目標: build_muscle, lose_fat, general"
        ),
        days_per_week: int = Field(3, description="每週想運動的天數 (3-6)"),
    ) -> str:
        """
        生成每週的運動安排架構。
        """
        schedule = ""

        if days_per_week <= 3:
            schedule = """
            【每週 3 天 - 全身訓練 (Full Body)】
            - Day 1: 全身 A (深蹲+推+拉)
            - Day 2: 休
            - Day 3: 全身 B (硬舉+推+拉)
            - Day 4: 休
            - Day 5: 全身 C (腿+核心+有氧)
            - Day 6, 7: 休
            """
        elif days_per_week == 4:
            schedule = """
            【每週 4 天 - 上下肢分化 (Upper/Lower)】
            - Day 1: 上肢 (胸背肩)
            - Day 2: 下肢 (腿臀)
            - Day 3: 休
            - Day 4: 上肢 (手臂細節)
            - Day 5: 下肢 (爆發力/耐力)
            - Day 6, 7: 休
            """
        else:
            schedule = """
            【每週 5-6 天 - 推拉腿 (PPL)】
            - Day 1: 推 (胸肩三頭)
            - Day 2: 拉 (背二頭)
            - Day 3: 腿 (下肢)
            - Day 4: 休
            - Day 5: 上肢混合
            - Day 6: 下肢+核心
            - Day 7: 休
            """

        #  這裡加入了關鍵的系統提示，叫 AI 不要再囉嗦
        return (
            f"根據您的目標與頻率，建議以下課表架構：\n{schedule}\n"
            "若需要特定部位(如胸、背)的詳細動作教學，請告訴我！\n\n"
            "SYSTEM_NOTE: 請直接將上述課表呈現給用戶。用戶的身體數據已知，**請勿**再次詢問體重、身高或年齡。"
        )

    # --- 工具 3: 提供特定部位詳細動作 - 防跳針版 ---
    def get_detailed_body_part_routine(
        self,
        target_parts: str = Field(
            ..., description="想練的部位，例如: '胸', '背', '腿', '肩膀', '核心'"
        ),
    ) -> str:
        """
        提供特定身體部位的詳細訓練動作。
        """
        routines = {
            "chest": "【胸部訓練】\n1. 臥推: 4x8-12\n2. 上胸臥推: 3x10-12\n3. 夾胸: 3x15\n4. 伏地挺身: 3x力竭",
            "back": "【背部訓練】\n1. 引體向上/下拉: 4x8-12\n2. 划船: 4x8-12\n3. 面拉: 3x15\n4. 直臂下壓: 3x15",
            "shoulder": "【肩膀訓練】\n1. 肩推: 4x8-12\n2. 側平舉: 4x15-20\n3. 俯身飛鳥: 3x15\n4. 聳肩: 3x12",
            "legs": "【腿部訓練】\n1. 深蹲: 4x6-10\n2. 硬舉/RDL: 3x10-12\n3. 腿推: 3x12-15\n4. 弓箭步: 3x12",
            "arms": "【手臂訓練】\n1. 二頭彎舉: 3x12\n2. 錘式彎舉: 3x12\n3. 三頭下壓: 3x15\n4. 法式推舉: 3x12",
            "abs": "【核心訓練】\n1. 懸垂舉腿: 3x12\n2. 棒式: 3x60秒\n3. 俄羅斯轉體: 3x20",
        }

        query = target_parts.lower()
        result = "以下是針對您要求的部位建議的詳細菜單：\n\n"
        found = False

        if "胸" in query or "chest" in query or "推" in query:
            result += routines["chest"] + "\n\n"
            found = True
        if "背" in query or "back" in query or "拉" in query:
            result += routines["back"] + "\n\n"
            found = True
        if "肩" in query or "shoulder" in query:
            result += routines["shoulder"] + "\n\n"
            found = True
        if "腿" in query or "leg" in query or "蹲" in query:
            result += routines["legs"] + "\n\n"
            found = True
        if "手" in query or "arm" in query or "二頭" in query:
            result += routines["arms"] + "\n\n"
            found = True
        if "腹" in query or "核心" in query or "abs" in query:
            result += routines["abs"] + "\n\n"
            found = True

        if not found:
            return "抱歉，我目前只有 胸、背、腿、肩、手、核心 的詳細菜單。請問您想練哪個部位？"

        #  同樣加入封口令
        return (
            result
            + "SYSTEM_NOTE: 請直接顯示上述菜單。**請勿**在結尾詢問用戶的體重、身高或年齡，這些資訊已確認。"
        )

    # --- 工具: 成大健身房爬蟲 ---
    def get_ncku_gym_schedule(self) -> str:
        """
        使用 requests 爬取成大體適能中心(健身房)的網頁公告與時間表。
        """
        import requests
        from datetime import datetime

        # 嘗試匯入 BeautifulSoup，如果沒有安裝則提示錯誤
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            return "系統錯誤：請先安裝 beautifulsoup4 套件 (pip install beautifulsoup4) 才能解析網頁。"

        url = "https://pe-acad.ncku.edu.tw/p/406-1045-201827,r2330.php?Lang=zh-tw"

        try:
            # 1. 偽裝成瀏覽器 (有些學校網站會擋爬蟲)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            # 2. 發送請求
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = "utf-8"

            # 3. 解析 HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # 4. 提取主要內容區 (針對成大 Rpage 系統的結構)
            content = ""
            main_div = soup.find("div", class_="mcont")

            if main_div:
                # 移除 script 和 style 標籤，只留文字
                for script in main_div(["script", "style"]):
                    script.extract()
                content = main_div.get_text(separator="\n", strip=True)
            else:
                # 如果找不到特定區塊，就抓整個 body 的文字 (備案)
                content = soup.body.get_text(separator="\n", strip=True)

            # 5. 整理資訊回傳給 AI
            # 獲取今天日期與星期，這對判斷開放時間至關重要
            today = datetime.now()
            week_days = ["一", "二", "三", "四", "五", "六", "日"]
            current_date_str = f"{today.year}年{today.month}月{today.day}日 (星期{week_days[today.weekday()]})"

            # 截斷過長的內容，保留前 3000 字給 AI 閱讀即可
            return f"""
            【系統資訊】
            今天是：{current_date_str}
            
            【成大健身房網頁抓取內容】
            {content[:3000]}
            
            【系統指示】
            請根據「今天是星期幾」以及「網頁內容中的學期/寒暑假/國定假日規定」，
            判斷今天的具體開放時間。如果網頁提到今日是特定維修日或國定假日，請特別標註。
            """

        except Exception as e:
            return f"爬取失敗：{str(e)}"
