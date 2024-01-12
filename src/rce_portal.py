
####### IMPORT STATEMENTS #######

import os
from pathlib import Path
from glob import glob
import pandas as pd
import numpy as np
from typing import Union

import ipywidgets as ipw
from ipywidgets import Layout, Button, Box
from IPython.display import display, clear_output, HTML

import rce_projects
import acronyms



def zoeken(folder_RCE:Union[str, Path]= '~/Documents/RCE', dict_to_inject_into={}):
    """Search engine to perform query on aanvraag projects.

    Parameters
    ----------
    folder_RCE : Union[str, Path], optional
        Path of the root folder containing everything related to the RCE, by default '~/Documents/RCE'

    dict_to_inject_into : dict, optional
        Parameter that set the results to be a global variable by calling the variable "results" in any other cells. To make it worked, it should be set to globals(), by default {}
    """
    
    style = {"description_width": "initial"}

    folder_RCE = Path(folder_RCE).expanduser()
    folder_DB = folder_RCE / 'databases' 

    objects_DB = pd.read_csv(folder_DB / 'DB_objects.csv')
    projects_DB = pd.read_csv(folder_DB / 'DB_projects.csv')     

    dic_objects = dict(zip(objects_DB.columns,[sorted(set(objects_DB[col].dropna())) for col in objects_DB.columns]))
    dic_projects = dict(zip(projects_DB.columns,[sorted(set(projects_DB[col].dropna())) for col in projects_DB.columns]))

    dic_projects['analyses'] = list(acronyms.analyses.keys())

    dic_criteria = {**dic_objects, **dic_projects}
    dic_criteria['Select a criteria'] = ['']

    projects_DB = projects_DB.set_index('project_id')
    all_projects = projects_DB.index

    for project in all_projects:
        p = rce_projects.RCEProject(project)
        projects_DB.loc[project,'analyses'] = f"{p.techniques}"

    projects_DB = projects_DB.reset_index()



    def setup_dropdown_combobox_pair(data_dict, default_value, selected_values):
        
        # Create the Dropdown widget
        dropdown = ipw.Dropdown(
            options=sorted(list(data_dict.keys())),
            value=default_value,
            #description='Select an option:'
        )

        # Create the Combobox widget
        combobox = ipw.Combobox(
            placeholder='Select from the list',
            options=data_dict[default_value],
            #description='List elements:'
        )

        # Define a function to update the Combobox options when the Dropdown value changes
        def update_combobox_options(change):
            selected_value = change['new']
            combobox.options = data_dict[selected_value]
            combobox.value = None  # Reset the Combobox value

        # Attach the function to the Dropdown widget's observe method
        dropdown.observe(update_combobox_options, names='value')

        # Define a function to track the selected values
        def on_combobox_change(change):
            selected_values.append((dropdown.value, change['new']))

        # Attach the function to the Combobox widget's observe method
        combobox.observe(on_combobox_change, names='value')

        # Container for the pair
        pair_container = ipw.HBox([dropdown, combobox])

        # Display the widgets
        display(pair_container)

    # Display title
    display(HTML("<h1>Input selection</h1>"))

    # List to track selected values
    selected_values = []
    
    # Use the function to set up multiple dropdown-combobox pairs
    setup_dropdown_combobox_pair(dic_criteria, default_value='Select a criteria', selected_values=selected_values)
    setup_dropdown_combobox_pair(dic_criteria, default_value='Select a criteria', selected_values=selected_values)
    setup_dropdown_combobox_pair(dic_criteria, default_value='Select a criteria', selected_values=selected_values)
    setup_dropdown_combobox_pair(dic_criteria, default_value='Select a criteria', selected_values=selected_values)
    setup_dropdown_combobox_pair(dic_criteria, default_value='Select a criteria', selected_values=selected_values)
    setup_dropdown_combobox_pair(dic_criteria, default_value='Select a criteria', selected_values=selected_values)
    setup_dropdown_combobox_pair(dic_criteria, default_value='Select a criteria', selected_values=selected_values)


    # Create a single dataframe combining info from db_projects and db_objects

    
    projects_DB = projects_DB.set_index('project_id')

    DB = objects_DB

    project_params = list(projects_DB.columns) + ['analyses']
    DB[project_params] = len(project_params) * ['']
    

    DB_copy = DB.T
    DB_mutliprojects = pd.DataFrame(index = DB_copy.index)

    for col in DB_copy.columns:
        info = DB_copy[col]        
        
        project_id = info.loc['project_id']        
        
        if project_id == 'na':
            len(project_params) * ['']
            
        else:
            
            if '_' in project_id:
                project_ids = project_id.split('_')
                analyses = rce_projects.RCEProject(project_ids[0]).techniques
                
                DB_copy[col]['project_id'] = project_ids[0]
                project_info = list(projects_DB.loc[project_ids[0]]) + [analyses]
                DB_copy[col][project_params] = np.asarray(project_info, dtype=object)            
                #data_col = pd.DataFrame(db_copy[col])
                
                for Id in project_ids[1:]:
                    DB_mutliprojects[col] = DB_copy[col]
                    project_id = Id
                    analyses = rce_projects.RCEProject(project_id).techniques
                    project_info = list(projects_DB.loc[project_id]) + [analyses]
                    
                    DB_mutliprojects[col]['project_id'] = project_id
                    DB_mutliprojects[col][project_params] = np.asarray(project_info, dtype=object)     
                    
                    
                
            else:
                
                analyses = rce_projects.RCEProject(project_id).techniques            
                project_info = list(projects_DB.loc[project_id])  + [analyses]            
                DB_copy[col][project_params] = np.asarray(project_info, dtype=object)
            
    DB_final = pd.concat([DB_copy,DB_mutliprojects], axis=1).T


    # Display title
    display(HTML("<h1>Output selection</h1>"))

    output_selection = ipw.SelectMultiple(
        options = sorted(list(DB_final.columns)),
        layout=Layout(width="25%", height="300px"),
        style = style
    )                    
                      
    display(output_selection)


    run = ipw.Button(
        description = 'Run'
    )

    button_run_output = ipw.Output()
    results_output = ipw.Output()    # widgets that will store the output of the query

    display(run)
    


    # Define a function that perform the query
    def button_run_pressed(b): 
        nonlocal dict_to_inject_into

        with results_output:
            results_output.clear_output(wait=True)
            #print("Selected values:")
            data = DB_final.reset_index()
            
            for pair in selected_values:
                print(pair)
                if pair[0] == 'analyses':
                    data = pd.DataFrame([data.T[col] for col in data.T.columns if pair[1] in data.T[col].loc['analyses']])
                    
                else:                    
                    data = data.query(f'{pair[0]}=="{pair[1]}"')
                #print(f"Dropdown: {pair[0]}, Combobox: {pair[1]}")

            
            data = data[list(output_selection.value)]
            display(data)
            #display(data.drop_duplicates())

        # Inject the final output into a dictionary
        dict_to_inject_into['results'] = data.drop_duplicates()         
            

            
    # Display title
    display(HTML("<h1>Results</h1>"))
    display(results_output)


    # Connect the widgets 'run" with the function 'button_run_pressed', so that when one clicks on the button 'run', the function is executed
    run.on_click(button_run_pressed)
