####### IMPORT PACKAGES #######

import os
from re import X
from tkinter import font
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from glob import glob
import imageio

from IPython import get_ipython

import colour
from colour.plotting import *
from colour.colorimetry import *
from colour.models import *
from colour import SDS_ILLUMINANTS

from ipywidgets import Layout, Button, Box, interact, interactive, fixed, interact_manual
import ipywidgets as ipw
from IPython.display import display, clear_output

import plotly.express as px  
from pathlib import Path 

# self made packages
import acronyms
import measurements
#import microfading
#import reflectance
#import class_project


####### DEFINE GENERAL PARAMETERS #######

style = {"description_width": "initial"}
d65 = colour.CCS_ILLUMINANTS["cie_10_1964"]["D65"]


plt.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
    "font.sans-serif": "Helvetica",
})


####### DEFINE FOLDERS #######





####### THE FUNCTIONS #######


def CIELAB(data, std=[], labels=[], title='none', color_data='sample', fontsize=24, line=False, save=False, path_fig='cwd', *args, **kwargs):
    """
    Description: Plot the CIELAB coordinates of one or several datasets.

    
    Args:
        _ data (list): A list of data points, where each data point is a numpy array. 

        _ std (list, optional): A list of standard variation values respective to each element given in the data parameter. Defaults to [].

        _ labels (list, optional): A list of labels respective to each element given in the data parameter that will be shown in the legend. When the list is empty there is no legend displayed. Defaults to [].
        
        _ title (str, optional): Suptitle of the figure. When 'none' is passed as an argument, there is no suptitle displayed. Defaults to 'none'.
        
        _ color_data (str or list, optional): Color of the data points. When 'sample' is passed as an argument, the color will correspond to the srgb values of the sample. A list of colors - respective to each element given in the data parameter - can be passed. Defaults to 'sample'.
        
        _ fs (int, optional): Fontsize of the plot (title, ticks, and labels). Defaults to 24.
        
        _ line (boolean, optional): Add a gray dash line to a time-series of Lab values. Defaults to False.

    
    Returns: A figure showing the Lab values in the CIELAB color space.

    """

    if Path('~/Documents/RCE/docs/colour_circle.png').expanduser().exists():
        path_colour_circle = Path('~/Documents/RCE/docs/colour_circle.png').expanduser()

    elif Path('~/Documents/docs/colour_circle.png').expanduser().exists():
        path_colour_circle = Path('~/Documents/docs/colour_circle.png').expanduser()

    else:
        print(f'Plotting process aborted ! Add colour_circle.png in the following folder: {Path("~/Documents/RCE/docs").expanduser()}')
        return


    sns.set()
    fig, ax = plt.subplots(2,2, figsize=(10, 10), gridspec_kw=dict(width_ratios=[1, 2], height_ratios=[2, 1]))
    
            
    Lb = ax[0,0]
    ab = ax[0,1]
    AB = ax[1,0]
    aL = ax[1,1]

    i = 0    # a counting value that is used to loop over color_data values, when required.

    if len(labels) == 0:
        labels = ['none'] * len(data)


    for el_data, label in zip(data,labels):

        el_data = el_data.transpose()
        

        L = el_data[0]
        a = el_data[1]
        b = el_data[2]        

        if color_data == 'sample':
            Lab = np.array([L, a, b]).transpose()
            srgb = colour.XYZ_to_sRGB(colour.Lab_to_XYZ(Lab), d65).clip(0, 1)
            color = srgb
            color_line = color[1:]
        elif color_data == None:
            color = None
            color_line = None
        elif type(color_data) == str:            
            color = color_data
        else:
            color = color_data[i]
            color_line = color
        
        
        im_colour_circle = imageio.imread(path_colour_circle)
        AB.imshow(im_colour_circle, extent=(-110,110,-110,110))  
        AB.axhline(0, color="black", lw=0.5)
        AB.axvline(0, color="black", lw=0.5)
        
        if len(el_data.shape) == 1:            

            Lb.scatter(L, b, color = color, **kwargs)
            ab.scatter(a, b, color = color, **kwargs, label = label)
            aL.scatter(a, L, color = color, **kwargs) 
            AB.scatter(a,b, color = '0.5', marker = 'o')

        else:            

            Lb.scatter(L[1:], b[1:], color=color_line, **kwargs)
            ab.scatter(a[1:], b[1:], color=color_line, label = label, **kwargs)            
            aL.scatter(a[1:], L[1:], color=color_line, **kwargs)

            Lb.scatter(L[0], b[0], marker = 'x', color='k', **kwargs)
            ab.scatter(a[0], b[0], marker = 'x', color='k', **kwargs)
            aL.scatter(a[0], L[0], marker = 'x', color='k', **kwargs) 

            AB.scatter(a,b, color = '0.5', marker = 'o')  

            if line:
                Lb.plot(L,b, color='0.6', ls='--', lw=1)
                ab.plot(a,b, color='0.6', ls='--', lw=1)
                aL.plot(a,L, color='0.6', ls='--', lw=1)


        i = i + 1 


    AB.grid(False) 
    AB.set_xlim(-110, 110)
    AB.set_ylim(-110, 110)         
                     
    Lb.set_xlabel("CIE $L^*$", fontsize=fontsize)
    Lb.set_ylabel("CIE $b^*$", fontsize=fontsize)
    AB.set_xlabel("CIE $a^*$", fontsize=fontsize)
    AB.set_ylabel("CIE $b^*$", fontsize=fontsize)
    aL.set_xlabel("CIE $a^*$", fontsize=fontsize)
    aL.set_ylabel("CIE $L^*$", fontsize=fontsize) 
        
        
    Lb.xaxis.set_tick_params(labelsize=fontsize)
    Lb.yaxis.set_tick_params(labelsize=fontsize)
    ab.xaxis.set_tick_params(labelsize=fontsize)
    ab.yaxis.set_tick_params(labelsize=fontsize)   
    AB.xaxis.set_tick_params(labelsize=fontsize)
    AB.yaxis.set_tick_params(labelsize=fontsize)
    aL.xaxis.set_tick_params(labelsize=fontsize)
    aL.yaxis.set_tick_params(labelsize=fontsize)

        
    if title != 'none':
        plt.suptitle(title, fontsize = fontsize+3)

    if labels[0] != 'none' and len(labels) < 9:
        ab.legend(loc = 'best', fontsize=fontsize-5)

    plt.tight_layout()

    if save == True:
        if path_fig == 'cwd':
            path_fig = f'{os.getcwd()}/CIELAB.png'                    
            
        fig.savefig(path_fig,dpi=300, facecolor='white')  
    
    
    plt.show()


def colour_patches(data, color_unit='Lab', labels=[], title='none', fontsize=28, save=False, path_fig='cwd', *args, **kwargs):

    if len(labels) == 0:
        labels = ['none'] * len(data)

    N = len(data)

    if color_unit == 'Lab':
        data = [colour.XYZ_to_sRGB(colour.Lab_to_XYZ(el), d65).clip(0, 1) for el in data]


    fig, ax = plt.subplots(1,1,figsize = (15,7))        
    fig.patch.set_facecolor((0.75, 0.75, 0.75))

    w = 0.05 / (N*0.5)        # width empty space between each colour patch
    W = (0.9 - ((N-1)*w))/N   # width of each colour patch
    x1 = 0
    x2 = 0

    for el, label in zip (data,labels):        

        cp = matplotlib.patches.Rectangle((0.05+x1+x2,0.1), W, 0.8, color=el)
        ax.add_patch(cp)
        ax.annotate(label,(0.05+(x1+x2), 0.92),weight='bold',fontsize=fontsize-N*0.9)

        x1 = x1 + W
        x2 = x2 + w
        
        

        


    ax.grid(False)
    ax.axis('off')

    plt.tight_layout()

    if save == True:
        if path_fig == 'cwd':
            path_fig = f'{os.getcwd()}/CP.png'                    
            
        fig.savefig(path_fig,dpi=300, facecolor='white')  

    plt.show()




        
    
            




def colour_patches_fading(data, group=False, title='Colour patches', fontsize=20, save=False, path_fig='cwd'):

    
    if group == False:

        E_rad = data[0]
        E_pho = data[1]
        t = data[2]
        L = data[3]
        a = data[4]
        b = data[5]
        
        t_fin = int(np.round((t[-1]/60),0))
        Lab = np.array([L, a, b]).transpose()
        srgb = colour.XYZ_to_sRGB(colour.Lab_to_XYZ(Lab), d65).clip(0, 1)

        fig, axes = plt.subplots(2,1,figsize = (15,7))        
        fig.patch.set_facecolor((0.75, 0.75, 0.75))
            
        E_rad_final = E_rad[-1]  # in MJ/m²
        E_pho_final = E_pho[-1]  # in klx.hr

        x = np.linspace(0,len(srgb),num = 5, endpoint = True,dtype = 'int')
        #t_int = np.linspace(0,t_fin,num = 5, endpoint = True,dtype = 'int')
        E_rad_values = np.round(np.linspace(0,E_rad_final, num = 5, endpoint = True, dtype = 'float'),2)
        E_pho_values = np.round(np.linspace(0,E_pho_final, num = 5, endpoint = True, dtype = 'float'),2)

        cp_0 = matplotlib.patches.Rectangle((0,0), 0.2, 1, color=srgb[0])
        cp_1 = matplotlib.patches.Rectangle((0.2,0), 0.2, 1, color=srgb[x[1]])
        cp_2 = matplotlib.patches.Rectangle((0.4,0), 0.2, 1, color=srgb[x[2]])
        cp_3 = matplotlib.patches.Rectangle((0.6,0), 0.2, 1, color=srgb[x[3]])
        cp_4 = matplotlib.patches.Rectangle((0.8,0), 0.2, 1, color=srgb[-1])

        axes[0].add_patch(cp_0)
        axes[0].add_patch(cp_1)    
        axes[0].add_patch(cp_2) 
        axes[0].add_patch(cp_3) 
        axes[0].add_patch(cp_4) 
        axes[0].grid(False)
        axes[0].axis('off')

        if L[0] > 50:
            axes[0].annotate('0 MJ/m²',(0.05, 0.05),weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_rad_values[1]} MJ/m²',(0.24, 0.05),weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_rad_values[2]} MJ/m²',(0.44, 0.05),weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_rad_values[3]} MJ/m²',(0.63, 0.05),weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_rad_values[4]} MJ/m²',(0.83, 0.05),weight='bold',fontsize = fontsize)            
            axes[0].annotate('0 klx.hr',(0.05, 0.87),weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_pho_values[1]} klx.hr',(0.22, 0.87),weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_pho_values[2]} klx.hr',(0.42, 0.87),weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_pho_values[3]} klx.hr',(0.62, 0.87),weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_pho_values[4]} klx.hr',(0.82, 0.87),weight='bold',fontsize = fontsize)  
                
        else:
            axes[0].annotate('0 MJ/m²',(0.05, 0.05),color = 'white', weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_rad_values[1]} MJ/m²',(0.24, 0.05),color = 'white', weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_rad_values[2]} MJ/m²',(0.44, 0.05),color = 'white', weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_rad_values[3]} MJ/m²',(0.63, 0.05),color = 'white', weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_rad_values[4]} MJ/m²',(0.83, 0.05),color = 'white', weight='bold',fontsize = fontsize)  
            axes[0].annotate('0 klx.hr',(0.05, 0.87),color = 'white',weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_pho_values[1]} klx.hr',(0.22, 0.87),color = 'white',weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_pho_values[2]} klx.hr',(0.42, 0.87),color = 'white',weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_pho_values[3]} klx.hr',(0.62, 0.87),color = 'white',weight='bold',fontsize = fontsize)
            axes[0].annotate(f'{E_pho_values[4]} klx.hr',(0.82, 0.87),color = 'white',weight='bold',fontsize = fontsize) 

        cp_i = matplotlib.patches.Rectangle((0,0), 0.5, 1, color=srgb[0])
        cp_f = matplotlib.patches.Rectangle((0.5,0), 0.5, 1, color=srgb[-1])
        axes[1].add_patch(cp_i)
        axes[1].add_patch(cp_f)    
        axes[1].grid(False)
        axes[1].axis('off')

        if L[0] > 50:
            axes[1].annotate('Initial - 0 min',(0.02, 0.05),weight='bold',fontsize = fontsize)
            axes[1].annotate(f'Final - {t_fin} min',(0.8, 0.05),weight='bold',fontsize = fontsize)
            
        else:
            axes[1].annotate('Initial - 0 min',(0.02, 0.05),color = 'white', weight='bold',fontsize = fontsize)
            axes[1].annotate(f'Final - {t_fin} min',(0.8, 0.05),color = 'white', weight='bold',fontsize = fontsize) 

        plt.suptitle(title,fontsize = fontsize+3)
        plt.tight_layout()

        if save == True:
            if path_fig == 'cwd':
                path_fig = f'{os.getcwd()}/MFT-CP.png'                    
            
            fig.savefig(path_fig,dpi=300, facecolor='white')

        plt.show()



def delta_E(data, yerr=[], labels=[], title='none', fontsize=28, x_scale=['He','Hv'], methods=['dE00'], save=False, path_fig='cwd'):    
    """_summary_

    Args:
        data (_type_): _description_
        title (str, optional): _description_. Defaults to 'none'.        
        fontsize (int, optional): _description_. Defaults to 28.
    """

 
    labels_eq = {
        'dE76': r'$\Delta E^*_{ab}$',
        'dE94': r'$\Delta E^*_{94}$',
        'dE00': r'$\Delta E^*_{00}$',        
    }

    x_labels = {
        'Hv': 'Exposure dose $H_v$ (klxh)',
        'He': 'Radiant Exposure $H_e$ ($MJ/m^2$)',
        't_s': 'Exposure duration (sec)',
        't_m': 'Exposure duration (min)'
    }

    ls_dic = {
        'dE76': '--',
        'dE00': '-',
        'dE94': ':',
    }

    colors = {
        'dE76': 'red',
        'dE00': 'blue',
        'dE94': 'green',
    }    

    if len(labels) == 0:
        labels = ['none'] * len(data)
        
    sns.set()
    fig, ax1 = plt.subplots(1,1, figsize=(15,9))    

    i = 0
    j = 0
    ls = '-'
    highest_final_dE = 0

    
    if len(x_scale) == 1:        
        
        for d, label in zip (data, labels):   

            if isinstance(d, pd.DataFrame):
                d = d.T.values          
                
            x = d[0] 
                     
            for y_val in d[1:]:                

                if len(data) == 1:                    
                    label = labels_eq[labels[i]]
                    ls = ls_dic[labels[i]]
                    

                if y_val[-1] > highest_final_dE:
                    highest_final_dE = y_val[-1]                    
                
                ax1.plot(x, y_val, ls=ls, label=label)

                if len(yerr) != 0:
                    ax1.fill_between(x, y_val-yerr[i], y_val+yerr[i], alpha=0.3, color='0.5', edgecolor='none')
                    j = j + 1               

                i = i + 1      
            

        ax1.set_xlabel(x_labels[x_scale[0]],fontsize=fontsize)
                
    
    else: 

        ax2 = ax1.twiny()       
        
        for d, label in zip (data, labels):  

            if isinstance(d, pd.DataFrame):
                d = d.T.values                  
            
            x1 = d[0]
            x2 = d[1]            

            for y_val in d[2:]:

                if len(data) == 1:                    
                    label = labels_eq[labels[i]]
                    ls = ls_dic[labels[i]]
                    

                ax1.plot(x1, y_val, ls=ls, label=label)
                ax2.plot(x2, y_val, ls=ls)

                if y_val[-1] > highest_final_dE:
                    highest_final_dE = y_val[-1]

                if len(yerr) != 0:
                    ax1.fill_between(x1, y_val-yerr[j], y_val+yerr[j], alpha=0.3, color='0.5', edgecolor='none')
                    j = j+1
                
                i = i + 1
            
        ax1.set_xlabel(x_labels[x_scale[0]], fontsize=fontsize)
        ax2.set_xlabel(x_labels[x_scale[1]], fontsize=fontsize)  
        
        ax2.set_xlim(0)            
        ax2.set_ylim(0)
        ax2.grid(False)        
        ax2.xaxis.set_tick_params(labelsize=fontsize)   
            
    

    ax1.xaxis.set_tick_params(labelsize=fontsize)
    ax1.yaxis.set_tick_params(labelsize=fontsize)
        
    ax1.set_xlim(0)
    ax1.set_ylim(0, highest_final_dE*1.05)
    
    if title != 'none':
        ax1.set_title(title, fontsize=fontsize+2)


    if len(methods) > 1:
        ax1.set_ylabel('Colour difference', fontsize=fontsize)
    else:
        ax1.set_ylabel(labels_eq[methods[0]], fontsize=fontsize)

    if labels[0] != 'none' and len(labels) < 9:
        ax1.legend(loc = 'best', fontsize=fontsize-3)
    
    plt.tight_layout()

    if save == True:
        if path_fig == 'cwd':
            path_fig = f'{os.getcwd()}/dE.png'                    
            
        fig.savefig(path_fig,dpi=300, facecolor='white')  

    plt.show()


def delta_R(data, std=[], x_scale='rad', labels=[], title='Colorimetric coordinates', fontsize=18, save=False, path_fig='cwd', *args, **kwargs):

    sns.set()
    fig, ax1 = plt.subplots(1,1, figsize=(15,9))  

    ax1.xaxis.set_tick_params(labelsize=fontsize)
    ax1.yaxis.set_tick_params(labelsize=fontsize)
        
    ax1.set_xlim(0)
    ax1.set_ylim(0, highest_final_dE*1.05)
    
    if title != 'none':
        ax1.set_title(title, fontsize=fontsize+2)



    if labels[0] != 'none' and len(labels) < 9:
        ax1.legend(loc = 'best', fontsize=fontsize-3)
    
    plt.tight_layout()

    if save == True:
        if path_fig == 'cwd':
            path_fig = f'{os.getcwd()}/dE.png'                    
            
        fig.savefig(path_fig,dpi=300, facecolor='white')  

    plt.show()      



def LabCh(data, std=[], x_scale='He', labels=[], title='Colorimetric coordinates', fontsize=18, save=False, path_fig='cwd', *args, **kwargs):

    if len(labels) == 0:
        labels = ['none'] * len(data)

    sns.set()
    fig, [ax1,ax2,ax3,ax4,ax5] = plt.subplots(5,1,figsize=(10,20))
    
    l = 0
    for d in data:

        if len(labels) == 0:
            label_data = ''
        else:
            label_data = labels[l]
            l = l+1 

        E_rad = d[0]
        L = d[1]
        a = d[2]
        b = d[3]
        C = d[4]
        h = d[5]

        delta_L_rel = delta_L = np.round(L[-1] - L[0],2)
        delta_a = np.round(a[-1] - a[0],2)
        delta_b = np.round(b[-1] - b[0],2)
        delta_C = np.round(C[-1] - C[0],2)
        delta_h = np.round(h[-1] - h[0],2)

        delta_a_rel = np.round(delta_a / 120 * 100,2)
        delta_b_rel = np.round(delta_b / 120 * 100,2)
        delta_C_rel = np.round(delta_C / 120 * 100,2)
        delta_h_rel = np.round(delta_h / 360 * 100,2)

            

        # plot L* values
        ax1.plot(E_rad,L, label = f'{label_data} $\Delta L$ = {delta_L} ({delta_L_rel}\%)')

        # plot a* values
        ax2.plot(E_rad,a, label = f'{label_data} $\Delta a$ = {delta_a} ({delta_a_rel}\%)')

        # plot b* values
        ax3.plot(E_rad,b, label = f'{label_data} $\Delta b$ = {delta_b} ({delta_b_rel}\%)')

        # plot C* values
        ax4.plot(E_rad,C, label = f'{label_data} $\Delta C$ = {delta_C} ({delta_C_rel}\%)')

        # plot h values
        ax5.plot(E_rad,h, label = f'{label_data} $\Delta b$ = {delta_h} ({delta_h_rel}\%)')


        if len(std) != 0:
            L_std = std[0]
            a_std = std[1]
            b_std = std[2]
            C_std = std[3]
            h_std = std[4]

            ax1.fill_between(E_rad, L-L_std, L+L_std, alpha=0.3, color='0.5', edgecolor='none')
            ax2.fill_between(E_rad, a-a_std, a+a_std, alpha=0.3, color='0.5', edgecolor='none')
            ax3.fill_between(E_rad, b-b_std, b+b_std, alpha=0.3, color='0.5', edgecolor='none')
            ax4.fill_between(E_rad, C-C_std, C+C_std, alpha=0.3, color='0.5', edgecolor='none')
            ax5.fill_between(E_rad, h-h_std, h+h_std, alpha=0.3, color='0.5', edgecolor='none')

    ax1.set_ylabel(r'Brigthness (CIE $L\textsuperscript{*}$)', fontsize=fontsize)
    ax2.set_ylabel(r'CIE $a\textsuperscript{*}$', fontsize=fontsize)
    ax3.set_ylabel(r'CIE $b\textsuperscript{*}$', fontsize=fontsize)
    ax4.set_ylabel(r'CIE $C\textsuperscript{*}$', fontsize=fontsize)
    ax5.set_ylabel(r'CIE $h$', fontsize=fontsize)
    
       
    
    ax1.xaxis.set_tick_params(labelsize=fontsize)
    ax1.yaxis.set_tick_params(labelsize=fontsize) 
    ax2.xaxis.set_tick_params(labelsize=fontsize)
    ax2.yaxis.set_tick_params(labelsize=fontsize)   
    ax3.xaxis.set_tick_params(labelsize=fontsize) 
    ax3.yaxis.set_tick_params(labelsize=fontsize) 
    ax4.xaxis.set_tick_params(labelsize=fontsize)
    ax4.yaxis.set_tick_params(labelsize=fontsize) 
    ax5.xaxis.set_tick_params(labelsize=fontsize)
    ax5.yaxis.set_tick_params(labelsize=fontsize) 
     
    ax1.set_xlim(left=0)
    ax2.set_xlim(left=0)
    ax3.set_xlim(left=0)
    ax4.set_xlim(left=0)
    ax5.set_xlim(left=0)
    
    

    if x_scale == 'He':
        ax5.set_xlabel(r'Radiant exposure (MJ/m$^2$)', fontsize=fontsize)

    if x_scale == 'Hv':
        ax5.set_xlabel(r'Exposure dose (klx.hr)', fontsize=fontsize)    

    if x_scale == 't_h':
        ax5.set_xlabel(r'Exposure duration (hours)', fontsize=fontsize)  

    

    if labels[0] != 'none' and len(labels) < 9:
        ax1.legend(loc='best', fontsize=fontsize-3)
        ax2.legend(loc='best', fontsize=fontsize-3)
        ax3.legend(loc='best', fontsize=fontsize-3)
        ax4.legend(loc='best', fontsize=fontsize-3)
        ax5.legend(loc='best', fontsize=fontsize-3)
    
    plt.suptitle(title,fontsize=fontsize+3)
    plt.tight_layout(rect = (0,0,1,0.99))
    plt.show()



def power(data, labels=[], title='none', fontsize=24, save=False, path_fig='cwd'):

    sns.set()
    fig, ax = plt.subplots(1,1, figsize=(15,7))


    if len(labels) == 0:
        labels = ['none'] * len(data)


    for d, label in zip(data,labels):

        time = d[0]
        power = d[1]               

        ax.plot(time,power, label=label)        

    ax.set_xlim(0)
    
    ax.set_xlabel("Time (s)", fontsize=fontsize)
    ax.set_ylabel("Radiant power (mW)", fontsize=fontsize)

    ax.xaxis.set_tick_params(labelsize=fontsize)
    ax.yaxis.set_tick_params(labelsize=fontsize)

    if title != 'none':
        ax.set_title(title, fontsize = fontsize+3)

    if list(set(labels)) != ['none']:
        plt.legend(fontsize=fontsize)

    plt.tight_layout()

    if save == True:
        if path_fig == 'cwd':
            path_fig = f'{os.getcwd()}/Power.png'                    
            
        fig.savefig(path_fig,dpi=300, facecolor='white')    

    plt.show()



def RS_SP(data, std=[], labels=[], title='none', fontsize=24, x_range=(), save=False, path_fig='cwd', derivation="none", *args, **kwargs):
    """
    Description: Plot the reflectance spectrum of one or several datasets.

    
    Args:
        _ data (list): A list of data elements, where each element corresponds to a reflectance spectrum is a numpy array. 

        _ std (list, optional): A list of standard variation values respective to each element given in the data parameter. Defaults to [].

        _ labels (list, optional): A list of labels respective to each element given in the data parameter that will be shown in the legend. When the list is empty there is no legend displayed. Defaults to [].
        
        _ title (str, optional): Suptitle of the figure. When 'none' is passed as an argument, there is no suptitle displayed. Defaults to 'none'.
        
        _ color_data (str or list, optional): Color of the data points. When 'sample' is passed as an argument, the color will correspond to the srgb values of the sample. A list of colors - respective to each element given in the data parameter - can be passed. Defaults to 'sample'.
        
        _ fs (int, optional): Fontsize of the plot (title, ticks, and labels). Defaults to 24.    

        _ x_range (tuple, optional): Lower and upper limits of the x-axis. Defaults to (). 

        

    
    Returns: A figure showing the reflectance spectra.
    """

    sns.set()
    fig, ax = plt.subplots(1,1, figsize=(15, 9))

    if len(labels) == 0:
        labels = ['none'] * len(data)
    

    for el_data, label in zip(data,labels):        

        df_data = pd.DataFrame(el_data).T.set_index(0)
        
        if x_range != ():
            df_data = df_data.loc[x_range[0]:x_range[1]]  

        wl = df_data.index
        sp = df_data.iloc[:,0]     

        ax.plot(wl, sp, label = label, *args, **kwargs)

    if x_range != ():
        ax.set_xlim(x_range[0],x_range[1])
    
    ax.set_xlabel('Wavelength $\lambda$ (nm)', fontsize = fontsize)

    if derivation == "none":
        ax.set_ylabel('Reflectance factor', fontsize = fontsize)
    elif derivation == "first":
        ax.set_ylabel(r'$\frac{dR}{d\lambda}$', fontsize = fontsize+10)

    ax.xaxis.set_tick_params(labelsize = fontsize)
    ax.yaxis.set_tick_params(labelsize = fontsize)

    if title != 'none':
        ax.set_title(title, fontsize = fontsize+3)

    if labels[0] != 'none' and len(labels) < 9:
        plt.legend(loc = 'best', fontsize=fontsize-2)

    plt.tight_layout()

    if save == True:
        if path_fig == 'cwd':
            path_fig = f'{os.getcwd()}/RS-SP.png'        
        
        fig.savefig(path_fig,dpi=300, facecolor='white')

    plt.show()


def SP_diff(sp1, sp2, wl='none', labels=[], title='none', fontsize=28, x_range=(), y_range=(), save=True, path_fig='cwd', *args, **kwargs):

    if len(sp1) != len(sp2):

        print(f'There are {len(sp1)} spectra in sp1 and {len(sp2)} spectra in sp1. sp1 and sp2 should contain a similar amount of spectra.')

        return
    
    diff = sp2 - sp1
    

    if len(labels) == 0:
        labels = ['none'] * len(sp1)
    
    if wl == 'none':
        print('hello')
        wl = np.arange(0,len(sp1[0]))

    sns.set()
    fig, ax = plt.subplots(1,1, figsize=(15,8))

    for sp_diff, label in zip(diff,labels):

        ax.plot(wl, sp_diff, label=label)
    

    if x_range != ():
        ax.set_xlim(x_range[0], x_range[1])

    if y_range!=():    
        ax.set_ylim(y_range[0], y_range[1])
    
    ax.set_xlabel('Wavelength $\lambda$ (nm)', fontsize = fontsize)
    ax.set_ylabel('Difference in reflectance factor', fontsize = fontsize)

    ax.xaxis.set_tick_params(labelsize = fontsize)
    ax.yaxis.set_tick_params(labelsize = fontsize)

    if title != 'none':
        ax.set_title(title, fontsize = fontsize+3)

    if labels[0] != 'none' and len(labels) < 9:
        plt.legend(loc = 'best', fontsize=fontsize-2)

    plt.tight_layout()

    if save == True:
        if path_fig == 'cwd':
            path_fig = f'{os.getcwd()}/SP-diff.png'        
        
        fig.savefig(path_fig,dpi=300, facecolor='white')

    plt.show()


