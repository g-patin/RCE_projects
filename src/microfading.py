from fileinput import filename
import measurements
import microfading
import plotting
import visualize

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from scipy.optimize import curve_fit
import colour

from ipywidgets import Layout, Button, Box, interact, interactive, fixed, interact_manual
import ipywidgets as ipw
from IPython.display import display, clear_output

from uncertainties import ufloat
from uncertainties.umath import *
from uncertainties import ufloat_fromstr
from uncertainties import unumpy as unp



class MF(measurements.data):

    def __init__(self, Id, project_id, data_category='interim'):
        super().__init__(Id, project_id, data_category)   


    def fit(self, coordinate='dE00', dose_unit='H_e', fitted_eq='eq1', range_x=(0,1000,1), plot=False, return_data=True):
        
        doses = {'H_e':'H_MJ/m2', 'H_v':'H_klx_hr'}
        
        data = self.get_data(data='dE').reset_index()[[doses[dose_unit],coordinate]]
        x = data.iloc[:,0]
        y = data.iloc[:,1]

        if fitted_eq == 'eq1':
            c0 = 0.1
            c1 = 0.5
            c2 = 0

            def fitting(x,c0,c1,c2):
                generic_fn = c0*(x**c1) + c2
                return generic_fn
            
            popt,pcov = curve_fit(fitting,x,y,p0 = [c0,c1,c2])
            popt = np.round(popt,4)
            fitted_fn = f'{popt[0]} (x^{f"{popt[1]}"}) + {popt[2]}'

            wanted_x = np.arange(range_x[0],range_x[1], range_x[2])
            y_fitted = fitting(wanted_x,*popt)

            residuals = y - fitting(x,*popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y-np.mean(y))**2)
            r_squared = np.round(1 - (ss_res / ss_tot),3)


        if fitted_eq == 'eq2':
            c0 = 0.1
            c1 = 0.5
            c2 = 0
            c3 = 0.1

            def fitting(x,c0,c1,c2,c3): 
                f = c0+ c1*x - c2*np.exp(-c3*x)        
                return f
            
            popt,pcov = curve_fit(fitting,x,y,p0 = [c0,c1,c2,c3])
            popt = np.round(popt,4)
            fitted_fn = f'{popt[0]} + {popt[1]}*x -{popt[2]}**(-{popt[3]}*x)'

            wanted_x = np.arange(range_x[0],range_x[1], range_x[2])
            y_fitted = fitting(wanted_x,*popt)

            residuals = y - fitting(x,*popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y-np.mean(y))**2)
            r_squared = np.round(1 - (ss_res / ss_tot),3)


        if plot == True:

            labels_eq = {
                'L*': r'CIE $L^*$',
                'a*': r'CIE $a^*$',
                'b*': r'CIE $b^*$',
                'C*': r'CIE $C^*$',
                'h': r'CIE $h$',
                'dE76': r'$\Delta E^*_{ab}$',
                'dE00': r'$\Delta E^*_{00}$',
                'dR_VIS': r'$\Delta R_{\rm vis}$',
            }

            labels_H = {
                'H_v': 'Exposure dose $H_v$ (klx.hr)',
                'H_e': 'Radiant Exposure $H_e$ (MJ/m²)'
            }

            sns.set()
            fig, ax = plt.subplots(1,1, figsize=(15,9))
            fs = 24

            ax.plot(x,y, ls='-', lw=3, label='original data')
            ax.plot(wanted_x,y_fitted, ls='--', lw=2, label='fitted data')

            ax.set_xlabel(labels_H[dose_unit], fontsize=fs)
            ax.set_ylabel(labels_eq[coordinate],fontsize=fs)
            title = f'Microfading, data fitting, $y = {fitted_fn}$, $R^2 = {r_squared}$'
            ax.set_title(title, fontsize = fs+2)   
            
            ax.set_xlim(0)
            ax.set_ylim(0)     

            ax.xaxis.set_tick_params(labelsize=fs)
            ax.yaxis.set_tick_params(labelsize=fs)


            plt.legend(fontsize=fs)
            plt.tight_layout()
            plt.show()

            
        if return_data == True:
            return np.array([wanted_x, y_fitted])

    
    def plot_data(self, fontsize=26, group=False, save=False, path_fig='cwd'):


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


        #tab = ipw.Tab(children = [out1,out2,out3,out4,out5,out6,out7,out8,out9,out10,out11,out12])

        tabs_spectra = ipw.Tab(children = [out1,out2,out3])
        tabs_colorimetry = ipw.Tab(children = [out4,out5,out6])
        tabs_color = ipw.Tab(children = [out7,out8])


        tabs_spectra.set_title(0,'Spectra')
        tabs_spectra.set_title(1,'Spectral differences')
        tabs_spectra.set_title(2,'Delta R')
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
            tabs_spectra,
            tabs_colorimetry,
            tabs_color,
        ]

        tabs = ipw.Tab(children=list_tabs)
        tabs.set_title(0, 'Spectral change')
        tabs.set_title(1, 'Colorimetric change')
        tabs.set_title(2, 'Color perception')

        display(tabs)
        
        ###### SET PARAMATERS #######

        fs1 = 25
        fs2 = 19
        fs_leg = 24
        s = 30


        ###### FILL EACH TAB #######

    
    
        with out1:
            if group == False:
                data = self.get_data(data='sp')
                sp_i = np.array([data.index,data.iloc[:,0]])
                sp_f = np.array([data.index,data.iloc[:,-1]])

                info = self.get_info()['value']
                date = info.loc['date_time'].split(' ')[0]
                project = info.loc['project']
                meas_Id = info.loc['meas_Id']
                object_technique = info.loc['object_technique']
                object_support = info.loc['object_support']

                title = f'Microfading analysis - Reflectance spectra, {date}, {project}, {meas_Id}, ' + r"\textbf{"+object_technique+"}" + f', {object_support}'                

                plotting.RS_SP([sp_i,sp_f], labels=['Initial', 'Final'], title=title, save=save, path_fig=path_fig)

            else:

                info = self.get_info()
                object_Id = info.loc['object_Id']['value']
                group_nb = info.loc['group']['value']
                

                interim_folder = self.get_path(type='interim_folder')
                all_files = os.listdir(interim_folder)                

                files_group = sorted([x for x in all_files if group_nb in x and object_Id in x and 'SP.csv' in x])
                
                data = []
                labels = []

                for file in files_group:
                    df = pd.read_csv(interim_folder + file, index_col='wavelength_nm')
                    sp_i = np.array([df.index, df.iloc[:,0]])
                    label = file.split('_')[2]
                    
                    labels.append(label)
                    data.append(sp_i)

                plotting.RS_SP(data, labels=labels, title='Initial spectra', save=save, path_fig=path_fig)  

                

        
        with out2:

            if group == False:

                data = self.get_data(data='sp')

                sp_i = data.iloc[:,0]
                sp_f = data.iloc[:,-1]
                sp_diff = sp_f - sp_i   

                info = self.get_info()['value']
                date = info.loc['date_time'].split(' ')[0]
                project = info.loc['project']
                meas_Id = info.loc['meas_Id']
                object_technique = info.loc['object_technique']
                object_support = info.loc['object_support']

                title = f'Microfading analysis - Reflectance spectra, {date}, {project}, {meas_Id}, ' + r"\textbf{"+object_technique+"}" + f', {object_support}'           

                fig, ax = plt.subplots(1,1, figsize=(15,9))
                fs = 28

                ax.plot(data.index, sp_diff)    

                ax.set_xlabel('Wavelength $\lambda$ (nm)', fontsize=fs)
                ax.set_ylabel('Change in reflectance values',fontsize=fs)
                ax.set_title(title, fontsize = fs)        

                ax.xaxis.set_tick_params(labelsize=fs)
                ax.yaxis.set_tick_params(labelsize=fs)

                plt.tight_layout()
                plt.show()

            else:
                info = self.get_info()
                object_Id = info.loc['object_Id']['value']
                group_nb = info.loc['group']['value']
                

                interim_folder = self.get_path(type='interim_folder')
                all_files = os.listdir(interim_folder)                

                files_group = sorted([x for x in all_files if group_nb in x and object_Id in x and 'SP.csv' in x])
                
                data = []
                labels = []

                for file in files_group:
                    df = pd.read_csv(interim_folder + file, index_col='wavelength_nm')  
                    df = df.loc[400:1001] 

                    sp_diff = np.array([df.index, df.iloc[:,-1] - df.iloc[:,0]])
                    label = file.split('_')[2]
                    
                    labels.append(label)
                    data.append(sp_diff)
                

                plotting.RS_SP(data, labels=labels, title='Change in reflectance values', save=save, path_fig=path_fig)  



        
        with out4:

            if group == False:            

                data = self.get_data(data='dE')

                data_dE = data.reset_index()[['H_MJ/m2','H_klx_hr','dE76','dE00']].values.T

                info = self.get_info()['value']
                date = info.loc['date_time'].split(' ')[0]
                project = info.loc['project']
                meas_Id = info.loc['meas_Id']
                group_nb = info.loc['group']
                object_technique = info.loc['object_technique']
                object_support = info.loc['object_support']

                title = f'Microfading analysis - {date}, {project}, {meas_Id}, ' + r"\textbf{"+object_technique+"}" + f', {object_support}' 
                filename_dE = f'{date}_{project}_{meas_Id}_{group_nb}_dE.png'
                path_fig_dE = Path(self.get_dir(folder_type='figures')) / filename_dE

                plotting.delta_E(data=[data_dE], title=title, methods=['dE76', 'dE00'], labels=['dE76', 'dE00'], save=save, path_fig=path_fig_dE)
                

            else:

                info = self.get_info()['value']               
                date = info.loc['date_time'].split(' ')[0]
                project = info.loc['project']                
                object_technique = info.loc['object_technique']
                object_support = info.loc['object_support']
                object_Id = info.loc['object_Id']
                group_nb = info.loc['group']
                

                interim_folder = self.get_path(type='interim_folder')
                all_files = os.listdir(interim_folder)                

                Ids = sorted([x.split('_')[2] for x in all_files if group_nb in x and object_Id in x and 'dE.csv' in x])
                
                dEs = []
                for Id in Ids:
                    itm = microfading.MF(Id, self.project_id)
                    data = itm.get_data(data='dE').reset_index()[['H_MJ/m2','dE00']].T.values
                    dEs.append(data)

                title = f'Microfading analysis - Colour differences, {date}, {project}, {object_Id}, {group_nb}, ' + r"\textbf{"+object_technique+"}" + f', {object_support}'

                plotting.delta_E(data=dEs, labels=Ids, x_scale=['rad'], title=title, )
        

        
        with out5:

            if group == False:

                data = self.get_data(data='dE')[['L*','a*','b*','C*','h']].reset_index().T.values

                info = self.get_info()['value']
                date = info.loc['date_time'].split(' ')[0]
                project = info.loc['project']
                meas_Id = info.loc['meas_Id']
                object_technique = info.loc['object_technique']
                object_support = info.loc['object_support']

                title = f'Microfading analysis - Colorimetric coordinates, {date}, {project}, {meas_Id}, ' + r"\textbf{"+object_technique+"}" + f', {object_support}' 
                               

                visualize.LabCh(data=[data], title=title)

            else:

                info = self.get_info()['value']               
                date = info.loc['date_time'].split(' ')[0]
                project = info.loc['project']                
                object_technique = info.loc['object_technique']
                object_support = info.loc['object_support']
                object_Id = info.loc['object_Id']
                group_nb = info.loc['group']

                title = f'Microfading analysis - Colorimetric coordinates, {date}, {project}, {object_Id}, {group_nb}, ' + r"\textbf{"+object_technique+"}" + f', {object_support}'


                interim_folder = self.get_path(type='interim_folder')
                all_files = os.listdir(interim_folder)                

                Ids = sorted([x.split('_')[2] for x in all_files if group_nb in x and object_Id in x and 'dE.csv' in x])

                LabCh_data = []
                for Id in Ids:
                    itm = microfading.MF(Id, self.project)
                    data = itm.get_data(data='dE').reset_index()[['H_MJ/m2','L*','a*','b*','C*','h']].T.values
                    LabCh_data.append(data)

                visualize.LabCh(data=LabCh_data, labels=Ids, title=title)






        with out6:

            if group == False:

                data = self.get_data(data='dE')[['L*','a*','b*']]

                info = self.get_info()['value']
                date = info.loc['date_time'].split(' ')[0]
                project = info.loc['project']
                meas_Id = info.loc['meas_Id']
                object_technique = info.loc['object_technique']
                object_support = info.loc['object_support']

                title = f'Microfading analysis - CIELAB color space, {date}, {project}, {meas_Id}, ' + r"\textbf{"+object_technique+"}" + f', {object_support}' 


                visualize.CIELAB([data.values], title=title)

            else:

                info = self.get_info()['value']               
                date = info.loc['date_time'].split(' ')[0]
                project = info.loc['project']                
                object_technique = info.loc['object_technique']
                object_support = info.loc['object_support']
                object_Id = info.loc['object_Id']
                group_nb = info.loc['group']

                title = f'Microfading analysis - CIELAB color space, {date}, {project}, {object_Id}, {group_nb}, ' + r"\textbf{"+object_technique+"}" + f', {object_support}'


                interim_folder = self.get_path(type='interim_folder')
                all_files = os.listdir(interim_folder)                

                Ids = sorted([x.split('_')[2] for x in all_files if group_nb in x and object_Id in x and 'dE.csv' in x])

                Lab_data = []
                for Id in Ids:
                    itm = class_MFT.MFT(Id, self.project)
                    data = itm.get_data(data='dE').reset_index()[['L*','a*','b*']].values
                    Lab_data.append(data)

                visualize.CIELAB(data=Lab_data, labels=Ids, title=title)

        with out7:

            if group == False:

                data = self.get_data(data='dE').reset_index()[['H_MJ/m2','H_klx_hr', 'time_s', 'L*','a*','b*']].T.values

                info = self.get_info()['value']
                date = info.loc['date_time'].split(' ')[0]
                project = info.loc['project']
                meas_Id = info.loc['meas_Id']
                object_technique = info.loc['object_technique']
                object_support = info.loc['object_support']

                title = f'Microfading analysis - Color patches, {date}, {project}, {meas_Id}, ' + r"\textbf{"+object_technique+"}" + f', {object_support}' 

                visualize.colour_patches(data=data, title=title)
            
        
    def delta(self, equation='dE00', dose_unit='H_e', extrapolation=False, range_dose=(0,100,1), plot=False, return_data=True):

        doses = {'H_e': 'H_MJ/m2', 'H_v': 'H_klx_hr'}
        data = self.get_data(data='dE').reset_index()[[doses[dose_unit],equation]]      
        

        if extrapolation == True:
            data = self.fit(coordinate=equation, dose_unit=dose_unit, range_x=range_dose, plot=plot, return_data=return_data)            
        
        else:        
            H = data.iloc[:,0]
            dE = data.iloc[:,1]
            data = np.array([H,dE])

            if plot == True:

                fig, ax = plt.subplots(1,1)
                ax.plot(H,dE)
                plt.show()
        
        if return_data == True:
            return data
     
    
    def delta_rate(self, equation='dE00', dose_unit='H_e', extrapolation=False, fitted_eq='eq1', range_dose=(0,100,1), group=False, plot=False, return_data=True):

        data = self.get_data(data='dE').reset_index()

        doses = {'H_e': 'H_MJ/m2', 'H_v': 'H_klx_hr'}

        if group == False:

            if extrapolation == False:

                H = data[doses[dose_unit]]
                dE = data[equation]

                rate_dE = np.gradient(dE, H[1]-H[0])

            else:

                data_pred = self.fit(coordinate=equation, fitted_eq=fitted_eq, dose_unit=dose_unit, range_x=range_dose, plot=False, return_data=True)    
                H = data_pred[0] 
                dE = data_pred[1]                          

                rate_dE = np.gradient(dE, H[1]-H[0])

            if plot == True:

                fig, ax = plt.subplots(1,1)
                ax.plot(H,rate_dE)
                plt.show()

            if return_data == True:
                return rate_dE
            
        else:
            group_nb = self.get_info().loc['group']['value']
            object_Id = self.get_info().loc['object_Id']['value']

            folder_interim = self.get_path(type='interim_folder')
            all_interim_files = os.listdir(folder_interim)

            ids_group = sorted([x.split('_')[2] for x in all_interim_files if object_Id in x and group_nb in x and 'INFO.txt' in x])
            
            rates_dE = []
            for Id in ids_group:
                
                itm = class_MFT.MFT(Id, project = self.project)
                data = itm.get_data(data='dE').reset_index()                

                if extrapolation == False:

                    H = data[doses[dose]]
                    dE = data[equation]

                    rate_dE = np.gradient(dE, H[1]-H[0])

                    rates_dE.append(rate_dE)

                else:

                    data_pred = pd.DataFrame({})
                    H = np.arange(range_dose[0],range_dose[1],range_dose[2])
                    data_pred['x'] = H
                
                    fitted_eq = itm.get_info().loc['fitted_dE00_eq']['value']
                
                    dE = data_pred.eval(f'{fitted_eq}')['y']

                    rate_dE = np.gradient(dE, H[1]-H[0])
                    rates_dE.append(rate_dE)
            

            return rates_dE


    def JND(self, quantity=1, fitted_eq='eq1' ,dose_unit='H_v', JND_dE = 1, light_intensity=50, daily_exposure=10, yearly_exposure=360, group=False, return_data=True):
        
        dose_final = {'H_v':300, 'H_e':10}      
               
        rate_data = self.delta_rate(equation='dE00',dose_unit=dose_unit, extrapolation=True, fitted_eq=fitted_eq, range_dose=(0,dose_final[dose_unit],1))
        rate = rate_data[-1]
        

        if dose_unit == 'H_v':
            JND_dose = (JND_dE / rate) * 1e3                     # in lxh
            time_hours = JND_dose / light_intensity
            time_years = time_hours / (daily_exposure * yearly_exposure)
       

        if dose_unit == 'H_e':
            JND_dose = (JND_dE / rate) * 1e6                     # in J/m²
            time_sec = JND_dose / light_intensity
            time_hours = time_sec / 3600
            time_years = time_hours / (daily_exposure * yearly_exposure)
            
        return time_years

        
    def mean(self, files=[], group=False):

        group_nb = self.get_info().loc['group']['value']
        object_Id = self.get_info().loc['object_Id']['value']

        folder_interim = self.get_path(type='interim_folder')
        folder_processed = self.get_path(type='processed_folder')
        files_interim = os.listdir(folder_interim)

        Ids = sorted(list(set([x.split('_')[2] for x in files_interim if object_Id in x and group_nb in x])))

        Ids_range = sorted(list(set([x.split('_')[2].split('.')[2] for x in files_interim if object_Id in x and group_nb in x])))

        final_H_e_values = [float(class_MFT.MFT(Id, self.project).get_info().loc['total_dose_MJ/m**2']['value']) for Id in Ids]        

        df_dE_arr = []
        intg = []
        avg = []
        duration = []
        N = []
        res = []
        power = []
        FWHM = []
        lum = []
        irr = []
        ill = []

        for Id in Ids:

            itm = class_MFT.MFT(Id, self.project)

            #### INFO FILE #####
                        
            df_INFO =itm.get_info()            

            intg.append(float(df_INFO.loc['integration_time_ms']['value']))
            avg.append(float(df_INFO.loc['average']['value']))
            duration.append(float(df_INFO.loc['duration_min']['value']))
            N.append(float(df_INFO.loc['measurements_N']['value']))
            res.append(float(df_INFO.loc['resolution_micron/pixel']['value']))
            power.append(ufloat_fromstr(df_INFO.loc['power_mW']['value'].split('_')[1]))
            FWHM.append(float(df_INFO.loc['FWHM_micron']['value']))
            lum.append(float(df_INFO.loc['luminuous_flux_lm']['value']))
            irr.append(ufloat_fromstr(df_INFO.loc['irradiance_W/m**2']['value']))
            ill.append(float(df_INFO.loc['illuminance_lux']['value']))


            #### dE FILE #####

            df_dE = itm.get_data(data='dE').loc[0:(np.min(final_H_e_values)),:]
            df_dE_arr.append(df_dE.values)
            







        ###### INFO FILE #######

        final_df_INFO = df_INFO

        # rename title file
        final_df_INFO.rename({'[SINGLE MICRO-FADING ANALYSIS]': '[MEAN MICRO-FADING ANALYSES]'}, inplace=True)
        
        # insert the new values (mean values)
        final_df_INFO.loc['meas_Id','value'] = f'MF.{object_Id}.{"-".join(Ids_range)}'    
        final_df_INFO.loc['integration_time_ms','value'] = np.mean(intg)
        final_df_INFO.loc['average','value'] = np.mean(avg)
        final_df_INFO.loc['duration_min','value'] = np.mean(duration)
        final_df_INFO.loc['measurements_N','value'] = np.mean(N)
        final_df_INFO.loc['resolution_micron/pixel','value'] = np.round(np.mean(res),4)
        final_df_INFO.loc['FWHM_micron','value'] = np.round(np.mean(FWHM),0)
        final_df_INFO.loc['power_mW','value'] = np.round(np.mean(power).n,3)
        final_df_INFO.loc['irradiance_W/m**2','value'] = np.round(np.mean(irr).n,0)
        final_df_INFO.loc['luminuous_flux_lm','value'] = np.round(np.mean(lum),2)
        final_df_INFO.loc['illuminance_lux','value'] = np.round(np.mean(ill),2)


        # insert the std values
        final_df_INFO['value_std'] = pd.Series(dtype='float')   # create to a new empty column for the std values

        final_df_INFO.loc['integration_time_ms','value_std'] = np.round(np.std(intg),1)
        final_df_INFO.loc['average','value_std'] = np.std(avg)
        final_df_INFO.loc['duration_min','value_std'] = np.std(duration)
        final_df_INFO.loc['measurements_N','value_std'] = np.std(N)
        final_df_INFO.loc['resolution_micron/pixel','value_std'] = np.round(np.std(res),4)
        final_df_INFO.loc['FWHM_micron','value_std'] = np.round(np.std(FWHM),0)
        final_df_INFO.loc['power_mW','value_std'] = np.round(np.mean(power).s,3)
        final_df_INFO.loc['irradiance_W/m**2','value_std'] = np.round(np.mean(irr).s,0)
        final_df_INFO.loc['luminuous_flux_lm','value_std'] = np.round(np.std(lum),2)
        final_df_INFO.loc['illuminance_lux','value_std'] = np.round(np.std(ill),0)

        
        # rename the INFO file        
        filename_INFO = self.get_fname().replace(self.get_fname().split('_')[2],f'MF.{object_Id}.{"-".join(Ids_range)}')
        filename_INFO = filename_INFO.replace('INFO.png', 'INFO.txt')

        # save the INFO file
        final_df_INFO.to_csv(f'{folder_processed}{filename_INFO}', index=True)

    
        ###### dE FILE #######
            
        df_dE_arr = np.stack(df_dE_arr, axis=0)  
        
        df_dE_mean = pd.DataFrame(np.mean(df_dE_arr, axis=0), index = df_dE.index,columns = df_dE.columns[:])
        df_dE_std = pd.DataFrame(np.std(df_dE_arr, axis=0), index = df_dE.index,columns = df_dE.columns[:])
        
        #df_dE_mean.index.rename('cum_MJ/m2', inplace=True)
        #df_dE_std.index.rename('cum_MJ/m2', inplace=True)
        
        final_df_dE = pd.concat([df_dE_mean,df_dE_std], keys=['mean','std'], axis=1)    

        #final_df_dE['time_s'] = t_intp
        #final_df_dE['cum_klux_hr'] = E_pho_intp

        #final_df_dE.reset_index(inplace=True)
        #final_df_dE.set_index(['H_MJ/m2','H_klx_hr','time_s'], inplace=True)
        
        #sample_nb = dE_files[0].split('_')[1].split('.')[1]    
        #filename = dE_files[0].replace(dE_files[0].split('_')[1],f'MF.{sample_nb}.{"-".join(Ids_range)}')[11:]
        
        filename_dE = filename_INFO.replace('INFO.txt', 'dE.csv')
        final_df_dE.to_csv(f'{folder_processed}{filename_dE}', index=True)

        return final_df_dE



        

        


    