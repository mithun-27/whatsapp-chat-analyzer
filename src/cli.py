import argparse
from pathlib import Path
from .parser import parse_chat
from .analyzer import export_csv_summaries
from .visuals import plot_all
from .utils import ensure_dir, save_df, read_table

def cmd_parse(args):
    df = parse_chat(Path(args.input))
    out = Path(args.output)
    save_df(df, out)
    print(f"Parsed -> {out}")

def cmd_analyze(args):
    df = read_table(Path(args.input))
    export_csv_summaries(df, Path(args.outdir))
    print(f"CSV summaries saved to {args.outdir}")

def cmd_visualize(args):
    df = read_table(Path(args.input))
    plot_all(df, Path(args.outdir))
    print(f"Charts saved to {args.outdir}")

def cmd_full(args):
    raw = Path(args.input)
    workdir = Path(args.workdir)
    proc = workdir / "data" / "processed" / (raw.stem + ".parquet")
    reports = workdir / "reports"
    ensure_dir(proc.parent); ensure_dir(reports)
    df = parse_chat(raw)
    save_df(df, proc)
    export_csv_summaries(df, reports)
    plot_all(df, reports)
    print(f"Done. Processed={proc}  Reports={reports}")

def build_parser():
    p = argparse.ArgumentParser(prog="whatsapp-chat-analyzer", description="WhatsApp Chat Data Analyzer")
    sp = p.add_subparsers(dest="cmd", required=True)

    pp = sp.add_parser("parse", help="Parse .txt -> dataframe")
    pp.add_argument("--input", required=True)
    pp.add_argument("--output", required=True)
    pp.set_defaults(func=cmd_parse)

    pa = sp.add_parser("analyze", help="Compute CSV summaries")
    pa.add_argument("--input", required=True)
    pa.add_argument("--outdir", required=True)
    pa.set_defaults(func=cmd_analyze)

    pv = sp.add_parser("visualize", help="Create PNG charts")
    pv.add_argument("--input", required=True)
    pv.add_argument("--outdir", required=True)
    pv.set_defaults(func=cmd_visualize)

    pf = sp.add_parser("full", help="Parse + analyze + visualize")
    pf.add_argument("--input", required=True)
    pf.add_argument("--workdir", required=True)
    pf.set_defaults(func=cmd_full)
    return p

def main():
    args = build_parser().parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
