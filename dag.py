from typing import Iterable, Union, TYPE_CHECKING
from matplotlib import pyplot as plt # lo usa para el plot
from matplotlib import get_backend # lo usa para el plot
from collections import Counter # lo usa para el plot
import numpy as np # lo usa para el plot
import networkx as nx
import asyncio
import concurrent.futures 

plt.style.use('ggplot')
_CONTEXT_MANAGER_DAG = None

if TYPE_CHECKING:
    from job import Job

class DAG:
    """
    Workflow wrapper
    """
    __slots__ = ['graph', 'name', '_old_context_manager_dag', 'env']

    def __init__(self, name: str = 'dag', env: dict = None) -> None:
        """ Constructor for DAG """
        self.graph = nx.DiGraph()
        self.name = name
        if env:
            self.env = env
        else:
            self.env = {}

    @property
    def source(self) -> 'Job':
        return [n for n, d in self.graph.in_degree() if d == 0][0]

    @property
    def sink(self) -> 'Job':
        return [n for n, d in self.graph.out_degree() if d == 0][0]

    def __str__(self) -> str:
        return f'{self.name}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name}, {self.env})'

    def __enter__(self):
        # insipired by airflow's implementation
        # (https://github.com/apache/airflow/blob/1.10.2/airflow/models.py#L3456-L3468)
        # print("3. funcion del Dag __enter__")
        global _CONTEXT_MANAGER_DAG
        self._old_context_manager_dag = _CONTEXT_MANAGER_DAG
        _CONTEXT_MANAGER_DAG = self
        return self

    def __exit__(self, *args, **kwargs):
        global _CONTEXT_MANAGER_DAG
        _CONTEXT_MANAGER_DAG = self._old_context_manager_dag

    def set_children(self, root: 'Job', children: Iterable) -> None:
        self._set_relationship(root, children, forward=True)

    def set_parents(self, root: 'Job', parents: Iterable) -> None:
        self._set_relationship(root, parents, forward=False)

    def _set_relationship(self, root: 'Job', rel: Union[str, Iterable],
                          forward=True) -> None:
        try:
            rel_list = list(rel)
        except TypeError:
            rel_list = [rel]
        for node in rel_list:
            if forward:
                pair = (root, node)
            else:
                pair = (node, root)
            self.graph.add_edge(*pair)

    def run(self) -> None:
        pool = concurrent.futures.ThreadPoolExecutor()
        pool.submit(asyncio.run, self._run(self.sink))

    async def _run(self, node: 'Job'):
        up_jobs = node.upstream_jobs
        if not up_jobs:
            node.submit()
        else:
            up_ids = []
            for up_job in up_jobs:
                if not up_job.id:
                    await self._run(up_job)
                up_ids.append(up_job.id)
            node.submit(up_ids)

    def _find_paths(self):
        start = self.source
        path_dict = {}
        if type(start) == list:
            for node in start:
                levels = nx.single_source_shortest_path_length(self.graph,
                                                               node)
                path_dict.update(levels)
        else:
            path_dict = nx.single_source_shortest_path_length(self.graph,
                                                              start)
        return path_dict
    
    def _create_dag_positions(self):
        levels = self._find_paths()
        level_counts = Counter(levels.values())
        level_decrement = level_counts.copy()
        pos_mapping = dict()
        for k, v in levels.items():
            count = level_counts[v]
            if count == 1:
                pos_mapping[k] = (v, 0)
            else:
                bound = level_counts[v] // 2
                y_min, y_max = -bound, bound
                arr = np.linspace(y_min, y_max, level_counts[v])
                level_decrement[v] -= 1
                cur = level_decrement[v]
                scaled_val = arr[cur]
                pos_mapping[k] = (v, scaled_val)
        return pos_mapping

    def plot(self) -> None:
        plt.figure(figsize=(15, 10))
        pos = self._create_dag_positions()
        node_size = [len(v.name) * 400 for v in self.graph.nodes()]
        nx.draw_networkx(self.graph, pos=pos, node_size=node_size,
                         arrows=True, node_color='cadetblue')
        plt.title(f'DAG representation of {self.name}')
        ax = plt.gca()
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)
        plt.grid(True)
        if get_backend() == 'agg':
            plt.savefig(f'{self.name}_DAG_visualization.png')
        else:
            plt.show()


