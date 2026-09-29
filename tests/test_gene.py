"""宠物基因与遗传系统 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pet.gene import GeneSystem, Pet

class TestGeneVariance:
    def test_same_type_pets_have_different_genes(self):
        gs = GeneSystem(seed=42)
        g1 = gs.generate_genes("cat")
        g2 = gs.generate_genes("cat")
        assert g1 != g2

class TestDominantRecessive:
    def test_recessive_allele_not_expressed_in_heterozygote(self):
        gs = GeneSystem()
        assert gs.is_dominant("a") == False
        assert gs.is_dominant("A") == True

class TestMendelianInheritance:
    def test_parents_pass_one_allele_each(self):
        gs = GeneSystem(seed=1)
        p1 = {"color": "AA"}
        p2 = {"color": "aa"}
        child = gs.inherit_genes(p1, p2)
        # 应该是Aa（一个来自父一个来自母）
        assert "A" in child["color"] and "a" in child["color"]

class TestMutationRate:
    def test_mutation_rate_is_positive_but_low(self):
        gs = GeneSystem()
        rate = gs.get_mutation_rate()
        assert 0 < rate < 0.1

class TestGeneLock:
    def test_legendary_gene_has_lock(self):
        gs = GeneSystem()
        assert gs.has_gene_lock("legendary") == True
        assert gs.has_gene_lock("common") == False

class TestPurityCalculation:
    def test_crossbreed_has_lower_purity(self):
        gs = GeneSystem()
        standard = {"color": "A", "size": "B"}
        pure = {"color": "AA", "size": "BB"}
        cross = {"color": "Aa", "size": "Bb"}
        p1 = gs.calculate_purity(pure, standard)
        p2 = gs.calculate_purity(cross, standard)
        assert p1 > p2

class TestRecombinationRestriction:
    def test_cannot_recombine_unlinked_genes(self):
        gs = GeneSystem()
        assert gs.can_recombine("color", "size") == False

class TestInbreedingPenalty:
    def test_close_relative_has_penalty(self):
        gs = GeneSystem()
        result = gs.get_inbreeding_penalty(0.5)  # 兄妹
        assert result["stat_mod"] < 1.0
        assert result["defect_rate"] > 0
