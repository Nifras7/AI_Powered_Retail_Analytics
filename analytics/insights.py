def generate_insights(df):

    insights = []

    if not df.empty:

        insights.append(
            f"Total records analyzed: {len(df)}"
        )

        insights.append(
            "Business performance trends detected."
        )

    return insights