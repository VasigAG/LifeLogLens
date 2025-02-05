import plotly.express as px
import altair as alt
import pandas as pd

def create_timeline(data):
    if len(data) == 0:
        return None

    chart = alt.Chart(data).mark_line(point=True).encode(
        x='timestamp:T',
        y='activity:N',
        color='category:N',
        tooltip=['timestamp', 'activity', 'category']
    ).properties(
        width=800,
        height=400,
        title='Activity Timeline'
    ).interactive()

    return chart

def create_activity_distribution(data):
    if len(data) == 0:
        return None

    fig = px.pie(
        data,
        values='count',
        names='category',
        title='Activity Distribution by Category',
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