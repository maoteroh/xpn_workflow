from job import Job
from dag import DAG

env = {} 

with DAG('simple_xpn_slurm_workflow', env=env) as d:
    
    #Trabajo #1
    #El primer paramentro es el nombre del trabajo
    #El segundo parametro es la ruta del script que será lanzado en el cluster
    j1 = Job('Task1', 'validar_pgms.c', dag=d,flush=False)
    #hacerlo con directorios
    j1.in_path("demo1.txt","/tmp/expand/xpn/demo1.txt")
    #hacerlo con direcorios
    j1.out_path("demo1_out.txt","/tmp/expand/xpn/demo1_out.txt") 

    #Trabajo #2
    j2 = Job('Task2', 'validar_ppms.c', dag=d,flush=False)
    j2.in_path("demo2.txt","/tmp/expand/xpn/demo2.txt")
    j2.out_path("demo2_out.txt","/tmp/expand/xpn/demo2_out.txt")

    #Trabajo #3
    j3 = Job('Task3', 'c_task_wf_3.c', dag=d,flush=True)
    j3.in_path("demo3.txt","/tmp/expand/xpn/demo3.txt")
    j3.out_path("demo3_out.txt","/tmp/expand/xpn/demo3_out.txt")

#Flujo de trabajo donde j3 es dependiente de j1 y j2
[j1, j2] >> j3
d.run()
