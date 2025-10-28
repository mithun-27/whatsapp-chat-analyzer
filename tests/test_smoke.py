from pathlib import Path
from src.parser import parse_chat

def test_parse_runs():
    sample = Path("data/raw/sample.txt")
    sample.parent.mkdir(parents=True, exist_ok=True)
    sample.write_text("12/10/2024, 10:15 - Alice: Hello\n12/10/2024, 10:16 - Bob: Hi!")
    df = parse_chat(sample)
    assert len(df) == 2
