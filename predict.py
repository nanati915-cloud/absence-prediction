import numpy as np
import pandas as pd
from config import PREDICT_MONTHS, STABLE_THRESHOLD, STABLE_MONTHS

# ==========================================================
# ■ 1. 推論用・特徴量リアルタイム生成関数
# ==========================================================
def build_features(window):
    """
    【概要】直近6ヶ月の窓データから、推論（予測）に必要な統計特徴量をリアルタイムに計算します。
    【工夫点】学習時（feature_engineering.py）と完全に同一の列名・順序を持った pandas.DataFrame 形式で
    データを成形して返却することで、LightGBMなどの機械学習ライブラリ特有の「列名不一致による警告（Warning）」を完全に解消しています。
    """
    window = np.array(window, dtype=float)
    mean = window.mean()
    std = window.std()
    maximum = window.max()
    minimum = window.min()
    
    # 6ヶ月前の起点と直近月との単純差分（全体トレンド）
    trend = window[-1] - window[0]

    # 直近とその前月との微細な変化量（直近のモメンタム）
    diff_last = 0
    if len(window) >= 2:
        diff_last = window[-1] - window[-2]

    # ウィンドウ内での「前月より悪化した回数」と「改善した回数」のカウント
    increasing = np.sum(np.diff(window) > 0)
    decreasing = np.sum(np.diff(window) < 0)

    # 機械学習モデルへ一貫したフォーマットで入力するための辞書マッピング
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
# ■ 2. 独自アルゴリズム：健康安定時期の自動検出（判定ロジック）
# ==========================================================
def detect_stable_month(series, threshold=STABLE_THRESHOLD, continue_month=STABLE_MONTHS):
    """
    【概要】AIが予測した未来の時系列データから、子供の体調が「安定圏」に突入する時期を自動算出します。
    【アルゴリズム】単に1ヶ月だけ閾値を下回った瞬間を捉えるのではなく、
    『閾値（例：月2日以下）を、設定期間（例：3ヶ月連続）で維持し続けた最初の月』をインデックス逆算によって検出します。
    これにより、突発的なノイズに惑わされない確実な「安定期」を特定できます。
    """
    count = 0
    for i, value in enumerate(series):
        if value <= threshold:
            count += 1
            if count >= continue_month:
                # 連続条件を満たした「突入の起点月」を算出して返す
                return i - continue_month + 2
        else:
            count = 0 # 途中で体調を崩した（閾値を超えた）場合はカウンターをリセット
    return None # 予測期間内に安定期が訪れない場合はNoneを返却

# ==========================================================
# ■ 3. 再帰的逐次予測（未来シミュレーション・メイン関数）
# ==========================================================
def run_future_prediction(model, monthly_df, child_name):
    """
    【概要】子供ごとの個別の学習済みモデルを用い、未来24ヶ月先までの欠席日数を「再帰的（オートレグレッシブ）」にシミュレート予測します。
    【アピール点】「AIの予測値を次の月の入力データとして使い、さらにその次の月を予測する」という
    スライディング・タイムウィンドウのループ処理を実装しており、限られた過去データからでも長期の健康予測を可能にしています。
    """
    history = (
        monthly_df[child_name]
        .dropna()
        .astype(float)
        .tolist()
    )

    # 過去データが6ヶ月未満の新規入子供などの場合、平均値ベースのセーフティ値を返してシステム停止を防ぐガード設定
    if len(history) < 6:
        return {
            "future_series": history,
            "predicted_absence": np.mean(history) if history else 0,
            "stable_month": None
        }

    future = []
    work = history.copy() # 予測値を順次追加していくシミュレーション用のワークリスト

    # ------------------------------------------------------
    # 逐次シミュレーション・ループ（例：24回繰り返して2年先まで予測）
    # ------------------------------------------------------
    for _ in range(PREDICT_MONTHS):
        # 常に最新の「直近6ヶ月分」のデータを切り出す
        window = work[-6:]
        
        # 切り出したデータから8つの統計特徴量を抽出
        X = build_features(window)
        
        # AIモデルによる次月（1ヶ月先）の予測を実行
        pred = model.predict(X)[0]
        
        # 【ビジネスルール・ガード】計算ノイズにより欠席日数が「マイナス（負の値）」になる物理的矛盾を強力に防止
        pred = max(float(pred), 0)
        
        # 予測結果を成果物リストと、次の予測のための入力データ（work）の末尾へ同時に追加
        future.append(pred)
        work.append(pred)

    # 24ヶ月の予測系列が完成した後、独自アルゴリズムで「安定化する時期」を特定
    stable = detect_stable_month(future)

    return {
        "future_series": future,                       # 未来24ヶ月の予測値の時系列リスト
        "predicted_absence": float(np.mean(future)), # 予測期間中の平均欠席日数（全体リスクの指標）
        "stable_month": stable                         # 「〇ヶ月後に安定化するか」の答え（Noneの場合は判定不可）
    }