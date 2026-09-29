"""宠物基因与遗传系统

修复点：
1. 基因序列按个体随机生成，同类型宠物存在个体差异
2. 区分显性（大写）/隐性（小写）等位基因，隐性纯合才表达
3. 按孟德尔分离定律遗传，父母各传一个等位基因
4. 基因突变有低概率（默认 0.1%），诱变剂可提升突变率
5. 高级基因带遗传锁，繁殖时可能不遗传，越高级锁越强
6. 按基因与品种标准的相似度计算血统纯度，纯种加成 / 杂种优势
7. 基因重组受基因座限制，只能在同一基因座内重组
8. 近亲繁殖有全属性惩罚与畸形概率
"""
import random
from dataclasses import dataclass, field

# 各基因座可选的等位基因池（大写为显性，小写为隐性）
DEFAULT_ALLELE_POOL = {
    "color": ["A", "a", "B", "b"],
    "size": ["B", "b", "S", "s"],
    "strength": ["C", "c", "D", "d"],
}

# 各类型宠物的特有等位基因池，缺省回退到默认池
TYPE_ALLELE_POOL = {
    "cat": {"color": ["A", "a", "B", "b"],
            "size": ["S", "s", "B", "b"],
            "strength": ["C", "c"]},
    "dog": {"color": ["D", "d", "B", "b"],
            "size": ["B", "b", "S", "s"],
            "strength": ["D", "d", "C", "c"]},
}

# 稀有度 -> 遗传锁强度（繁殖时该基因无法传给后代的概率）
LOCK_CHANCE = {
    "common": 0.0,
    "uncommon": 0.05,
    "rare": 0.15,
    "epic": 0.35,
    "legendary": 0.6,
}

DEFAULT_MUTATION_RATE = 0.001  # 0.1%


@dataclass
class Pet:
    pid: str
    name: str
    genes: dict = field(default_factory=dict)
    purity: float = 1.0


class GeneSystem:
    def __init__(self, seed=None, mutation_rate=DEFAULT_MUTATION_RATE):
        self.rng = random.Random(seed)
        self.mutation_rate = mutation_rate

    # ---- 1. 个体基因随机生成 ----
    def _allele_pool(self, pet_type: str) -> dict:
        return TYPE_ALLELE_POOL.get(pet_type, DEFAULT_ALLELE_POOL)

    def generate_genes(self, pet_type: str) -> dict:
        """为单个个体随机生成二倍体基因型，每个基因座抽两个等位基因。"""
        pool = self._allele_pool(pet_type)
        genes = {}
        for locus, alleles in pool.items():
            genes[locus] = self.rng.choice(alleles) + self.rng.choice(alleles)
        return genes

    # ---- 2. 显性 / 隐性 ----
    def is_dominant(self, allele: str) -> bool:
        return allele[0].isupper()

    def get_phenotype(self, genotype: str) -> str:
        """返回基因型所表达的表型：杂合子只表达显性，隐性纯合才表达隐性。"""
        dominant = [a for a in genotype if self.is_dominant(a)]
        if dominant:
            return dominant[0]
        return genotype[0]

    def is_carrier(self, genotype: str, recessive: str) -> bool:
        """携带者：携带隐性等位基因但不表达（杂合）。"""
        return recessive in genotype and self.get_phenotype(genotype) != recessive

    # ---- 3. 孟德尔分离定律 ----
    def inherit_genes(self, parent1: dict, parent2: dict) -> dict:
        """每个基因座父母各随机传一个等位基因给后代。"""
        child = {}
        for locus in parent1.keys() | parent2.keys():
            g1 = parent1.get(locus)
            g2 = parent2.get(locus)
            a1 = self.rng.choice(g1) if g1 else self.rng.choice(g2)
            a2 = self.rng.choice(g2) if g2 else a1
            child[locus] = a1 + a2
        return child

    # ---- 4. 基因突变 ----
    def get_mutation_rate(self) -> float:
        return self.mutation_rate

    def apply_mutagen(self, multiplier: float) -> float:
        """使用诱变剂提升突变率（倍数提升，上限 100%）。"""
        self.mutation_rate = min(1.0, self.mutation_rate * multiplier)
        return self.mutation_rate

    def mutate_genes(self, genes: dict, pet_type: str = "") -> dict:
        """按突变率逐基因座判定是否突变；突变时随机替换一个等位基因。"""
        pool = self._allele_pool(pet_type) if pet_type else DEFAULT_ALLELE_POOL
        mutated = dict(genes)
        for locus, genotype in list(mutated.items()):
            if self.rng.random() < self.mutation_rate:
                alleles = pool.get(locus, [c for c in genotype])
                variants = [a for a in alleles if a not in genotype] or alleles
                idx = self.rng.randrange(len(genotype))
                chars = list(genotype)
                chars[idx] = self.rng.choice(variants)
                mutated[locus] = "".join(chars)
        return mutated

    # ---- 5. 基因遗传锁 ----
    def has_gene_lock(self, gene_rank: str) -> bool:
        return self.gene_lock_chance(gene_rank) > 0.0

    def gene_lock_chance(self, gene_rank: str) -> float:
        return LOCK_CHANCE.get(gene_rank, 0.0)

    def passes_gene_lock(self, gene_rank: str) -> bool:
        """判定本次繁殖该锁定基因是否成功传给后代（锁越强越难过）。"""
        return self.rng.random() >= self.gene_lock_chance(gene_rank)

    # ---- 6. 血统纯度 ----
    def calculate_purity(self, genes: dict, breed_standard: dict) -> float:
        """逐基因座统计与品种标准等位基因的相似度，取平均。"""
        if not breed_standard:
            return 1.0
        total = 0.0
        for locus, standard_allele in breed_standard.items():
            genotype = genes.get(locus, "")
            if len(genotype) == 0:
                continue
            matches = sum(1 for a in genotype if a == standard_allele)
            total += matches / len(genotype)
        return total / len(breed_standard)

    def get_breed_stat_modifier(self, purity: float) -> float:
        """纯种有最高 +20% 加成；中间纯度有杂种优势，上限 +10%。"""
        if purity >= 0.8:
            return 1.0 + 0.2 * ((purity - 0.8) / 0.2)
        if purity >= 0.4:
            # 纯度 0.5 附近杂种优势最大，向两侧衰减
            return 1.0 + 0.1 * (1.0 - abs(purity - 0.5) / 0.5)
        return 1.0

    # ---- 7. 基因重组受基因座限制 ----
    @staticmethod
    def _locus_of(gene: str) -> str:
        for sep in (":", "_"):
            if sep in gene:
                return gene.split(sep, 1)[0]
        return gene

    def can_recombine(self, gene1: str, gene2: str) -> bool:
        """只有位于同一基因座的基因才能重组，不能跨基因座组合。"""
        return self._locus_of(gene1) == self._locus_of(gene2)

    def recombine(self, gene1: str, gene2: str):
        if not self.can_recombine(gene1, gene2):
            return None
        return gene1 + "+" + gene2

    # ---- 8. 近亲繁殖惩罚 ----
    def get_inbreeding_penalty(self, relation: float) -> dict:
        """亲缘系数越高，全属性惩罚越大，畸形概率越高。

        兄妹（relation=0.5）：全属性 -10%，畸形率 25%。
        """
        relation = max(0.0, min(1.0, relation))
        return {
            "stat_mod": max(0.0, 1.0 - 0.2 * relation),
            "defect_rate": 0.5 * relation,
        }

    def roll_birth_defect(self, relation: float) -> bool:
        penalty = self.get_inbreeding_penalty(relation)
        return self.rng.random() < penalty["defect_rate"]

    # ---- 繁殖总流程 ----
    def breed(self, parent1: dict, parent2: dict, pet_type: str = "",
              breed_standard: dict = None, gene_ranks: dict = None,
              relation: float = 0.0) -> dict:
        """完整繁殖流程：遗传锁过滤 -> 孟德尔遗传 -> 突变 -> 纯度/近亲判定。"""
        ranks = gene_ranks or {}
        locked_loci = [locus for locus in ranks
                       if not self.passes_gene_lock(ranks[locus])]

        available1 = {k: v for k, v in parent1.items() if k not in locked_loci}
        available2 = {k: v for k, v in parent2.items() if k not in locked_loci}

        child_genes = self.inherit_genes(available1, available2)
        child_genes = self.mutate_genes(child_genes, pet_type)

        standard = breed_standard or {}
        purity = self.calculate_purity(child_genes, standard)
        penalty = self.get_inbreeding_penalty(relation)
        defect = self.roll_birth_defect(relation) if relation > 0 else False

        return {
            "genes": child_genes,
            "purity": purity,
            "locked_loci": locked_loci,
            "stat_mod": self.get_breed_stat_modifier(purity) * penalty["stat_mod"],
            "defect": defect,
            "defect_rate": penalty["defect_rate"],
        }
