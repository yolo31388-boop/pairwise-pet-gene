"""宠物基因与遗传系统 - 含8个bug"""
import random
from dataclasses import dataclass, field

@dataclass
class Pet:
    pid: str
    name: str
    genes: dict = field(default_factory=dict)  # bug1: 固定
    purity: float = 1.0  # bug6: 不计算

class GeneSystem:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)

    def generate_genes(self, pet_type: str) -> dict:
        # bug1: 固定基因
        return {"color": "A", "size": "B", "strength": "C"}

    def is_dominant(self, allele: str) -> bool:
        # bug2: 都表达
        return True

    def inherit_genes(self, parent1: dict, parent2: dict) -> dict:
        # bug3: 随机遗传
        result = {}
        for k in parent1:
            result[k] = self.rng.choice([parent1[k], parent2[k]])
        return result

    def get_mutation_rate(self) -> float:
        # bug4: 无控制
        return 0.0

    def has_gene_lock(self, gene_rank: str) -> bool:
        # bug5: 无基因锁
        return False

    def calculate_purity(self, genes: dict, breed_standard: dict) -> float:
        # bug6: 不计算
        return 1.0

    def can_recombine(self, gene1: str, gene2: str) -> bool:
        # bug7: 任意组合
        return True

    def get_inbreeding_penalty(self, relation: float) -> dict:
        # bug8: 无惩罚
        return {"stat_mod": 1.0, "defect_rate": 0.0}
