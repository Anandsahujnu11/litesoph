from litesoph.utilities import units
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert
from scipy.constants import e,h
from math import pi
import numpy, scipy.optimize
from fourier import Fourier 

def freq_fourier(envelope_filename, twin, wframe:int, fourier_outfile:str, directionaxis:int, timeaxis=0):
    """ function to generate envelope data"""
    from scipy.signal import find_peaks

    dat=np.loadtxt(envelope_filename,comments="#") 
    nt=len(dat) 

    time = dat[:,timeaxis] 
    fn = dat[:,directionaxis] 
    delt = time[1]-time[0]

    fou=Fourier(nt,delt,twin)
    f_trans  = fou.transform(fn[:])
    # freq =(f_trans[0])
    # fw   =(f_trans[1])
    
    # f_trans_data=np.stack((abs(freq), fw), axis=-1) 
    np.savetxt(f"{str(fourier_outfile)}.dat", f_trans)
    # np.savetxt("fw.dat", f_trans[1])

    return f_trans

    
env_data='/home/anand/Documents/myprojects/litesoph-testing-myworks/laser-masking/envelope.dat'
prop_fr=freq_fourier(env_data, 210, 10500, 'fourier_outfile',1)
print('properties of fourier transform :', prop_fr )
plt.plot(prop_fr[0], prop_fr[1].real)
plt.show()
