from pathlib import Path

# =========================================================
# ■ 1. パス・ディレクトリ構造の定義
# =========================================================
# システム内のすべてのファイル位置の基準となるルートディレクトリ（プログラムの配置場所）を自動取得します。
BASE_DIR = Path(__file__).resolve().parent

# 入力データ、Excelテンプレート、解析結果の出力先、AIモデルの保存先フォルダを定義
DATA_DIR = BASE_DIR / "data"
EXCEL_FILE = DATA_DIR / "欠席.xlsx"
SHEET_NAME = "病欠集約"

TEMPLATE_DIR = BASE_DIR / "template"
TEMPLATE_PATH = TEMPLATE_DIR / "報告書ひな形.xlsx"

OUTPUT_DIR = BASE_DIR / "output"
GRAPH_DIR = OUTPUT_DIR / "graphs"
REPORT_DIR = OUTPUT_DIR / "reports"

# =========================================================
# ■ 2. 環境の自動初期化（フォルダ自動生成）
# =========================================================
GRAPH_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# ■ 3. 機械学習（LightGBM）のハイパーパラメータ設定
# =========================================================

RANDOM_STATE = 42

# LightGBM
N_ESTIMATORS = 300
LEARNING_RATE = 0.05
MAX_DEPTH = 5
NUM_LEAVES = 31
MIN_CHILD_SAMPLES = 5
SUBSAMPLE = 0.8
COLSAMPLE_BYTREE = 0.8

# 予測区間（分位点回帰）の設定
LOWER_ALPHA = 0.05 #予測区間の下限（5%）を定義
UPPER_ALPHA = 0.95 #予測区間の上限（95%）を定義

# =========================================================
# ■ 4. 未来リスク予測および「健康安定化」の判定基準
# =========================================================
PREDICT_MONTHS = 24
STABLE_THRESHOLD = 2
STABLE_MONTHS = 6
WINDOW_SIZE = 6

# 傾向分析において「増加・減少」と判定する平均差（日）
TREND_THRESHOLD = 0.5
# 季節性の影響があると判定する閾値（日）
SEASON_THRESHOLD = 0.5

# =========================================================
# ■ 5. データサイエンス・欠損値処理ポリシーの設定
# =========================================================
# 入園「後」に発生した突発的な記録漏れ（欠損値）をどう補完するかを定義
# 'median': その子の過去の中央値で埋める（極端な外れ値に強く、最も標準的で妥当性が高い）
# 'zero': 一律0日として埋める
IMPUTATION_METHOD = "median"

# =========================================================
# ■ 6. 成果物レポートの設定
# =========================================================
REPORT_FILENAME_FORMAT = "{date}_欠席分析報告書.xlsx"