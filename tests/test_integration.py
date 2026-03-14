import pytest
import shutil
from pathlib import Path

# Adjust imports since compare_runs is in tests/
from compare_runs import evaluate_tolerances
from atc138.driver import run_analysis

# Discover fixtures dynamically
def get_model_fixtures():
    fixtures_dir = Path(__file__).parent / "fixtures" / "matlab_comparison"
    models = []
    
    if not fixtures_dir.exists():
        return models
        
    for model_dir in fixtures_dir.iterdir():
        if model_dir.is_dir() and model_dir.name != "__pycache__":
            models.append((model_dir.name, model_dir))
    return models

@pytest.mark.parametrize("model_name, model_dir", get_model_fixtures())
def test_matlab_python_comparison(model_name, model_dir, tmp_path):
    # Ensure corresponding example directory exists
    repo_root = Path(__file__).parent.parent
    example_dir = repo_root / "examples" / model_name
    
    if not example_dir.is_dir():
        raise FileNotFoundError(f"Example directory for {model_name} not found at {example_dir}")
        
    matlab_dir = model_dir / "output_MATLAB"
    
    # Run the Python implementation on the fly
    run_analysis(str(example_dir), str(tmp_path))
    
    # Compare generated Python outputs against the MATLAB fixtures
    results = evaluate_tolerances(str(matlab_dir), str(tmp_path))
        
    hl = results["high_level"]
    
    # High-level tests
    for metric_key, label in [("reoc", "Reoccupancy"), ("func", "Functional"), ("full", "Full repair")]:
        if metric_key in hl:
            m = hl[metric_key]
            assert m["pass"], (
                f"High-level metric '{label}' failed tolerance check for {model_name}. "
                f"Py Mean: {m['mean']:.1f}, Mat Mean: {m['mat_mean']:.1f}, Diff: {m['pct_diff']:.3f}%"
            )

    # TODO: Add assertions for Pointwise metrics here using results["pointwise"] 
    #       when specified by user
    
    # TODO: Add assertions for AUC metrics here using results["auc"]
    #       when specified by user
    
    # E.g.
    # for metric in results["pointwise"]["reoc"]:
    #     assert metric["pass"], f"Pointwise metric failed for Reoccupancy, System: {metric['system']}"
    
