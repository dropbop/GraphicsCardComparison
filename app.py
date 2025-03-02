from flask import Flask, render_template
import plotly.graph_objs as go
import plotly.io as pio

app = Flask(__name__)

@app.route('/')
def index():
    # Create an interactive Plotly chart
    fig = go.Figure(
        data=go.Scatter(
            x=[1, 2, 3, 4],
            y=[10, 20, 15, 25],
            mode='lines+markers'
        )
    )
    fig.update_layout(title="Interactive Plotly Chart")
    
    # Convert the plot to HTML
    plot_html = pio.to_html(fig, full_html=False)
    
    return render_template('index.html', plot_html=plot_html)

if __name__ == '__main__':
    app.run(debug=False)
