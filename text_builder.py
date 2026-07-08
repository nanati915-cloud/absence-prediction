import pandas as pd
from config import TREND_THRESHOLD , SEASON_THRESHOLD , CHILDREN

# 共通メッセージ
NO_DATA_MESSAGE = "データが不足しているため、判定できませんでした。"

class TextBuilder:
    """
    【概要】統計データの欠損を自動検知し、適切な文章のみを生成するレポート生成エンジン。
    """

    # ==========================================================
    # ■ 共通処理（各分析で利用する補助関数）
    # ==========================================================
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

    # 分析①②③④⑥で共通利用する傾向文章生成処理
    def _trend_text(self, df, child, before_label, after_label, target_name):
        """
        前半・後半の平均欠席日数を比較し、傾向文章を生成する共通処理。

        Parameters
        ----------
        df : DataFrame
            分析対象データ
        child : str
            子供名
        before_label : str
            前半の説明文（例："月齢が低い時期"）
        after_label : str
            後半の説明文（例："後半"）
        target_name : str
            分析対象名（例："月齢"、"学年"）
        """
        if not self._is_valid(df):
            return None

        values = pd.to_numeric(df[child], errors="coerce").dropna()
        if len(values) < 2:
            return None

        # 前半・後半に分割して平均値を算出
        mid = len(values) // 2
        front_avg = values.iloc[:mid].mean()
        back_avg = values.iloc[mid:].mean()

        diff = front_avg - back_avg

        if diff > TREND_THRESHOLD:
            return (
                f"{before_label}の平均欠席日数は約{front_avg:.1f}日であったが、"
                f"{after_label}では約{back_avg:.1f}日となり、"
                "全体として減少傾向がみられた。"
            )

        elif diff < -TREND_THRESHOLD:
            return (
                f"{before_label}の平均欠席日数は約{front_avg:.1f}日であったが、"
                f"{after_label}では約{back_avg:.1f}日となり、"
                "全体として増加傾向がみられた。"
            )

        return (
            f"{before_label}の平均欠席日数は約{front_avg:.1f}日、"
            f"{after_label}では約{back_avg:.1f}日であり、"
            f"{target_name}による大きな変化は認められなかった。"
        )
    


    # ==========================================================
    # ■ 1. 分析文章（過去データ）の生成
    # ==========================================================

    # 分析① 月齢別欠席日数の説明文を生成
    def _age_trend(self, graph_data, child):
        
        df = graph_data.get("age_graph")
        return self._trend_text(
            df=df,
            child=child,
            before_label="月齢が低い時期",
            after_label="後半",
            target_name="月齢"
        )
    

    # 分析② 学年別欠席日数の説明文を生成
    def _grade_trend(self, graph_data, child):
        df = graph_data.get("grade_graph")
        return self._trend_text(
            df=df,
            child=child,
            before_label="低学年",
            after_label="高学年",
            target_name="学年"
        )
    

    # 分析③ 登園月数別欠席日数の説明文を生成
    def _attendance_trend(self, graph_data, child):
        df = graph_data.get("attendance_graph")
        return self._trend_text(
            df=df,
            child=child,
            before_label="登園初期",
            after_label="後半",
            target_name="登園月数"
        )


    # 分析④ 登園年数別欠席日数の説明文を生成 
    def _year_trend(self, graph_data, child):
        df = graph_data.get("years_graph")
        return self._trend_text(
            df=df,
            child=child,
            before_label="登園年数の前半",
            after_label="後半",
            target_name="登園年数"
        )
    

    # 分析⑤ 月別（季節性）の説明文を生成
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

        if peak_value - average >= SEASON_THRESHOLD:
            return f"{peak_month}の欠席日数が{peak_value}日と最も高く、季節性の影響がみられた。"

        return "年間を通して大きな季節性は認められなかった。"
    

    # 分析⑥ 月間推移の説明文を生成
    def _monthly_trend(self, graph_data, child):
        df = graph_data.get("monthly_graph")
        return self._trend_text(
            df=df,
            child=child,
            before_label="期間前半",
            after_label="後半",
            target_name="月間推移"
        )
    

    # シート2・シート7で使用する「分析傾向」の文章を生成    
    def trend_analysis(self, graph_data):
        lines = []

        for child in CHILDREN:
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
                lines.append(NO_DATA_MESSAGE)


        return "\n".join(lines).rstrip()
    

    # シート2で使用する「未来予測結果」の文章を生成
    def future_prediction_summary(self, results):
        if not results:
            return NO_DATA_MESSAGE
        lines = []
        for child in CHILDREN:
            result = results.get(child)
            lines.append(f"【{child}】")
            if (
                result is None
                or len(result.get("future_series", [])) < 2
            ):
                lines.append(NO_DATA_MESSAGE)
                continue

            avg = result.get("predicted_absence", 0)
            lower = result.get("min_absence", avg)
            upper = result.get("max_absence", avg)
            stable = result.get("stable_month")

            if abs(upper - lower) >= 0.1:
                text = (
                    f"平均欠席日数は約{avg:.1f}日"
                    f"（予測範囲：約{lower:.1f}～{upper:.1f}日）と予測された。"
                )
            else:
                text = (
                    f"平均欠席日数は約{avg:.1f}日と予測された。"
                )

            if stable is not None:
                text += f"約{stable}か月後に安定基準へ到達すると予測された。"
            else:
                text += "予測期間内に安定基準へ到達しないと予測された。"

            lines.append(text)

        return "\n".join(lines).rstrip()
    

    # シート2・シート7で使用する「業務改善提案」の文章を生成
    def business_improvement(self, results):
        if not results:
            return NO_DATA_MESSAGE

        lines = []

        for child in CHILDREN:
            result = results.get(child)
            lines.append(f"【{child}】")
            if (
                result is None
                or len(result.get("future_series", [])) < 2
            ):
                lines.append(NO_DATA_MESSAGE)
                continue

            avg = result.get("predicted_absence", 0)
            stable = result.get("stable_month")

            if stable is not None:
                lines.append(
                    f"平均欠席日数は約{avg:.1f}日と予測された。約{stable}か月後に安定が見込まれるため、それまでは健康観察と、家庭と保育園・学校との情報共有を継続することが望ましい。"
                )
            else:
                lines.append(
                    f"平均欠席日数は約{avg:.1f}日と予測された。予測期間内で安定化は見込まれないため、健康観察や個別支援を継続することが望ましい。"
                )


        return "\n".join(lines).rstrip()
    

    # シート8で使用する「総合所見」の文章を生成
    def overall_summary(self, results):
        if not results:
            return NO_DATA_MESSAGE

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
    

    # シート8で使用する「最終結論」の文章を生成
    def final_conclusion(self, results):
        if not results:
            return NO_DATA_MESSAGE

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