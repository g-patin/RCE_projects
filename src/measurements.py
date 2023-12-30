####### IMPORT PACKAGES #######

import os
import pandas as pd
import matplotlib 
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from IPython import get_ipython

import colour
from colour.plotting import *
from colour.colorimetry import *
from colour.models import *
from colour import SDS_ILLUMINANTS

from ipywidgets import Layout, Button, Box, interact, interactive, fixed, interact_manual
import ipywidgets as ipw
from IPython.display import display, clear_output, HTML

import imageio
from pathlib import Path

# self made packages
import acronyms
import plotting
import measurements



####### DEFINE GENERAL PARAMETERS #######

style = {"description_width": "initial"}
d65 = colour.CCS_ILLUMINANTS["cie_10_1964"]["D65"]


plt.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
    "font.sans-serif": "Helvetica",
})


#matplotlib.rcParams.update(matplotlib.rcParamsDefault)


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



####### INTERIM CLASS #######


class data(object):

    def __init__(self,Id,project_id, data_category='interim'):
        self.Id = Id
        self.project_id = project_id
        self.data_category = data_category
        self.initial = self.Id.split('.')[0]

        types = {
            'ill': 'Illuminance',                     
            'irr': 'Irradiance',
            'I': 'Absolute irradiance spectrum', 
            'MF': 'Microfading',           
            'P':'Radiant power',
            'RH': 'Relative humidity',
            'RS': 'Reflectance spectrum',
            'T': 'Temperature',                 
            'TS': 'Transmission spectrum'
        }
           
        self.type = types[self.initial]


    def __repr__(self):                  
        return f'Measurement: Id = {self.Id}, type = {self.type}, project = {self.project_id}, data_category = {self.data_category})'   
    

    def get_path(self, data_category='interim', file_category='single', file_path='absolute'):      
        """Obtain the path for given files.

        Args:
            data_category (str, optional):
                Select the type of data being asked ('interim' or 'processed'). Default to 'interim'.

            file_category (str, optional):
                Select the category of file ('single', 'group', 'object'). Default to 'single'.
                'single' returns the file corresponding to the given measurement Id.
                'group' returns the files related to the corresponding group.
                'object' returns the files related to the corresponding object.

            file_path (str, optional):
                Select the type of path ('absolute', 'name', 'stem', 'suffix'). Default to 'absolute'.
            

        Returns:
            list: Return the full path of the file.
        """ 

        ####### DEFINE GLOBAL VARIABLES ########
    
        global folder_root, folder_main


        ####### DEFINE FOLDERS ########

        folder_types = {
            'ill': 'Ill',                     
            'irr': 'Irr',
            'I': 'AIS', 
            'MF': 'MFT',           
            'P':'Power',
            'RH': 'RH',
            'RS': 'RS',
            'T': 'Temp',                 
            'TS': 'TS'
        }
        
        if folder_main == f'{folder_root}measurements/':
            folder_start = f'{folder_main}{folder_types[self.initial]}/'                       
            folder_interimdata = f'{folder_start}data/interim/'
            folder_processeddata = f'{folder_start}data/processed/'                    
                    
        elif folder_main == f'{folder_root}projects/':
            name_folder = [x for x in os.listdir(folder_main) if self.project_id in x][0] 
            folder_start = f'{folder_main}{name_folder}/'            
            folder_interimdata = f'{folder_start}data/interim/{folder_types[self.initial]}/' 
            folder_processeddata = f'{folder_start}data/processed/{folder_types[self.initial]}/'                                 

        else:
            print('Path to the folders is incorrect. This might potentially leads to some error messages.')          

        

        ####### RETRIEVE THE INTERIM FILENAME ########
            
        all_interim_files = sorted(os.listdir(folder_interimdata))        
        interim_filename = [x for x in all_interim_files if f"{self.Id}" in x][0]
            

        ####### RETRIEVE GROUP AND OBJECT_ID ########

        df = pd.read_csv(folder_interimdata + interim_filename, index_col='parameter')
        group = df.loc['group'].iloc[0]

        if self.initial == 'P':
            object_Id = df.loc['lamp'].iloc[0]

        else:
            object_Id = df.loc['object_id'].iloc[0] 

            

        if data_category == 'interim':            

            ####### SELECT FILES ACCORDING TO THEIR CATEGORY ########

            file_categories = {'single': [Path(x) for x in all_interim_files if f"{self.Id}" in x],
                            'object': [Path(x) for x in all_interim_files if f"{object_Id}" in x], 
                            'group': [Path(x) for x in all_interim_files if f"{object_Id}" in x and group in x]}
            
            wanted_files = file_categories[file_category]     



            ####### SELECT WANTED FILE_PATHS ########

            dic_file_path={'absolute': [f'{folder_interimdata}{x.name}' for x in wanted_files],            
            'name': [x.name for x in wanted_files],
            'stem': [x.stem for x in wanted_files],
            'suffix': [x.suffix for x in wanted_files],
            'parent': [x.parent for x in wanted_files]}
            
            paths = dic_file_path[file_path]


        else:

            ####### PROCESSED FILE ######## 

            all_processed_files = sorted(os.listdir(folder_processeddata))      


            ####### SELECT FILES ACCORDING TO THEIR CATEGORY ########

            file_categories = {'single': [Path(x) for x in all_processed_files if f"{object_Id}" in x and group in x],
                            'object': [Path(x) for x in all_processed_files if f"{object_Id}" in x], 
                            'group': [Path(x) for x in all_processed_files if f"{object_Id}" in x and group in x]}
            
            wanted_files = file_categories[file_category] 


            ####### SELECT WANTED FILE_PATHS ########

            dic_file_path={'absolute': [f'{folder_processeddata}{x.name}' for x in wanted_files],            
            'name': [x.name for x in wanted_files],
            'stem': [x.stem for x in wanted_files],
            'suffix': [x.suffix for x in wanted_files],
            'parent': [x.parent for x in wanted_files]}
            
            paths = dic_file_path[file_path]


        return paths
         
    
    def get_dir(self, folder_type='interim'):

        ####### DEFINE GLOBAL VARIABLES ########
    
        global folder_root, folder_main  


        ####### DEFINE FOLDERS ########

        folder_types = {
            'ill': 'Ill',                     
            'irr': 'Irr',
            'I': 'AIS', 
            'MF': 'MFT',           
            'P':'Power',
            'RH': 'RH',
            'RS': 'RS',
            'T': 'Temp',                 
            'TS': 'TS'
        }         


        if folder_main == f'{folder_root}measurements/':
            folder_start = f'{folder_main}{folder_types[self.initial]}/'
            folder_rawdata = f'{folder_start}data/raw/'            
            folder_interimdata = f'{folder_start}data/interim/'
            folder_processeddata = f'{folder_start}data/processed/'
            folder_figures = f'{folder_start}figures/'            
                               

            
        elif folder_main == f'{folder_root}projects/':
            name_folder = [x for x in os.listdir(folder_main) if self.project_id in x][0] 
            folder_start = f'{folder_main}{name_folder}/'
            folder_rawdata = f'{folder_start}data/raw/{folder_types[self.initial]}/'  
            folder_interimdata = f'{folder_start}data/interim/{folder_types[self.initial]}/'
            folder_processeddata = f'{folder_start}data/processed/{folder_types[self.initial]}/'
            folder_figures =  f'{folder_start}figures/{folder_types[self.initial]}/'
                      

        else:
            print('Path to the folders is incorrect. This might potentially leads to some error messages.') 


        folders = {'raw':folder_rawdata,
                   'interim':folder_interimdata,
                   'processed':folder_processeddata,
                   'figures':folder_figures}
        
        return folders[folder_type]


    def get_info(self, dataframe=True):
        """Retrieve the metadata of the measurement.

        Args:
            No argument is required.            

        Returns:
            It returns information about the measurement as a Pandas series.
        """

        file = self.get_path()[0]
        

        if self.initial == 'RS':
            df = pd.read_csv(file, index_col='parameter')
            df_info = df.loc[:'[COLORIMETRIC DATA]':][:-1].iloc[:,0]

        if self.initial == 'MF':            
            df_info = pd.read_csv(file, index_col='parameter') 

        if self.initial == 'P':
            df = pd.read_csv(file, index_col='parameter')
            df_info = pd.DataFrame(df.loc[:'[MEASUREMENT DATA]'][:-1].iloc[:,0])      


        if dataframe == True:
            return pd.DataFrame(df_info)
        
        else:
            return df_info


    def get_data(self, data='all', show_plot = False):
        """Retrieve the data of the measurement.

        Args:
            data (str, optional): 
            Enables to select which aspect of the data to retrieve. Default to 'all'. For reflectance spectra (RS), possibility to select the LabCh values ('Lab') or the spectral values only ('sp).

            show_plot(boolean, optional):
            Gives the possibility to display the data inside a plot, when set to 'True'. Default to 'False'.

        Returns:
            It returns the data in a Pandas dataframe.
        """

        file = self.get_path()[0]
        
        df = pd.read_csv(file, index_col='parameter')

        if self.initial == 'RS':
            if data == 'all':
                df_data = df.loc['[COLORIMETRIC DATA]':]
            elif data == 'sp':
                df_data = pd.to_numeric(df.loc['[MEASUREMENT DATA]':][2:].iloc[:,0])
            elif data == 'Lab':
                df_data = df.loc[['observer','illuminant','L*','a*','b*','C*','h']]

        elif self.initial == 'MF':
            data_sp = pd.read_csv(file.replace('INFO.txt', 'SP.csv'), index_col='wavelength_nm')
            data_dE = pd.read_csv(file.replace('INFO.txt', 'dE.csv'), index_col='H_MJ/m2')

            if data == 'all':
                df_data = np.array([data_sp,data_dE])
            elif data == 'sp':
                df_data = data_sp
            elif data == 'Lab' or data == 'dE':
                df_data = data_dE

        else:
            df_data = pd.to_numeric(df.loc['[MEASUREMENT DATA]':][2:].iloc[:,0])

        if show_plot == True:
            self.plot_data()


        return df_data   

        
    def plot_data(self,fontsize=26,save=False, plot_category='single',x_range='all', *args, **kwargs):
        """Plot the data. 

        Args:
            fontsize (int, optional):
            Fontsize of the text and numbers in the plot. Default to 26.

            save (boolean, optional):
            Enables to save the figure when set to 'True'. Default to 'False'.  

            group (boolean, optional): 
            When 'False', it displays the data individually (one curve per plot). When True, it shows all the curves related to a similar group. Default to False.
        """

        data = self.get_data()

        if self.initial == 'P':

            info = self.get_info(dataframe=False)
            data = self.get_data()            

            time = data.index.astype(float)
            power = data.values.astype(float)
            title = f'Power measurement, project {self.project_id}, {self.Id}'                       

            plotting.power(data=[np.array([time,power])], title=title)            



        if self.initial == 'RS':

            info = self.get_info(dataframe=False)
            date = info['date_time'].split(' ')[0]
            Id = info['Id']
            project_Id = info['project_id']
            object_Id = info['object_id']
            object_type = info['object_type']            
            device = info['device'].split('_')[0]
            filter = info['filter']
            group = info['group']
            
            data_folder = self.get_dir(folder_type=self.data_category)                      
            all_files = os.listdir(data_folder)     

            plot_categories = {'single':Id, 'group':group, 'object':object_Id} 
            files = sorted([x for x in all_files if plot_categories[plot_category] in x and object_Id in x])  
                         
            out1 = ipw.Output()
            out2 = ipw.Output()
            out3 = ipw.Output()
            out4 = ipw.Output()
            out5 = ipw.Output()
                
            tab = ipw.Tab(children = [out1,out2,out3,out4,out5])   

            tab.set_title(0,'RS')
            tab.set_title(1,'CIELAB')
            tab.set_title(2,'Colour patches')  
            tab.set_title(3,'Mean')  
            tab.set_title(4,'Data')     

            display(tab) 

            if plot_category == 'single':
                title = f'project {project_Id}, object {object_Id}, {object_type}, {self.Id}'
                    
            elif plot_category == 'object':
                title = f'project {project_Id}, object {object_Id}, {object_type}'

            else:
                title = f'project {project_Id}, object {object_Id}, {object_type}, group {group}'
                
                
            with out1:

                data = []
                labels = []

                for file in files:
                        Id = file.split('_')[2]
                        itm = measurements.data(Id, project_Id)
                        data_RS = itm.get_data(data='sp')

                        wl = data_RS.index.astype(float)
                        sp = data_RS.values.astype(float)
                        

                        data.append(np.array([wl,sp])) 
                        labels.append(Id)                                   
                

                plotting.RS_SP(data=data, title=title, labels=labels, *args, **kwargs)

                """
                sns.set()
                fs = 24
                fig1, ax = plt.subplots(1,1,figsize = (13,6))

                for file in files:

                    df = pd.read_csv(data_folder + file, index_col='parameter')
                    Id = file.split('_')[2]                    

                    
                    if x_range == 'all':
                        df_sp = df.loc['[MEASUREMENT DATA]':][2:]
                    else:
                        df_sp = df.loc[f'{x_range[0]}':f'{x_range[1]}']
                                             
                        ax.set_xlim(x_range[0],x_range[1])


                    wl = df_sp.index.astype(float)
                    sp = df_sp.iloc[:,0].values.astype(float)

                    if 'std' in '-'.join(df.columns.values):
                        sp_std = df_sp['value_std'].values.astype(float)
                        ax.plot(wl, sp, label=Id)
                        ax.fill_between(wl, sp+sp_std, sp-sp_std, alpha=0.5, color='0.7', ec='none')
                    
                    else:
                        ax.plot(wl,sp, label=Id)

                    
                ax.set_xlabel('Wavelength $\lambda$ (nm)', fontsize=fs)
                ax.set_ylabel('Reflectance factor', fontsize=fs)

                ax.set_title(title, fontsize=fs+2)

                ax.xaxis.set_tick_params(labelsize=fs)
                ax.yaxis.set_tick_params(labelsize=fs)

                plt.legend(loc='best', fontsize=fs)
                plt.tight_layout()

                if save == True:           

                    folder_fig = self.get_path(type = 'figure_folder')
                    fname = f'{self.get_fname(group=True, plot_type="RS-SP")}'
                    fig1.savefig(f'{folder_fig}{fname}',dpi=300, facecolor='white')


                plt.show()
                """

            with out2:

                data = []
                labels = []

                for file in files:
                        Id = file.split('_')[2]
                        itm = measurements.data(Id, project_Id)
                        Lab = itm.get_data(data='Lab')['value1'][['L*','a*','b*']].astype(float).values

                        data.append(Lab) 
                        labels.append(Id)                                   


                plotting.CIELAB(data=data, title=title, labels=labels, *args, **kwargs)


                """
                fig2, ax = plt.subplots(2,2, figsize=(11, 11), gridspec_kw=dict(width_ratios=[1, 2], height_ratios=[2, 1]), layout='constrained')

                Lb = ax[0,0]
                ab = ax[0,1]
                AB = ax[1,0]
                aL = ax[1,1]

                L_list = []
                a_list = []
                b_list = []

                    
                for file in files:

                    df = pd.read_csv(data_folder + file, index_col='parameter')
                    Id = file.split('_')[2]

                    L = float(df.loc['L*']['value1'])
                    a = float(df.loc['a*']['value1'])
                    b = float(df.loc['b*']['value1'])
                        

                    L_list.append(L)
                    a_list.append(a)
                    b_list.append(b)

                    Lb.scatter(L,b)
                    ab.scatter(a,b, label = Id)
                    aL.scatter(a,L)
                    AB.scatter(a,b)

                    
                L_mean = np.mean(L_list)
                a_mean = np.mean(a_list)
                b_mean = np.mean(b_list)

                L_std = np.std(L_list)
                a_std = np.std(a_list)
                b_std = np.std(b_list)             


                Lb.xaxis.set_tick_params(labelsize=fs)
                Lb.yaxis.set_tick_params(labelsize=fs)  
                ab.xaxis.set_tick_params(labelsize=fs)
                ab.yaxis.set_tick_params(labelsize=fs)  
                aL.xaxis.set_tick_params(labelsize=fs)
                aL.yaxis.set_tick_params(labelsize=fs) 
                AB.xaxis.set_tick_params(labelsize=fs)
                AB.yaxis.set_tick_params(labelsize=fs) 

                AB.set_xlim(-110, 110)
                AB.set_ylim(-110, 110)         
                                    
                Lb.set_xlabel("CIE $L^*$", fontsize=fs)
                Lb.set_ylabel("CIE $b^*$", fontsize=fs)
                AB.set_xlabel("CIE $a^*$", fontsize=fs)
                AB.set_ylabel("CIE $b^*$", fontsize=fs)
                aL.set_xlabel("CIE $a^*$", fontsize=fs)
                aL.set_ylabel("CIE $L^*$", fontsize=fs) 

                if plot_category == 'object':
                    plt.suptitle(f'{project_Id}, object {object_Id}, {object_type}', fontsize=fs+2)

                else:

                    Lb.errorbar(L_mean,b_mean,yerr=b_std,xerr=L_std,fmt='s', markerfacecolor='black', ecolor='black', capsize=5)
                    ab.errorbar(a_mean,b_mean,yerr=b_std,xerr=a_std,fmt='s', markerfacecolor='black', ecolor='black', capsize=5, label='Average')
                    aL.errorbar(a_mean,L_mean,yerr=L_std,xerr=b_std,fmt='s', markerfacecolor='black', ecolor='black', capsize=5)

                    plt.suptitle(f'{project_Id}, object {object_Id}, {object_type}, group {group}', fontsize=fs+2)  

                  


                AB.axhline(0, color="black", lw=0.5)
                AB.axvline(0, color="black", lw=0.5)

                path_docs = f'{folder_root}docs/'         
                path_colour_circle = path_docs + 'colour_circle.png'
                im_colour_circle = imageio.imread(path_colour_circle)
                AB.imshow(im_colour_circle, extent=(-110,110,-110,110))   

                ab.legend(loc='best', fontsize=fs)

                if save == True:           

                    folder_fig = self.get_path(type = 'figure_folder')
                    fname = f'{self.get_fname(group=True, plot_type="RS-CIELAB")}'
                    fig2.savefig(f'{folder_fig}{fname}',dpi=300, facecolor='white', bbox_inches='tight')                    
                    
                plt.show()
            """

            with out3:

                fig3, ax3 = plt.subplots(1,1,figsize=(13,6))
                fig3.patch.set_facecolor((0.75, 0.75, 0.75))

                ax3.grid(False)
                ax3.axis('off')

                N = len(files)
                x = 0

                for file in files:

                    df = pd.read_csv(data_folder + file, index_col='parameter')
                    Id = file.split('_')[2]

                    L = float(df.loc['L*']['value1'])
                    a = float(df.loc['a*']['value1'])
                    b = float(df.loc['b*']['value1'])

                    Lab = np.array([L,a,b])
                    srgb = colour.XYZ_to_sRGB(colour.Lab_to_XYZ(Lab), d65).clip(0, 1) 

                    cp = matplotlib.patches.Rectangle((0.07+x,0.15), 0.86-x, 0.7, color=srgb)
                    ax3.add_patch(cp)

                    ax3.annotate(Id, (0.08+x,0.89), weight='bold',fontsize = fontsize-3)

                    x = x + (0.86/N)

                
                plt.tight_layout()
                plt.show()



            with out4:

                sp_list = []
                L_list = []
                a_list = []
                b_list = []
                C_list = []
                h_list = []

                illuminant = 'D65'
                observer = '10°'

                    
                for file in files:

                    df = pd.read_csv(data_folder + file, index_col='parameter')

                    data_sp = df.loc['[MEASUREMENT DATA]':][2:].iloc[:,0]
                    wl = data_sp.index.astype(float)
                    sp = data_sp.values.astype(float)

                    L = float(df.loc['L*']['value1'])
                    a = float(df.loc['a*']['value1'])
                    b = float(df.loc['b*']['value1'])
                    C = float(df.loc['C*']['value1'])
                    h = float(df.loc['h']['value1'])
                        
                    sp_list.append(sp)
                    L_list.append(L)
                    a_list.append(a)
                    b_list.append(b)
                    C_list.append(C)
                    h_list.append(h)

                        
                sp_mean = np.mean(sp_list, axis=0)
                L_mean = np.round(np.mean(L_list),2)
                a_mean = np.round(np.mean(a_list),2)
                b_mean = np.round(np.mean(b_list),2)
                C_mean = np.round(np.mean(C_list),2)
                h_mean = np.round(np.mean(h_list),2)
                Lab_mean = np.array([L_mean,a_mean,b_mean])
                srgb_mean = colour.XYZ_to_sRGB(colour.Lab_to_XYZ(Lab_mean), d65).clip(0, 1) 

                    
                sp_std = np.std(sp_list, axis=0)
                L_std = np.round(np.std(L_list),2)
                a_std = np.round(np.std(a_list),2)
                b_std = np.round(np.std(b_list),2)
                C_std = np.round(np.std(C_list),2)
                h_std = np.round(np.std(h_list),2)


                sns.set()
                gs_kw = dict(width_ratios=[11,3], height_ratios=[1])
                fig4, [ax1,ax2] = plt.subplots(1,2,figsize = (13,6), gridspec_kw = gs_kw)
                    

                                        
                ax1.plot(wl,sp_mean)
                ax1.fill_between(wl,sp_mean-sp_std,sp_mean+sp_std, alpha=0.5, color='0.7')

                cp = matplotlib.patches.Rectangle((0,0), 1, 0.4, color=srgb_mean)
                ax2.add_patch(cp)

                text_ax1 = '\n'.join((     
                f'Device : {device}',
                f'Filter : {filter}',     
                ))


                text_ax2 = '\n'.join((
                f'{illuminant} - {observer}',
                r' ',
                r'$L^*$ = '+ str(L_mean) + '+/-' + str(L_std),
                r'$a^*$ = '+ str(a_mean) + '+/-' + str(a_std),
                r'$b^*$ = '+ str(b_mean) + '+/-' + str(b_std),
                r'$C^*$ = '+ str(C_mean) + '+/-' + str(C_std),
                r'$h$ = '+ str(h_mean) + '+/-' + str(h_std),
                ))

                props_ax1 = dict(boxstyle='round', facecolor='white', alpha=0.6, edgecolor=None)
                props_ax2 = dict(boxstyle='round', facecolor='0.89', alpha=0.6, edgecolor=None)

                # place a text box in upper left in axes coords
                ax1.text(0.02,0.96,text_ax1,transform=ax1.transAxes,fontsize=fontsize-6,verticalalignment='top', bbox=props_ax1)
                ax2.text(0.04,0.98,text_ax2,transform=ax2.transAxes,fontsize=fontsize-4,verticalalignment='top', bbox=props_ax2)

                ax1.set_xlim(wl[0],wl[-1])

                ax1.set_xlabel('Wavelength $\lambda$ (nm)', fontsize=fontsize)
                ax1.set_ylabel('Reflectance factor', fontsize=fontsize)
                ax1.set_title(f'{date}, {project_Id}, {Id.split("-")[0]}, {group}', fontsize=fontsize)

                ax1.xaxis.set_tick_params(labelsize=fontsize)
                ax1.yaxis.set_tick_params(labelsize=fontsize)

                fig4.patch.set_facecolor('0.94')

                ax2.axis('off')

                plt.tight_layout()

                if save == True:           

                    folder_fig = self.get_path(type = 'figure_folder')
                    fname = f'{self.get_fname(group=True, plot_type="RS-mean")}'
                    fig4.savefig(f'{folder_fig}{fname}',dpi=300, facecolor='white', bbox_inches='tight')

                                    
                plt.show()

            with out5:
                pd.set_option('display.max_rows', None)
                
                df_all_data = pd.DataFrame()

                for file in files:

                    df = pd.read_csv(data_folder + file, index_col='parameter')
                    Id = file.split('_')[2]
                    
                    df_data = df.loc['[COLORIMETRIC DATA]':][1:]                 
                    df_all_data[Id] = df_data[['value1']]

                
                display(HTML("<div style='height: 350px; overflow:auto; width: fit-content'>" + df_all_data.style.to_html() + "</div>"))

         


            





    
