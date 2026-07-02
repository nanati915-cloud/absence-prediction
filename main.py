from data_processing import preprocess
from feature_engineering import create_stability_dataset
from train_model import train_model
from predict import run_future_prediction
from visualization import create_all_graphs, create_future_graphs
from report_generator import ReportGenerator
from config import TEMPLATE_PATH, REPORT_DIR, REPORT_FILENAME_FORMAT

def main():
    """
    【概要】保育園欠席予測システムのメイン実行エントリーポイント（全体パイプライン）。
    【アピール点】前処理、特徴量生成、モデル学習、未来予測、可視化、帳票出力までの
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
    # 園児ごとの過去の健康傾向を示す各種グラフを自動で一括描画・保存します。
    create_all_graphs(graph_data)
    print("グラフ出力完了")

    # ------------------------------------------
    # ターゲット児童（カラム名）の動的抽出
    # ------------------------------------------
    # Excel内の児童数が「2人」でも「100人」でも柔軟に対応できるよう、
    # 「期間」列以外のすべての児童名をループ対象として動的に取得します（拡張性の担保）。
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

        # 児童一人ひとりの体質・傾向に完全パーソナライズされたAIモデル（LightGBM）を個別に学習
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
    # AIが予測した24ヶ月先までの欠席予測値と、事前に設定した「健康安定化基準（月2日以下）」を
    # 照らし合わせた「未来リスク視覚化グラフ」を生成します。
    create_future_graphs(results)
    print("未来グラフ出力完了")

    # ==========================================
    # ■ 6. 自動レポート生成 (成果物出力フェーズ)
    # ==========================================
    from excel_writer import ExcelWriter
    from cell_map import CELL_MAP
    from text_builder import TextBuilder
    from datetime import datetime # 日付取得用

    # ① まず出力ファイル名をここで定義する
    filename = REPORT_FILENAME_FORMAT.format(
        date=datetime.now().strftime("%Y%m%d")
    )
    output_path = REPORT_DIR / filename
    
    # ② 定義した output_path を使って writer を作成
    writer = ExcelWriter(TEMPLATE_PATH, output_path) 
    
    # ③ 部品をすべて渡して初期化し、実行
    report = ReportGenerator(writer, CELL_MAP, TextBuilder())
    report.run(results, graph_data, monthly_df)
    
    print(f"レポート出力完了: {output_path}")

if __name__ == "__main__":
    main()