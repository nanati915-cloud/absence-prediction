# =========================================
# ■ Excelレポートのセル定義
# =========================================
# 新しいテンプレExcelのシート構造とセル配置の定義

CELL_MAP = {
    # 「表紙」シート
    "cover_date": ("表紙", "J44"),

    # 「2」シート：分析サマリー
    "summary_trend": ("2", "B7"),        # 主な傾向 (B7～AC16)
    "summary_future": ("2", "B20"),      # 未来予測結果 (B20～AC29)
    "summary_business": ("2", "B33"),    # 業務への示唆 (B33～AC42)

    # 「3」シート
    "age_chart": ("3", "B4"),            # 分析① 月齢別 (B4～AC24)
    "grade_chart": ("3", "B27"),         # 分析② 学年別 (B27～AC45)

    # 「4」シート
    "attendance_chart": ("4", "B4"),     # 分析③ 登園月数 (B4～AC24)
    "years_chart": ("4", "B27"),         # 分析④ 登園年数別 (B27～AC45)

    # 「5」シート
    "monthly_chart": ("5", "B4"),        # 分析⑤ 月間 (B4～AC24)
    "month_chart": ("5", "B27"),         # 分析⑥ 月別推移 (B27～AC45)

    # 「6」シート：分析 傾向考察
    "trend_analysis": ("6", "B6"),       # 考察 (B6～AC14)
    "business_improvement": ("6", "B18"), # 業務改善提案 (B18～AC25)

    # 「7」シート：分析⑦ 未来リスク
    "future_risk_chart1": ("7", "B4"),   # 子供001 (B4〜)
    "future_risk_chart2": ("7", "B16"),  # 子供002 (B16〜 縦並び用)

    # 「8」シート
    "total_summary": ("8", "B4"),        # 総合所見 (B4～AC11)
    "total_conclusion": ("8", "B16"),    # 結論 (B16～AC23)
}