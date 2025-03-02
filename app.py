from flask import Flask, render_template, Response
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot.png')
def plot_png():
    # Create a new figure and axis using matplotlib
    fig, ax = plt.subplots()
    # Example: Generate a simple line chart
    ax.plot([1, 2, 3, 4], [10, 20, 15, 25], marker='o')
    ax.set_title("Sample Chart")
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    
    # Save the plot to a BytesIO object in PNG format
    png_image = io.BytesIO()
    fig.savefig(png_image, format='png')
    plt.close(fig)  # Close the figure to free up memory
    png_image.seek(0)
    
    # Return the image data with a PNG MIME type
    return Response(png_image.getvalue(), mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=False)
