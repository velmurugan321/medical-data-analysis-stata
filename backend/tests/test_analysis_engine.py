import pandas as pd

from app.analysis_engine import categorical_association, diagnostic_accuracy, robust_poisson, data_quality


def test_diagnostic_accuracy():
    df = pd.DataFrame({"test": [0, 0, 1, 1], "ref": [0, 1, 0, 1]})
    result = diagnostic_accuracy(df, "test", "ref")
    assert result["tp"] == 1
    assert result["tn"] == 1
    assert result["fp"] == 1
    assert result["fn"] == 1
    assert result["sensitivity"] == 0.5
    assert result["specificity"] == 0.5


def test_categorical_association():
    df = pd.DataFrame({"x": [0, 0, 1, 1], "y": [0, 1, 0, 1]})
    result = categorical_association(df, "x", "y")
    assert result["df"] == 1
    assert result["fisher_p"] is not None


def test_robust_poisson_with_reference_category():
    df = pd.DataFrame({
        "outcome": [0, 1, 0, 1, 0, 1, 0, 1],
        "sex": [0, 0, 0, 0, 1, 1, 1, 1],
        "age": [20, 21, 22, 23, 30, 31, 32, 33],
    })
    result = robust_poisson(
        df, "outcome", ["sex", "age"], ["sex"], {"sex": "0"}
    )
    assert result["n"] == 8
    assert result["converged"] is True
    assert any(row["variable"] == "sex" and row["reference"] == "0" for row in result["adjusted"])


def test_data_quality():
    df = pd.DataFrame({"a": [1, 2, None], "b": [1, 1, 1]})
    result = data_quality(df)
    assert result["rows"] == 3
    assert result["duplicate_rows"] == 0
    assert "missing" in result["variables"][0]["issues"]
    assert "constant_or_empty" in result["variables"][1]["issues"]
