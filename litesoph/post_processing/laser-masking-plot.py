from litesoph.utilities import units

def extract_dipolemoment_data(source_data,dm_total_file,dm_masked_file,dm_unmasked_file):
    
    
    dm=open(source_data, "r")
    
    # Create output files
    dm_total = open(dm_total_file,"w")
    dm_masked = open(dm_masked_file,"w")
    dm_unmasked = open(dm_unmasked_file,"w")
          
    lines = dm.readlines()

    f1=lines[3].strip().split()

    # Total dipole moment at time t=0 fs.
    dm_x_t0=float(f1[2])
    dm_y_t0=float(f1[3])
    dm_z_t0=float(f1[4])

    # The dipole moment of the unmasked region at time t=0 fs.
    dm_um_x_t0=float(f1[5])
    dm_um_y_t0=float(f1[6])
    dm_um_z_t0=float(f1[7])

    # The dipole moment of the masked region at time t=0 fs.
    dm_m_x_t0=dm_x_t0-dm_um_x_t0
    dm_m_y_t0=dm_y_t0-dm_um_y_t0
    dm_m_z_t0=dm_z_t0-dm_um_z_t0

    for line in lines[2:]:
          f = line.strip().split()
          # time and dipole moments
          t = float(f[0])
          norm = float(f[1])
          # total dipole moment
          dm_x = float(f[2])
          dm_y = float(f[3])
          dm_z = float(f[4])
          # dipole moment of the unmasked region
          dm_um_x = float(f[5])
          dm_um_y = float(f[6])
          dm_um_z = float(f[7])

          # convert time from atomic units to femtoseconds
          t = round(t*units.au_to_fs,7)
          # Write the x, y, and z components of the induced dipole moments 
          # of the masked and the unmasked regions in separate files  
          
            
          #total dm region
          dm_total.write(str(t)+ "  " + str(dm_x_t0) + "  " + str(dm_y_t0)+ "  " + str(dm_z_t0))
          dm_unmasked.write(str(t)+ "  " + str(dm_um_x-dm_um_x_t0) + "  " + str(dm_um_y-dm_um_y_t0)+ "  " + str(dm_um_z-dm_um_z_t0))
          dm_masked.write(str(t)+ "  " + str(dm_x-dm_um_x-dm_m_x_t0) + "  " + str(dm_y-dm_um_y-dm_m_y_t0)+ "  " + str(dm_z-dm_um_z-dm_m_z_t0))
          dm_masked.write("\n")
          
    dm_total.close()
    dm_unmasked.close()
    dm_masked.close()
    dm.close()
    
  


def plot_graph(data, imgfile:str,row:int, column:int, TITLE:str,XLABEL,YLABEL,xlimit=(0.0, 100.0)):

    """general function for plotting graph using data file"""
    import numpy as np
    import matplotlib.pyplot as plt
    

    #loading data and separating x & y axes
    dat=np.loadtxt(data)  
    X=dat[:,row]  
    Y=dat[:,column]  
    
    #properties of graph
    plt.rcParams["figure.figsize"] = (10,8)

    plt.title(TITLE, fontsize = 25)
    plt.xlabel(XLABEL, fontsize=15, weight = 'bold')
    plt.ylabel(YLABEL, fontsize=15, weight = 'bold')
        
    plt.xticks(fontsize=14,  weight = 'bold')
    plt.yticks(fontsize=14, weight = 'bold')
    
    plt.xlim(xlimit[0], xlimit[1])
    plt.grid() 
       
    plt.plot(X, Y,'k')
    plt.savefig(imgfile)
    plt.show()


