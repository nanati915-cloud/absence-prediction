"""
LightGBMを用いた機械学習モデルを学習する。
中央値予測および予測区間モデルを生成する。
"""

from lightgbm import LGBMRegressor
from config import RANDOM_STATE, N_ESTIMATORS, LEARNING_RATE, MAX_DEPTH, NUM_LEAVES, MIN_CHILD_SAMPLES, SUBSAMPLE, COLSAMPLE_BYTREE, LOWER_ALPHA, UPPER_ALPHA


def _create_model(objective="regression", alpha=None):
    """
    LightGBMモデル生成
    """

    params = {
        # 学習目的（regression：通常回帰、quantile：分位点回帰）
        "objective": objective,
        # 作成する決定木の数（増やすと表現力が上がるが、学習時間も増加する）
        "n_estimators": N_ESTIMATORS,
        # 各決定木の予測結果をどれだけ反映するか（小さいほど学習は緩やかになる）
        "learning_rate": LEARNING_RATE,
        # 決定木の深さ（深いほど複雑なルールを学習するが過学習しやすい）
        "max_depth": MAX_DEPTH,
        # 1本の決定木が持つ葉（終端ノード）の最大数（増やすと複雑なパターンを学習できるが過学習しやすい）
        "num_leaves": NUM_LEAVES,
        # 葉を作るために必要な最小データ数（小さいほど複雑なモデルになりやすい）
        "min_child_samples": MIN_CHILD_SAMPLES,
        # 各決定木の学習に使用するデータ割合（小さくすると過学習抑制につながる）
        "subsample": SUBSAMPLE,
        # 各決定木で使用する特徴量の割合（小さくすると過学習を抑えやすい）
        "colsample_bytree": COLSAMPLE_BYTREE,
        # 乱数を固定（毎回同じ学習結果を再現できる）
        "random_state": RANDOM_STATE,
        # 学習ログを非表示（0以上にすると学習状況を表示）
        "verbose": -1,
    }

    # 分位点回帰の場合のみ予測する分位点を設定
    if objective == "quantile":
        params["alpha"] = alpha

    return LGBMRegressor(**params)


def train_model(X, y):
    """
    回帰モデルと予測区間モデルを学習する。

    Returns
    -------
    dict
        {
            "median": 中央値予測モデル,
            "lower": 下限予測モデル(config.pyで制御),
            "upper": 上限予測モデル(config.pyで制御)
        }
    """

    if len(X) == 0:
        raise ValueError("学習データがありません。")

    # 中央値（通常予測）
    median_model = _create_model()
    median_model.fit(X, y)

    # 下限
    lower_model = _create_model(
        objective="quantile",
        alpha=LOWER_ALPHA
    )
    lower_model.fit(X, y)

    # 上限
    upper_model = _create_model(
        objective="quantile",
        alpha=UPPER_ALPHA
    )
    upper_model.fit(X, y)

    return {
        "median": median_model,
        "lower": lower_model,
        "upper": upper_model,
    }