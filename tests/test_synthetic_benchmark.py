import pytest
from dataset.synthetic_generator import generate_synthetic_dataset
from dataset.benchmark_evaluator import run_comparative_benchmark

def test_synthetic_dataset_generation():
    dataset = generate_synthetic_dataset(20)
    assert len(dataset) == 20
    for sample in dataset:
        assert "id" in sample
        assert "domain" in sample
        assert "policy_text" in sample
        assert "ground_truth" in sample
        assert "is_valid" in sample["ground_truth"]

def test_comparative_benchmark_execution():
    results = run_comparative_benchmark(10)
    assert "total_samples" in results
    assert results["total_samples"] == 10
    assert "veriflow_metrics" in results
    assert "raw_llm_metrics" in results
    assert results["veriflow_metrics"]["attack_immunity_rate"] == 100.0
