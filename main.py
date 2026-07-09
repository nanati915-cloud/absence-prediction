"""
欠席予測システムの実行エントリーポイント。

データ読み込み、前処理、特徴量生成、モデル学習、
未来予測、可視化、Excelレポート生成までの処理を統括する。
"""

from data_processing import preprocess
from feature_engineering import create_stability_dataset
from train_model import train_model
from predict import run_future_prediction
from visualization import create_all_graphs, create_future_graphs
from report_generator import ReportGenerator
from config import TEMPLATE_PATH, REPORT_DIR, REPORT_FILENAME_FORMAT
from excel_writer import ExcelWriter
from cell_map import CELL_MAP
from text_builder import TextBuilder
from datetime import datetime # 日付取得用

def main():
    """
    【概要】欠席予測システムのメイン実行エントリーポイント（全体パイプライン）。
    前処理、特徴量生成、モデル学習、未来予測、可視化、帳票出力までの
    一連のデータサイエンス・ワークフローを完全に自動化し、ワンショットで実行可能にしています。
    """
    print("欠席予測プロジェクト開始")

    # ==========================================
    # ■ 1. データの読み込みと前処理 (ETLフェーズ)
    # ==========================================
    # 生データ（Excel）から、機械学習用の時系列データ(monthly_df)と、
    # 統計グラフ用の多軸データ(graph_data)を分離・生成します。
    monthly_df, graph_data = preprocess()

    # ==========================================
    # ■ 2. 過去の欠席傾向の可視化 (EDAフェーズ)
    # ==========================================
    # 読み込んだ統計データから、月齢別、学年別、季節別など、
    # 子供ごとの過去の欠席傾向を示す各種グラフを生成します。
    create_all_graphs(graph_data)
    print("グラフ出力完了")

    # ------------------------------------------
    # ターゲット児童（カラム名）の動的抽出
    # ------------------------------------------
    children = [col for col in monthly_df.columns if col != "期間"]
    
    models = {}
    results = {}

    # ==========================================
    # ■ 3. 機械学習（AIモデルのループ学習フェーズ）
    # ==========================================
    print("学習開始")
    for child in children:
        # 各児童の過去の時系列データから、8つの統計特徴量（X）と次月正解ラベル（y）を生成
        X, y = create_stability_dataset(monthly_df, child)

        # 途中入園直後などで、過去データがウィンドウサイズ（6ヶ月）に満たない児童のバグを回避
        if len(X) == 0:
            print(f"{child}：学習データ不足のためスキップ")
            continue

        # 児童ごとの過去データを用いて個別のLightGBMモデルを学習
        model = train_model(X, y)
        models[child] = model # 学習済みモデルを児童名と紐づけて保持

    print("学習完了")

    # ==========================================
    # ■ 4. 未来リスク予測（シミュレーションフェーズ）
    # ==========================================
    print("未来予測開始")
    for child in children:
        if child not in models:
            continue

        # 直近のデータを起点に、configで定義された24ヶ月（2年間）先までの
        # 未来の月間欠席日数を、AIモデルを用いて再帰的にシミュレーション予測します。
        result = run_future_prediction(models[child], monthly_df, child)
        results[child] = result

    print("未来予測完了")

    # ==========================================
    # ■ 5. 未来予測リスクの可視化
    # ==========================================
    # 設定した欠席日数基準と照らし合わせた未来予測グラフを生成
    create_future_graphs(results)
    print("未来グラフ出力完了")

    # ==========================================
    # ■ 6. 自動レポート生成 (成果物出力フェーズ)
    # ==========================================
    # ① まず出力ファイル名をここで定義する
    filename = REPORT_FILENAME_FORMAT.format(
        date=datetime.now().strftime("%Y%m%d")
    )
    output_path = REPORT_DIR / filename
    
    # ② 定義した output_path を使って writer を作成
    writer = ExcelWriter(TEMPLATE_PATH, output_path) 
    
    # ③ 部品をすべて渡して初期化し、実行
    report = ReportGenerator(writer, CELL_MAP, TextBuilder())
    report.run(results, graph_data)
    
    print(f"レポート出力完了: {output_path}")

if __name__ == "__main__":
    main()