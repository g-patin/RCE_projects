import measurements
import visualize
import plotting

import pandas as pd
import numpy as np

import colour
from colour.plotting import *
from colour.colorimetry import *
from colour.models import *
from colour import SDS_ILLUMINANTS


class RS(measurements.data):
    def __init__(self,Id,project_id, data_category='interim'):
        super().__init__(Id,project_id,data_category)
        
        

    def Lab(self, illuminant='D65', observer='10deg'):
        """
        Description: Retrieve the CIE L*a*b* values.

        Args:
            _ illuminant (str, optional):  Reference *illuminant* ('D65', or 'D50'). Defaults to 'D65'.
 
            _ observer (str, optional): Reference *observer* ('10deg' or '2deg'). Defaults to '10deg'.

        Returns:
            class `numpy.ndarray`: *CIE L\*a\*b\** colourspace array.
        """

        file = self.get_path(data_category=self.data_category)[0]
        df = pd.read_csv(file, index_col='parameter')
        

        sp = pd.to_numeric(df.loc['[MEASUREMENT DATA]':][2:].iloc[:,0])
        wl = sp.index.astype(float)
        sd = colour.SpectralDistribution(sp,wl) 

        illuminants = {'D65':colour.SDS_ILLUMINANTS['D65'], 'D50':colour.SDS_ILLUMINANTS['D50']}
        observers = {
            '10deg': 'cie_10_1964',
            '2deg' : 'cie_2_1931',
        }
        cmfs_observers = {
            '10deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
            '2deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
            }
        
        ccs_ill = colour.CCS_ILLUMINANTS[observers[observer]][illuminant]

        XYZ = colour.sd_to_XYZ(sd,cmfs_observers[observer], illuminant=illuminants[illuminant])        
        Lab = np.round(colour.XYZ_to_Lab(XYZ/100,ccs_ill),2)

        if self.data_category == 'processed':
            #Lab_std = 
            Lab = np.array(Lab)


        return Lab
    

    def sp(self):
        """Return the reflectance spectrum.

        Returns
        -------
        A numpy array of shape (2,number of reflectance values), where the first values are the wavelengths and the second the reflectance values.
        """

        file = self.get_path() 
        df = pd.read_csv(file, index_col='parameter')
        sp = pd.to_numeric(df.loc['[MEASUREMENT DATA]':][2:].iloc[:,0])
        wl = sp.index.astype(float)

        

        return np.array([wl,sp.values])


    def XYZ(self, illuminant='D65', observer='10deg'):
        """Return the *CIE XYZ* tristimulus values.

        Args:
            illuminant (str, optional): Reference *illuminant* ('D65', or 'D50'). Defaults to 'D65'.
            observer (str, optional): Reference *observer* ('10deg' or '2deg'). Defaults to '10deg'.


        Returns:
            class `numpy.ndarray` : *CIE XYZ* tristimulus values.
        """

        file = self.get_path(data_category=self.data_category)[0]
        df = pd.read_csv(file, index_col='parameter')

        sp = pd.to_numeric(df.loc['[MEASUREMENT DATA]':][2:].iloc[:,0])
        wl = sp.index.astype(float)
        sd = colour.SpectralDistribution(sp,wl) 

        illuminants = {'D65':colour.SDS_ILLUMINANTS['D65'], 'D50':colour.SDS_ILLUMINANTS['D50']}
        cmfs_observers = {
            '10deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
            '2deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
            }
        
        XYZ = colour.sd_to_XYZ(sd,cmfs_observers[observer], illuminant=illuminants[illuminant])
   
        return XYZ
    

    def xy(self, illuminant='D65', observer='10deg'):
        """Return the *CIE xy* chromaticity coordinates.

        Args:
            illuminant (str, optional): Reference *illuminant* ('D65', or 'D50'). Defaults to 'D65'.
            observer (str, optional): Reference *observer* ('10deg' or '2deg'). Defaults to '10deg'.


        Returns:
            class `numpy.ndarray`: *CIE xy* chromaticity coordinates.
        """

        file = self.get_path(data_category=self.data_category)[0]
        df = pd.read_csv(file, index_col='parameter')

        sp = pd.to_numeric(df.loc['[MEASUREMENT DATA]':][2:].iloc[:,0])
        wl = sp.index.astype(float)
        sd = colour.SpectralDistribution(sp,wl) 

        illuminants = {'D65':colour.SDS_ILLUMINANTS['D65'], 'D50':colour.SDS_ILLUMINANTS['D50']}
        observers = {
            '10deg': 'cie_10_1964',
            '2deg' : 'cie_2_1931',
        }
        cmfs_observers = {
            '10deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
            '2deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
            }
        
        ccs_ill = colour.CCS_ILLUMINANTS[observers[observer]][illuminant]

        XYZ = colour.sd_to_XYZ(sd,cmfs_observers[observer], illuminant=illuminants[illuminant])
        xy = np.round(colour.XYZ_to_xy(XYZ,illuminant=ccs_ill),4)
   
        return xy
    
    
    def RGB(self, illuminant='D65', observer='10deg'):
        """_summary_

        Args:
            illuminant (str, optional): Reference *illuminant* ('D65', or 'D50'). Defaults to 'D65'.
            observer (str, optional): Reference *observer* ('10deg' or '2deg'). Defaults to '10deg'.
        """

        file = self.get_path(data_category=self.data_category)[0]
        df = pd.read_csv(file, index_col='parameter')

        sp = pd.to_numeric(df.loc['[MEASUREMENT DATA]':][2:].iloc[:,0])
        wl = sp.index.astype(float)
        sd = colour.SpectralDistribution(sp,wl) 


        illuminants = {'D65':colour.SDS_ILLUMINANTS['D65'], 'D50':colour.SDS_ILLUMINANTS['D50']}
        observers = {
            '10deg': 'cie_10_1964',
            '2deg' : 'cie_2_1931',
        }
        cmfs_observers = {
            '10deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
            '2deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
            }
        
        ccs_ill = colour.CCS_ILLUMINANTS[observers[observer]][illuminant]        

        XYZ = colour.sd_to_XYZ(sd,cmfs_observers[observer], illuminant=illuminants[illuminant])

        #rgb = colour.XYZ_to_RGB(XYZ / 100,illuminant_XYZ = ccs_ill,illuminant_RGB = ccs_ill, matrix_XYZ_to_RGB=)
        #return rgb   


    def sRGB(self, illuminant='D65', observer='10deg'):
        """Compute the sRGB values 

        Parameters
        ----------
        illuminant : str, optional
            _description_, by default 'D65'
        observer : str, optional
            _description_, by default '10deg'

        Returns
        -------
        _type_
            _description_
        """
        

        file = self.get_path(data_category=self.data_category)[0]
        df = pd.read_csv(file, index_col='parameter')

        sp = pd.to_numeric(df.loc['[MEASUREMENT DATA]':][2:].iloc[:,0])
        wl = sp.index.astype(float)
        sd = colour.SpectralDistribution(sp,wl) 


        illuminants = {'D65':colour.SDS_ILLUMINANTS['D65'], 'D50':colour.SDS_ILLUMINANTS['D50']}
        observers = {
            '10deg': 'cie_10_1964',
            '2deg' : 'cie_2_1931',
        }
        cmfs_observers = {
            '10deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
            '2deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
            }
        
        ccs_ill = colour.CCS_ILLUMINANTS[observers[observer]][illuminant]

        XYZ = colour.sd_to_XYZ(sd,cmfs_observers[observer], illuminant=illuminants[illuminant])
        srgb = colour.XYZ_to_sRGB(XYZ / 100, illuminant=ccs_ill)

        return srgb   
    

    def dE(self, itm_RS, method = 'dE00', illuminant='D65', observer='10deg'):
        """Compute the colour difference between two or more CIE L*a*b* values. 

        Args:
            itm_RS (list): a list of interim class variables
            method (str, optional): Colour difference equation ('dE00', 'dE94', 'dE76', 'CMC'). Defaults to 'dE00'.
            illuminant (str, optional): Reference *illuminant* ('D65', or 'D50'). Defaults to 'D65'.
            observer (str, optional): Reference *observer* ('10deg' or '2deg'). Defaults to '10deg'.

        Returns:
            class `numpy.ndarray`: dE values.
        """

        Lab_1 = self.Lab(illuminant,observer)
        methods = {'dE76': 'CIE 1976', 'dE94':'CIE 1994', 'dE00': 'CIE 2000', 'CMC': 'CMC'}
        dEs = []

        for el in itm_RS:
            Lab = el.Lab(illuminant,observer)
            dE = colour.delta_E(Lab_1,Lab, method = methods[method])
            dEs.append(dE)

        return np.array(dEs)
    

    def mean(self, itm_RS, illuminant='D65', observer='10deg'):

        all_data = itm_RS + self


    def plot_CIELAB(self, **kwargs):

        Lab = self.Lab()
        return plotting.CIELAB(data=[Lab], **kwargs)
    

    def plot_data(self, fontsize=26, save=False, plot_category='single', x_range='all', *args, **kwargs):

        if self.data_category == 'interim':
            return super().plot_data(fontsize, save, plot_category, x_range, *args, **kwargs)
        
        else:
            return super().plot_data(fontsize, save, plot_category, x_range, data_category=self.data_category, *args, **kwargs)
    

    def plot_RS(self, **kwargs):

        sp = self.get_data(data='sp')
        data = np.array([sp.index.astype(float),sp])
        label = self.Id

        return plotting.RS_SP(data=[data], labels=[label], **kwargs)


        


        

            

       