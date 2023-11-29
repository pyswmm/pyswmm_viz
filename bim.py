import pyvista as pv
import streamlit as st
from stpyvista import stpyvista
import numpy as np





def bim_view():
    junctions_coord = st.session_state['junctions_coord']
    # outfalls_coord = st.session_state['outfalls_coord']
    # dividers_coord = st.session_state['dividers_coord']
    # storageUnits_coord = st.session_state['storageUnits_coord']
    # raingages_coord = st.session_state['raingages_coord']
    # subs_coord = st.session_state['subs_coord']
    # conduits = st.session_state['conduits']
    #st.dataframe(junctions_coord)
    # st.dataframe(conduits)
    #initialise the plotter window
    plotter = pv.Plotter(window_size=[600,600])
    plotter.background_color = '#dddddd'
    #create tube for the first junction
    junction = junctions_coord.iloc[0]
    #st.write(junction, junction[7], junction[1] )
             #for junction in junctions_coord.itertuples():
    junction_bottom = (junction[5]/1000, junction[6]/1000, junction[0]/1000)
    junction_top = (junction[5]/1000, junction[6]/1000, junction[1] + junction[0]/1000)
    st.write(junction_bottom, junction_top)
    #mesh = pv.Tube(junction_bottom, junction_top)
    mesh = pv.Tube((4,9,0),(4,9,4))
    plotter.add_mesh(mesh, color="red")

    #zoom setting
    
    #plotter.zoom(1.5)
    # Pass the plotter (not the mesh) to stpyvista
    stpyvista(plotter)
        