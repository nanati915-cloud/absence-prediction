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

        values = df.iloc[:, 1:].mean(axis=1)

        if len(values) < 2:
            return "月齢別の比較に必要なデータが不足しています。"

        first = float(values.iloc[0])
        last = float(values.iloc[-1])
        diff = first - last

        if diff > 0.5:
            return (
                f"月齢が低い時期の平均欠席日数は約{first:.1f}日であり、"
                f"成長後には約{last:.1f}日まで減少した。"
                f"全体で約{diff:.1f}日の改善がみられ、成長に伴い欠席日数が減少する傾向が確認された。"
            )

        elif diff < -0.5:
            return (
                f"月齢が高くなるにつれて平均欠席日数は約{last:.1f}日となり、"
                "欠席日数がやや増加する傾向が認められた。"
            )

        return (
            f"月齢別の平均欠席日数は約{first:.1f}～{last:.1f}日で推移しており、"
            "大きな差は認められなかった。"
        )

    def _grade_trend(self, graph_data):
        """所属クラス（学年）に応じた欠席傾向の動的判定"""

        df = graph_data.get("grade_graph")

        if df is None or df.empty or len(df) < 1:
            return "学年別のデータが不足しているため、傾向は判定できませんでした。"

        values = df.iloc[:, 1:].mean(axis=1)

        if len(values) < 2:
            return "学年別の比較に必要なデータが不足しています。"

        first = float(values.iloc[0])
        last = float(values.iloc[-1])
        diff = first - last

        if diff > 0.5:
            return (
                f"低学年の平均欠席日数は約{first:.1f}日であり、"
                f"高学年では約{last:.1f}日まで減少した。"
                f"全体で約{diff:.1f}日の改善がみられ、"
                "進級に伴い欠席日数が減少する傾向が確認された。"
            )

        elif diff < -0.5:
            return (
                f"高学年になるにつれて平均欠席日数は約{last:.1f}日となり、"
                "欠席日数がやや増加する傾向が認められた。"
            )

        return (
            f"学年別の平均欠席日数は約{first:.1f}～{last:.1f}日で推移しており、"
            "学年間で大きな差は認められなかった。"
        )

    def _attendance_trend(self, graph_data):
        """登園月数に応じた欠席傾向の動的判定"""

        df = graph_data.get("attendance_graph")

        if df is None or df.empty or len(df) < 1:
            return "登園月数別のデータが不足しているため、傾向は判定できませんでした。"

        values = df.iloc[:, 1:].mean(axis=1)

        if len(values) < 2:
            return "登園月数別の比較に必要なデータが不足しています。"

        first = float(values.iloc[0])
        last = float(values.iloc[-1])
        diff = first - last

        if diff > 0.5:
            return (
                f"登園開始直後の平均欠席日数は約{first:.1f}日であり、"
                f"登園月数の経過とともに約{last:.1f}日まで減少した。"
                f"全体で約{diff:.1f}日の改善がみられ、"
                "園生活への適応が進むにつれて欠席日数が減少する傾向が確認された。"
            )

        elif diff < -0.5:
            return (
                f"登園月数の経過とともに平均欠席日数は約{last:.1f}日となり、"
                "やや増加する傾向が認められた。"
            )

        return (
            f"登園月数別の平均欠席日数は約{first:.1f}～{last:.1f}日で推移しており、"
            "登園月数による大きな差は認められなかった。"
        )

    def _year_trend(self, graph_data):
        """在園年数に応じた体力の向上傾向を判定"""

        df = graph_data.get("years_graph")

        if df is None or df.empty or len(df) < 1:
            return "登園年数別のデータが不足しているため、傾向は判定できませんでした。"

        values = df.iloc[:, 1:].mean(axis=1)

        if len(values) < 2:
            return "登園年数別の比較に必要なデータが不足しています。"

        first = float(values.iloc[0])
        last = float(values.iloc[-1])
        diff = first - last

        if diff > 0.5:
            return (
                f"登園年数が短い時期の平均欠席日数は約{first:.1f}日であり、"
                f"在園年数の増加とともに約{last:.1f}日まで減少した。"
                f"全体で約{diff:.1f}日の改善がみられ、"
                "園生活への適応や生活習慣の定着に伴い、欠席日数が減少する傾向が確認された。"
            )

        elif diff < -0.5:
            return (
                f"登園年数の増加とともに平均欠席日数は約{last:.1f}日となり、"
                "欠席日数がやや増加する傾向が認められた。"
            )

        return (
            f"登園年数別の平均欠席日数は約{first:.1f}～{last:.1f}日で推移しており、"
            "登園年数による大きな差は認められなかった。"
        )

    def _season_trend(self, graph_data):
        """
        月別の欠席傾向から季節性を判定
        """

        df = graph_data.get("month_graph")

        if df is None or df.empty or len(df) < 1:
            return "月別の季節性データが不足しているため、傾向は判定できませんでした。"

        values = df.iloc[:, 1:].mean(axis=1)

        if values.empty:
            return "月別データから平均値を算出できませんでした。"

        idx = values.idxmax()

        try:

            if "月" in df.columns:
                peak_month = str(df.loc[idx, "月"])
            else:
                peak_month = str(df.iloc[idx, 0])

            peak_value = float(values.max())
            overall = float(values.mean())

            if peak_value - overall >= 0.5:
                return (
                    f"月別では{peak_month}の平均欠席日数が約{peak_value:.1f}日と最も高く、"
                    "季節性による影響が比較的強く現れていることが示唆された。"
                )

            return (
                f"月別では{peak_month}が最も高い傾向を示したが、"
                "年間を通して大きな季節差は認められなかった。"
            )

        except Exception:
            return "月別データから季節性を判定できませんでした。"

    def _monthly_trend(self, graph_data):
        """直近の時系列データが全体として上向きか下向きかのモメンタムを判定"""

        df = graph_data.get("monthly_graph")

        if df is None or df.empty or len(df) < 1:
            return "月間推移のデータが不足しているため、傾向は判定できませんでした。"

        values = df.iloc[:, 1:].mean(axis=1)

        if len(values) < 2:
            return "月間推移を評価するためのデータが不足しています。"

        first = float(values.iloc[0])
        last = float(values.iloc[-1])
        diff = first - last

        if diff > 0.5:
            return (
                f"月間平均欠席日数は約{first:.1f}日から約{last:.1f}日へ推移し、"
                f"全体で約{diff:.1f}日の減少がみられた。"
                "継続的な改善傾向が確認されている。"
            )

        elif diff < -0.5:
            return (
                f"月間平均欠席日数は約{first:.1f}日から約{last:.1f}日へ推移し、"
                f"約{abs(diff):.1f}日の増加がみられた。"
                "今後も健康状態の継続的な観察が望まれる。"
            )

        return (
            f"月間平均欠席日数は約{first:.1f}～{last:.1f}日で推移しており、"
            "全体として大きな変動は認められなかった。"
        )

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
        """【シート2】AIモデルによる個別児童の未来予測結果を生成"""

        if not results:
            return "未来予測データが存在しません。"

        lines = [
            "AI（LightGBM回帰モデル）による24か月先までの未来予測を実施した結果、以下の見通しが得られました。"
        ]

        for child, result in results.items():

            avg = result.get("predicted_absence", 0)
            minimum = result.get("min_absence", avg)
            maximum = result.get("max_absence", avg)
            stable = result.get("stable_month")

            if stable is not None:

                lines.append(
                    f"・{child}：予測期間中の平均欠席日数は約{avg:.1f}日"
                    f"（{minimum:.1f}～{maximum:.1f}日）と推定された。"
                    f"約{stable}か月後に欠席日数が安定基準へ到達する見込みである。"
                )

            else:

                lines.append(
                    f"・{child}：予測期間中の平均欠席日数は約{avg:.1f}日"
                    f"（{minimum:.1f}～{maximum:.1f}日）と推定された。"
                    "予測期間内では安定基準に達しない可能性が示された。"
                )

        return "\n".join(lines)

    def business_improvement(self, graph_data, results):
        """【シート2＆6】予測結果を踏まえた業務改善提案を生成"""

        lines = [
            "過去データおよびAI予測結果を踏まえると、年齢や登園初期、季節要因によって欠席日数が増加する傾向が確認された。",
            "これらの時期には感染症対策や健康観察を強化するとともに、家庭との情報共有を継続することが重要である。"
            ""
        ]

        if not results:
            lines.append(
                "個別予測データが存在しないため、対象児童の状況に応じた健康管理を継続することが望ましい。"
            )
            return "\n".join(lines)

        for child, result in results.items():

            avg = result.get("predicted_absence", 0)
            stable = result.get("stable_month")

            if stable is not None:

                lines.append(
                    f"・{child}：平均欠席日数は約{avg:.1f}日と予測され、"
                    f"約{stable}か月後に安定が見込まれる。"
                    "安定期までは体調管理や家庭との連携を継続し、その後も継続的な経過観察を行うことが望ましい。"
                )

            else:

                lines.append(
                    f"・{child}：平均欠席日数は約{avg:.1f}日と予測され、"
                    "予測期間内では安定基準への到達が見込まれなかった。"
                    "健康観察を継続するとともに、家庭との情報共有や個別支援を強化することが望ましい。"
                )

        return "\n".join(lines)

    def overall_summary(self, graph_data, results):
        """【シート8】AI予測結果を基に園全体の傾向を要約"""

        if not results:
            return "予測データがないため、総合所見を生成できません。"

        predicted = [
            r.get("predicted_absence", 0)
            for r in results.values()
        ]

        average = sum(predicted) / len(predicted)

        stable_count = sum(
            1 for r in results.values()
            if r.get("stable_month") is not None
        )

        total = len(results)
        unstable = total - stable_count

        text = (
            f"AI（LightGBM回帰モデル）による未来予測では、"
            f"対象児童{total}名の平均予測欠席日数は月あたり約{average:.1f}日と推定された。"
        )

        if stable_count == total:

            text += (
                "全ての対象児童で予測期間内に欠席日数の安定化が見込まれており、"
                "今後も現在の健康管理や感染症対策を継続することで、"
                "安定した登園状況を維持できる可能性が示された。"
            )

        elif stable_count == 0:

            text += (
                "予測期間内に安定化が見込まれる児童はいなかった。"
                "継続的な健康観察と家庭との連携を強化し、"
                "個々の状況に応じた支援を継続することが望まれる。"
            )

        else:

            text += (
                f"{stable_count}名は予測期間内に安定化が見込まれた一方、"
                f"{unstable}名については継続的な支援が必要と予測された。"
                "児童ごとの状況に応じた個別対応を継続することが重要である。"
            )

        return text

    def final_conclusion(self, graph_data, results):
        """【シート8】報告書の最終結論を生成"""

        if not results:
            return "予測データがないため、結論を生成できません。"

        stable = [
            r.get("stable_month")
            for r in results.values()
            if r.get("stable_month") is not None
        ]

        total = len(results)
        stable_count = len(stable)

        if stable:

            earliest = min(stable)

            return (
                f"AI（LightGBM回帰モデル）による予測では、対象児童{total}名のうち"
                f"{stable_count}名で予測期間内の安定化が見込まれた。"
                f"最も早い児童では約{earliest}か月後に欠席日数が安定すると予測された。"
                "本システムにより欠席傾向を定量的に把握することで、"
                "健康観察や家庭との情報共有を適切な時期に実施するための判断材料として活用できることが期待される。"
            )

        return (
            "AI（LightGBM回帰モデル）による予測では、予測期間内に安定化が見込まれる児童は確認されなかった。"
            "今後も継続的な健康観察や家庭との連携を行いながら、"
            "児童一人ひとりの状況に応じた支援を継続することが重要である。"
            "本システムは欠席傾向を可視化し、継続的な健康管理を支援するための参考資料として活用できる。"
        )