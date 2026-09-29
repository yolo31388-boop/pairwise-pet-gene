"""宠物基因与遗传系统"""
import random
from dataclasses import dataclass, field

# 各基因座的等位基因池（大写显性，小写隐性）
LOCUS_ALLELES = {
    "color": ["A", "a"],
    "size": ["B", "b"],
    "strength": ["C", "c"],
}

# 基因锁：等级越高，繁殖时不遗传的概率越大
GENE_LOCK_RATES = {
    "common": 0.0,
    "uncommon": 0.1,
    "rare": 0.25,
    "epic": 0.4,
    "legendary": 0.6,
}

BASE_MUTATION_RATE = 0.001  # 0.1%
INBREEDING_THRESHOLD = 0.25  # 亲缘系数超过此值开始惩罚


@dataclass
class Pet:
    pid: str
    name: str
    genes: dict = field(default_factory=dict)
    purity: float = 1.0


class GeneSystem:
    def __init__(self, seed=42, mutagen: float = 0.0):
        self.seed = seed
        self.rng = random.Random(seed)
        self.mutagen = mutagen  # 诱变剂强度，提升突变率
        self._gen_counter = 0

    def generate_genes(self, pet_type: str) -> dict:
        # fix1: 每个个体在每个基因座随机抽取两个等位基因，保证多样性
        self._gen_counter += 1
        rng = random.Random(f"{self.seed}:{pet_type}:{self._gen_counter}")
        genes = {}
        for locus, alleles in LOCUS_ALLELES.items():
            genes[locus] = rng.choice(alleles) + rng.choice(alleles)
        return genes

    def is_dominant(self, allele: str) -> bool:
        # fix2: 大写为显性，小写为隐性
        return allele.isupper()

    def expressed_allele(self, genotype: str) -> str:
        # 显性等位基因优先表达；隐性只有纯合才表达
        for allele in genotype:
            if self.is_dominant(allele):
                return allele
        return genotype[0]

    def inherit_genes(self, parent1: dict, parent2: dict) -> dict:
        # fix3: 孟德尔分离定律——父母各随机传一个等位基因
        child = {}
        for locus in parent1:
            a1 = self.rng.choice(parent1[locus])
            a2 = self.rng.choice(parent2[locus])
            genotype = a1 + a2
            # fix4: 低概率突变，受诱变剂提升
            if self.rng.random() < self.get_mutation_rate():
                genotype = self._mutate(locus, genotype)
            child[locus] = genotype
        return child

    def _mutate(self, locus: str, genotype: str) -> str:
        alleles = LOCUS_ALLELES.get(locus, ["A", "a"])
        idx = self.rng.randrange(len(genotype))
        new_allele = self.rng.choice(alleles)
        return genotype[:idx] + new_allele + genotype[idx + 1:]

    def get_mutation_rate(self) -> float:
        # fix4: 默认0.1%，诱变剂可提升
        return BASE_MUTATION_RATE * (1.0 + self.mutagen)

    def has_gene_lock(self, gene_rank: str) -> bool:
        # fix5: 高级基因有遗传锁
        return GENE_LOCK_RATES.get(gene_rank, 0.0) > 0.0

    def inherit_locked_gene(self, gene_rank: str) -> bool:
        # 繁殖时按锁定概率判定高级基因是否遗传（越高级越难传）
        return self.rng.random() >= GENE_LOCK_RATES.get(gene_rank, 0.0)

    def calculate_purity(self, genes: dict, breed_standard: dict) -> float:
        # fix6: 按与品种标准的基因相似度计算血统纯度
        if not breed_standard:
            return 1.0
        matches = 0.0
        for locus, standard_allele in breed_standard.items():
            genotype = genes.get(locus, "")
            if not genotype:
                continue
            hit = sum(1 for a in genotype if a == standard_allele)
            matches += hit / len(genotype)
        return matches / len(breed_standard)

    def can_recombine(self, gene1: str, gene2: str) -> bool:
        # fix7: 重组受基因座限制，只有同一基因座才能重组
        return gene1 == gene2

    def get_inbreeding_penalty(self, relation: float) -> dict:
        # fix8: 近亲繁殖惩罚——全属性-10%，并有畸形概率
        if relation >= INBREEDING_THRESHOLD:
            return {"stat_mod": 0.9, "defect_rate": min(relation * 0.2, 0.5)}
        return {"stat_mod": 1.0, "defect_rate": 0.0}
