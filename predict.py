import numpy as np
import pandas as pd
from config import PREDICT_MONTHS, STABLE_THRESHOLD, STABLE_MONTHS

# ==========================================================
# ■ 1. 推論用・特徴量リアルタイム生成関数
# ==========================================================
def build_features(window):
    """
    【概要】直近6ヶ月の窓データから、推論（予測）に必要な統計特徴量をリアルタイムに計算します。
    """
    window = np.array(window, dtype=float)

    mean = window.mean()
    std = window.std()
    maximum = window.max()
    minimum = window.min()

    trend = window[-1] - window[0]

    diff_last = 0
    if len(window) >= 2:
        diff_last = window[-1] - window[-2]

    increasing = np.sum(np.diff(window) > 0)
    decreasing = np.sum(np.diff(window) < 0)

    feature_dict = {
        "mean": [mean],
        "std": [std],
        "maximum": [maximum],
        "minimum": [minimum],
        "trend": [trend],
        "diff_last": [diff_last],
        "increasing": [increasing],
        "decreasing": [decreasing]
    }

    return pd.DataFrame(feature_dict)


# ==========================================================
# ■ 2. 健康安定時期の自動検出
# ==========================================================
def detect_stable_month(series,
                        threshold=STABLE_THRESHOLD,
                        continue_month=STABLE_MONTHS):

    count = 0

    for i, value in enumerate(series):

        if value <= threshold:
            count += 1

            if count >= continue_month:
                return i - continue_month + 2

        else:
            count = 0

    return None


# ==========================================================
# ■ 3. 再帰的未来予測
# ==========================================================
def run_future_prediction(model, monthly_df, child_name):
    """
    AIモデルを用いて未来24ヶ月を再帰的に予測する。

    Returns
    -------
    dict
        future_series : 中央値予測
        future_lower  : 下限予測(5%)
        future_upper  : 上限予測(95%)
        predicted_absence : 平均予測欠席日数
        stable_month : 安定化時期
    """

    history = (
        monthly_df[child_name]
        .dropna()
        .astype(float)
        .tolist()
    )

    # データ不足
    if len(history) < 6:

        avg = float(np.mean(history)) if history else 0.0

        return {
            "future_series": history,
            "future_lower": history,
            "future_upper": history,
            "predicted_absence": avg,
            "stable_month": None
        }

    future = []
    future_lower = []
    future_upper = []

    work = history.copy()

    # ==========================================
    # 24ヶ月未来予測
    # ==========================================
    for _ in range(PREDICT_MONTHS):

        window = work[-6:]

        X = build_features(window)

        # 中央値
        pred = model["median"].predict(X)[0]

        # 下限
        lower = model["lower"].predict(X)[0]

        # 上限
        upper = model["upper"].predict(X)[0]

        pred = max(float(pred), 0)
        lower = max(float(lower), 0)
        upper = max(float(upper), 0)

        # 念のため上下が逆なら入れ替え
        if lower > upper:
            lower, upper = upper, lower

        future.append(pred)
        future_lower.append(lower)
        future_upper.append(upper)

        # 次月予測には中央値を使用
        work.append(pred)

    stable = detect_stable_month(future)

    return {
        "future_series": future,
        "future_lower": future_lower,
        "future_upper": future_upper,
        "predicted_absence": float(np.mean(future)),
        "stable_month": stable
    }