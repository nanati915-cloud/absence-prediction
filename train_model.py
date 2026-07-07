from lightgbm import LGBMRegressor
from config import RANDOM_STATE, N_ESTIMATORS, LEARNING_RATE, MAX_DEPTH, NUM_LEAVES, MIN_CHILD_SAMPLES, SUBSAMPLE, COLSAMPLE_BYTREE, LOWER_ALPHA, UPPER_ALPHA


def _create_model(objective="regression", alpha=None):
    """
    LightGBMモデル生成
    """

    params = {
        # 学習方法を指定（regression：数値予測、binary：2値分類）
        "objective": objective,
        # 決定木を何本作るか（増やすと精度↑・学習時間↑）
        "n_estimators": N_ESTIMATORS,
        # 1回の学習でどれだけ修正するか（小さいほどゆっくり・安定して学習）
        "learning_rate": LEARNING_RATE,
        # 決定木の深さ（深いほど複雑なルールを学習するが過学習しやすい）
        "max_depth": MAX_DEPTH,
        # 木の葉（終端ノード）の最大数（増やすと複雑な予測が可能）
        "num_leaves": NUM_LEAVES,
        # 1つの葉に必要な最小データ数（小さいほど細かく学習する）
        "min_child_samples": MIN_CHILD_SAMPLES,
        # 学習時に使用するデータの割合（1.0なら全データ、0.8なら80%　小さくすると過学習を抑えやすい）
        "subsample": SUBSAMPLE,
        # 学習時に使用する特徴量の割合（1.0なら全特徴量、0.8なら80%　小さくすると過学習を抑えやすい）
        "colsample_bytree": COLSAMPLE_BYTREE,
        # 乱数を固定（毎回同じ学習結果を再現できる）
        "random_state": RANDOM_STATE,
        # 学習ログを非表示（0以上にすると学習状況を表示）
        "verbose": -1,
    }

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