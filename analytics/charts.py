import plotly.express as px

def sales_chart(df):

    fig = px.bar(
        df,
        x=df.columns[0],
        y=df.columns[1],
        title="Sales Analysis"
    )

    return fig