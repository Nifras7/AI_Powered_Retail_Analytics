def format_response(df):

    if hasattr(df, "empty"):

        if df.empty:
            return "No results found."

        return df.to_markdown(index=False)

    return str(df)