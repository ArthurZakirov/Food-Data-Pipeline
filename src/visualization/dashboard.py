import numpy as np
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler


def create_radar_chart(df, names, 1=0, 2=10):

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
