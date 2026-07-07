import numpy as np
import pandas as pd
from config import IMPUTATION_METHOD, WINDOW_SIZE ,FEATURE_COUNT

# ==========================================================
# ■ タイムウィンドウの設定（スライディングウィンドウ法）
# ==========================================================

def remove_long_missing_period(series, threshold=3):
    """
    3か月以上連続する欠損期間を除外する。
    入園前・一時退園などの対象外期間を削除する。
    """

    is_nan = series.isna()

    # NaN / 非NaNの切り替わりごとにグループ化
    groups = (is_nan != is_nan.shift()).cumsum()

    remove_idx = []

    for _, group in series.groupby(groups):
        if group.isna().all() and len(group) >= threshold:
            remove_idx.extend(group.index)

    return series.drop(remove_idx)


def create_stability_dataset(monthly_df, child_name):
    """
    【概要】生系列データから、入園前期間を除外し、入園後の欠損値を適切に補完した上で特徴量を生成します。
    入園前のデータを一律0埋めせず削除することで、免疫獲得トレンドの歪みを防止します。
    """
    # 対象児童の時系列データを取得
    raw_series = monthly_df[child_name].copy()

    first_valid_idx = raw_series.first_valid_index()

    if first_valid_idx is None:
        return np.empty((0, FEATURE_COUNT)), np.empty((0,))


    # 入園前を除外
    admitted_series = raw_series.loc[first_valid_idx:]


    # 3か月以上連続空欄を除外
    admitted_series = remove_long_missing_period(
        admitted_series,
        threshold=3
    )


    # 残った短期間欠測だけ補完
    if admitted_series.isna().sum() > 0:

        if IMPUTATION_METHOD == "median":

            fill_value = admitted_series.median()

            if np.isnan(fill_value):
                fill_value = 0.0

            admitted_series = admitted_series.fillna(fill_value)

        else:
            admitted_series = admitted_series.fillna(0.0)

    # 統計計算用に型を確定させ、インデックスを初期化
    series = admitted_series.astype(float).reset_index(drop=True)

    X = []
    y = []

    # トリミングした結果、入園後の在籍期間がウィンドウサイズ（6ヶ月）以下の場合はスキップ
    if len(series) <= WINDOW_SIZE:
        return np.empty((0, FEATURE_COUNT)), np.empty((0,))

    # ------------------------------------------------------
    # 2. 特徴量エンジニアリング（統計的アプローチ）
    # ------------------------------------------------------
    for i in range(WINDOW_SIZE, len(series)):
        # 直近6ヶ月間のデータスライス（窓）を抽出
        window= series.iloc[i - WINDOW_SIZE:i]

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