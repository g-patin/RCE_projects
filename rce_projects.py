####### IMPORT STATEMENTS #######

import os
from pathlib import Path
from glob import glob
import pandas as pd
from typing import Union
import nbformat as nbf
from nbformat.v4 import new_markdown_cell

import ipywidgets as wg
from ipywidgets import Layout, Button, Box
from IPython.display import display, clear_output

import web_utils
import acronyms


####### GENERAL PARAMETERS #######

style = {"description_width": "initial"}


####### PROJECT CLASS #######


class RCEProject(object):

    def __init__(self,project_id:str, folder_RCE:Union[str, Path]= '~/Documents/RCE'):

        self.project_id = project_id  
        self.folder_RCE = Path(folder_RCE).expanduser() 
        self._init_folders()
        self._init_structure()
        
        
        if self.project_id == 'create':

            # Retrieve list of institutions
            institutions_file = open(str(self.folder_DB / 'Institutions.txt'), 'r')
            institutions = institutions_file.read()
            institutions_list = institutions.split("\n")            
            
            # Create several python ipywidgets
            project_Id = wg.Text(        
                value='',
                placeholder='Type something',
                description='Project Id',
                disabled=False,
                layout=Layout(width="95%", height="30px"),
                style=style,   
            )

            institution = wg.Combobox(
                placeholder = 'Enter an institution',
                options = institutions_list,
                description = 'Institution',
                ensure_option=False,
                disabled=False,
                layout=Layout(width="95%", height="30px"),
                style=style,
            )

            aanvraagdatum = wg.DatePicker(
                description='Aanvraagdatum',
                disabled=False,
                layout=Layout(width="90%", height="30px"),
                style=style,
            )

            uiterste_datum = wg.DatePicker(
                description='Uiterste datum',
                disabled=False,
                layout=Layout(width="90%", height="30px"),
                style=style,
            )

            PL = wg.Dropdown(
                options=sorted(list(acronyms.medewerkers.keys())),
                value=list(acronyms.medewerkers.keys())[0],
                description='PL',
                disabled=False,
                #layout=Layout(width="10%", height="30px"),
                #style=style,
            )

            ML = wg.SelectMultiple(
                options=sorted(list(acronyms.medewerkers.keys())),
                value=[list(acronyms.medewerkers.keys())[0]],
                rows=8,
                description='ML',
                disabled=False,
                #layout=Layout(width="10%", height="30px"),
                #style=style,
            )

            recording = wg.Button(
                description='Create record',
                disabled=False,
                button_style='', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Click me',
                #layout=Layout(width="50%", height="30px"),
                #style=style,               
            )

            folders = wg.Button(
                description='Create folders',
                disabled=False,
                button_style='', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Click me',
                #layout=Layout(width="50%", height="30px"),
                #style=style,                
            )

            github_repo = wg.Button(
                description='Create Github repo',
                disabled=False,
                button_style='',
                tooltip='Click me',
            )

            methods = wg.SelectMultiple(
                options = acronyms.analyses.keys(),
                value = [list(acronyms.analyses.keys())[0]],
                rows = 9,
                description = 'Methods',
                disabled = False,
            )

            project_keyword = wg.Text(
                placeholder = 'Describe project in 1 word',
                description = 'Project keyword',
                disabled = False,
                layout=Layout(width="95%", height="40px"),
                style = style,
            )

            project_description = wg.Textarea(
                placeholder = 'Description of the project (optional).',
                description = 'Project description',
                disabled = False,
                layout=Layout(width="95%", height="80px"),
                style = style,
            )

            button_record_output = wg.Output()
            button_folders_output = wg.Output()
            button_repo_output = wg.Output()


            # Define a function to record the project in the projects database file
            def button_record_pressed(b):
                with button_record_output:
                    button_record_output.clear_output(wait=True)

                    Projects_DB_file = self.folder_DB / 'DB_projects.csv'
                    Projects_DB = pd.read_csv(Projects_DB_file)

                
                    new_row = pd.DataFrame({'project_Id':project_Id.value,
                            'institution':institution.value, 
                            'aanvraagdatum':aanvraagdatum.value, 
                            'uiterste_datum':uiterste_datum.value,
                            'PL':PL.value,
                            'ML':'-'.join(ML.value),
                            'keyword':project_keyword.value},                       
                            index=[0] 
                            )           
                    institutions_list = list(institution.options)
                    
                    if institution.value not in institutions_list:                       
                        institutions_list.append(str(institution.value))         
                        institutions_list = sorted(institutions_list)

                        with open(str(self.folder_DB / 'Institutions.txt'), 'w') as f:
                            f.write('\n'.join(institutions_list))

                        f.close()
                    
                    Projects_DB_new = pd.concat([Projects_DB, new_row],)
                    Projects_DB_new.to_csv(Projects_DB_file, index= False)
                    print(f'Project {project_Id.value} added to database.')

            
            # Define a function to create the folder structure of the project
            def button_folders_pressed(b):
                with button_folders_output:
                    button_folders_output.clear_output(wait=True)            

                    ML_full = ''
                    for initials in ML.value:
                        name =  acronyms.medewerkers[initials]
                        ML_full = ML_full + f'{name} ({initials}), ' 

                    ML_full = ML_full[:-2]
                    
                    institution_short = list(acronyms.institutions.keys())[list(acronyms.institutions.values()).index(institution.value)]
                    folder_project = self.folder_projects / f'{project_Id.value}_{PL.value}_{institution_short}_{project_keyword.value}'
                    
                    if not folder_project.exists():        # if the folder has not been already created
                        
                        # create the main folder of the project
                        os.mkdir(folder_project)

                        # create the subfolders
                        os.mkdir(f'{folder_project}/data')
                        os.mkdir(f'{folder_project}/docs')
                        os.mkdir(f'{folder_project}/figures')
                        os.mkdir(f'{folder_project}/notebooks')
                        os.mkdir(f'{folder_project}/reports')

                        # create the subsubfolders
                        os.mkdir(f'{folder_project}/data/external')
                        os.mkdir(f'{folder_project}/data/interim')
                        os.mkdir(f'{folder_project}/data/processed')
                        os.mkdir(f'{folder_project}/data/raw')

                                                
                        # create a readme for the raw files
                        with open(f'{folder_project}/data/raw/README.md', 'w') as f:
                                f.write('#### NAMING CONVENTIONS FOR RAW FILES ####\n')
                                f.write('\n')
                                f.write('write here naming conventions')           
                    
                        # create data folders for each analytical technique selected
                        for method in methods.value:
                            
                            # create the subsubsubfolders
                            os.mkdir(f'{folder_project}/data/raw/{method}')
                            os.mkdir(f'{folder_project}/data/interim/{method}')
                            os.mkdir(f'{folder_project}/data/processed/{method}')

                            os.mkdir(f'{folder_project}/data/raw/{method}/To_process')
                            os.mkdir(f'{folder_project}/data/interim/{method}/To_process')

                            # create jupyter notebooks
                            web_utils.create_jupyter_notebook(f'{folder_project}/notebooks/{method}_data.ipynb', 'hello there !') 

                            code_folder = f'''\
        cd {folder_project}/data/interim/{method}/'''
                            
                            code = f'''\
        files = sorted(glob('**'))'''

                            with open(f'{folder_project}/notebooks/{method}_data.ipynb', 'r') as file:
                                notebook = nbf.read(file, nbf.NO_CONVERT)

                                new_code_cell_folder = nbf.v4.new_code_cell(source=code_folder)
                                new_md_cell = new_markdown_cell(f'## {method}')
                                new_code_cell = nbf.v4.new_code_cell(source=code)

                                notebook['cells'].append(new_md_cell)
                                notebook['cells'].append(new_code_cell_folder) 
                                notebook['cells'].append(new_code_cell)                        
                            
                            with open(f'{folder_project}/notebooks/{method}_data.ipynb', 'w') as file:
                                nbf.write(notebook,file)                 
                            


                         # create a readme file for the project
                        readme_template = self.folder_RCE / 'docs' / 'Project_README_template.md'                        
                        result = open(readme_template).read().format(
                            project_Id = project_Id.value,
                            institution = f'{institution.value} ({institution_short})',
                            PL = f'{acronyms.medewerkers[PL.value]} ({PL.value})',
                            ML = ML_full, 
                            project_description = project_description.value,
                            )
                        output_filename = f'{project_Id.value}_README.md'
                        open(f'{folder_project}/{output_filename}', 'w').write(result)

                        print(f'Wrote file {output_filename}')
                        print(f'Project {project_Id.value} -> folders and files created')

                    else:
                        print(f'The folder "{folder_project}" already exists.')

            recording.on_click(button_record_pressed)
            folders.on_click(button_folders_pressed)

            # Display the ipywidgets
            display(wg.HBox([
                wg.VBox([
                    wg.HBox([
                        wg.VBox([project_Id,institution, project_keyword],layout=Layout(width="60%", height="95%")),
                        wg.VBox([aanvraagdatum,uiterste_datum],layout=Layout(width="60%", height="95%")),
                        ]),
                    project_description,
                    ], layout=Layout(width="50%", height="100%")),
                wg.VBox([PL,ML]),
                wg.VBox([methods])
                ], layout=Layout(width="100%", height="110%"))
            )     
    
            display(wg.HBox([recording, button_record_output]))
            display(wg.HBox([folders, button_folders_output]))
            display(wg.HBox([github_repo, button_repo_output]))

    
    def __repr__(self):                  
       return f'RCE project(project_Id = {self.project_id})'

    
    def _init_folders(self):  
         
        self.folder_DB = self.folder_RCE / 'databases'
        self.folder_projects = self.folder_RCE / 'projects'

        if self.project_id != 'create':

            possible_matches = list(self.folder_projects.glob(f'*{self.project_id}_*'))

            if len(possible_matches) !=1:
                raise RuntimeError(f'There is no unique project folder corresponding to {self.project_id}. Please, first create a project using the following command: RCEProject("create")')
            
            self.folder_project = possible_matches[0]
            self.folder_rawdata = self.folder_project / 'data' / 'raw'
            self.folder_interimdata = self.folder_project / 'data' / 'interim'

       
   
    def _init_structure(self):
        '''Explore the folder structure and initialize techniques and objects
        
        '''

        if self.project_id != 'create':

            # -------------------------------
            # Techniques
            # -------------------------------
            self.techniques = [ x.name for x in sorted(list(self.folder_rawdata.glob('*'))) if x.is_dir() ]


            # -------------------------------
            # Objects
            # -------------------------------
            objects_DB = pd.read_csv(self.folder_DB / 'DB_objects.csv')

            list_objects = []
            for column in objects_DB.T:
                projects = objects_DB.T[column].loc['project_Id']
                
                if self.project_id in projects:
                    object_Id = objects_DB.T[column].loc['object_Id']
                    list_objects.append(object_Id)
            
            self.objects = sorted(list_objects)


            # -------------------------------
            # Objects info
            # -------------------------------
            objects_DB = pd.read_csv(self.folder_DB / 'DB_objects.csv')            
            
            self.objects_info = objects_DB[objects_DB['object_Id'].isin(self.objects)]



            # -------------------------------
            # Info
            # -------------------------------
            DB_info_path = self.folder_DB / 'DB_projects.csv'
            DB_info = pd.read_csv(DB_info_path, index_col='project_Id')

            self.info = pd.DataFrame(DB_info.loc[self.project_id])
            
            

            # -------------------------------
            # Main dataframe
            # -------------------------------
            main_df = pd.DataFrame(columns=['object_Id', 'analyses', 'number of analyses', 'number of interim files', 'size of interim files (KB)'])

            for technique in self.techniques:

                all_files = list((self.folder_interimdata / technique).glob('*'))
                

                Ids = sorted(set([file.name.split('_')[2] for file in all_files if self.project_id in file.name]))
                nb_analyses = len(Ids)
                nb_files = len(all_files)

                total_size_files = sum([ f.stat().st_size for f in all_files if f.is_file() ]) // 1000

                if technique in ['Power', 'AIS']:
                    all_files = all_files[:-1]
                    object = 'NaN'
                    main_df.loc[len(main_df)] = [object, technique, nb_analyses, nb_files, total_size_files]
                else:
                    for object in self.objects:

                        wanted_files = [file for file in all_files if object in file.name]

                        Ids = sorted(set([file.name.split('_')[2] for file in wanted_files if self.project_id in file.name]))
                        nb_analyses = len(Ids)
                        nb_files = len(wanted_files)
                        total_size_files = sum([ f.stat().st_size for f in wanted_files if f.is_file() ]) // 1000

                        list_row = [object, technique, nb_analyses, nb_files, total_size_files]
                        main_df.loc[len(main_df)] = list_row

            self.overview = main_df.set_index(['object_Id','analyses']).sort_index() 

 

    def measurement_files(self, techniques=['all'], objects=['all'], file_type=['all'], data_category='interim'):
        """Obtain the filenames of the measurements performed in the framework of a given project.

        Parameters
        ----------
        techniques : list, optional
            Type of measurements requested, possible options can be found in the acronyms.py file ('analyses' dictionary). When 'all', it retrieves measurements for all techniques used during the corresponding project, by default 'all'.

        objects : list, optional
            A list of object_id number. When 'all', it retries measurements for all objects analysed in during the corresponding project, by default 'all'.

        file_type : list, optional
            Type of file formats being asked, possible options are: 'txt', 'csv', 'png', 'tif', etc. When 'all', it retrieves all types of files, by default 'all'.
            
        data_category : str, optional
            Either 'interim' or 'processed', by default 'interim'.

        Returns
        -------
        dict
            Returns a dictionary, where keys correspond to the techniques and where the values are given as a list of str, in which each string corresponds to the absolute path of a measurement file.
        """

        files = {}

        if techniques[0] == 'all':
            techniques = self.techniques

        for technique in techniques:
            folder_data = self.folder_project / 'data' / data_category / technique             

            technique_files = [str(f) for f in Path(folder_data).iterdir() if f.is_file()]

            if objects[0] == 'all':                
                files[technique] = technique_files

            else:
                objects_files = []
                for object in objects:
                    object_files = [file for file in technique_files if object in file]
                    objects_files = objects_files + object_files

                files[technique] = objects_files

        # remove empty list in the files dictionary
        for i in files.copy():
            if not files[i]:
                files.pop(i)  

        return files

    

    def measurement_ids(self, techniques=['all'], objects=['all']):
        """Retrieve measurement id numbers performed in the framework of a given project.

        Parameters
        ----------
        techniques : list, optional
            Type of measurements requested, possible options can be found in the acronyms.py file ('analyses' dictionary). When 'all', it retrieves measurements for all techniques used during the corresponding project, by default 'all'.

        objects : list, optional
            A list of object_id number. When 'all', it retries measurements for all objects analysed in during the corresponding project, by default 'all'.

        Returns
        -------
        dict
            Returns a dictionary, where keys correspond to the techniques and where the values are given as a list of str, in which each string corresponds to the id number of a given analyses.
        """

        ids = {}

        if techniques[0] == 'all':
            techniques = self.techniques

        for technique in techniques:

            folder_data = self.folder_project / 'data' / 'interim' / technique
            measurement_ids = sorted(set([str(f).split('/')[-1].split('_')[2] for f in Path(folder_data).iterdir() if f.is_file()]))

            if objects[0] == 'all':                
                ids[technique] = measurement_ids

            else:
                objects_ids = []
                for object in objects:
                    object_ids = [id for id in measurement_ids if object in id]
                    objects_ids = objects_ids + object_ids

                ids[technique] = objects_ids

        
        # remove empty list in the ids dictionary
        for i in ids.copy():
            if not ids[i]:
                ids.pop(i)

        return ids