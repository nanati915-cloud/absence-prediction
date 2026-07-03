import pandas as pd
import numpy as np

class TextBuilder:
    """
    【概要】統計データの欠損を自動検知し、適切な文章のみを生成するレポート生成エンジン。
    """

    def _is_valid(self, df):
        """
        データが分析可能か判定する。
        Returns
        -------
        bool
            True : 分析可能
            False : データ不足
        """
        if df is None or df.empty:
            return False
        numeric = df.iloc[:, 1:]
        if numeric.notna().sum().sum() == 0:
            return False
        return True

    def _calculate_avg(self, df, child):
        values = pd.to_numeric(df[child], errors="coerce").dropna()
        if values.empty:
            return None
        return float(values.mean())

    def _age_trend(self, graph_data, child):
        df = graph_data.get("age_graph")
        if not self._is_valid(df):
            return None

        values = pd.to_numeric(df[child], errors="coerce").dropna()
        if len(values) < 2:
            return None

        first = int(values.iloc[0])
        last = int(values.iloc[-1])
        diff = first - last

        if diff > 0.5:
            return f"月齢が上がるにつれて欠席日数は{first}日から{last}日へ減少した。"
        elif diff < -0.5:
            return f"月齢が上がるにつれて欠席日数は{first}日から{last}日へ増加した。"

        return "月齢による欠席日数の大きな変化は認められなかった。"
    def _grade_trend(self, graph_data, child):
        df = graph_data.get("grade_graph")
        if not self._is_valid(df):
            return None

        values = pd.to_numeric(df[child], errors="coerce").dropna()
        if len(values) < 2:
            return None

        first = int(values.iloc[0])
        last = int(values.iloc[-1])
        diff = first - last

        if diff > 0.5:
            return f"学年が上がるにつれて欠席日数は{first}日から{last}日へ減少した。"
        elif diff < -0.5:
            return f"学年が上がるにつれて欠席日数は{first}日から{last}日へ増加した。"

        return "学年による欠席日数の大きな変化は認められなかった。"

    def _attendance_trend(self, graph_data, child):
        df = graph_data.get("attendance_graph")
        if not self._is_valid(df):
            return None

        values = pd.to_numeric(df[child], errors="coerce").dropna()
        if len(values) < 2:
            return None

        first = int(values.iloc[0])
        last = int(values.iloc[-1])
        diff = first - last

        if diff > 0.5:
            return f"登園月数の経過に伴い欠席日数は{first}日から{last}日へ減少した。"
        elif diff < -0.5:
            return f"登園月数の経過に伴い欠席日数は{first}日から{last}日へ増加した。"

        return "登園月数による欠席日数の大きな変化は認められなかった。"
    
    def _year_trend(self, graph_data, child):
        df = graph_data.get("years_graph")
        if not self._is_valid(df):
            return None

        values = pd.to_numeric(df[child], errors="coerce").dropna()
        if len(values) < 2:
            return None

        first = int(values.iloc[0])
        last = int(values.iloc[-1])
        diff = first - last

        if diff > 0.5:
            return f"登園年数の経過に伴い欠席日数は{first}日から{last}日へ減少した。"
        elif diff < -0.5:
            return f"登園年数の経過に伴い欠席日数は{first}日から{last}日へ増加した。"

        return "登園年数による欠席日数の大きな変化は認められなかった。"

    def _season_trend(self, graph_data, child):
        df = graph_data.get("month_graph")
        if not self._is_valid(df):
            return None

        values = pd.to_numeric(df[child], errors="coerce").dropna()
        if len(values) < 2:
            return None

        peak_idx = values.idxmax()
        peak_month = df.loc[peak_idx, df.columns[0]]
        peak_value = int(values.max())
        average = int(values.mean())

        if peak_value - average >= 0.5:
            return f"{peak_month}の欠席日数が{peak_value}日と最も高く、季節性の影響がみられた。"

        return "年間を通して大きな季節性は認められなかった。"

    def _monthly_trend(self, graph_data, child):
        df = graph_data.get("monthly_graph")
        if not self._is_valid(df):
            return None

        values = pd.to_numeric(df[child], errors="coerce").dropna()
        if len(values) < 2:
            return None

        first = int(values.iloc[0])
        last = int(values.iloc[-1])
        diff = first - last

        if diff > 0.5:
            return f"月間推移では欠席日数が{first}日から{last}日へ減少した。"
        elif diff < -0.5:
            return f"月間推移では欠席日数が{first}日から{last}日へ増加した。"

        return "月間推移に大きな変化は認められなかった。"
    
    def trend_analysis(self, graph_data, results):
        lines = []

        for child in ["子供001", "子供002"]:
            texts = [
                self._age_trend(graph_data, child),
                self._grade_trend(graph_data, child),
                self._attendance_trend(graph_data, child),
                self._year_trend(graph_data, child),
                self._season_trend(graph_data, child),
                self._monthly_trend(graph_data, child),
            ]

            texts = [t for t in texts if t]

            lines.append(f"【{child}】")
            if texts:
                lines.extend(texts)
            else:
                lines.append("データが不足しているため、判定できませんでした。")

            lines.append("")

        return "\n".join(lines).rstrip()

    def future_prediction_summary(self, graph_data, results):
        if not results:
            return "データが不足しているため、判定できませんでした。"

        lines = []

        for child in ["子供001", "子供002"]:

            result = results.get(child)

            lines.append(f"【{child}】")

            if (
                result is None
                or len(result.get("future_series", [])) < 2
            ):
                lines.append("データが不足しているため、判定できませんでした。")
                lines.append("")
                continue

            avg = result.get("predicted_absence", 0)
            lower = result.get("min_absence", avg)
            upper = result.get("max_absence", avg)
            stable = result.get("stable_month")

            if abs(upper - lower) >= 0.1:
                lines.append(
                    f"平均欠席日数は約{avg:.1f}日（予測範囲：約{lower:.1f}～{upper:.1f}日）と予測された。"
                )
            else:
                lines.append(
                    f"平均欠席日数は約{avg:.1f}日と予測された。"
                )

            if stable is not None:
                lines.append(f"約{stable}か月後に安定基準へ到達すると予測された。")
            else:
                lines.append("予測期間内に安定基準へ到達しないと予測された。")

            lines.append("")

        return "\n".join(lines).rstrip()

    def business_improvement(self, graph_data, results):
        if not results:
            return "データが不足しているため、判定できませんでした。"

        lines = []

        for child in ["子供001", "子供002"]:

            result = results.get(child)

            lines.append(f"【{child}】")

            if (
                result is None
                or len(result.get("future_series", [])) < 2
            ):
                lines.append("データが不足しているため、判定できませんでした。")
                lines.append("")
                continue

            avg = result.get("predicted_absence", 0)
            stable = result.get("stable_month")

            if stable is not None:
                lines.append(
                    f"平均欠席日数は約{avg:.1f}日と予測された。"
                    f"約{stable}か月後に安定が見込まれるため、それまでは健康観察と、家庭と保育園・学校との情報共有を継続することが望ましい。"
                )
            else:
                lines.append(
                    f"平均欠席日数は約{avg:.1f}日と予測された。"
                    "予測期間内で安定化は見込まれないため、健康観察や個別支援を継続することが望ましい。"
                )

            lines.append("")

        return "\n".join(lines).rstrip()

    def overall_summary(self, graph_data, results):
        if not results:
            return "データが不足しているため、判定できませんでした。"

        predicted = [r.get("predicted_absence", 0) for r in results.values()]
        average = sum(predicted) / len(predicted)

        stable_count = sum(
            1 for r in results.values()
            if r.get("stable_month") is not None
        )

        total = len(results)

        text = (
            f"AIによる予測では、対象児童{total}名の平均欠席日数は約{average:.1f}日と推定された。"
        )

        if stable_count == total:
            text += "全員が予測期間内に安定化すると予測され、現在の健康管理を継続することが望まれる。"
        elif stable_count == 0:
            text += "予測期間内に安定化が見込まれる児童はおらず、継続的な健康観察と、家庭と保育園・学校との連携が重要と考えられる。"
        else:
            text += (
                f"{stable_count}名は予測期間内に安定化が見込まれ、"
                f"{total - stable_count}名は継続的な支援が必要と予測された。"
            )

        return text

    def final_conclusion(self, graph_data, results):
        if not results:
            return "データが不足しているため、判定できませんでした。"

        total = len(results)
        stable = [
            r.get("stable_month")
            for r in results.values()
            if r.get("stable_month") is not None
        ]

        if stable:
            earliest = min(stable)
            return (
                f"AI予測では対象児童{total}名中{len(stable)}名で予測期間内の安定化が見込まれた。"
                f"最も早い児童は約{earliest}か月後に安定すると予測された。"
                "今後も健康観察と、家庭と保育園・学校との情報共有を継続し、児童ごとの状況に応じた支援を行うことが望まれる。"
            )

        return (
            "AI予測では予測期間内に安定化が見込まれる児童は確認されなかった。"
            "継続的な健康観察と、家庭と保育園・学校との情報共有を行いながら、個々の状況に応じた支援を継続することが望まれる。"
        )