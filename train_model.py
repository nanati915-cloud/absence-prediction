from lightgbm import LGBMRegressor
from config import RANDOM_STATE


def _create_model(objective="regression", alpha=None):
    """
    LightGBMモデル生成
    """

    params = {
        "objective": objective,
        "n_estimators": 300,
        "learning_rate": 0.05,
        "max_depth": 5,
        "num_leaves": 31,
        "min_child_samples": 5,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": RANDOM_STATE,
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
            "lower": 下限予測モデル(5%),
            "upper": 上限予測モデル(95%)
        }
    """

    if len(X) == 0:
        raise ValueError("学習データがありません。")

    # 中央値（通常予測）
    median_model = _create_model()
    median_model.fit(X, y)

    # 下限5%
    lower_model = _create_model(
        objective="quantile",
        alpha=0.05
    )
    lower_model.fit(X, y)

    # 上限95%
    upper_model = _create_model(
        objective="quantile",
        alpha=0.95
    )
    upper_model.fit(X, y)

    return {
        "median": median_model,
        "lower": lower_model,
        "upper": upper_model,
    }