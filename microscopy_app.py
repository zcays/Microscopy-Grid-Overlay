import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
from PIL import Image
import numpy as np
import requests
from io import BytesIO
import base64

app = dash.Dash(__name__, title="Microscopy Grid Aligner")

# Load a sample microscopy-like image (or fallback to dummy)
try:
    # Try fetching a sample image (e.g., immunofluorescence cells)
    url = "https://raw.githubusercontent.com/scikit-image/scikit-image/main/skimage/data/cells3d.tif"
    # Actually, a simple PNG is safer
    url = "https://raw.githubusercontent.com/scikit-image/scikit-image/main/skimage/data/immunohistochemistry.png"
    response = requests.get(url, timeout=5)
    original_image = Image.open(BytesIO(response.content)).convert('RGB')
except:
    # Fallback dummy image if network fails
    img_array = np.zeros((800, 800, 3), dtype=np.uint8)
    for i in range(0, 800, 80):
        img_array[i:i+40, :] = [50, 0, 100]
        img_array[:, i:i+40] = [0, 100, 50]
    original_image = Image.fromarray(img_array)

app.layout = html.Div([
    html.Div([
        html.H2("Microscopy Aligner", style={'color': '#ffffff', 'margin': '0 0 20px 0', 'fontFamily': 'sans-serif'}),
        
        html.Div([
            dcc.Upload(
                id='upload-image',
                children=html.Div(['Drag and Drop or ', html.A('Select an Image', style={'color': '#00aaff', 'textDecoration': 'underline'})]),
                style={
                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed',
                    'borderRadius': '5px', 'textAlign': 'center',
                    'marginBottom': '20px', 'color': '#bbbbbb', 'borderColor': '#777',
                    'cursor': 'pointer'
                },
                multiple=False
            )
        ]),
        
        html.Div([
            html.Label("Image Rotation (degrees)", style={'color': '#bbbbbb', 'fontFamily': 'sans-serif'}),
            dcc.Slider(
                id='rotation-slider',
                min=0, max=360, step=0.1, value=0,
                marks={i: {'label': str(i), 'style': {'color': '#777'}} for i in range(0, 361, 90)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'marginBottom': '30px'}),
        
        html.Div([
            html.Label("Grid Spacing", style={'color': '#bbbbbb', 'fontFamily': 'sans-serif'}),
            dcc.Slider(
                id='grid-spacing-slider',
                min=10, max=400, step=1, value=100,
                marks={i: {'label': str(i), 'style': {'color': '#777'}} for i in range(50, 401, 100)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'marginBottom': '30px'}),
        
        html.Div([
            html.Label("Grid X Offset", style={'color': '#bbbbbb', 'fontFamily': 'sans-serif'}),
            dcc.Slider(
                id='grid-x-offset-slider',
                min=-200, max=200, step=1, value=0,
                marks={i: {'label': str(i), 'style': {'color': '#777'}} for i in range(-200, 201, 100)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'marginBottom': '30px'}),
        
        html.Div([
            html.Label("Grid Y Offset", style={'color': '#bbbbbb', 'fontFamily': 'sans-serif'}),
            dcc.Slider(
                id='grid-y-offset-slider',
                min=-200, max=200, step=1, value=0,
                marks={i: {'label': str(i), 'style': {'color': '#777'}} for i in range(-200, 201, 100)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'marginBottom': '30px'}),
        
        html.Div([
            html.Label("Grid Opacity", style={'color': '#bbbbbb', 'fontFamily': 'sans-serif'}),
            dcc.Slider(
                id='grid-opacity-slider',
                min=0, max=1, step=0.1, value=0.7,
                marks={0: {'label': '0', 'style': {'color': '#777'}}, 1: {'label': '1', 'style': {'color': '#777'}}},
                tooltip={"placement": "bottom", "always_visible": False}
            )
        ], style={'marginBottom': '30px'}),
        
        html.Div("Tip: Use the tools on the top right of the image to pan and zoom. The grid is locked to the axes and will scale appropriately.",
                 style={'color': '#777', 'fontStyle': 'italic', 'fontSize': '0.9em', 'fontFamily': 'sans-serif'})
        
    ], style={
        'width': '25%', 
        'height': '100vh',
        'padding': '30px', 
        'boxSizing': 'border-box',
        'display': 'inline-block', 
        'verticalAlign': 'top',
        'backgroundColor': '#1e1e1e',
        'borderRight': '1px solid #333'
    }),
    
    html.Div([
        dcc.Graph(
            id='image-graph', 
            style={'height': '100vh', 'width': '100%'},
            config={
                'scrollZoom': True,
                'displayModeBar': True,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            }
        )
    ], style={'width': '75%', 'height': '100vh', 'display': 'inline-block', 'verticalAlign': 'top', 'backgroundColor': '#000000'})
], style={'margin': '0', 'padding': '0', 'display': 'flex'})

@app.callback(
    Output('image-graph', 'figure'),
    [Input('upload-image', 'contents'),
     Input('rotation-slider', 'value'),
     Input('grid-spacing-slider', 'value'),
     Input('grid-x-offset-slider', 'value'),
     Input('grid-y-offset-slider', 'value'),
     Input('grid-opacity-slider', 'value')],
    [State('image-graph', 'relayoutData')]
)
def update_image(upload_contents, rotation, grid_spacing, offset_x, offset_y, grid_opacity, relayoutData):
    current_image = original_image
    
    if upload_contents is not None:
        try:
            content_type, content_string = upload_contents.split(',')
            decoded = base64.b64decode(content_string)
            current_image = Image.open(BytesIO(decoded)).convert('RGB')
        except Exception as e:
            pass

    # Rotate image (expand=True ensures corners are not cut off)
    # Using BICUBIC for smoother rotation quality
    rotated_img = current_image.rotate(-rotation, expand=True, resample=Image.BICUBIC)
    
    fig = px.imshow(rotated_img)
    
    grid_color = f'rgba(0, 255, 255, {grid_opacity})'
    
    # Add grid lines using shapes so they strictly overlay the image
    shapes = []
    width, height = rotated_img.size
    
    start_x = offset_x % grid_spacing
    for x in np.arange(start_x, width, grid_spacing):
        shapes.append(dict(
            type='line', x0=x, x1=x, y0=0, y1=height,
            line=dict(color=grid_color, width=1.5)
        ))
        
    start_y = offset_y % grid_spacing
    for y in np.arange(start_y, height, grid_spacing):
        shapes.append(dict(
            type='line', x0=0, x1=width, y0=y, y1=y,
            line=dict(color=grid_color, width=1.5)
        ))
        
    fig.update_layout(
        shapes=shapes,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title='',
            constrain='range',
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title='',
            constrain='range',
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        uirevision='constant' # Prevents zoom/pan from resetting on callback
    )
    
    # If the user has zoomed/panned, keep those axis ranges
    if relayoutData:
        if 'xaxis.range[0]' in relayoutData:
            fig.update_layout(
                xaxis_range=[relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']],
                yaxis_range=[relayoutData['yaxis.range[0]'], relayoutData['yaxis.range[1]']]
            )
            
    return fig

if __name__ == '__main__':
    # Start the Dash app on localhost
    app.run(debug=True, port=8050)
