import pathlib

ground_state = {'inp':'orca/GS/gs.inp',
            'out_log' : 'orca/GS/gs.out',
            'req' : ['coordinate.xyz', 'orca/restart'],
            'check_list':['Converged', 'Fermi level:','Total:']}


restart = 'orca/restart'

task_dirs =[
        ('orcaGroundState', 'GS')]
