from datetime import datetime
from config import TEMPLATE_PATH, REPORT_DIR, REPORT_FILENAME_FORMAT
from cell_map import CELL_MAP
from excel_writer import ExcelWriter
from text_builder import TextBuilder

class ReportGenerator:
    """
    【概要】AIの分析・予測結果、および可視化した全グラフを、Excelテンプレートへ自動流し込みする帳票生成エンジン。
    【アピール点】データ（ロジック）と、Excelの配置情報（レイアウト）を『CELL_MAP』を介して完全分離しています。
    これにより、Excelのデザインやセルの位置が将来的に変更されても、このプログラムを1行も修正することなく対応できる
    高い「保守性」と「柔軟性」を実現しています。
    """
    def __init__(self):
        # 実行当日の日付（例: 20260701）を組み込んだユニークな出力ファイル名を動的に生成
        filename = REPORT_FILENAME_FORMAT.format(
            date=datetime.now().strftime("%Y%m%d")
        )
        self.output_path = REPORT_DIR / filename
        
        # テンプレートをベースに、スタイル（フォントや色、罫線）を維持したまま上書きするためのWriterを初期化
        self.writer = ExcelWriter(TEMPLATE_PATH, self.output_path)
        
        # 統計データから文脈に合わせた自然な日本語（考察文・業務改善提案）を動的生成するテキストビルダーを初期化
        self.text = TextBuilder()

    def run(self, results, graph_data, monthly_df):
        print("レポート生成開始")
        today = datetime.now().strftime("%Y/%m/%d")

        # ==================================================
        # ■ 1. 「表紙」シート処理（トレーサビリティの担保）
        # ==================================================
        # レポートの発行日を動的に書き込み、帳票としての信頼性を確保します。
        sheet, cell = CELL_MAP.get("cover_date", CELL_MAP.get("date"))
        self.writer.write_cell(sheet, cell, today)

        # ==================================================
        # ■ 2. 「2」シート：分析サマリー（経営層向けサマリー）
        # ==================================================
        # 園の経営層や施設長が「一目で全体の動向を把握できる」よう、
        # 過去の傾向、未来の予測、業務への具体的なアクションプランを一箇所に集約。
        sheet, cell = CELL_MAP["summary_trend"]
        self.writer.write_cell(sheet, cell, self.text.trend_analysis(graph_data, results))
        
        sheet, cell = CELL_MAP["summary_future"]
        self.writer.write_cell(sheet, cell, self.text.future_prediction_summary(graph_data, results))
        
        sheet, cell = CELL_MAP["summary_business"]
        self.writer.write_cell(sheet, cell, self.text.business_improvement(graph_data, results))

        # ==================================================
        # ■ 3. 「3」〜「5」シート：過去統計分析グラフの自動挿入
        # ==================================================
        # 各分析軸のグラフを対応するシート・セルへ一括マッピング。
        # 【技術的工夫】height（高さ）を None に指定し width（横幅）のみを固定することで、
        # 元グラフの縦横比（アスペクト比）を綺麗に維持したまま、Excelが歪むことなく高解像度で挿入されます。
        
        # シート3：分析① 月齢別 / 分析② 学年別
        sheet, cell = CELL_MAP["age_chart"]
        self.writer.insert_image(sheet, "output/graphs/月齢別欠席日数.png", cell=cell, width=520, height=None)
        sheet, cell = CELL_MAP["grade_chart"]
        self.writer.insert_image(sheet, "output/graphs/学年別欠席日数.png", cell=cell, width=520, height=None)

        # シート4：分析③ 登園月数 / 分析④ 登園年数別
        sheet, cell = CELL_MAP["attendance_chart"]
        self.writer.insert_image(sheet, "output/graphs/登園月数別欠席日数.png", cell=cell, width=520, height=None)
        sheet, cell = CELL_MAP["years_chart"]
        self.writer.insert_image(sheet, "output/graphs/登園年数別欠席日数.png", cell=cell, width=520, height=None)

        # シート5：分析⑤ 月間 / 分析⑥ 月別推移
        sheet, cell = CELL_MAP["monthly_chart"]
        self.writer.insert_image(sheet, "output/graphs/月間欠席推移.png", cell=cell, width=520, height=None)
        sheet, cell = CELL_MAP["month_chart"]
        self.writer.insert_image(sheet, "output/graphs/月別欠席日数.png", cell=cell, width=520, height=None)

        # ==================================================
        # ■ 4. 「6」シート：分析 傾向考察（現場保育士向けの示唆）
        # ==================================================
        # グラフから読み解くべき詳細な考察と、具体的な業務改善の提案テキストを埋め込みます。
        sheet, cell = CELL_MAP["trend_analysis"]
        self.writer.write_cell(sheet, cell, self.text.trend_analysis(graph_data, results))

        sheet, cell = CELL_MAP["business_improvement"]
        self.writer.write_cell(sheet, cell, self.text.business_improvement(graph_data, results))

        # ==================================================
        # ■ 5. 「7」シート：分析⑦ 未来リスク（AIシミュレーション結果）
        # ==================================================
        # AIが予測した未来リスク曲線を、園児ごとに縦並びで配置。
        # 【レイアウト崩れ対策】縦横比維持による画像の被りを防ぐため、
        # 2枚目の開始位置は cell_map.py 側で十分な余白（例: B20 等）を確保する設計を推奨しています。
        sheet, cell1 = CELL_MAP["future_risk_chart1"]
        self.writer.insert_image(sheet, "output/graphs/子供001_未来リスク曲線.png", cell=cell1, width=520, height=None)
        
        sheet, cell2 = CELL_MAP["future_risk_chart2"]
        self.writer.insert_image(sheet, "output/graphs/子供002_未来リスク曲線.png", cell=cell2, width=520, height=None)

        # ==================================================
        # ■ 6. 「8」シート：総合（最終結論と意思決定の支援）
        # ==================================================
        # 統計とAI予測を包括した全体の総括、および最終的なネクストステップ（結論）を流し込みます。
        sheet, cell = CELL_MAP["total_summary"]
        self.writer.write_cell(sheet, cell, self.text.overall_summary(graph_data, results))

        sheet, cell = CELL_MAP["total_conclusion"]
        self.writer.write_cell(sheet, cell, self.text.final_conclusion(graph_data, results))

        # ==================================================
        # ■ 7. ファイルの永続化とクローズ
        # ==================================================
        # メモリ上のデータを最終的な成果物（Excel）として物理ディスクへ書き出します。
        self.writer.save()
        print("レポート生成完了")