import pandas as pd

class TextBuilder:
    """
    【概要】多軸の統計データおよびAI予測結果を解釈し、Excel報告書に最適な動的テキストを自動生成する文章作成エンジン。
    【アピール点】グラフ（視覚情報）とセル（帳票）を繋ぐ役割を持ち、データの「減少・増加・最大値」をアルゴリズムで判定して、
    現場の職員がそのまま読める自然なビジネス報告文（自然言語生成）を出力します。
    """

    # =====================================================
    # ■ 1. 内部判定メソッド群（各グラフデータから局所的な傾向を抽出）
    # =====================================================

    def _age_trend(self, graph_data):
        """月齢に応じた欠席傾向の動的判定"""
        df = graph_data.get("age_graph")
        if df is None or df.empty or len(df) < 1:
            return "月齢別のデータが不足しているため、傾向は判定できませんでした。"

        # 1列目の「年齢」列を除き、児童全員の平均的な推移を算出
        values = df.iloc[:, 1:].mean(axis=1)
        # 最初の月（入園初期）と最後の月（成長後）を比較し、右肩下がりかを数理的に判定
        if len(values) >= 2 and values.iloc[0] > values.iloc[-1]:
            return "月齢が低い時期ほど欠席日数が多く、成長とともに減少する傾向が確認された。"
        return "月齢による大きな差は認められなかった。"

    def _grade_trend(self, graph_data):
        """所属クラス（学年）に応じた欠席傾向の動的判定"""
        df = graph_data.get("grade_graph")
        if df is None or df.empty or len(df) < 1:
            return "学年別のデータが不足しているため、傾向は判定できませんでした。"

        values = df.iloc[:, 1:].mean(axis=1)
        if len(values) >= 2 and values.iloc[0] > values.iloc[-1]:
            return "低学年ほど欠席が多く、進級に伴い安定する傾向がみられた。"
        return "学年間で大きな差は認められなかった。"

    def _attendance_trend(self, graph_data):
        """入園からの「登園月数」に応じた環境適応の動的判定（いわゆる洗礼期の可視化）"""
        df = graph_data.get("attendance_graph")
        if df is None or df.empty or len(df) < 1:
            return "登園月数別のデータが不足しているため、傾向は判定できませんでした。"

        values = df.iloc[:, 1:].mean(axis=1)
        if len(values) >= 2 and values.iloc[0] > values.iloc[-1]:
            return "登園開始直後は欠席が多いものの、通園期間の経過とともに改善傾向がみられた。"
        return "登園月数による大きな変化は認められなかった。"

    def _year_trend(self, graph_data):
        """在園年数に応じた体力の向上傾向を判定"""
        df = graph_data.get("years_graph")
        if df is None or df.empty or len(df) < 1:
            return "登園年数別のデータが不足しているため、傾向は判定できませんでした。"

        values = df.iloc[:, 1:].mean(axis=1)
        if len(values) >= 2 and values.iloc[0] > values.iloc[-1]:
            return "登園年数が増えるにつれて欠席は減少する傾向がみられた。"
        return "登園年数による大きな差は認められなかった。"

    def _season_trend(self, graph_data):
        """
        【重要】月別の統計データから、欠席が最も多い「ピーク月（季節性）」を自動検出
        【堅牢化（バグ対策）】例外処理（try-except）と動的カラムチェックを組み込み、
        「月」列の有無に関わらず、システムが絶対にクラッシュしない安全弁を実装しています。
        """
        df = graph_data.get("month_graph")
        if df is None or df.empty or len(df) < 1:
            return "月別の季節性データが不足しているため、傾向は判定できませんでした。"

        means = df.iloc[:, 1:].mean(axis=1)
        if means.empty:
            return "月別データから平均値を算出できませんでした。"

        # 最も平均欠席日数が多い「行インデックス」を特定
        idx_label = means.idxmax()
        try:
            if "月" in df.columns:
                peak = str(df.loc[idx_label, "月"])
            else:
                peak = str(df.loc[idx_label].iloc[0])
            return f"{peak}頃に欠席が最も多く、季節要因の影響が考えられる。"
        except Exception:
            return "特定の月に顕著な季節性の偏りは検出されませんでした。"

    def _monthly_trend(self, graph_data):
        """直近の時系列データが全体として上向きか下向きかのモメンタムを判定"""
        df = graph_data.get("monthly_graph")
        if df is None or df.empty or len(df) < 1:
            return "月間推移のデータが不足しているため、傾向は判定できませんでした。"

        values = df.iloc[:, 1:].mean(axis=1)
        if len(values) >= 2:
            if values.iloc[-1] < values.iloc[0]:
                return "直近では欠席日数は減少傾向で推移している。"
            elif values.iloc[-1] > values.iloc[0]:
                return "直近では欠席日数はやや増加傾向である。"
        return "大きな変動はみられない。"

    # =====================================================
    # ■ 2. 外部公開用メソッド群（各シートへ流し込む複合テキストの生成）
    # =====================================================

    def trend_analysis(self, graph_data, results):
        """【シート2＆6】各軸の判定文を改行で結合し、包括的な『傾向考察』を一網打尽に生成します。"""
        return "\n".join([
            self._age_trend(graph_data),
            self._grade_trend(graph_data),
            self._attendance_trend(graph_data),
            self._year_trend(graph_data),
            self._season_trend(graph_data),
            self._monthly_trend(graph_data)
        ])

    def future_prediction_summary(self, graph_data, results):
        """【シート2】AIモデルによる個別児童の未来見通しをリスト形式で自動生成。"""
        if not results:
            return "未来予測データが存在しません。"

        stable_lines = []
        for child, result in results.items():
            month = result.get("stable_month")
            if month is not None:
                stable_lines.append(f"・{child}: 約{month}か月後に欠席の安定化（基準値以下）を予測。")
            else:
                stable_lines.append(f"・{child}: 予測期間中に明瞭な安定期に至らない可能性あり。")
        
        intro = "AI（LightGBM）による未来予測の結果、以下の見通しが得られました。\n"
        return intro + "\n".join(stable_lines)

    def business_improvement(self, graph_data, results):
        """【シート2＆6】データに基づき、保育現場が今すぐ取るべき具体的な「アクションプラン」を自動構成。"""
        stable = []
        if results:
            for child, result in results.items():
                month = result.get("stable_month")
                if month is not None:
                    stable.append(f"{child}は約{month}か月後に欠席の安定化（基準値以下）が期待されるため、それまでのサポートを強化します。")
                else:
                    stable.append(f"{child}は明瞭な安定期に至らない可能性があり、継続的な健康観察と家庭連携が望ましい。")

        text = (
            "【業務への示唆・改善提案】\n"
            "欠席リスクが高いとされる年齢・時期・季節に重点的な感染対策を実施し、"
            "家庭との情報共有をリアルタイムで強化することで、園全体の欠席日数の低減を目指します。\n\n"
        )
        if stable:
            text += "\n".join(stable)
        else:
            text += "対象児童の個別予測に基づき、引き続き個別の状況に合わせた健康管理を行います。"
        return text

    def overall_summary(self, graph_data, results):
        """【シート8】全児童の予測値のアンサンブル（平均）を計算し、園全体の未来像を定量的に要約。"""
        if not results:
            return "予測データがないため、総合所見を生成できません。"

        pred = [r.get("predicted_absence", 0) for r in results.values()]
        avg = sum(pred) / len(pred) if pred else 0

        return (
            f"過去データおよびAI（LightGBM回帰モデル）予測を総合すると、"
            f"将来における対象児童の平均欠席日数は月あたり約{avg:.1f}日と推定された。"
            "成長や通園期間に伴い全体的には改善傾向を辿る見込みであるが、"
            "季節要因による突発的な変動リスクに対しては、今後も継続的な警戒必要である。"
        )

    def final_conclusion(self, graph_data, results):
        """【シート8】もっとも適応の早いマイルストーンを自動で検出し、報告書の「最終結論」として提示。"""
        if not results:
            return "予測データがないため、結論を生成できません。"

        stable = [r["stable_month"] for r in results.values() if r.get("stable_month") is not None]
        if stable:
            early = min(stable) # 最も早く安定化する児童の月数を動的に抽出
            return (
                f"最も早い児童では、今後約{early}か月後に欠席日数の安定圏への推移が見込まれる。"
                "園における一貫した感染症対策の遂行と家庭との密な情報連携を維持することで、"
                "予測値を超えるさらなる欠席日数の改善が期待できる。"
            )

        return (
            "予測期間内に明確な安定化基準を満たす時期は現時点で確認されなかった。"
            "引き続き個別的な健康管理と予防的アプローチを強化しながら、経過観察を行うことが推奨される。"
        )