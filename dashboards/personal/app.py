import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output


def build_dashboard(data):
    df = data.copy()
    df["dteday"] = pd.to_datetime(df["dteday"])
    df = df.sort_values("dteday")
    df["year"] = df["dteday"].dt.year.astype(str)
    df["day_type"] = df["workingday"].map({
        0: "Weekend or holiday",
        1: "Working day"
    })
    df["month_start"] = df["dteday"].dt.to_period("M").dt.to_timestamp()

    colors = {"2011": "darkorange", "2012": "steelblue"}
    day_order = ["Weekend or holiday", "Working day"]
    edges = np.linspace(df["cnt"].min(), df["cnt"].max(), 21)
    histogram_max = np.histogram(df["cnt"], bins=edges)[0].max() * 1.15

    app = Dash(__name__)

    panels = [
        ("Daily rental distribution", "histogram"),
        ("Working-day comparison", "boxplot"),
        ("Temperature and rentals", "scatter"),
        ("Monthly rental trend", "trend")
    ]

    app.layout = html.Div([
        html.H1("Capital Bikeshare: Daily Rental Patterns, 2011–2012"),
        html.P(
            "Explore historical rental demand, weather, and calendar patterns."
        ),
        html.Label("Select year"),
        dcc.Dropdown(
            id="year",
            options=[
                {"label": "Both years", "value": "all"},
                {"label": "2011", "value": "2011"},
                {"label": "2012", "value": "2012"}
            ],
            value="all",
            clearable=False,
            style={"maxWidth": "300px"}
        ),
        html.P("The selector updates all four charts and sample sizes."),
        html.Div(id="summary", style={"margin": "16px 0"}),
        html.Div([
            html.Div([html.H3(title), dcc.Graph(id=chart_id)])
            for title, chart_id in panels
        ], style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(420px, 1fr))",
            "gap": "20px"
        }),
        html.H3("How to read the charts"),
        html.P(
            "Counts are rentals, not unique riders. Temperature is normalized, "
            "not degrees Celsius. Monthly averages divide total rentals by "
            "observed days. Scales and histogram bins remain fixed."
        ),
        html.H3("Checked conclusion — both years"),
        html.P(
            "Across 731 days, median rentals were 4,548 per day. Working-day "
            "and weekend/holiday medians were 4,582 and 4,459. Rentals generally "
            "rose with temperature. Monthly averages ranged from 1,231.90 in "
            "January 2011 to 7,285.77 in September 2012. These findings describe "
            "both years, not only the current selection."
        ),
        html.H3("Source"),
        html.A(
            "UCI Bike Sharing dataset and documentation",
            href="https://archive.ics.uci.edu/dataset/275/bike-sharing-dataset",
            target="_blank"
        ),
        html.P("Local files: data/day.csv and data/Readme.txt."),
        html.H3("Limitations"),
        html.P(
            "Historical system-wide records do not represent current demand "
            "or individual stations. Weather, season, and system growth may "
            "overlap. Associations do not establish causation, and monthly "
            "averages hide daily extremes."
        )
    ], style={
        "fontFamily": "Arial, sans-serif",
        "maxWidth": "1300px",
        "margin": "auto",
        "padding": "24px"
    })

    @app.callback(
        Output("histogram", "figure"),
        Output("boxplot", "figure"),
        Output("scatter", "figure"),
        Output("trend", "figure"),
        Output("summary", "children"),
        Input("year", "value")
    )
    def update(selected_year):
        selected = df.copy()
        if selected_year != "all":
            selected = selected.loc[df["year"].eq(str(selected_year))].copy()

        if selected.empty:
            figures = []
            for _ in range(4):
                fig = go.Figure()
                fig.add_annotation(
                    text="No observations for this selection.",
                    x=0.5, y=0.5,
                    xref="paper", yref="paper",
                    showarrow=False
                )
                fig.update_layout(height=400)
                figures.append(fig)
            return (*figures, "No days selected.")

        histogram = px.histogram(
            selected, x="cnt",
            labels={"cnt": "Daily Rental Count"}
        )
        histogram.update_traces(
            marker_color="steelblue",
            xbins={
                "start": float(edges[0]),
                "end": float(edges[-1]),
                "size": float(edges[1] - edges[0])
            }
        )
        histogram.update_xaxes(range=[0, 9000])
        histogram.update_yaxes(
            title="Number of Days",
            range=[0, float(histogram_max)]
        )

        boxplot = px.box(
            selected, x="day_type", y="cnt",
            category_orders={"day_type": day_order},
            labels={"day_type": "Day Type", "cnt": "Daily Rental Count"}
        )
        boxplot.update_traces(
            quartilemethod="linear",
            marker_color="steelblue"
        )
        boxplot.update_yaxes(range=[0, 9000])

        scatter = px.scatter(
            selected, x="temp", y="cnt", color="year",
            color_discrete_map=colors,
            category_orders={"year": ["2011", "2012"]},
            hover_data=["dteday", "day_type"],
            opacity=0.65,
            labels={
                "temp": "Normalized Temperature (source scale)",
                "cnt": "Daily Rental Count",
                "year": "Year",
                "dteday": "Date",
                "day_type": "Day Type"
            }
        )
        scatter.update_xaxes(range=[0, 1])
        scatter.update_yaxes(range=[0, 9000])

        monthly = (
            selected.groupby("month_start")
            .agg(
                mean_daily_rentals=("cnt", "mean"),
                observed_days=("cnt", "size")
            )
            .reset_index()
            .sort_values("month_start")
        )
        trend = px.line(
            monthly, x="month_start", y="mean_daily_rentals",
            markers=True,
            hover_data=["observed_days"],
            labels={
                "month_start": "Month",
                "mean_daily_rentals": "Mean Daily Rentals",
                "observed_days": "Observed Days"
            }
        )
        trend.update_traces(line_color="steelblue")
        trend.update_xaxes(range=["2011-01-01", "2012-12-31"])
        trend.update_yaxes(range=[0, 9000])

        for fig in [histogram, boxplot, scatter, trend]:
            fig.update_layout(
                height=400,
                template="plotly",
                margin={"l": 55, "r": 20, "t": 25, "b": 65}
            )

        counts = selected["day_type"].value_counts()
        label = "Both years" if selected_year == "all" else str(selected_year)
        summary = (
            f"{label} | {len(selected):,} days | "
            f"{selected['dteday'].min():%Y-%m-%d} to "
            f"{selected['dteday'].max():%Y-%m-%d} | "
            f"Working days: {counts.get('Working day', 0):,} | "
            f"Weekend/holiday days: "
            f"{counts.get('Weekend or holiday', 0):,}"
        )
        return histogram, boxplot, scatter, trend, summary

    return app
    
from pathlib import Path

data = pd.read_csv(
    Path(__file__).resolve().parent / "data" / "day.csv"
)

app = build_dashboard(data)
server = app.server

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8055, debug=False)