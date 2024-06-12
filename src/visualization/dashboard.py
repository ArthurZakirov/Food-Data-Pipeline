import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px


def create_radar_chart(df, names):

    scaler = MinMaxScaler()
    df_scaled = scaler.fit_transform(df)

    axis_limits = df.max(axis=0)

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=df_scaled[1],
            theta=df_scaled.columns,
            fill="toself",
            name=names[1],
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=df_scaled[2],
            theta=df_scaled.columns,
            fill="toself",
            name=names[2],
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=False,
                range=[
                    0,
                    1,
                ],  # Setting the overall range from 0 to maximum of max values for better visual uniformity
            ),
            angularaxis=dict(
                tickvals=np.arange(len(df_scaled.columns)),
                ticktext=[
                    f"{category} (max: {axis_limits[category]})"
                    for category in df_scaled.columns
                ],
            ),
        ),
        title=f"Nutritional values per 100g",
    )
    return fig


def visualize_optimization_result_nutrient_breakdown(results_df):
    macro_df = pd.concat(
        [results_df[["Macronutrient"]], results_df[[("Non Nutrient Data", "Amount")]]],
        axis=1,
    )
    macro_df = macro_df.set_index(results_df[("Non Nutrient Data", "FDC Name")].values)
    macro_df = macro_df[~macro_df.index.isin(["Total", "Lower Bound", "Upper Bound"])]
    macro_df.columns = macro_df.columns.get_level_values(1)
    macro_df = macro_df.drop(columns=["Amount"])
    df_t = macro_df.transpose()

    macro_fig = px.bar(
        df_t,
        x=df_t.index,
        y=df_t.columns,
        title="Nutrient Contributions by Food",
        labels={"index": "Nutrients", "value": "Total Amount", "variable": "Food"},
        orientation="v",
    )

    # Customize the layout
    macro_fig.update_layout(
        barmode="stack",
        xaxis_title="Nutrients",
        yaxis_title="Total Macronutrient Amount",
        legend_title="Foods",
    )

    micro_df = pd.concat(
        [results_df[["Micronutrient"]], results_df[[("Non Nutrient Data", "Amount")]]],
        axis=1,
    )
    micro_df = micro_df.set_index(results_df[("Non Nutrient Data", "FDC Name")].values)
    micro_df = micro_df[~micro_df.index.isin(["Total", "Lower Bound", "Upper Bound"])]
    micro_df.columns = micro_df.columns.get_level_values(1)
    micro_df = micro_df.drop(columns=["Amount"])
    df_t = micro_df.transpose()

    micro_fig = px.bar(
        df_t,
        x=df_t.index,
        y=df_t.columns,
        title="Nutrient Contributions by Food",
        labels={"index": "Nutrients", "value": "Total Amount", "variable": "Food"},
        orientation="v",
    )

    # Customize the layout
    micro_fig.update_layout(
        barmode="stack",
        xaxis_title="Nutrients",
        yaxis_title="Total Micronutrient Amount",
        legend_title="Foods",
    )

    return macro_fig, micro_fig


def visualize_polar_chart(df, names):
    macro_df = df.copy()
    macro_df.columns = macro_df.columns.get_level_values(1)
    macro_df = macro_df[
        [
            "FDC Name",
            "Energy [KCAL]",
            "Carbohydrate [G]",
            "Fiber [G]",
            "Protein [G]",
            "Total Fat [G]",
        ]
    ]

    max_values = df.loc[:, df.columns.get_level_values(1) != "FDC Name"].max()

    scaler = MinMaxScaler()
    polar_df = macro_df.copy()
    polar_df.loc[:, polar_df.columns != "FDC Name"] = scaler.fit_transform(
        macro_df.loc[:, macro_df.columns != "FDC Name"]
    )

    fig = go.Figure()

    for name in names:
        index = macro_df[macro_df["FDC Name"] == name].index.values[0]

        fig.add_trace(
            go.Scatterpolar(
                r=polar_df.drop(columns="FDC Name").loc[index],
                theta=polar_df.columns.difference(["FDC Name"]),
                fill="toself",
                name=polar_df.loc[index, "FDC Name"],
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                # Set ticktext to empty to hide labels
                tickvals=np.linspace(0, 1.2, num=5),
                ticktext=[
                    "" for _ in np.linspace(0, 1, num=5)
                ],  # Empty strings for each tick
            ),
            angularaxis=dict(
                tickvals=np.arange(len(polar_df.columns.difference(["FDC Name"]))),
                ticktext=[
                    f"{category} (max: {int(macro_df.max(axis=0)[category])})"
                    for category in polar_df.columns.difference(["FDC Name"])
                ],
            ),
        ),
        title=f"Nutritional values per 100g",
    )
    fig.update_layout(
        autosize=False,
        width=800,
        height=800,
    )
    return fig


def visualize_micronutrient_polar_chart(relative_df, names):
    macro_df = relative_df.copy()
    macro_df.columns = macro_df.columns.get_level_values(1)
    macro_df = macro_df[["FDC Name"] + relative_df["Micronutrient"].columns.to_list()]

    polar_df = macro_df

    fig = go.Figure()

    for name in names:
        index = macro_df[macro_df["FDC Name"] == name].index.values[0]

        fig.add_trace(
            go.Scatterpolar(
                r=polar_df.drop(columns="FDC Name").loc[index],
                theta=polar_df.columns.difference(["FDC Name"]),
                fill="toself",
                name=polar_df.loc[index, "FDC Name"],
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                # Set ticktext to empty to hide labels
                tickvals=np.linspace(0, 1.2, num=5),
                ticktext=[
                    "" for _ in np.linspace(0, 1, num=5)
                ],  # Empty strings for each tick
            ),
            angularaxis=dict(
                tickvals=np.arange(len(polar_df.columns.difference(["FDC Name"]))),
                ticktext=[
                    f"{category} (max: {int(macro_df.max(axis=0)[category])})"
                    for category in polar_df.columns.difference(["FDC Name"])
                ],
            ),
        ),
        title=f"Nutritional values per 100g",
    )
    fig.update_layout(
        autosize=False,
        width=800,
        height=800,
    )
    return fig


def nutrition_scatter_plot(df, x_col, y_col, z_col, title, delimiter=", "):
    x_col_str = delimiter.join(x_col).strip()
    y_col_str = delimiter.join(y_col).strip()
    z_col_str = delimiter.join(z_col).strip()

    plotly_df = df.copy()
    plotly_df.columns = [", ".join(col).strip() for col in df.columns.values]
    fig = px.scatter(
        plotly_df,
        x=x_col_str,
        y=y_col_str,
        color=z_col_str,
        color_continuous_scale=px.colors.sequential.Viridis,
        hover_name="Non Nutrient Data, FDC Name",
        hover_data={x_col_str: True, y_col_str: True},
        labels={x_col_str: x_col_str, y_col_str: y_col_str},
        title=title,
    )

    return fig
