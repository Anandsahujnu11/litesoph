from litesoph.utilities import units
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert
from scipy.constants import e,h
from math import pi
import numpy, scipy.optimize
from fourier import Fourier 


def extract_dipolemoment_data(source_data,dm_total_file:str,dm_masked_file:str,dm_unmasked_file:str):
    
    data = np.loadtxt(source_data,comments="#")

    data[:,0] *= units.au_to_fs
    dm_total = data[:,[0,2,3,4]]
    dm_masked = data[:,[0,5,6,7]]
    dm_unmasked=dm_total-dm_masked
    
    np.savetxt(f"{str(dm_total_file)}.dat", dm_total)
    np.savetxt(f"{str(dm_masked_file)}.dat", dm_masked)
    np.savetxt(f"{str(dm_unmasked_file)}.dat", dm_unmasked)


def fit_sin_for_envelope(time, envelope):

    '''Fit sin to the input time sequence, and return  "period" '''
    time = numpy.array(time)
    envelope = numpy.array(envelope)
    ff = numpy.fft.fftfreq(len(time), (time[1]-time[0]))   
    Fyy = abs(numpy.fft.fft(envelope))
    guess_freq = abs(ff[numpy.argmax(Fyy[1:])+1])  
    guess_amp = numpy.std(envelope) * 2.**0.5
    guess_offset = numpy.mean(envelope)
    guess = numpy.array([guess_amp, 2.*numpy.pi*guess_freq, 0., guess_offset])

    def sinfunc(t, A, w, p, c):  return A * numpy.sin(w*t + p) + c
    popt, pcov = scipy.optimize.curve_fit(sinfunc, time, envelope, p0=guess)
    A, w, p, c = popt
    f = w/(2.*numpy.pi)
    time_period= 1./f
    time_period_for_envelope= 2*time_period
    fitfunc = lambda t: A * numpy.sin(w*t + p) + c
    
    return time_period_for_envelope

def time_period_fourier(*args, **kwargs):

    import fourier as fr

    pass 



def generate_envelope(datafilename, twin, wframe:int, envelope_outfile:str, directionaxis:int, timeaxis=0):
    """ function to generate envelope data"""
    
    dat=np.loadtxt(datafilename,comments="#") 
    nt=len(dat) 

    time = dat[:,timeaxis] 
    fn = dat[:,directionaxis] 
    delt = time[1]-time[0]

    fou=Fourier(nt,delt,twin)
    env  = fou.envelope(fn[:])
    amplitude_envelope=env[0]

    envelope_data=np.stack((time, amplitude_envelope), axis=-1) 
    np.savetxt(f"{str(envelope_outfile)}.dat", envelope_data)

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
    freq =(f_trans[0])
    fw   =(f_trans[1])
    
    f_trans_data=np.stack((freq, fw), axis=-1) 
    np.savetxt(f"{str(fourier_outfile)}.dat", f_trans_data)

    peaks_index, properties = find_peaks(np.abs(fw), height=5)

    print('Positions and magnitude of frequency peaks:')
    [print("%4.4f    \t %3.4f" %(freq[peaks_index[i]], properties['peak_heights'][i])) for i in range(len(peaks_index))]

    plt.plot(freq, np.abs(fw.real),'-', freq[peaks_index],properties['peak_heights'],'x')
    plt.xlabel("Frequency")
    plt.ylabel("Amplitude")
    plt.show()
    # return properties


# env_data='/home/anand/Documents/myprojects/litesoph-testing-myworks/laser-masking/envelope.dat'
# data1='/home/anand/Downloads/dmpulse_Gauss_Delta_laser.dat'
# data2='/home/anand/Downloads/dm.dat'


# prop_fr=freq_fourier(data1, 100, len(data1), 'fourier_outfile',2)
# print('properties of fourier transform :', prop_fr )









def Energy_coupling_constant(timeperiodmethod, *args,**kwargs):

    timeperiod_in_sec= timeperiodmethod(args,kwargs)
    sec_to_fs= 10**(-15)
    coupling_constant_in_eV= h/(timeperiod_in_sec*sec_to_fs*e)
    return coupling_constant_in_eV
    

def envelope_plot(dm_data,env_data,imgfile:str,dm_column:int,title, x_label,y_label,env_column=1,time_column=0):
    
    dm_dat=np.loadtxt(dm_data)
    env_dat=np.loadtxt(env_data)

    t=dm_dat[:,time_column]  
    dm_signal=dm_dat[:,dm_column]
    amplitude_envelope=env_dat[:,env_column]
         
    plt.rcParams["figure.figsize"] = (10,8)
    plt.title(title, fontsize = 25)
    plt.xlabel(x_label, fontsize=15, weight = 'bold')
    plt.ylabel(y_label, fontsize=15, weight = 'bold')
        
    plt.xticks(fontsize=14,  weight = 'bold')
    plt.yticks(fontsize=14, weight = 'bold')
    
    plt.grid() 

    plt.plot(t, dm_signal,label='dipole moment')
    plt.plot(t, amplitude_envelope,label='envelope')
    plt.legend(loc ="upper right")

    plt.savefig(imgfile)
    plt.show()
    