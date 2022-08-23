import tkinter as tk
from tkinter import ttk
from tkinter import font
from litesoph.gui import images
from litesoph.gui.input_validation import Onlydigits, Decimalentry
from litesoph.gui.visual_parameter import myfont, myfont1, myfont2, label_design, myfont15

from litesoph.gui.engine_views import EngineViews
from litesoph.simulations.models import dummyengineModel


class dummyengineGSPage(EngineViews):

    def __init__(self, gspage) -> None:
        self.gspage = gspage
        self.default_para = dummyengineModel.ground_state

    def show_system_tab(self, parent):
        """ Creates widgets for system tab inputs"""

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
        mode_frame = ttk.Frame(parent)
        mode_frame.grid(row=0, column=0)      

        self.heading = tk.Label(mode_frame,text="LITESOPH input for Ground State",fg='green')
        self.heading['font'] = myfont15()
        self.heading.grid(row=0, column=0, pady=5)
                
        self.label_proj = tk.Label(mode_frame,text="mode",bg=label_design['bg'], fg=label_design['fg'])
        self.label_proj['font'] = label_design['font']
        self.label_proj.grid(row=2, column=0, sticky='w', padx=2, pady=4)

        task = ttk.Combobox(mode_frame, textvariable = self._var['mode'], values= self.default_para['mode']['values'])
        task['font'] = label_design['font']
        task.grid(row=2, column= 1, sticky='w', padx=2, pady=2)
        task['state'] = 'readonly'
        
        self.parameter2 = tk.Label(mode_frame, text="Parameter2",bg=label_design['bg'], fg=label_design['fg'])
        self.parameter2['font'] = label_design['font']
        self.parameter2.grid(row=4, column=0, sticky='w', padx=2, pady=4)

        sub_task = ttk.Combobox(mode_frame, textvariable= self._var['parameter2'], value = self.default_para['parameter2']['values'])
        sub_task['font'] = label_design['font']
        sub_task.grid(row=4, column=1, sticky='w', padx=2, pady=2)
        sub_task['state'] = 'readonly'
       

        self.parameter4 = tk.Label(mode_frame, text="Parameter3",bg=label_design['bg'], fg=label_design['fg'])
        self.parameter4['font'] = label_design['font']
        self.parameter4.grid(row=6, column=0, sticky='w', padx=2, pady=4)

        self.entry_chrg = Onlydigits(mode_frame,textvariable=self._var['parameter4'])
        self.entry_chrg['font'] = label_design['font']
        self.entry_chrg.grid(row=6, column=1, sticky='w', padx=2, pady=2)

        self.multiplicity_label = tk.Label(mode_frame, text='Parameter4',bg=label_design['bg'], fg=label_design['fg'])
        self.multiplicity_label['font'] = label_design['font']
        self.multiplicity_label.grid(row=7, column=0, sticky='w', padx=2, pady=4)

        self.multiplicity_entry = Onlydigits(mode_frame,textvariable= self._var['parameter6'])
        self.multiplicity_entry['font'] =label_design['font']
        self.multiplicity_entry.grid(row=7, column=1, sticky='w', padx=2, pady=2)


    def show_cal_tab(self, parent):
        nw_frame = ttk.Frame(parent, borderwidth=2)
        nw_frame.grid(row=0, column=0, sticky='w')
        
        myFont = font.Font(family='Helvetica', size=10, weight='bold')
       
        self.Frame2_note = tk.Label(nw_frame,text="LITESOPH input for dummyengine      ",fg="blue")
        self.Frame2_note['font'] =  myFont
        self.Frame2_note.grid(row=0, column=0, sticky='w', padx=2, pady=4)
 
        self.nwxc = tk.Label(nw_frame,text="Parameter5",bg=label_design['bg'], fg=label_design['fg'])
        self.nwxc['font'] = label_design['font']
        self.nwxc.grid(row=2, column=0, sticky='w', padx=2, pady=4)

        self.entry_pol_x = ttk.Combobox(nw_frame, textvariable= self._var['parameter3'], value = self.default_para['parameter3']['values'])
        self.entry_pol_x['font'] = label_design['font']
        self.entry_pol_x['state'] = 'readonly'
        self.entry_pol_x.grid(row=2, column=1, sticky='w', padx=2, pady=2)
   
        em_frame = ttk.Frame(nw_frame, borderwidth=2)
        em_frame.grid(row=8, column=0)
        
        title = tk.Label(em_frame,  height=3)
        title.grid(row=0, column=0, sticky= 'NSEW')

        em_frame.grid_columnconfigure(0, weight=1)
        em_frame.grid_rowconfigure(1, weight=1)

    def show_advance_tab(self, parent):
        
        nwchem_conv = ttk.Frame(parent, borderwidth=2)
        nwchem_conv.grid(row=0, column=0, sticky='w')

        myFont = font.Font(family='Helvetica', size=10, weight='bold')
     
        self.label_pol_z = tk.Label(nwchem_conv, text="dummyengine advanced info     ", fg="blue")
        self.label_pol_z['font'] =  label_design['font']
        self.label_pol_z.grid(row=0, column=0, sticky='w', padx=2, pady=4)

        self.label_pol_z = tk.Label(nwchem_conv, text="Parameter6", bg=label_design['bg'], fg=label_design['fg'])
        self.label_pol_z['font'] = label_design['font']
        self.label_pol_z.grid(row=2, column=0, sticky='w', padx=2, pady=4)

        #entry = ttk.Entry(self.Frame1,textvariable= self._var['parameter5'])
        entry = Onlydigits(nwchem_conv,textvariable= self._var['parameter5'])
        entry['font'] = label_design['font']
        entry.grid(row=2, column=1, sticky='w', padx=6, pady=2)

        self.Frame2_note = tk.Label(nwchem_conv,text="Parameter7",bg=label_design['bg'], fg=label_design['fg'])
        self.Frame2_note['font'] = label_design['font']
        self.Frame2_note.grid(row=4, column=0, sticky='w', padx=2, pady=4)

        self.entry_ener = tk.Entry(nwchem_conv, textvariable= self._var['parameter7'])
        #self.entry_ener = Validatedconv(self.Frame1)
        self.entry_ener['font'] = label_design['font']
        self.entry_ener.grid(row=4, column=1, sticky='w', padx=2, pady=2)

        self.label_proj = tk.Label(nwchem_conv,text="Parameter8",bg=label_design['bg'], fg=label_design['fg'])
        self.label_proj['font'] = label_design['font']
        #self.label_proj.place(x=10,y=10)
        self.label_proj.grid(row=6, column=0, sticky='w', padx=2, pady=4)

        self.entry_proj = tk.Entry(nwchem_conv,textvariable= self._var['parameter8'])
        self.entry_proj['font'] = label_design['font']
        self.entry_proj.delete(0,tk.END)
        self.entry_proj.insert(0,"1.0e-4")
        #self.entry_proj.place(x=280,y=10)
        self.entry_proj.grid(row=6, column=1, sticky='w', padx=2, pady=2)

        self.label_proj = tk.Label(nwchem_conv,text="Parameter9",bg=label_design['bg'], fg=label_design['fg'])
        self.label_proj['font'] = label_design['font']
        #self.label_proj.place(x=10,y=10)
        self.label_proj.grid(row=8, column=0, sticky='w', padx=2, pady=4)

        self.entry_grd = tk.Entry(nwchem_conv,textvariable= self._var['parameter9'])
        self.entry_grd['font'] = label_design['font']
        self.entry_grd.delete(0,tk.END)
        self.entry_grd.insert(0,"1.0e-4")
        #self.entry_proj.place(x=280,y=10)
        self.entry_grd.grid(row=8, column=1, sticky='w', padx=2, pady=2)

    def create_input_widgets(self) -> None:
        self.show_system_tab(self.gspage.system_frame)
        self.show_cal_tab(self.gspage.calculation_frame)
        self.show_advance_tab(self.gspage.advanced_info_frame)

    def get_parameters(self) -> dict:
        inp_dict_nw = {
            'dft':{'parameter3': self._var['parameter3'].get(),
                    'convergence':{'parameter7': self._var['parameter7'].get(),
                                    'parameter8' : self._var['parameter8'].get(),
                                    'parameter9':self._var['parameter9'].get()},
                    'mult' : self._var['parameter6'].get(),
                    'iterations' : self._var['parameter5'].get()},
            'parameter2': self._var['parameter2'].get(),
            'parameter4' : self._var['parameter4'].get(),
            'engine':'nwchem'
                    }     
        return inp_dict_nw