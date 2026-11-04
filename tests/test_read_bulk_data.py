import pyarrow as pa

from osdu_samples.welllogs.read_bulk_data import _print_table


def test_preview_preserves_adjacent_depths_and_null_sentinel(capsys):
    table = pa.table({"DEPTH": [1234.6524, 1234.8048], "GR": [-999.25, None]})

    _print_table(table)

    lines = capsys.readouterr().out.splitlines()
    assert lines[0].split() == ["DEPTH", "GR"]
    assert lines[1].split() == ["1234.6524", "-999.25"]
    assert lines[2].split() == ["1234.8048"]
