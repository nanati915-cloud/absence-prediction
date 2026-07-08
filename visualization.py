"""
分析結果をグラフとして可視化する。
Excel報告書へ貼り付ける画像を生成する。
"""

import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
from config import GRAPH_DIR, PREDICT_MONTHS

def savefig(filename):
    """グラフ画像ファイルの出力フルパスを解決するヘルパー関数"""
    return GRAPH_DIR / filename

# ==========================================================
# ■ 1. 統計分析用：共通折れ線グラフ（時系列・推移の可視化）
# ==========================================================
def create_line_graph(df, x_col, title, filename):
    """
    【概要】月齢、学年、登園期間などの『連続的な変化トレンド』を抽出するための折れ線グラフを生成。
    複数児童のデータを1つのグラフに動的プロットし、個人のノイズに囚われない全体の傾向線を一目で比較可能にしています。
    """
    # Excel報告書のセル幅（520px）にジャストフィットするアスペクト比（10:4）を黄金比として採用
    plt.figure(figsize=(10, 4))
    x = df[x_col].astype(str)

    for col in df.columns:
        if col == x_col:
            continue
        # マーカー（o）と程よい線の太さ（linewidth=2）を適用し、視認性の向上
        plt.plot(x, df[col], marker="o", linewidth=2, label=col)

    plt.title(title)
    plt.ylabel("欠席日数")
    plt.xticks(rotation=90) # X軸のラベル（〇歳児クラス、年月など）の重なりを防ぐ90度回転処理
    plt.legend()
    plt.tight_layout() # レイアウトの自動最適化（ラベルの端が切れる現象を完全にシャットアウト）
    plt.savefig(savefig(filename), dpi=200) # 印刷やExcel埋め込みに耐えうる、高解像度（DPI=200）での書き出し
    plt.close()

# ==========================================================
# ■ 2. 統計分析用：共通棒グラフ（季節性・個別数値の比較）
# ==========================================================
def create_bar_graph(df, x_col, title, filename):
    """
    【概要】「何月に欠席が多いか」など、独立したカテゴリー間の『絶対量の差』を明快に比較するための並列棒グラフを生成。
    """
    plt.figure(figsize=(10, 4))
    x = np.arange(len(df))
    width = 0.35 # 児童ごとの棒が被らないよう、適切なマージンを持った棒幅
    children = [c for c in df.columns if c != x_col]

    for i, child in enumerate(children):
        # グループごとにX軸の位置を計算し、児童同士の数値を綺麗に「並列並び（Side-by-Side）」でプロット
        plt.bar(x + (i - 0.5) * width, df[child], width, label=child)

    plt.xticks(x, df[x_col].astype(str))
    plt.title(title)
    plt.ylabel("欠席日数")
    plt.legend()
    plt.tight_layout()
    plt.savefig(savefig(filename), dpi=200)
    plt.close()

# ==========================================================
# ■ 3. 統計グラフの一括制御タスク
# ==========================================================
def create_all_graphs(graph_data):
    """メインロジックから呼び出され、過去統計の全5軸＋時系列推移の計6枚のグラフをワンストップで自動生成。"""
    # 1. 分析① 月齢別
    create_line_graph(graph_data["age_graph"], "月齢", "月齢別欠席日数", "月齢別欠席日数.png")
    # 2. 分析② 学年別
    create_line_graph(graph_data["grade_graph"], "クラス", "学年別欠席日数", "学年別欠席日数.png")
    # 3. 分析③ 登園月数別
    create_line_graph(graph_data["attendance_graph"], "登園月数", "登園月数別欠席日数", "登園月数別欠席日数.png")
    # 4. 分析④ 登園年数別
    create_line_graph(graph_data["years_graph"], "登園年数", "登園年数別欠席日数", "登園年数別欠席日数.png")
    # 5. 分析⑤ 月間推移（時系列変化）
    create_line_graph(graph_data["monthly_graph"], "期間", "月間欠席推移", "月間欠席推移.png")
    # 6. 分析⑥ 月別（季節性）
    create_bar_graph(graph_data["month_graph"], "月", "月別欠席日数", "月別欠席日数.png")

# ==========================================================
# ■ 4. AI予測用：未来リスクシミュレーション曲線（予測の可視化）
# ==========================================================
def create_future_risk_curve(result, child_name):
    """
    【概要】AI（LightGBM）が24ヶ月先までシミュレーションした『未来の欠席リスク』をプロット。
    ただの線グラフではなく、AIモデル独自の基準値を下回った瞬間（安定開始月）を
    赤い「赤垂直破線」で自動プロットし、現場に一目で改善時期を伝えるUXデザインを実現しています。
    """
    future = result["future_series"]
    months = np.arange(1, len(future) + 1)
    plt.figure(figsize=(10, 4))
    
    # 将来予測の軌跡をプロット
    plt.plot(months, future, marker="o", linewidth=2, label="予測欠席日数")
    
    # 【ビジュアル演出】予測線の下部をシアン調のグラデーション（fill_between）で塗り潰し、
    # 報告書内での「未来の蓄積リスク」としての重大性を視覚的に強調
    plt.fill_between(months, future, alpha=0.2)
    
    # AIが算出した「安定化に到達する月」を検知し、予測線上にマイルストーン（垂直線）を動的マーク
    stable = result["stable_month"]
    if stable is not None:
        plt.axvline(stable, color="red", linestyle="--", label=f"安定開始（{stable}ヶ月後）")

    plt.title(f"{child_name} 未来欠席予測")
    plt.xlabel("未来（月）")
    plt.ylabel("予測欠席日数")
    plt.xticks(range(1, PREDICT_MONTHS + 1, 2)) # 目盛りの間隔を2ヶ月おきにしてスッキリさせる工夫
    plt.grid(alpha=0.3) # 背景にうっすらとしたグリッド線を敷き、数値の読み取りをサポート
    plt.legend()
    plt.tight_layout()
    plt.savefig(savefig(f"{child_name}_未来リスク曲線.png"), dpi=200)
    plt.close()

# ==========================================================
# ■ 5. 未来グラフの一括制御タスク
# ==========================================================
def create_future_graphs(results):
    """子供ごとに独立したデータ構造を持つAI結果をループ処理し、各児童専用の未来予測グラフを全自動生成。"""
    for child, result in results.items():
        create_future_risk_curve(result, child)