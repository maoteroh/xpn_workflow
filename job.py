import random
import subprocess
from dag import DAG
from typing import List
from xpn_generator import XpnGenerator
import os
import subprocess
import shutil

_CONTEXT_MANAGER_DAG = None
  
class Job:

    def __init__(self, name: str, script: str, dag: DAG = None,flush=False) -> None:
        self.name = name
        self.script = script
        self.in_path_local = None
        self.in_path_back_end = None
        self.out_path_local = None
        self.out_path_back_end = None
        self.id = None 
        self.flush = flush
        if not dag and _CONTEXT_MANAGER_DAG:
            dag = _CONTEXT_MANAGER_DAG
        if dag:
            self._dag = dag

    def in_path(self,local,back_end):
        self.in_path_local = local
        self.in_path_back_end =  back_end

    def out_path(self,local,back_end):
        self.out_path_local = local
        self.out_path_back_end = back_end

    @property
    def downstream_jobs(self):
        return set(self._dag.graph.successors(self))

    @property
    def upstream_jobs(self):
        return set(self._dag.graph.predecessors(self))

    def set_downstream(self, downstream) -> None:
        self._dag.set_children(self, downstream)

    def set_upstream(self, upstream) -> None:
        self._dag.set_parents(self, upstream)

    def __lshift__(self, other) -> None:
        self.set_upstream(other)
        return other

    def __rshift__(self, other) -> None:
        self.set_downstream(other)
        return other

    def __rrshift__(self, other) -> None:
        self.__lshift__(other)
        return self 

    def __rlshift__(self, other) -> None:
        self.__rshift__(other)
        return self

    def __str__(self) -> str:
        return f'{self.name}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name}, {self.script}, \
        {self._dag})'

    def submit(self, upstream_ids: List[str] = None) -> str:
        job_id = self.get_job_id()
        self.job_to_slurm()
        self.add_to_main_script(upstream_ids,job_id)
        print(f"Job_id: {job_id}")
        self.id = job_id
        return job_id
    
    def get_job_id(self):
        return f"job_id_{self.name}" 

    def xpn_file_slurm_name(self):
        base_name = os.path.basename(self.script)
        name_without_extension = os.path.splitext(base_name)[0]
        return f"{name_without_extension}_xpn.sh"
    
    def get_file_name(self):
        base_name = os.path.basename(self.script)
        name_without_extension = os.path.splitext(base_name)[0]
        return name_without_extension
    
    def get_extension(self):
        base_name = os.path.basename(self.script)
        return os.path.splitext(base_name)[1]
    
    def compile_c_code(self):
        compiler = None
        if shutil.which("clang"):
            compiler = "clang"
        elif shutil.which("gcc"):
            compiler = "gcc"
        else:
            print("No se encontró un compilador C.")
            return False

        print(f"Compilando {self.script} con {compiler}...")
        compile_command = [compiler, self.script, '-o', self.get_file_name()]
        compilation = subprocess.run(compile_command, capture_output=True, text=True)

        if compilation.returncode == 0:
            print(f"Compilación exitosa: {self.script}")
            return True
        else:
            print("Error en la compilación")
            print("Detalle del error:", compilation.stderr)
            return False
        
    def add_to_main_script(self,upstream_ids,job_id=None):
        """Agrega el comando sbatch al script principal"""
        dag_name = str(self._dag) if self._dag else "workflow"
        script_filename = f"{dag_name}_xpn.sh"
        
        if not os.path.exists(script_filename):
            with open(script_filename, 'w') as script_file:
                script_file.write("#!/bin/bash\n\n")
        
        """ upstrem_ids es una lista de ids de trabajos que son dependientes de este trabajo"""
        if upstream_ids:
            command_str = (
                f"{job_id}=$(sbatch --dependency=afterok:$"
                f"{':$'.join(upstream_ids)} {self.xpn_file_slurm_name()} | awk '{{print $4}}')"
            )
        else:
            command_str = (
                f"{job_id}=$(sbatch {self.xpn_file_slurm_name()} | awk '{{print $4}}')"
            )
        
        with open(script_filename, 'a') as script_file:
            script_file.write(command_str + "\n")
        
        print(f'Sbatch command: {command_str}')

    def job_to_slurm(self):
        """BashScriptCreator es una clase que se encarga de crear el script de bash creator es una 
        instancia de BashScriptCreator creator se usa para crear el scritp slurm que contiene la 
        implementacion de xpn"""
        if self.get_extension() == '.c':
            if self.compile_c_code():
                params = {
                        "path_script": self.script,
                        "in_path_back_end": self.in_path_back_end,
                        "in_path_local": self.in_path_local,
                        "out_path_local":"",
                        "out_path_back_end":"",
                        "file_name": self.get_file_name(),
                        "template_path":"xpn_template_slurm.sh"
                    }
                if self.flush:
                    params["out_path_local"] = self.out_path_local
                    params["out_path_back_end"] = self.out_path_back_end
                    
                print("Params:")
                print(params)
                creator = XpnGenerator(**params)
                creator.create_script(self.xpn_file_slurm_name())