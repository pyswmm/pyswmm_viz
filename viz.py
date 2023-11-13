import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pyswmm import Simulation, Nodes, Links
from swmm.toolkit.shared_enum import SubcatchAttribute, NodeAttribute, LinkAttribute
from pyswmm import Output
import numpy as np
from swmm_api.input_file import read_inp_file, SwmmInput, section_labels as sections
from swmm_api import swmm5_run, read_out_file
from tempfile import NamedTemporaryFile
import pathlib
import tempfile
import os
# set streamlit page title
st.title('SWMM Visualization')
st.text('')

# upload file
st.sidebar.title('Navigation')
uploaded_file = st.sidebar.file_uploader("Choose a swmm input file (.inp)", type = ['inp'])

# read swmm file
if uploaded_file is not None:
    #st.write(type(uploaded_file))
    file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type}
    #st.write(file_details)
    
    with open(os.path.join("tempDir",'temp.inp'),'wb') as f:
        f.write(uploaded_file.getbuffer())
    st.success('Uploaded file successfully')
    
    
    temp_file = "tempDir/temp.inp"
    inp = SwmmInput.read_file(temp_file)
    #inp = SwmmInput.read_file(uploaded_file)
    #inp.write_file('temp.inp')
    #inp = SwmmInput.read_file('temp.inp')
    #st.write(file_read)
    #inp = SwmmInput.read_file(file_read)

    #print(inp)
else:
    uploaded_file = "inp/Example1.inp"
    inp = SwmmInput.read_file(uploaded_file)
  

#run  swmm model using pyswmm  
#swmm5_run('new_inputfile.inp', progress_size=100)    

## Read the OUT-File
#out = read_out_file('new_inputfile.out')   # type: swmm_api.SwmmOut
#df = out.to_frame()  # type: pandas.DataFrame


# layout
options = st.sidebar.radio('Pages',
                           options = ['Home',
                                      'Stats',
                                      '2D view',
                                      '3D view',
                                      'Simulation results',
                                      'Path view',
                                      'Water flux view'])

# home page

# stats page
def stats(inp):
    
    # Create a dropdown button
    selected_option = st.selectbox("Select an option:", inp.keys())

    # Display the selected option
    st.write("You selected:", selected_option)
    
    # Convert selected option into dataframe format
    try:
        option = inp[selected_option].frame
    except:
        option = pd.DataFrame(inp[selected_option].items())
    
    st.dataframe(option)
    
    return None



# 2D view page
def twoD_view(inp):
    raingages = inp[sections.RAINGAGES].frame
    junctions = inp[sections.JUNCTIONS].frame
    subs = inp[sections.SUBCATCHMENTS].frame
    outfalls = inp[sections.OUTFALLS].frame
    conduits = inp[sections.CONDUITS].frame
    
    coordinates = inp[sections.COORDINATES].frame    #junctions
    polygons = inp[sections.POLYGONS].frame  #subcatchment
    symbols = inp[sections.SYMBOLS].frame  #raingage
    
    #frames = [df1, df2, df3]
    #result = pd.concat(frames)
    
    # add xy coordinates to junctions
    junctions_coord = pd.concat([junctions, coordinates], axis=1, join="inner")

    # add xy coordinates to subcatchments
    subs_coord = pd.concat([subs, polygons], axis=1, join="inner")

    # add xy coordinates to raingages
    raingages_coord = pd.concat([raingages, symbols], axis=1, join="inner")
    
    # add xy coordinates to outfalls
    outfalls_coord = pd.concat([outfalls, coordinates], axis=1, join="inner")
    
    # add xy coordinates to conduits
    st.dataframe(conduits)


    
    # Create scatter plot using go.Scatter
    fig = go.Figure()

    # Add scatter trace
    fig.add_trace(
        go.Scatter(
            x=junctions_coord['x'],
            y=junctions_coord['y'],
            mode='markers+text',
            text=junctions_coord.index,
            textposition='top center',
            marker=dict(size=12, opacity=0.8),
            
        )
    )
    
    # add polygon trace for subcatchments
    for polygon in subs_coord['polygon']:
        x,y = zip(*polygon)
        fig.add_trace(go.Scatter(
                        x=list(x) + [x[0]],  # Close the polygon by repeating the first point
                        y=list(y) + [y[0]],
                        fill="toself",
                        fillcolor='rgba(0,176,246,0.2)',
                        line_color='rgba(0,176,246,0.8)',
                    )
                    )
    # add symbol trace for raingages
    fig.add_trace(
        go.Scatter(
            x=raingages_coord['x'],
            y=raingages_coord['y'],
            mode='markers+text',
            text=raingages_coord.index,
            textposition='top center',
            marker=dict(size=12, opacity=0.8),
            
        )
    )
    
     # add symbol trace for outfalls
    fig.add_trace(
        go.Scatter(
            x=outfalls_coord['x'],
            y=outfalls_coord['y'],
            mode='markers+text',
            text=outfalls_coord.index,
            textposition='top center',
            marker=dict(size=12, opacity=0.8),  
        )
    )   
    
    # Set the x and y axes to have the same range
    x_min = junctions_coord['x'].min()
    x_max = junctions_coord['x'].max()
    y_min = junctions_coord['y'].min()
    y_max = junctions_coord['y'].max()
    
    fig.update_layout(
        xaxis=dict(scaleratio=1, showgrid=False),
        yaxis=dict(scaleratio=1, showgrid=False)
    )
    #fig.update_layout(yaxis_scaleanchor="x")
    fig.update_layout(
                    autosize=False,
                    width=600,
                    height=600,)
    # Customize layout
    fig.update_xaxes(title_text='X-axis')
    fig.update_yaxes(title_text='Y-axis')
    fig.update_layout(title='Node Plot')
    
    
    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig)
    
    return None


if options == 'Home':
    st.header('Home')
    st.text('This is a web app for visualizing SWMM models.')
elif options == 'Stats':
    stats(inp)
elif options == '2D view':
    twoD_view(inp)

