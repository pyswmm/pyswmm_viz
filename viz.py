import streamlit as st
import pandas as pd
import plotly.graph_objects as go
#from pyswmm import Simulation, Nodes, Links
#from swmm.toolkit.shared_enum import SubcatchAttribute, NodeAttribute, LinkAttribute
#from pyswmm import Output
import numpy as np
from swmm_api.input_file import read_inp_file, SwmmInput, section_labels as sections
from swmm_api.output_file import VARIABLES, OBJECTS
from swmm_api import swmm5_run, read_out_file,SwmmOutput
import os


# Initialization of session state variables
if 'out' not in st.session_state:
    st.session_state['out'] = None
if 'out_df' not in st.session_state:
    st.session_state['out_df'] = None    



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
    
    with open(os.path.join("pyswmm_viz/tempDir",'temp.inp'),'wb') as f:
        f.write(uploaded_file.getbuffer())
    st.success('Uploaded file successfully')
    
    
    temp_file = "pyswmm_viz/tempDir/temp.inp"
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
                                      'Run the model',
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
    junctions_coord['node_id'] = junctions_coord.index
    outfalls_coord['node_id'] = outfalls_coord.index
    all_nodes = pd.concat([junctions_coord, outfalls_coord], ignore_index=True)#need to add more nodes like storage, ect.
    conduits['conduit_id']=conduits.index

    all_nodes.set_index('node_id', inplace=True)
    
    #set from_node as index for conduits and keep the original index  
    conduits.set_index('from_node', inplace=True)
    
    # Merging the 'x' and 'y' columns from the first DataFrame into the second DataFrame based on the index
    conduits = conduits.join(all_nodes[['x', 'y']])
    #rename xy columns 
    conduits.rename(columns={'x': 'from_x', 'y': 'from_y'}, inplace=True)
    conduits.set_index('to_node', inplace=True)
    conduits = conduits.join(all_nodes[['x', 'y']])
    conduits.rename(columns={'x': 'to_x', 'y': 'to_y'}, inplace=True)
    
    #set conduit id as index
    #conduits.set_index('conduit_id', inplace=True)

    # st.dataframe(junctions_coord) 
    # st.dataframe(all_nodes)
    #add dropdown menu for selecting dataframe
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
    num = 0
    for polygon in subs_coord['polygon']:
        x,y = zip(*polygon)
        fig.add_trace(go.Scatter(
                        x=list(x) + [x[0]],  # Close the polygon by repeating the first point
                        y=list(y) + [y[0]],
                        fill="toself",
                        fillcolor='rgba(92,96,232,0.2)',
                        line_color='rgba(92,96,232,0.2)',
                    )
                    )
        
        fig.add_trace(go.Scatter(x = [sum(x)/len(x)],
                                 y = [sum(y)/len(y)],
                                 mode = 'text',
                                 text = 'Sub ' + subs_coord.index[num],
                                 textfont = dict(color='black', size=12),))
        num = num + 1                        
        
    # # add symbol trace for raingages
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
    

    # add trace for conduits
    for conduit in conduits.itertuples():

        fig.add_trace(go.Scatter(x = [conduit[8], conduit[10]],
                                 y = [conduit[9], conduit[11]],
                                 mode = 'lines',
                                 line = dict(width = 3, color = 'crimson'),
                                 )
                      )
        fig.add_trace(go.Scatter(x = [(conduit[8]+conduit[10])/2],
                                 y = [(conduit[9]+conduit[11])/2],
                                 mode = 'text',
                                 showlegend=True,
                                 text = 'Conduit '+ conduit[7],
                                 textfont = dict(color='black', size=12),))
   
    
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
    fig.update_layout(showlegend=False,
                    autosize=False,
                    width=800,
                    height=800,)
    # Customize layout
    fig.update_xaxes(title_text='X-axis')
    fig.update_yaxes(title_text='Y-axis')
    fig.update_layout(title='Node Plot')
    
    
    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig)
    
    return None

# 3D view page
def threeD_view(inp):
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
    junctions_coord['node_id'] = junctions_coord.index
    outfalls_coord['node_id'] = outfalls_coord.index
    all_nodes = pd.concat([junctions_coord, outfalls_coord], ignore_index=True)#need to add more nodes like storage, ect.
    conduits['conduit_id']=conduits.index

    all_nodes.set_index('node_id', inplace=True)
    conduits.set_index('from_node', inplace=True)
    
    # Merging the 'x' and 'y' columns from the first DataFrame into the second DataFrame based on the index
    conduits = conduits.join(all_nodes[['x', 'y', 'elevation']])
    #rename xy columns 
    conduits.rename(columns={'x': 'from_x', 'y': 'from_y','elevation':'from_z'}, inplace=True)
    conduits.set_index('to_node', inplace=True)
    conduits = conduits.join(all_nodes[['x', 'y', 'elevation']])
    conduits.rename(columns={'x': 'to_x', 'y': 'to_y','elevation':'to_z'}, inplace=True)
    

    #st.dataframe(junctions_coord) 
    subs_coord = subs_coord.join(all_nodes[['elevation']], on='outlet')
    #st.dataframe(conduits) 
    # st.dataframe(all_nodes)
    #add dropdown menu for selecting dataframe
    #st.dataframe(conduits)
    
    # Create scatter plot using go.Scatter
    fig = go.Figure()

    # Add scatter trace
    fig.add_trace(
        go.Scatter3d(
            x=junctions_coord['x'],
            y=junctions_coord['y'],
            z=junctions_coord['elevation'],
            mode='markers+text',
            text=junctions_coord.index,
            textposition='top center',
            marker=dict(size=4, opacity=0.8),
            
        )
    )
    
    # add polygon trace for subcatchments
    num = 0
    for polygon in subs_coord['polygon']:
        x,y = zip(*polygon)
        fig.add_trace(go.Scatter3d(
                        x=list(x) + [x[0]],  # Close the polygon by repeating the first point
                        y=list(y) + [y[0]],
                        z=[subs_coord['elevation'][num]]*(len(x)+1),
                        mode='lines',
                        showlegend=False,
                        line_color='grey',
                    )
                    )
        
        fig.add_trace(go.Scatter3d(x = [sum(x)/len(x)],
                                 y = [sum(y)/len(y)],
                                 z=[subs_coord['elevation'][num]],
                                 mode = 'text',
                                 showlegend=False,
                                 text = 'Sub ' + subs_coord.index[num],
                                 textfont = dict(color='black', size=12),))
        num = num + 1                        
        
    # # add symbol trace for raingages
    # fig.add_trace(
    #     go.Scatter3d(
    #         x=raingages_coord['x'],
    #         y=raingages_coord['y'],
    #         z=raingages_coord['elevation'],
    #         mode='markers+text',
    #         text=raingages_coord.index,
    #         textposition='top center',
    #         marker=dict(size=3, opacity=0.8),
            
    #     )
    # )
    
     # add symbol trace for outfalls
    fig.add_trace(
        go.Scatter3d(
            x=outfalls_coord['x'],
            y=outfalls_coord['y'],
            z=outfalls_coord['elevation'],
            mode='markers+text',
            text=outfalls_coord.index,
            textposition='top center',
            marker=dict(size=4, opacity=0.8),  
        )
    )   
    

    # add trace for conduits
    for conduit in conduits.itertuples():

        fig.add_trace(go.Scatter3d(x = [conduit[8], conduit[11]],
                                 y = [conduit[9], conduit[12]],
                                 z = [conduit[10], conduit[13]],
                                 mode = 'lines',
                                 line = dict(width = 3, color = 'crimson'),
                                 showlegend=False,
                                 )
                      )
        fig.add_trace(go.Scatter3d(x = [(conduit[8]+conduit[11])/2],
                                 y = [(conduit[9]+conduit[12])/2],
                                 z = [(conduit[10]+conduit[13])/2],
                                 mode = 'text',
                                 showlegend=False,
                                 text = 'Conduit '+ conduit[7],
                                 textfont = dict(color='black', size=12),))
   
    
    # Set the x and y axes to have the same range
    # x_min = junctions_coord['x'].min()
    # x_max = junctions_coord['x'].max()
    # y_min = junctions_coord['y'].min()
    # y_max = junctions_coord['y'].max()
    # z_min = junctions_coord['z'].min()
    # z_max = junctions_coord['z'].max()
    
    fig.update_layout(
        xaxis=dict(scaleratio=1, showgrid=False),
        yaxis=dict(scaleratio=1, showgrid=False),
    )
    #fig.update_layout(yaxis_scaleanchor="x")
    fig.update_layout(showlegend=False,
                    autosize=False,
                    width=800,
                    height=800,)
    # # Customize layout
    fig.update_xaxes(title_text='X-axis')
    fig.update_yaxes(title_text='Y-axis')
    
    fig.update_layout(title='Node Plot')
    
    
    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig)
    
    return None

def run_model(inp):
    from pyswmm import Simulation, Nodes, Links
    #import time
    
    with Simulation(r'inp/Example1.inp') as sim:
        #show progress bar
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        for ind, step in enumerate(sim):  
            my_bar.progress(round(sim.percent_complete*100), text=progress_text)
        #time.sleep(1)
        my_bar.empty()

    st.write("Simulation Done!")

    
    #read the output file   
    out = read_out_file('inp/Example1.out')   
    df = out.to_frame() 
    
    return out,df


def simulation_results(out, df):

    #st.dataframe(df)
    col1, col2, col3 = st.columns(3)
    #create a dropdown button in col1 for selecting a variable
    with col1:
    #type_dropdown: subcatchment, node, link
        type_dropdown = st.selectbox("Select a type:", ['subcatchment', 'node', 'link'])
        #st.write("You selected:", type_dropdown)
    #id selections
    #show all ids in the selected column
    variable_selections = out.variables[type_dropdown]
    #add all option to the variable_selections
    variable_selections = ['all variables'] + variable_selections
    id_selections = out.labels[type_dropdown]
    
    with col2:
        #create a dropdown button for id_selections
        id_dropdown = st.selectbox("Select an id:", id_selections)
        #st.write("You selected:", id_dropdown)
    with col3:
        variable_dropdown = st.selectbox("Select a variable:", variable_selections)
        #st.write("You selected:", variable_dropdown)

    
    #create a sub dataframe for the selected variable
    if variable_dropdown == 'all variables':
        sub_out = out.get_part(type_dropdown,id_dropdown)
        st.dataframe(sub_out)
    else:
        sub_out = out.get_part(type_dropdown,id_dropdown,variable_dropdown)
        
        col1,col2 = st.columns(2)
        with col1:
            st.dataframe(sub_out)
        with col2:
        #plot the dataserie: sub_out
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=sub_out.index,
                                    y=sub_out,
                                    mode='lines',
                                    line = dict(width = 3, color = 'lightblue'),
                                    showlegend=False,
                                    )
                        )
            #set figure layout width and height
            fig.update_layout(
                autosize=False,
                width=500,
                height=400,)
            st.plotly_chart(fig)

    
    #
    #Create a time serie plot
    
    return None

if options == 'Home':
    st.header('Home')
    st.text('This is a web app for visualizing SWMM models.')
elif options == 'Stats':
    try:
        stats(inp)
    except Exception as error:
        st.write('Failed to load the file.')
        st.write("An error occurred:", error)
        #write the error message
        
        st.write()
elif options == '2D view':
    try:
        twoD_view(inp)
    except Exception as error:
        st.write('Failed to load the file.')
        st.write("An error occurred:", error)
elif options == '3D view':
    try:
        threeD_view(inp)
    except Exception as error:
        st.write('Failed to load the file.')
        st.write("An error occurred:", error)    
elif options == 'Run the model':
    #add a run button to start the function
    if 'run_button' not in st.session_state:
        st.session_state.run_button = False

    def click_button():
        st.session_state.run_button = True

    st.button('Run the model', on_click=click_button)

    if st.session_state.run_button:
        try:
            st.session_state.out, st.session_state.out_df = run_model(inp)
            st.dataframe(st.session_state.out_df)
        except Exception as error:
            st.write('Failed to load the file.')
            st.write("An error occurred:", error)
        
        st.session_state.run_button = False

    
elif options == 'Simulation results':

    try:
        if st.session_state.out is None or st.session_state.out_df is None:
            st.write('Please run the model first.')
        else:
            simulation_results(st.session_state.out, st.session_state.out_df)
    except Exception as error:
        st.write('Failed to load the file.')
        st.write("An error occurred:", error)