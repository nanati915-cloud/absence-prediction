import numpy as np
import pandas as pd
from config import IMPUTATION_METHOD

# ==========================================================
# ■ タイムウィンドウの設定（スライディングウィンドウ法）
# ==========================================================
WINDOW = 6

def create_stability_dataset(monthly_df, child_name):
    """
    【概要】生系列データから、入園前期間を除外し、入園後の欠損値を適切に補完した上で特徴量を生成します。
    【妥当性】入園前のデータを一律0埋めせず削除することで、免疫獲得トレンドの歪みを防止します。
    """
    # 対象児童の時系列データを取得
    raw_series = monthly_df[child_name].copy()

    # ------------------------------------------------------
    # 1. 段階的欠損値処理 (入園前と入園後の場合分け)
    # ------------------------------------------------------
    # 【処理A】入園月（最初の有効なデータが記録された位置）を特定
    first_valid_idx = raw_series.first_valid_index()
    
    if first_valid_idx is None:
        # 有効なデータが1件もない場合は、安全に空の配列を返す
        return np.empty((0, 8)), np.empty((0,))
        
    # 入園前の未在籍期間をデータセットから完全に「削除」（データサイエンス的妥当性の担保）
    admitted_series = raw_series.loc[first_valid_idx:]

    # 【処理B】入園「後」の記録漏れ（途中に残ったNaN）の補完（インピュテーション）
    if admitted_series.isna().sum() > 0:
        if IMPUTATION_METHOD == "median":
            # その児童自身の過去の中央値で補完（外れ値に強く、欠席ベースラインを壊さない）
            fill_value = admitted_series.median()
            # 過去データが少なすぎて中央値がNaNの場合は0でセーフティガード
            if np.isnan(fill_value):
                fill_value = 0.0
            admitted_series = admitted_series.fillna(fill_value)
        else:
            # Policyがzero、またはその他の場合は安全のため0日欠席として処理
            admitted_series = admitted_series.fillna(0.0)

    # 統計計算用に型を確定させ、インデックスを初期化
    series = admitted_series.astype(float).reset_index(drop=True)

    X = []
    y = []

    # トリミングした結果、入園後の在籍期間がウィンドウサイズ（6ヶ月）以下の場合はスキップ
    if len(series) <= WINDOW:
        return np.empty((0, 8)), np.empty((0,))

    # ------------------------------------------------------
    # 2. 特徴量エンジニアリング（統計的アプローチ）
    # ------------------------------------------------------
    for i in range(WINDOW, len(series)):
        # 直近6ヶ月間のデータスライス（窓）を抽出
        window = series.iloc[i - WINDOW:i]

        mean = window.mean()
        std = window.std()
        if np.isnan(std):
            std = 0.0  

        maximum = window.max()
        minimum = window.min()
        trend = window.iloc[-1] - window.iloc[0]
        diff_last = window.iloc[-1] - mean
        increasing = np.sum(np.diff(window) > 0)
        decreasing = np.sum(np.diff(window) < 0)

        features = [
            mean,
            std,
            maximum,
            minimum,
            trend,
            diff_last,
            increasing,
            decreasing,
        ]
        X.append(features)

        # 3. 教師あり学習用「正解ラベル」の生成
        next_value = float(series.iloc[i])
        y.append(next_value)

    X = np.array(X, dtype=float)
    y = np.array(y, dtype=float)

    return X, y