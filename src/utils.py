from pathlib import Path
import re
import pandas as pd

URL_PATTERN = re.compile(r"(https?://\S+)|(www\.\S+)")

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def save_df(df: pd.DataFrame, path: Path):
    ensure_dir(path.parent)
    if path.suffix.lower() == ".parquet":
        df.to_parquet(path, index=False)
    elif path.suffix.lower() in (".csv", ".txt"):
        df.to_csv(path, index=False)
    else:
        df.to_parquet(path.with_suffix(".parquet"), index=False)

def read_table(path: Path) -> pd.DataFrame:
    s = path.suffix.lower()
    if s == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)

def extract_urls(text: str) -> list[str]:
    return [m.group(0) for m in URL_PATTERN.finditer(text or "")]
