import plotly.express as px
import pandas as pd

def create_activity_distribution(data):
    if len(data) == 0:
        return None

    fig = px.pie(
        data,
        values='total_hours',
        names='category',
        title='Time Distribution by Category (Hours)',
        color_discrete_sequence=px.colors.sequential.Greys
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        showlegend=True,
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)'
        )
    )
    return fig