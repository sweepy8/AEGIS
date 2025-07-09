# Website Utilities
# Created on 7/7/2025

from matplotlib import figure
from io import BytesIO

def create_visualizer_fig(dpi : int = 100) -> bytes:
    '''
    PLACEHOLDER, TO BE FILLED IN LATER ***
    '''
    fig = figure.Figure(dpi=dpi)    # lol change this arg name
    axis = fig.add_subplot(1,1,1)

    # Placeholder fig
    x_vals = range(100)
    y_vals = [x ** 2 for x in x_vals]
    axis.plot(x_vals, y_vals, color="white")

    fig.patch.set_facecolor('black')
    axis.set_facecolor('black')
    for spine in axis.spines.values(): spine.set_edgecolor('white')
    axis.set_title("LiDAR Visualizer (Placeholder)", color='w')
    axis.set_xlabel("X", color='white')
    axis.set_ylabel("Y", color='white')
    axis.tick_params(colors='w', which='both')
    fig.tight_layout()

    output_png = BytesIO()
    fig.savefig(output_png, format='png')

    return output_png.getvalue()


if __name__ == "__main__":
    create_visualizer_fig()