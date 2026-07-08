import pandas as pd
from config import EXCEL_FILE, SHEET_NAME ,CHILDREN


# =========================================================
# ■ メイン入口（データ前処理の起点）
# =========================================================
def preprocess():
    """
    Excelから生データを読み込み、可視化用とAI学習用にそれぞれ整形して返します。
    """
    # Excelファイルからデータ読み込み (ヘッダーなし生データ前提)
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, header=None)

    # =========================
    # 可視化用データの生成
    # =========================
    graph_data = build_graph_data(df)

    # =========================
    # モデル学習用データの生成
    # =========================
    # 時系列の月間推移データをベースとしてAI学習に回す
    monthly_df = build_monthly_dataset(df)

    return monthly_df, graph_data


# =========================================================
# ■ グラフ用データの統合管理
# =========================================================
def build_graph_data(df):
    return {
        "age_graph": extract_age_graph(df),
        "attendance_graph": extract_attendance_graph(df),
        "monthly_graph": extract_month_graph(df),
        "month_graph": extract_month_summary(df),
        "grade_graph": extract_grade_graph(df),
        "years_graph": extract_years_graph(df),
    }


# =========================================================
# ■ 各分析軸のデータ抽出ロジック
# =========================================================
#月齢 (B～D列)
def extract_age_graph(df):
    sub = df.iloc[2:75, 1:4].copy()
    sub.columns = ["月齢"] + CHILDREN
    for child in CHILDREN:
        sub[child] = pd.to_numeric(sub[child], errors="coerce")
    return sub

#登園月数 (F～H列)
def extract_attendance_graph(df):
    sub = df.iloc[2:63, 5:8].copy()
    sub.columns = ["登園月数"] + CHILDREN
    for child in CHILDREN:
        sub[child] = pd.to_numeric(sub[child], errors="coerce")
    return sub

#月間 (J～L列)
def extract_month_graph(df):
    sub = df.iloc[2:63, 9:12].copy()
    sub.columns = ["期間"] + CHILDREN
    for child in CHILDREN:
        sub[child] = pd.to_numeric(sub[child], errors="coerce")
    return sub

#月 (N～P列)
def extract_month_summary(df):
    sub = df.iloc[2:14, 13:16].copy()
    sub.columns = ["月"] + CHILDREN
    for child in CHILDREN:
        sub[child] = pd.to_numeric(sub[child], errors="coerce")
    return sub

#学年 (R～T列)
def extract_grade_graph(df):
    sub = df.iloc[2:9, 17:20].copy()
    sub.columns = ["クラス"] + CHILDREN
    for child in CHILDREN:
        sub[child] = pd.to_numeric(sub[child], errors="coerce")
    return sub

#登園年数 (V～X列)
def extract_years_graph(df):
    sub = df.iloc[2:8, 21:24].copy()
    sub.columns = ["登園年数"] + CHILDREN
    for child in CHILDREN:
        sub[child] = pd.to_numeric(sub[child], errors="coerce")
    return sub


# =========================================================
# ■ 学習用データ生成（モデル入力用）
# =========================================================
def build_monthly_dataset(df):
    # 時系列データを抽出し、特徴量生成側へ引き渡す（未入園の判定は次工程で行う）
    return extract_month_graph(df)