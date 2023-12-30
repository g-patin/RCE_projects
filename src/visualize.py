####### IMPORT PACKAGES #######

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from glob import glob
from scipy.ndimage import gaussian_filter1d

import colour
from colour import SDS_ILLUMINANTS

from ipywidgets import Layout 
import ipywidgets as ipw
from IPython.display import display, clear_output, HTML

import plotly.express as px  
from pathlib import Path 

# self made packages
import acronyms
import measurements
import microfading
import plotting


####### DEFINE GENERAL PARAMETERS #######

style = {"description_width": "initial"}
d65 = colour.CCS_ILLUMINANTS["cie_10_1964"]["D65"]


plt.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
    "font.sans-serif": "Helvetica",
})


####### DEFINE FOLDERS #######


# get path root folder
folder_root = f'{os.path.expanduser("~")}/Documents/'

if os.path.isdir(folder_root+'RCE/') == True:  
    folder_root = f'{os.path.expanduser("~")}/Documents/RCE/'

elif os.path.isdir(folder_root) == True:
    folder_root = folder_root

else:
    print('The root folder is incorrect. This might potentially leads to some error messages.')


# get path for the main folder
folder_main = folder_root

if os.path.isdir(f'{folder_root}projects/') == True:      
    folder_main = f'{folder_root}projects/'    
else:
    folder_main = f'{folder_root}measurements/'


# get path databases folder
folder_DB = f'{folder_root}databases/'



####### THE FUNCTIONS #######


def MFT():
    """Graphical user interface to visualize the interim and processed data of microfading analyses.

    Args:
        No arguments is required.

    Returns:
        It returns a python widget object where the data of one or multiple measurements can be seen.
    """  

    ####### LOAD THE DATABASE FILES ########
        

    Objects_DB_file = folder_DB + 'DB_objects.csv'    
    Objects_DB = pd.read_csv(Objects_DB_file, index_col = 'object_id')

    Projects_DB_file = folder_DB + 'DB_projects.csv'
    Projects_DB = pd.read_csv(Projects_DB_file, index_col = 'project_id')

    Projects_techniques_file = folder_DB + 'Projects_techniques.csv'    
    Projects_techniques = pd.read_csv(Projects_techniques_file, index_col = 'Projects')

    
    ###### RETRIEVE MFT PROJECTS #######    

    projects_MFT = sorted(Projects_techniques[Projects_techniques['MFT'] == True].index.values, reverse=True)
    folders_MFT = []

    for project_MFT in projects_MFT:

        PL = Projects_DB.loc[project_MFT]['PL']
        institution = Projects_DB.loc[project_MFT]['institution']
        institution_short = list(acronyms.institutions.keys())[list(acronyms.institutions.values()).index(institution)] 
        keyword = Projects_DB.loc[project_MFT]['keyword']

        name_folder = f'{project_MFT}_{PL}_{institution_short}_{keyword}'
        folders_MFT.append(name_folder)

    

    ###### CREATE WIDGETS #######


    projects = ipw.SelectMultiple(        
        options = folders_MFT,
        description = 'Projects',
        rows = 10,
        ensure_option=False,
        disabled=False,
        layout=Layout(width="25%", height="140px"),
        style=style,
    )

    data_categories = ipw.Dropdown(
        options=['interim', 'processed'],
        value='interim',        
        disabled=False,
        layout=Layout(width="40%", height="30px"),
        #style=style,
    )

    plot_categories = ipw.Dropdown(
        options=['single', 'group', 'object'],
        value='single',        
        disabled=False,
        layout=Layout(width="40%", height="30px"),
        #style=style,
    )

    save_fig = ipw.Checkbox(
        value=False,
        description='Save figure',
        disabled=False,
        indent=False
    )

    wl_range = ipw.IntRangeSlider(
        value=[380, 1000],
        min=305,
        max=1100,
        step=1,
        description='Wavelength range (nm)',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='d',
        style=style,
        layout=Layout(width="40%", height="30px"),
    )
    

    MFT_Id_output = ipw.Output()
    MFT_data_output = ipw.Output()

    run_button = ipw.Button(description='Run')  

    display(ipw.HBox([projects,ipw.VBox([data_categories,plot_categories,save_fig])]))
    display(wl_range)
    display(run_button)


    def run_button_pressed(*args): 

        Ids_nb_list = []
        MFT_files_all = [] 

        with MFT_Id_output:
            MFT_Id_output.clear_output(wait=True)

            for project in projects.value:

                if folder_main == f'{folder_root}projects/': 
                    folder_start = f'{folder_main}{project}/data/interim/MFT/'
                    folder_fig = f'{folder_main}{project}/figures/MFT/'
                else:
                    folder_start = f'{folder_main}MFT/data/interim/'
                    folder_fig = f'{folder_main}MFT/figures/'

                # get the project id number
                project_id = project.split('_')[0]

                # select the desired data folder: interim or processed
                folder_data_MFT = folder_start.replace('interim',data_categories.value)

                # retrieve the microfading files in the choosen folder
                MFT_files_project =  sorted([x for x in os.listdir(folder_data_MFT) if f'{project.split("_")[0]}' in x and '.txt' in x]) 
                MFT_files_all.append(MFT_files_project)
                                
                # according to plot_categories values (single, group, or object), append the Id numbers in the Ids_nb_list
                if plot_categories.value == 'group':

                    objects_list = sorted(list(set([file.split("_")[2].split(".")[1] for file in MFT_files_project])))

                    for object in objects_list:

                        files_object = sorted(list(set([x for x in MFT_files_project if object in x])))

                        for file in files_object:
                            groups_list = sorted(list(set([file.split('_')[3] for file in files_object])))

                            for group in groups_list:
                                files_group = sorted([x for x in files_object if group in x and object in x])
                                Ids_nb_list.append(f'{files_group[0].split("_")[1]}_{files_group[0].split("_")[2].split(".")[1]}_{files_group[0].split("_")[3]}')

                                      

                elif plot_categories.value == 'single':        
                    for file in MFT_files_project:
                        full_Id = f'{file.split("_")[1]}_{file.split("_")[2]}_{file.split("_")[3]}'
                        Ids_nb_list.append(full_Id)


                elif plot_categories.value == 'object':
                    objects_list = sorted(list(set([file.split("_")[2].split(".")[1] for file in MFT_files_project])))

                    for object in objects_list:
                        Ids_nb_list.append(f'{project_id}_{object}')

                    
                Ids_nb_list = sorted(list(set(Ids_nb_list)))

                
            Ids_nb = ipw.SelectMultiple(options = Ids_nb_list, rows=20)
        
            display(Ids_nb)     

        
        wl_min = wl_range.value[0]
        wl_max = wl_range.value[1]

        MFT_files_all = [x for xs in MFT_files_all for x in xs]
        
        
        def values_change_Id(change):     
                
                with MFT_data_output:
                    MFT_data_output.clear_output(wait=True)
                    Id = change.new    
                    Ids_list = []

                    if plot_categories.value == 'single':                 
                        [Ids_list.append((val_id.split('_')[1],val_id.split('_')[0])) for val_id in Id]
                                                

                    if plot_categories.value == 'group' :                          
                        
                        for val_id in Id:
                            group_nb = val_id.split('_')[2]
                            object_id = val_id.split('_')[1]
                            
                            Ids = [(x.split('_')[2], x.split('_')[1]) for x in MFT_files_all if group_nb in x and object_id in x]
                            [Ids_list.append(id) for id in Ids]
                            

                    if plot_categories.value == 'object' :  
                                                
                        for val_id in Id:                  

                            Ids = [(x.split('_')[2], x.split('_')[1]) for x in MFT_files_all if val_id in x]
                            [Ids_list.append(id) for id in Ids]              


                    list_sp = []
                    list_rs_initial = []
                    list_sp_initial = []
                    list_sp_final = []
                    list_dE = []
                    list_Lab = []  
                    list_LabCh = []                    
                    list_labels = []

                    for val_id in Ids_list: 

                        mf = microfading.MF(Id=val_id[0], project_id=val_id[1]) 

                        print(wl_max, mf.get_data(data='sp').index.astype(float)[-1])

                        if wl_max > mf.get_data(data='sp').index.astype(float)[-1]:   
                                                    
                            new_wl_max = int(mf.get_data(data='sp').index.astype(float)[-1])
                                
                        else:
                            
                            new_wl_max = float(wl_max)
                            
                         
                        data_SP = mf.get_data(data='sp').loc[str(wl_min):str(new_wl_max)]                         
                        data_dE = mf.get_data(data='dE').reset_index()[['H_MJ/m2','H_klx_hr','dE00']].values.T 
                        data_Lab = mf.get_data(data='dE').reset_index()[['L*','a*','b*']].values
                        data_LabCh = mf.get_data(data='dE').reset_index()[['H_MJ/m2','L*','a*','b*','C*','h']].values.T
                        
                        

                        wl = data_SP.index.values

                        data_rs_initial = np.array([wl, data_SP.iloc[:,0].values])
                        data_sp_initial = np.array(data_SP.iloc[:,0].values)
                        data_sp_final = np.array(data_SP.iloc[:,-1].values)                        
                        
                        
                            
                        label=val_id[0]

                        list_sp.append(data_SP)
                        list_rs_initial.append(data_rs_initial)
                        list_sp_initial.append(data_sp_initial)
                        list_sp_final.append(data_sp_final)
                        list_dE.append(data_dE)
                        list_Lab.append(data_Lab)
                        list_LabCh.append(data_LabCh)                        
                        list_labels.append(label) 


                    ###### CREATE THE WIDGET TABS #######
    
                    out1 = ipw.Output()
                    out2 = ipw.Output()
                    out3 = ipw.Output()
                    out4 = ipw.Output()
                    out5 = ipw.Output()
                    out6 = ipw.Output()
                    out7 = ipw.Output()
                    out8 = ipw.Output()
                    out9 = ipw.Output()
                    out10 = ipw.Output()
                    out11 = ipw.Output()
                    out12 = ipw.Output()        

                    tabs_spectral = ipw.Tab(children = [out1,out2,out3])
                    tabs_colorimetry = ipw.Tab(children = [out4,out5,out6])
                    tabs_color = ipw.Tab(children = [out7,out8])


                    tabs_spectral.set_title(0,'Spectra')
                    tabs_spectral.set_title(1,'Spectral differences')
                    tabs_spectral.set_title(2,'Delta R')
                    tabs_colorimetry.set_title(0,'Colour differences')
                    tabs_colorimetry.set_title(1,'Lab-LCh')
                    tabs_colorimetry.set_title(2,'CIELAB space')
                    tabs_color.set_title(0,'Colour patches')
                    tabs_color.set_title(1,'Colour change slider')
                    #tab.set_title(7,'Data')
                    #tab.set_title(8,'Fading beam')
                    #tab.set_title(9,'Parameters')
                    #tab.set_title(10,'Statistics')
                    #tab.set_title(11,'Colour diff BWS')

                    list_tabs = [
                        tabs_spectral,
                        tabs_colorimetry,
                        tabs_color,
                    ]

                    tabs = ipw.Tab(children=list_tabs)
                    tabs.set_title(0, 'Spectral change')
                    tabs.set_title(1, 'Colorimetric change')
                    tabs.set_title(2, 'Colour change')

                    display(tabs)

                    with out1:                        
                        plotting.RS_SP(data=list_rs_initial, labels=list_labels)


                    with out2:                    
                        plotting.SP_diff(sp1=np.array(list_sp_initial), sp2=np.array(list_sp_final), wl=wl, labels=list_labels)


                    with out4:                       
                        if len(list_dE) == 1:
                            plotting.delta_E(data=list_dE, labels=['dE00'])
                        else:
                            plotting.delta_E(data=list_dE, labels=list_labels)


                    with out5:
                        plotting.LabCh(data=list_LabCh, labels=list_labels)


                    with out6:
                        plotting.CIELAB(data=list_Lab, labels=list_labels, color_data=None)                    
            
        Ids_nb.observe(values_change_Id, names='value')        

    display(ipw.HBox([MFT_Id_output,MFT_data_output]))
    run_button.on_click(run_button_pressed)



def power():
    """Graphical user interface to visualize the interim and processed data of power measurements.

    Args:
        No arguments is required.

    Returns:
        It returns a python widget object where the data of one or multiple measurements can be seen.
    """  

    ####### LOAD THE DATABASE FILES ########
        

    Objects_DB_file = folder_DB + 'DB_objects.csv'    
    Objects_DB = pd.read_csv(Objects_DB_file, index_col = 'object_id')

    Projects_DB_file = folder_DB + 'DB_projects.csv'
    Projects_DB = pd.read_csv(Projects_DB_file, index_col = 'project_id')

    Projects_techniques_file = folder_DB + 'Projects_techniques.csv'    
    Projects_techniques = pd.read_csv(Projects_techniques_file, index_col = 'Projects')

    
    ###### RETRIEVE MFT PROJECTS #######    

    projects_power = sorted(Projects_techniques[Projects_techniques['Power'] == True].index.values, reverse=True)
    folders_power = []

    for project_power in projects_power:

        PL = Projects_DB.loc[project_power]['PL']
        institution = Projects_DB.loc[project_power]['institution']
        institution_short = list(acronyms.institutions.keys())[list(acronyms.institutions.values()).index(institution)] 
        keyword = Projects_DB.loc[project_power]['keyword']

        name_folder = f'{project_power}_{PL}_{institution_short}_{keyword}'
        folders_power.append(name_folder)
        

    ###### CREATE WIDGETS #######


    projects = ipw.SelectMultiple(        
        options = folders_power,
        description = 'Projects',
        rows = 10,
        ensure_option=False,
        disabled=False,
        layout=Layout(width="25%", height="140px"),
        style=style,
    )

    data_categories = ipw.Dropdown(
        options=['interim', 'processed'],
        value='interim',
        #description='Data',
        disabled=False,
        layout=Layout(width="40%", height="30px"),
        #style=style,
    )

    plot_categories = ipw.Dropdown(
        options=['single', 'group', 'object'],
        value='single',
        #description='Data',
        disabled=False,
        layout=Layout(width="40%", height="30px"),
        #style=style,
    )

    save_fig = ipw.Checkbox(
        value=False,
        description='Save figure',
        disabled=False,
        indent=False
    )
    
    power_Id_output = ipw.Output()
    power_data_output = ipw.Output()
    power_info = ipw.Output()

    
    run_button = ipw.Button(description='Run')  

    display(ipw.HBox([projects,ipw.VBox([data_categories,plot_categories,save_fig])]))
    display(run_button)


    def run_button_pressed(*args): 

        Ids_nb_list = []

        with power_Id_output:
            power_Id_output.clear_output(wait=True)

            for project in projects.value:

                if folder_main == f'{folder_root}projects/': 
                    folder_start = f'{folder_main}{project}/data/interim/Power/'
                    folder_fig = f'{folder_main}{project}/figures/Power/'
                else:
                    folder_start = f'{folder_main}Power/data/interim/'
                    folder_fig = f'{folder_main}Power/figures/'

                folder_data_power = folder_start.replace('interim',data_categories.value)
                power_files =  sorted([x for x in os.listdir(folder_data_power) if f'{project.split("_")[0]}' in x and '.csv' in x]) 
                            
           
                if plot_categories.value == 'group':

                    objects_list = sorted(list(set([file.split("_")[2].split(".")[1] for file in power_files])))

                    for object in objects_list:

                        files_object = sorted(list(set([x for x in power_files if object in x])))

                        for file in files_object:
                            groups_list = sorted(list(set([file.split('_')[3] for file in files_object])))

                            for group in groups_list:
                                files_group = sorted([x for x in files_object if group in x and object in x])
                                Ids_nb_list.append(f'{files_group[0].split("_")[1]}_{files_group[0].split("_")[3]}_{files_group[0].split("_")[2]}') 

                                      

                elif plot_categories.value == 'single':        
                    for file in power_files:
                        full_Id = f'{file.split("_")[1]}_{file.split("_")[2]}_{file.split("_")[3]}'
                        Ids_nb_list.append(full_Id) 
                        
                                      


                elif plot_categories.value == 'object':

                    print('work in progress')

                Ids_nb_list = sorted(list(set(Ids_nb_list)))

                
            Ids_nb = ipw.SelectMultiple(options = Ids_nb_list, rows=20)
        
            display(Ids_nb)
            
            


        def values_change_Id(change):     
                
                with power_data_output:
                    power_data_output.clear_output(wait=True)
                    Id = change.new     
                                                 

                    if plot_categories.value == 'group':

                        itm_group = measurements.data(Id=Id.split('_')[2], project_id=Id.split('_')[0])                       

                        if save_fig.value == True:

                            fig = itm_group.plot_data(save=True, group = True)

                        else:
                            fig = itm_group.plot_data(group = True)                        
                        

                    elif plot_categories.value == 'single':                        
                        list_data = []
                        list_labels = []

                        for el in Id:
                            data = measurements.data(Id=el.split('_')[1], project_id=el.split('_')[0]).get_data()                            
                            data_array = np.array([data.index.astype(float),data.values.astype(float)])
                            label=el.split('_')[1]

                            list_data.append(data_array)
                            list_labels.append(label)
                            
                        fig = plotting.power(data=list_data, labels=list_labels,save=save_fig.value)

                    elif plot_categories.value == 'object':                        
                        print('work in progress')
                    
                    
                with power_info:
                    
                    power_info.clear_output(wait=True)
                    Id = change.new

                    pd.set_option('display.max_rows', None)
                    df_all_info = pd.DataFrame()

                    if plot_categories.value == 'single':                        

                        for val_id in Id:
                            info = measurements.data(Id=val_id.split('_')[1], project_id=val_id.split('_')[0]).get_info() 

                            df_all_info[val_id] = info

                        display(HTML("<div style='height: 350px; overflow:auto; width: fit-content'>" + df_all_info.style.to_html() + "</div>"))
                                 
                    
            
        Ids_nb.observe(values_change_Id, names='value')

    top_tab = ipw.Tab(children=[power_data_output, power_info])
    top_tab.set_title(0, 'Graph')
    top_tab.set_title(1, 'Info')

    display(ipw.HBox([power_Id_output,top_tab]))
    run_button.on_click(run_button_pressed)



def RS():
    """Graphical user interface to visualize the interim and processed data of reflectance measurements.

    Args:
        No arguments is required.

    Returns:
        It returns a python widget object where the data of one or multiple measurements can be seen.
    """  
       

    ####### LOAD THE DATABASE FILES ########    
    

    Objects_DB_file = folder_DB + 'DB_objects.csv'    
    Objects_DB = pd.read_csv(Objects_DB_file, index_col = 'object_id')

    Projects_DB_file = folder_DB + 'DB_projects.csv'
    Projects_DB = pd.read_csv(Projects_DB_file, index_col = 'project_id')

    Projects_techniques_file = folder_DB + 'Projects_techniques.csv'    
    Projects_techniques = pd.read_csv(Projects_techniques_file, index_col = 'Projects')

    
    projects_RS = sorted(Projects_techniques[Projects_techniques['RS'] == True].index.values, reverse=True)
    folders_RS = []

    for project_RS in projects_RS:

        PL = Projects_DB.loc[project_RS]['PL']
        institution = Projects_DB.loc[project_RS]['institution']
        institution_short = list(acronyms.institutions.keys())[list(acronyms.institutions.values()).index(institution)] 
        keyword = Projects_DB.loc[project_RS]['keyword']

        name_folder = f'{project_RS}_{PL}_{institution_short}_{keyword}'
        folders_RS.append(name_folder)
       

    ###### CREATE WIDGETS #######


    projects = ipw.SelectMultiple(        
        options = folders_RS,
        description = 'Projects',
        rows = 10,
        ensure_option=False,
        disabled=False,
        layout=Layout(width="25%", height="140px"),
        style=style,
    )

    data_categories = ipw.Dropdown(
        options=['interim', 'processed'],
        value='interim',
        #description='Data',
        disabled=False,
        layout=Layout(width="40%", height="30px"),
        #style=style,
    )

    plot_categories = ipw.Dropdown(
        options=['single', 'group', 'object'],
        value='single',
        #description='Data',
        disabled=False,
        layout=Layout(width="40%", height="30px"),
        #style=style,
    )

    groups = ipw.Checkbox(
        value=False,
        description='Groups',
        disabled=False,
        indent=False
    )

    save_fig = ipw.Checkbox(
        value=False,
        description='Save figure',
        disabled=False,
        indent=False
    )

    wl_range = ipw.IntRangeSlider(
        value=[400, 800],
        min=305,
        max=1100,
        step=1,
        description='Wavelength range (nm)',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='d',
        style=style,
        layout=Layout(width="40%", height="30px"),
    )

    sigma = ipw.IntSlider(
        min=1,
        max=50,
        step=1,
        description='Sigma',
        readout=True,
        style=style,
        layout=Layout(width="40%", height="30px"),
    )

    RS_Id_output = ipw.Output()
    RS_data_output = ipw.Output()

    run_button = ipw.Button(description='Run')  

    display(ipw.HBox([projects,ipw.VBox([data_categories,plot_categories,save_fig])]))
    display(wl_range)
    display(sigma)
    display(run_button)
    
     

    def run_button_pressed(*arg): 

        
        
        # create an empty list to store the Id numbers of the reflectance measurements
        Ids_nb_list = []
        RS_files_all = []        
        
        with RS_Id_output:
            RS_Id_output.clear_output(wait=True)                      
            
            for project in projects.value:

                if folder_main == f'{folder_root}projects/': 
                    folder_start = f'{folder_main}{project}/data/interim/RS/'
                    folder_fig = f'{folder_main}{project}/figures/RS/'
                else:
                    folder_start = f'{folder_main}RS/data/interim/'
                    folder_fig = f'{folder_main}RS/figures/'

                # get the project id number
                project_id = project.split('_')[0]
               
                # select the desired data folder: interim or processed
                folder_data_RS = folder_start.replace('interim',data_categories.value)

                # retrieve the reflectance files in the choosen folder
                RS_files_project =  sorted([x for x in os.listdir(folder_data_RS) if '.txt' in x]) 
                RS_files_all.append(RS_files_project)      

                            
                # according to plot_categories values (single, group, or object), append the Id numbers in the Ids_nb_list
                if plot_categories.value == 'group':
                    objects_list = sorted(list(set([file.split("_")[2].split(".")[1] for file in RS_files_project])))

                    for object in objects_list:

                        files_object = sorted(list(set([x for x in RS_files_project if object in x])))

                        for file in files_object:
                            groups_list = sorted(list(set([file.split('_')[3] for file in files_object])))

                            for group in groups_list:
                                files_group = sorted([x for x in files_object if group in x and object in x])
                                Ids_nb_list.append(f'{files_group[0].split("_")[1]}_{files_group[0].split("_")[2].split(".")[1]}_{files_group[0].split("_")[3]}')                    

                elif plot_categories.value == 'single':                            
                    for file in RS_files_project:
                        full_Id = f'{file.split("_")[1]}_{file.split("_")[2]}_{file.split("_")[3]}'            
                        Ids_nb_list.append(full_Id)
                                                

                elif plot_categories.value == 'object':
                    
                    objects_list = sorted(list(set([file.split('_')[2].split('.')[1] for file in RS_files_project])))
                    

                    for object in objects_list:
                        Ids_nb_list.append(f'{project_id}_{object}')
                                       

                Ids_nb_list = sorted(list(set(Ids_nb_list)))   

                
            Ids_nb = ipw.SelectMultiple(options = Ids_nb_list, rows=20)
        
            display(Ids_nb)
            
        
        wl_min = wl_range.value[0]
        wl_max = wl_range.value[1]
        
        RS_files_all = [x for xs in RS_files_all for x in xs]
        

        def values_change_Id(change):
            with RS_data_output:              
                RS_data_output.clear_output(wait=True)
                Id = change.new 
                Ids_list = []                
                

                if plot_categories.value == 'single': 
                    [Ids_list.append((val_id.split('_')[1],val_id.split('_')[0])) for val_id in Id]
                                                                  
                    
                if plot_categories.value == 'group':

                    for val_id in Id:
                        group_nb = val_id.split('_')[2]
                        object_id = val_id.split('_')[1]
                                            

                        Ids = [(x.split('_')[2], x.split('_')[1]) for x in RS_files_all if group_nb in x and object_id in x]    
                        [Ids_list.append(id) for id in Ids]
                                            

                if plot_categories.value == 'object':                       

                    for val_id in Id:                         
                        Ids = [(x.split('_')[2], x.split('_')[1]) for x in RS_files_all if val_id.split('_')[1] in x]                       
                        [Ids_list.append(id) for id in Ids]  
      
                  
             
                list_data_SP = []
                list_data_SP_deriv = []
                list_data_Lab = []
                list_labels = []

                for val_id in Ids_list:                    
                    rs = measurements.data(Id=val_id[0], project_id=val_id[1])
                        
                    if wl_max > rs.get_data(data='sp').index.astype(float)[-1]:                            
                        new_wl_max = int(rs.get_data(data='sp').index.astype(float)[-1])
                            
                    else:
                        new_wl_max = int(wl_max)
                       

                    data_sp = rs.get_data(data='sp').loc[str(wl_min):str(new_wl_max)] 
                    wl = data_sp.index.astype(float)                
                    data_SP = np.array([wl, gaussian_filter1d(data_sp.values.astype(float), sigma=sigma.value)])
                    data_SP_deriv = np.array([wl, np.gradient(data_SP[1], wl.values[1]-wl.values[0])])
                    data_Lab = rs.get_data(data='Lab')['value1'][['L*','a*','b*']].astype(float).values                                                 
                        
                    label=val_id[0]

                    list_data_SP.append(data_SP)
                    list_data_SP_deriv.append(data_SP_deriv)
                    list_data_Lab.append(data_Lab)
                    list_labels.append(label)

                
                ###### CREATE THE WIDGET TABS #######

                out1 = ipw.Output()
                out2 = ipw.Output()
                out3 = ipw.Output()
                out4 = ipw.Output()
                out5 = ipw.Output()
                        
                tab = ipw.Tab(children = [out1,out2,out3,out4,out5])   

                tab.set_title(0,'Spectra')
                tab.set_title(1,'SP 1st deriv.')
                tab.set_title(2,'CIELAB')
                tab.set_title(3,'Colour patches')  
                tab.set_title(4,'Data')  
                

                display(tab)

                with out1:                        
                    plotting.RS_SP(data=list_data_SP, labels=list_labels,)

                with out2:
                    plotting.RS_SP(data=list_data_SP_deriv, labels=list_labels)

                with out3:                                         
                    plotting.CIELAB(data=list_data_Lab, labels=list_labels, color_data=None)

                with out4:
                    plotting.colour_patches(data=list_data_Lab, labels=list_labels)
              
    
    
        Ids_nb.observe(values_change_Id, names='value')
    
    
    display(ipw.HBox([RS_Id_output,RS_data_output]))   

    run_button.on_click(run_button_pressed)



def overview():
    """Function that enables the selection and the visualization of various analyses.
    
    Args:
        

    Returns:
        It returns a python widget window in order to select and visualize the results of multiple analyses.
    """

    ####### LOAD THE DATABASE FILES ########

    folder_DB = '/home/gus/Documents/RCE/databases/'

    Objects_DB_file = folder_DB + 'DB_objects.csv'    
    Objects_DB = pd.read_csv(Objects_DB_file, index_col = 'object_id')
    object_ids_list = Objects_DB.index    

    Projects_DB_file = folder_DB + 'DB_projects.csv'
    Projects_DB = pd.read_csv(Projects_DB_file, index_col = 'project_id')
    project_ids_list = Projects_DB.index
      
    dates_list = ['All'] + sorted(set([p.split('-')[0] for p in project_ids_list]))
    techniques_list = ['All','FTIR','MFT','Raman','RS']  
    
    
    wg_techniques = ipw.SelectMultiple(options=techniques_list, value=['All'], rows=5, description='Analytical techniques', style=style)
    wg_projects = ipw.SelectMultiple(options=['All']+list(project_ids_list.values), value=['All'], rows=5, description='Project Ids', style=style)
    wg_dates = ipw.SelectMultiple(options=dates_list, value=['All'], rows=5, description='Project dates', style=style)
    wg_objects = ipw.SelectMultiple(options=['All']+list(object_ids_list.values), value=['All'], rows=5, description='Object Ids', style=style)
    wg_search_button = ipw.Button(description='Search')
    output_button = ipw.Output()

    params = ipw.VBox([ipw.HBox([wg_techniques,wg_projects,wg_dates, wg_objects]), wg_search_button,output_button])

    
    output_MFT_SP = ipw.Output()
    output_MFT_dE = ipw.Output()
    output_MFT_Lab = ipw.Output()
    output_MFT_CIELAB = ipw.Output()
    
    output_RS_SP = ipw.Output()
    output_RS_SP_plot = ipw.Output()
    output_RS_CIELAB = ipw.Output()
    output_RS_CIELAB_plot = ipw.Output()
    output_RS_fname = ipw.Output()

    tabs_MFT = ipw.Tab(children=[output_MFT_SP,output_MFT_dE,output_MFT_Lab,output_MFT_CIELAB])
    tabs_RS = ipw.Tab(children=[output_RS_SP,output_RS_CIELAB])

    tabs_MFT.set_title(0, 'SP')
    tabs_MFT.set_title(1, 'dE')
    tabs_MFT.set_title(2, 'Lab')
    tabs_MFT.set_title(3, 'CIELAB')
   
    tabs_RS.set_title(0, 'SP')
    tabs_RS.set_title(1, 'CIELAB')
    
    
    
    output_FTIR = ipw.Output()
    output_MFT = ipw.Output()
    output_Raman = ipw.Output()
    output_RS = ipw.Output()
    
    
    def get_fname(input):

        fnames_techniques = []
        fnames_projects = []
        fnames_dates = []        
        fnames_objects = []


        params_techniques = input['techniques']
        params_projects = input['projects']
        params_dates = input['dates']
        params_objects = input['objects']

        if params_techniques[0] == 'All':
            params_techniques = techniques_list[1:] 

        if params_projects[0] == 'All':
            params_projects = project_ids_list[1:] 

        if params_dates[0] == 'All':
            params_dates = dates_list[1:] 

        if params_objects[0] == 'All':
            params_objects = object_ids_list[1:] 

        folder_projects = '/home/gus/Documents/RCE/projects/'       


        for var_project in params_projects:
            for var_technique in params_techniques:
                name_folder = [x for x in os.listdir(folder_projects) if var_project in x][0]
                dir_files = f'/home/gus/Documents/RCE/projects/{name_folder}/data/interim/{var_technique}/'

                for path in os.listdir(dir_files):
                    full_path = os.path.join(dir_files,path)
                    if os.path.isfile(full_path):
                        fnames_techniques.append(full_path)


        for var_project in params_projects:
            files = sorted([x for x in fnames_techniques if var_project in x])
            fnames_projects.append(files)
            
        return fnames_projects


    def search_button(b):

        with output_button:

            clear_output()

            dic_params = {
                'techniques':wg_techniques.value,
                'projects':wg_projects.value,
                'dates':wg_projects.value,
                'objects':wg_objects.value}

            fnames_list = get_fname(dic_params)   
            
            #boxes = {f'{f.split("/")[-1].split("_")[1]}_{f.split("/")[-1].split("_")[2]}_{f.split("/")[-1].split("_")[3]}': wg.Checkbox(value=False, description=f'{f.split("/")[-1].split("_")[1]}_{f.split("/")[-1].split("_")[2]}_{f.split("/")[-1].split("_")[3]}') for f in fnames_list[0] }

            boxes = {f'{f.split("/")[-1].split("_")[1]}_{f.split("/")[-1].split("_")[2]}_{f.split("/")[-1].split("_")[3]}': ipw.Checkbox(value=False, description=f'{f.split("/")[-1].split("_")[2]}_{f.split("/")[-1].split("_")[3]}') for f in fnames_list[0] }

            

            techniques = dic_params['techniques']
            if list(techniques) == ['All']:
                techniques = techniques_list[1:]
            

            dict_tabs = {
                tuple(['All']): [output_FTIR,tabs_MFT,output_Raman,tabs_RS],
                tuple(['FTIR']): [output_FTIR],
                tuple(['MFT']): [tabs_MFT],
                tuple(['Raman']): [output_Raman],
                tuple(['RS']): [tabs_RS],
                tuple(['FTIR','MFT']): [output_FTIR,tabs_MFT],
                tuple(['MFT','RS']): [tabs_MFT,tabs_RS],
                tuple(['MFT','Raman','RS']): [tabs_MFT,output_Raman,tabs_RS],
                tuple(['FTIR','MFT','Raman','RS']): [output_FTIR,tabs_MFT,output_Raman,tabs_RS]}

            list_tabs = dict_tabs[tuple(list(techniques))]       
            

            tabs_techniques = ipw.Tab(children=list_tabs)

            

            if len(techniques) == 1:
                tabs_techniques.set_title(0,list(techniques)[0])

            if len(techniques) == 2:
                tabs_techniques.set_title(0,list(techniques)[0])
                tabs_techniques.set_title(1,list(techniques)[1])

            if len(techniques) == 3:
                tabs_techniques.set_title(0,list(techniques)[0])
                tabs_techniques.set_title(1,list(techniques)[1])
                tabs_techniques.set_title(2,list(techniques)[2])

            if len(techniques) == 4:
                tabs_techniques.set_title(0,list(techniques)[0])
                tabs_techniques.set_title(1,list(techniques)[1])
                tabs_techniques.set_title(2,list(techniques)[2])
                tabs_techniques.set_title(3,list(techniques)[3])

            
            with output_MFT:
                clear_output()
                print('plot MFT data')

                      
            
            
            def update_RS_SP(**kwargs):
                with output_RS_SP:
                    fig, ax = plt.subplots(1,1,figsize=(15,10))
                    sns.set()
                    fs = 20

                    ax.set_xlabel('Wavelength $\lambda$ (nm)', fontsize=fs)
                    ax.set_ylabel('Reflectance factor', fontsize=fs)

                    for (filename, enabled) in kwargs.items():
                        if enabled:                   
                            
                            project = filename.split('_')[0]
                            Id = filename.split('_')[1]                                                         
                            
                            itm = interim.itm(Id,project)
                            sp = itm.get_data(data='sp',show_plot=False)
                            wl = sp.index.astype('float')      

                            ax.plot(wl,sp,label=filename)

                            ax.xaxis.set_tick_params(labelsize=fs)
                            ax.yaxis.set_tick_params(labelsize=fs)

                            ax.legend()

            def update_RS_CIELAB(**kwargs):
                with output_RS_CIELAB:
                    fig, ax = plt.subplots(2,2, figsize=(10, 10), gridspec_kw=dict(width_ratios=[1, 2], height_ratios=[2, 1]))
                    sns.set()
                    fs = 20
                    cps = 6     # capsize values
                    Lb = ax[0,0]
                    ab = ax[0,1]
                    AB = ax[1,0]
                    aL = ax[1,1]

                    Lb.set_xlabel("CIE $L^*$", fontsize=fs)
                    Lb.set_ylabel("CIE $b^*$", fontsize=fs)
                    AB.set_xlabel("CIE $a^*$", fontsize=fs)
                    AB.set_ylabel("CIE $b^*$", fontsize=fs)
                    aL.set_xlabel("CIE $a^*$", fontsize=fs)
                    aL.set_ylabel("CIE $L^*$", fontsize=fs) 

                    for (filename,enabled) in kwargs.items():
                        if enabled:
                            project=filename.split('_')[0]                            
                            Id = filename.split('_')[1]  

                            itm = interim.itm(Id,project)
                            data = itm.get_data(data='Lab', show_plot=False)['value1']

                            L = np.float(data.loc['L*'])
                            a = np.float(data.loc['a*'])
                            b = np.float(data.loc['b*'])

                            Lab = np.array([L, a, b]).transpose()
                            srgb = colour.XYZ_to_sRGB(colour.Lab_to_XYZ(Lab), d65).clip(0, 1)

                            ab.scatter(a,b, color=srgb, label=filename)
                            Lb.scatter(L,b, color=srgb)
                            aL.scatter(a,L, color=srgb)

                            ab.xaxis.set_tick_params(labelsize=fs)
                            Lb.xaxis.set_tick_params(labelsize=fs)
                            aL.xaxis.set_tick_params(labelsize=fs)

                            ab.yaxis.set_tick_params(labelsize=fs)
                            Lb.yaxis.set_tick_params(labelsize=fs)
                            aL.yaxis.set_tick_params(labelsize=fs)

                            ab.legend()


            output_chart_RS_SP = ipw.interactive_output(update_RS_SP, boxes)
            output_chart_RS_CIELAB = ipw.interactive_output(update_RS_CIELAB, boxes)

            GUI_RS_SP = ipw.HBox([ipw.VBox(list(boxes.values())), output_chart_RS_SP])
            GUI_RS_CIELAB = ipw.HBox([ipw.VBox(list(boxes.values())), output_chart_RS_CIELAB])

            with output_RS_SP:                    
                display(GUI_RS_SP)

            with output_RS_CIELAB:
                display(GUI_RS_CIELAB)                

            '''
            with output_RS_fname:
                clear_output()
                @wg.interact(**boxes)
                
                def update(**kwargs):
                    
                    for f in fnames_list[0]:
                        clear_output()
                        display(boxes[f])               
            
               


            with output_RS_SP_plot:               
                

                
                fig, ax = plt.subplots(1,1, figsize = (15,10))
                sns.set()
                fs = 24


                
                for file in fnames_list[0]:
                    clear_output()
                    if boxes[file].value == True:                        

                        Id = file.split('/')[-1].split('_')[1]
                        project = 1
                        itm = class_interim.itm(Id,project)
                        sp = itm.get_data(data='sp',show_plot=False)
                        wl = sp.index.astype('float')      

                        ax.plot(wl,sp)


                ax.set_xlabel('Wavelength $\lambda (nm)$', fontsize=fs)
                ax.set_ylabel('Reflectance factor', fontsize=fs)

                ax.xaxis.set_tick_params(labelsize=fs)
                ax.yaxis.set_tick_params(labelsize=fs)                

                plt.tight_layout()
                plt.show()

            
                def update_plot(**kwargs):
                    
                    for f in fnames_list[0]:
                        if boxes[f].value == False:
                            print('it is off')

                        else:
                            print('it is on')

                update_plot()
            
                
            with output_RS_CIELAB_plot:

                fig, ax = plt.subplots(2,2, figsize=(10, 10), gridspec_kw=dict(width_ratios=[1, 2], height_ratios=[2, 1]))
                sns.set()
                fs = 20
                cps = 6     # capsize values
                Lb = ax[0,0]
                ab = ax[0,1]
                AB = ax[1,0]
                aL = ax[1,1]

                Lb.set_xlabel("CIE $L^*$", fontsize=fs)
                Lb.set_ylabel("CIE $b^*$", fontsize=fs)
                AB.set_xlabel("CIE $a^*$", fontsize=fs)
                AB.set_ylabel("CIE $b^*$", fontsize=fs)
                aL.set_xlabel("CIE $a^*$", fontsize=fs)
                aL.set_ylabel("CIE $L^*$", fontsize=fs) 

                for file in fnames_list[0]:
                    clear_output()


                plt.tight_layout()
                plt.show()    
            '''    
            
                

            with output_RS_SP:
                display(ipw.HBox([output_RS_SP_plot,output_RS_fname]))

            with output_RS_CIELAB:
                display(ipw.HBox([output_RS_CIELAB_plot,output_RS_fname]))




                
            display(tabs_techniques)

            #print(dic_params) 
            #print(fnames_list)
            #return dic_params
        
    wg_search_button.on_click(search_button)

    display(ipw.VBox([params]))
    





