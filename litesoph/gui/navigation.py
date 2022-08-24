from pathlib import Path
import tkinter as tk
import tkinter.ttk as ttk
import collections
from tkinter import *
import os
import ctypes
import pathlib

class ProjectList:

    def __init__(self, app):
        
        self.treedata = dict()
        self.current_path_list = []
        self.treeview = app.treeview
        
        self.treeview.bind('<<TreeviewOpen>>', self.open_node)
        self.treeview.bind("<Double-1>", self.OnDoubleClick)
        # self.treeview.bind("<Button-1>", self.OnSingleClick)


    def pathChange(self, project_path: Path):
        # Get all Files and Folders from the given Directory

        currentPath = StringVar(self, name='currentPath',value=pathlib.Path.cwd())

        directory = os.listdir(currentPath.get())
        # Clearing the list
        list.delete(0, END)
        # Inserting the files and directories into the list
        for file in directory:
            list.insert(0, file)
        
    def populate(self, project_path: Path):
        
        paths = [path for path in project_path.glob('**/*')]
        if not compare_list(paths, self.current_path_list):    
            rot = self.treeview.get_children()
            if rot:
                self.treeview.delete(rot)

            self.current_path_list = paths
            self.insert_node('', project_path.name, project_path)
        else:
            return

    def insert_node(self, parent, text, abspath):
        node = self.treeview.insert(parent, 'end', text=text, open=False)
        if Path.is_dir(abspath):
            self.treedata[node] = abspath
            self.treeview.insert(node, 'end')

    def open_node(self, event):
        node = self.treeview.focus()
        abspath = self.treedata.pop(node, None)
        if abspath:
            self.treeview.delete(self.treeview.get_children(node))
            for p in Path.iterdir(abspath):
                self.insert_node(node, p.name, Path.joinpath(abspath, p))
    def OnDoubleClick(self, event):
        item = self.treeview.selection()[0]
        print("you clicked on", self.treeview.item(item,"text"))

    # def OnSingleClick(self, event):
    #     item = self.treeview.selection()
    #     print("you clicked on", self.treeview.item(item,"text"))

def compare_list(list1,list2):
        if(collections.Counter(list1)==collections.Counter(list2)):
            return True
        else:
            return False

def summary_of_current_project(status):

    state = ["Summary of all the tasks performed."]

    s_dict = status.status_dict

    engine_list = s_dict.keys()
    if engine_list:
        state.append(" ")
        for engine in engine_list:
            state.append(f"Engine: {engine}")

            task_list = s_dict[engine].keys()

            if task_list:
                for i, task in  enumerate(task_list):
                    if s_dict[engine][task]['done'] == True:
                        state.append(f"     {task}")
                    
                
                state.append(" ")
    else:
        state.append("No tasks have been performed yet.")

    state = "\n".join(state)

    return state


