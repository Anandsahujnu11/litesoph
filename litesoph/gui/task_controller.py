import tkinter as tk
from tkinter import messagebox
from litesoph.gui.user_data import get_remote_profile, update_proj_list, update_remote_profile_list
import copy
from litesoph.common.workflow_manager import WorkflowManager, TaskSetupError
from litesoph.common.data_sturcture.data_classes import TaskInfo
from litesoph.common.task import Task, TaskFailed, InputError
from litesoph.common.task_data import TaskTypes as tt                                  
from litesoph.gui import views as v
from litesoph.common import models as m
from litesoph.gui.models.gs_model import choose_engine
from litesoph.common.decision_tree import EngineDecisionError
from litesoph.gui.utils import dict2string


class TaskController:

    def __init__(self, workflow_controller, app) -> None:
        self.app = app
        self.workflow_controller = workflow_controller
        self.main_window = app.main_window
        self.view_panel = app.view_panel
        self.status_engine = app.status_engine
        self.task_info = None
        self.task_view = None
        self.job_sub_page = None
        
    def set_task(self, workflow_manager: WorkflowManager, task_view: tk.Frame):
        self.workflow_manager = workflow_manager
        self.task_info = workflow_manager.current_task_info
        self.task_name = self.task_info.name
        self.engine = self.task_info.engine
        self.task_view = task_view
        self.task = None

        self.job_sub_page = v.JobSubPage(self.app.task_input_frame)
        self.job_sub_page.grid(row=0, column=0, sticky ="nsew")

        self.task_view = self.app.show_frame(task_view, self.task_info.engine, self.task_info.name)
        self.job_sub_page.back2task.config(command= self.show_task_view)

        self.main_window.bind_all(f'<<Generate{self.task_name}Script>>', self.generate_input)
        
        self.task_view.set_sub_button_state('disable') 

        if hasattr(self.task_view, 'set_parameters'):
            self.task_view.set_parameters(copy.deepcopy(self.task_info.param))

    # def create_task_view(self, view_class, *args, **kwargs):
    #     self.task_view = view_class(self.app.task_input_frame, *args, **kwargs)
    #     self.task_view.grid(row=0, column=0, sticky ='NSEW')
    #     self.task_view.tkraise()
    
    def update_wf_view_defaults(self, get_default_func=None):
        """ Checks task mode bool.
        If task mode: passes the engine updated task defaults.
        If workflow mode: updates the engine updated task defaults in context of workflow"""

        default_param = copy.deepcopy(self.task_info.param)
        if not self.workflow_manager.workflow_info.task_mode: 
            if get_default_func is not None:
                default_param.update(get_default_func())
        return default_param

    def show_task_view(self):
        self.task_view.tkraise()

    def generate_input(self, *_):
        
        self.task_info.param.clear()
        inp_dict = self.task_view.get_parameters()
        if not inp_dict:
            return

        if tt.GROUND_STATE == self.task_name:
            engine = choose_engine(copy.deepcopy(inp_dict))   
            if engine is None:
                return
            try:
                self.workflow_manager.set_engine(engine)
            except EngineDecisionError as e:
                messagebox.showerror(title="Engine Error", message=e)
                return

        #---------------------------------------------------------------
        self.task_info.param.clear()
        self.task_info.param.update(inp_dict)
        try:
            self.task = self.workflow_manager.get_engine_task()
        except InputError as error_msg:
            messagebox.showerror(message= error_msg)            
            return

        check = messagebox.askokcancel(title='Input parameters selected', message= dict2string(inp_dict))
        if not check:
            return
        
        self.task.create_input()
        txt = self.task.get_engine_input()
        self.view_panel.insert_text(text=txt, state='normal')
        self.bind_task_events()

        # check = messagebox.askokcancel(title='Input parameters selected', message= dict2string(inp_dict))
        # if not check:
        #     return
        
        # self.task_info.param.update(inp_dict)
        # self.task = self.workflow_manager.get_engine_task()
        # self.task.create_input()
        # txt = self.task.get_engine_input()
        # self.view_panel.insert_text(text=txt, state='normal')
        # self.bind_task_events()
    

    @staticmethod
    def _check_task_run_condition(task, network=False) -> bool:
        
        try:
           task.check_prerequisite(network)           
        except FileNotFoundError as e:
            return False
        else:
            return True
            
    def view_input_file(self, task:Task):
        self.view_panel.insert_text(task.template)
    
    def bind_task_events(self):
        self.main_window.bind_all(f'<<Save{self.task_name}Script>>', lambda _ : self._on_save_button(self.task, self.task_view))
        self.main_window.bind_all(f'<<SubLocal{self.task_name}>>', self._on_run_local_button)
        self.main_window.bind_all(f'<<SubNetwork{self.task_name}>>', self._on_run_network_button)
    
    def _on_save_button(self, task:Task, view, *_):
        template = self.view_panel.get_text()
        task.set_engine_input(template)
        task.save_input()
        if task.task_name == tt.GROUND_STATE:
            self.status_engine.set(self.engine)
            #TODO: disable/freeze the inputs
            #self.task_view.inp.freeze_widgets(state='disabled')
        view.set_sub_button_state('active')
        view.set_label_msg('saved')
    
    def _on_clear_button(self):
        pass

    def _on_run_network_button(self, *_):

        if not self._check_task_run_condition(self.task):
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
            return

        self.job_sub_page.back2main.config(command= self.workflow_controller.show_workmanager_page)
        self.job_sub_page.view_output_button.config(command= self._on_out_remote_view_button)
        self.job_sub_page.show_run_network(self._on_create_remote_job_script,
                                            self._on_save_job_script,
                                            self._run_network)

        self.job_sub_page.runtime_query_remote(self._on_check_job_status_remote,
                                               self._on_check_file_status_remote,
                                               self._on_kill_job_remote,
                                               self._on_download_all_files,
                                               self._on_download_specific_file,
                                               self._on_view_specific_file_remote,
                                               self._on_plot_file_remote)
                        
        remote = get_remote_profile()
        if remote:
            self.job_sub_page.set_network_profile(remote)
        self.job_sub_page.set_run_button_state('disable')
        self.job_sub_page.tkraise()

    def _on_run_local_button(self, *_):

        if not self._check_task_run_condition(self.task):
            messagebox.showerror(message="Input not saved. Please save the input before job submission")
            return
       
        self.job_sub_page.back2main.config(command= self.workflow_controller.show_workmanager_page)
        self.job_sub_page.view_output_button.config(command= self._on_out_local_view_button)        
        self.job_sub_page.show_run_local(self._on_create_local_job_script,
                                        self._on_save_job_script,
                                        self._run_local)
        
        self.job_sub_page.runtime_query_local(self._on_check_job_status_local,
                                        self._on_check_file_status_local,
                                        self._on_view_specific_file_local,
                                        self._on_plot_file_local)

        self.job_sub_page.set_run_button_state('disable')        
        self.job_sub_page.tkraise()

    def _on_check_file_status_local(self):
        try:
            error,msg=self.task.submit_local.get_fileinfo_local()                
        except TaskFailed:
            messagebox.showinfo(title='Info', message=error)
            return            
        # self.view_panel.insert_text(msg, 'disabled')
        self.task.submit_local.generate_list_of_files_local()
        
        choose_file= self.job_sub_page.combobox
        list_of_files=self.task.submit_local.get_list_of_files_local()
        self.dict_of_files_combobox=self.encode_decode_combobox_items(list_of_files)        
        list_of_files=list(self.dict_of_files_combobox.keys())

        choose_file['values'] = list_of_files
        choose_file.current()
        self.combobox_selected_file=choose_file.bind("<<ComboboxSelected>>",self.selection_changed)        
        self.job_sub_page.plot_file_button.config(state='active')
        self.job_sub_page.download_specific_file_button.config(state='active')
    
    def _on_view_specific_file_local(self):        
        try:
            error, message=self.task.submit_local.view_specific_file_local(self.selected_file)  
        except UnicodeDecodeError:
            messagebox.showinfo(title='Info', message="Unable to Read File")                    
            self.view_panel.insert_text(message, 'disabled')
        except AttributeError:
            messagebox.showinfo(title='Info', message="First Select the File") 
        self.view_panel.insert_text(message, 'disabled')

    def _on_plot_file_local(self):   
        from litesoph.visualization import ls_viz_app

        ls_viz_app.LSVizApp(self.main_window).run()

        
        
        # import os        
        # try:
        #     if os.path.exists(self.selected_file)==True:
        #         cmd=f'xmgrace {self.selected_file}'
        #         # cmd=f'"/home/anandsahu/softwares/visit_visualization/bin/visit" {file}'
        #         os.system(cmd)
        #     else:
        #         messagebox.showinfo(title='Info', message="File not found")
        # except ValueError:
        #     messagebox.showinfo(title='Info', message="Cannot plot selected File")   
        # except FileNotFoundError:
        #     messagebox.showinfo(title='Info', message="File not found")  
        # except AttributeError:
        #     messagebox.showinfo(title='Info', message="First Select the File")                    
            
    def _on_check_job_status_local(self):        
        if self.job_sub_page.submit_thread.is_alive(): 
            messagebox.showinfo(title='Info', message="Job is Running")
        else:
            messagebox.showinfo(title='Info', message="No Job Found")

    def selection_changed(self,event):
        selected_file = self.job_sub_page.combobox.get()
        self.selected_file=self.dict_of_files_combobox[selected_file]
        messagebox.showinfo(
        title="New Selection",
        message=f"Selected option: {self.selected_file}")
        
    def encode_decode_combobox_items(self,list_of_files):
        import pathlib
        from litesoph.common.lfm_database import coordinate_files,dipole_files,spectrum_files,script_output_files

        mapped_dict={}

        i = 0
        coordinate_count=0
        dipole_count=0
        spectrum_file_count=0
        script_output_count=0

        while i < len(list_of_files):
            
            file_path=pathlib.Path(list_of_files[i]).parent
            last_folder_name=pathlib.Path(list_of_files[i]).parent.name
            file_name=pathlib.Path(list_of_files[i]).name
            file_ext=pathlib.Path(list_of_files[i]).suffix
            
            if  file_ext in coordinate_files:                
                coordinate_file=f'coordinate_file_{coordinate_count+1}'
                mapped_dict[coordinate_file] = list_of_files[i]
                list_of_files[i] = coordinate_file            
                coordinate_count+=1    
        
            if  file_name in dipole_files:
                dipole_file=f'dipole-file-{dipole_count+1}'
                mapped_dict[dipole_file] = list_of_files[i]
                list_of_files[i] = dipole_files            
                dipole_count+=1    
            
            if  file_name in spectrum_files:
                spectrum_file=f'spectrum-file-{spectrum_file_count+1}'
                mapped_dict[spectrum_file] = list_of_files[i]
                list_of_files[i] = spectrum_files            
                spectrum_file_count+=1    
            
            if  file_name in script_output_files:
                file=f'script-output-{script_output_count+1}'
                mapped_dict[file] = list_of_files[i]
                list_of_files[i] = script_output_files            
                script_output_count+=1    
                                    
            i += 1
        return mapped_dict
            
    def _on_check_file_status_remote(self):    

        try:
            error, msg=self.task.submit_network.get_fileinfo_remote()            
        except TaskFailed:
            messagebox.showinfo(title='Info', message=error)            
        # self.view_panel.insert_text(msg, 'disabled')
        
        choose_file= self.job_sub_page.combobox
        list_of_files=self.task.submit_network.get_list_of_files_remote()
        self.dict_of_files_combobox=self.encode_decode_combobox_items(list_of_files)        
        list_of_files=list(self.dict_of_files_combobox.keys())
        
        choose_file['values'] =  list_of_files
        choose_file.current()
        self.combobox_selected_file=choose_file.bind("<<ComboboxSelected>>",self.selection_changed)
        
        self.job_sub_page.download_specific_file_button.config(state='active')
        self.job_sub_page.view_file_button.config(state='active')
        self.job_sub_page.plot_file_button.config(state='active')
        messagebox.showinfo(title='Info', message=f'Project Size: {self.task.submit_network.project_size_GB:.2f} GB')

    def _on_check_job_status_remote(self):
        try:
            job_status=self.task.submit_network.get_job_status_remote()    
            messagebox.showinfo(title='Info', message=job_status)   
        except TaskFailed:
            messagebox.showinfo(title='Info', message='error')   
        
    def _on_kill_job_remote(self):
    
        job_id=self.job_sub_page.job_id.get()            
        scheduler=self.job_sub_page.sub_command.get()
        scheduler_stat_cmd=self.job_sub_page.sub_stat_command.get()
        scheduler_kill_cmd=self.job_sub_page.sub_kill_command.get()

        if job_id == None:
            messagebox.showinfo(title='Info', message="Enter Job ID first")                  
        else:
            try:
                error, message=self.task.submit_network.kill_job_remote(job_id,scheduler,scheduler_stat_cmd,scheduler_kill_cmd)                
            except TaskFailed:
                messagebox.showinfo(title='Info', message=error)                    
            messagebox.showinfo(title='Info', message=message)   
            self.job_sub_page.progressbar.stop()
            label_progressbar = tk.Label(self.job_sub_page.Frame1, text="Job Killed ",font=('Helvetica', 14, 'bold'), bg='gray', fg='black')
            label_progressbar.grid(row=4, column=0,sticky='nsew')

    def _on_download_all_files(self):
        try:
            error, message=self.task.submit_network.download_all_files_remote()                
        except TaskFailed:
            messagebox.showinfo(title='Info', message=error)                    
        return (error, message)
    
    def _on_download_specific_file(self):        
        try:
            priority1_files_dict={self.selected_file: {'file_relevance': 'very_impt', 'file_lifetime': '', 'transfer_method': {'method': 'direct_transfer', 'compress_method': 'zstd', 'split_size': ''}}}        
            error, message=self.task.submit_network.download_specific_file_remote(self.selected_file,priority1_files_dict)                
        except TaskFailed:
            messagebox.showinfo(title='Info', message=error)                    
        except AttributeError:
            messagebox.showinfo(title='Info', message="First Select the file")
        messagebox.showinfo(title='Info', message=message)   

    def _on_view_specific_file_remote(self):        
        try:
            error, message=self.task.submit_network.view_specific_file_remote(self.selected_file)  
        except UnicodeDecodeError:
            messagebox.showinfo(title='Info', message="Unable to Read File")                    
            self.view_panel.insert_text(message, 'disabled')
        except AttributeError:
            messagebox.showinfo(title='Info', message="First Select the File") 
        self.view_panel.insert_text(message, 'disabled')

    def _on_plot_file_remote(self):
        import os        
        try:
            file = str(self.selected_file).replace( str(self.task.submit_network.remote_path), str(self.task.submit_network.project_dir))
            if os.path.exists(file)==True:
                cmd=f'xmgrace {file}'
                # cmd=f'"/home/anandsahu/softwares/visit_visualization/bin/visit" {file}'
                os.system(cmd)
            else:
                messagebox.showinfo(title='Info', message="First download the file")
        except ValueError:
            messagebox.showinfo(title='Info', message="Cannot plot selected File")   
        except FileNotFoundError:
            messagebox.showinfo(title='Info', message="File not found")  
        except AttributeError:
            messagebox.showinfo(title='Info', message="First Select the File")                    
            
    def _on_plot_button(self, *_):
        
        param = {}
        try:
            get_param_func = getattr(self.task_view, 'get_plot_parameters')
        except AttributeError:
            pass
        else:
            param = get_param_func()
        
        try:
            self.task.plot(**param)
        except Exception as e:
            messagebox.showerror(title='Error', message="Error occured during plotting", detail= e)

    def _run_local(self, np=None):

        if np:
            sub_job_type = 0
            cmd = 'bash'
        else:
            np = self.job_sub_page.get_processors()
            sub_job_type = self.job_sub_page.sub_job_type.get()
            cmd = self.job_sub_page.sub_command.get()

        if sub_job_type == 1:
            
            if not cmd:
                messagebox.showerror(title="Error", message=" Please provide submit command for queue submission")
                self.job_sub_page.set_run_button_state('active')
                return
        else:
           if cmd != 'bash':
                messagebox.showerror(title="Error", message=" Only bash is used for command line execution")
                self.job_sub_page.set_run_button_state('active')
                return

        self.task.set_submit_local(np)
        
        try:
            self.task.run_job_local(cmd)
        except FileNotFoundError as e:
            messagebox.showerror(title='yes',message=e)
            return
        except Exception as e:
            messagebox.showerror(title = "Error",message=f'There was an error when trying to run the job', detail = f'{e}')
            return
        else:
            if self.task.task_info.local['returncode'] != 0:
                messagebox.showerror(title = "Error",message=f"Job exited with non-zero return code.", detail = f" Error: {self.task.task_info.local['error']}")
            else:
                try:
                    self.job_sub_page.check_jobdone_progressbar()
                except:
                    AttributeError
                messagebox.showinfo(title= "Well done!", message='Job completed successfully!')
                
    def _on_out_local_view_button(self, *_):

        try:
            log_txt = self.task.get_engine_log()
        except TaskFailed:
            messagebox.showinfo(title='Info', message="Job not completed.")
            return
            
        self.view_panel.insert_text(log_txt, 'disabled')

    def _run_network(self):

        try:
            self.task.check_prerequisite()
        except FileNotFoundError as e:
            messagebox.showerror(title = "Error", message = e)
            self.job_sub_page.set_run_button_state('active')
            return

        sub_job_type = self.job_sub_page.sub_job_type.get()

        cmd = self.job_sub_page.sub_command.get()
        if sub_job_type == 1:
            
            if not cmd:
                messagebox.showerror(title="Error", message=" Please provide submit command for queue submission")
                self.job_sub_page.set_run_button_state('active')
                return
        else:
           if cmd != 'bash':
                messagebox.showerror(title="Error", message=" Only bash is used for command line execution")
                self.job_sub_page.set_run_button_state('active')
                return
        
        login_dict = self.job_sub_page.get_network_dict()
        update_remote_profile_list(login_dict)
        
        try:
            self.task.connect_to_network(hostname=login_dict['ip'],
                                    username=login_dict['username'],
                                    password=login_dict['password'],
                                    pkey_file=login_dict['pkey_file'],
                                    port=login_dict['port'],
                                    remote_path=login_dict['remote_path'],
                                    passwordless_ssh=login_dict['passwordless_ssh'])
        except Exception as e:
            messagebox.showerror(title = "Error", message = 'Unable to connect to the network', detail= e)
            self.job_sub_page.set_run_button_state('active')
            return
        try:
            self.task.submit_network.run_job(cmd)
        except Exception as e:
            messagebox.showerror(title = "Error",message=f'There was an error when trying to run the job', detail = f'{e}')
            self.job_sub_page.set_run_button_state('active')
            return
        else:
            if self.task.task_info.network['sub_returncode'] != 0:
                messagebox.showerror(title = "Error",message=f"Error occured during job submission.", detail = f" Error: {self.task.task_info.network['error']}")
            else:
                try:
                    self.job_sub_page.check_jobdone_progressbar()
                except:
                    AttributeError
                output=self.task.task_info.network['output']
                self.view_panel.insert_text(output, 'disabled')
                messagebox.showinfo(title= "Well done!", message='Job Completed successfully!', detail = f"output:{self.task.task_info.network['output']}")
            
    def _get_remote_output(self):
        self.task.submit_network.download_output_files()

    def _on_create_local_job_script(self, *_):
        np = self.job_sub_page.processors.get()
        b_file =  self.task.create_job_script(np)
        self.view_panel.insert_text(b_file, 'normal')

    def _on_create_remote_job_script(self, *_):
        np = self.job_sub_page.processors.get()
        rpath = self.job_sub_page.rpath.get()
        if rpath:
            b_file = self.task.create_job_script(np, remote_path=rpath)
        else:
            messagebox.showerror(title="Error", message="Please enter remote path")
            return
        self.view_panel.insert_text(b_file, 'normal')
       
    def _on_save_job_script(self, *_):
        self.job_sub_page.set_run_button_state('active')
        txt = self.view_panel.get_text()
        self.task.write_job_script(txt)
        self.task_info.state.job_script = True

    def _on_out_remote_view_button(self, *_):
        
        check =  self.task.task_info.network.get('sub_returncode', None)
        if check is None:
            messagebox.showinfo(title= "Warning", message="The job is not submitted yet.")
            return

        if check != 0:
            messagebox.showinfo(title= "Warning", message="Error occured during job submission.", detail = f"output:{self.task.task_info.network['output']}")
            return

        print("Checking for job completion..")
        if self.task.submit_network.check_job_status():

            print('job Done.')
            self._get_remote_output()   
            log_txt = self.task.get_engine_log()
            self.view_panel.insert_text(log_txt, 'disabled')
            self.task_info.state.calculation = True
            self.task_info.network.update({'data_downloaded': True})
        else:
            get = messagebox.askyesno(title='Info', message="Job not commpleted.", detail= "Do you what to download engine log file?")

            if get:
                self.task.submit_network.get_output_log()
                log_txt = self.task.get_engine_log()
                self.view_panel.insert_text(log_txt, 'disabled')
            else:
                return

class PostProcessTaskController(TaskController):

    def set_task(self, workflow_manager: WorkflowManager, task_view: tk.Frame):
        self.workflow_manager = workflow_manager
        self.task_info = workflow_manager.current_task_info
        self.task_name = self.task_info.name
        self.engine = self.task_info.engine
        self.task_view = task_view
        self.task = None

        self.task_view = self.app.show_frame(task_view, self.task_info.engine, self.task_info.name)        
        self.task_view.submit_button.config(command = self._run_task_serial)
        self.task_view.plot_button.config(command = self._on_plot_button)
        self.task_view.back_button.config(command= self.workflow_controller.show_workmanager_page)
           
        if hasattr(self.task_view, 'set_parameters'):
            self.task_view.set_parameters(copy.deepcopy(self.task_info.param))

    def _run_task_serial(self, *_):
        
        inp_dict = self.task_view.get_parameters()
        self.task_info.param.update(inp_dict)
        self.task = self.workflow_manager.get_engine_task()
        self.task.prepare_input()
        self.task_info.state.input = 'done'
        self.task_info.engine_param.update(self.task.user_input)
        self._run_local(np=1)



