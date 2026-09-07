"""Offline analysis of frozen V1 canonical output; never redetects signals."""
import argparse
import json
from pathlib import Path

from spy_research.break_hold.entry_timing_analysis import run_saved_analysis, json_default
from spy_research.break_hold.entry_timing_reporting import render_analysis, paired_csv


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=Path('reports/break_hold_2026_v1.json'))
    parser.add_argument('--output-prefix',type=Path,default=Path('reports/break_hold_2026_entry_timing_analysis'))
    args=parser.parse_args()
    paths=[Path(str(args.output_prefix)+suffix) for suffix in ('.json','.md','_paired.csv')]
    if any(path.resolve()==args.input.resolve() for path in paths):
        raise ValueError('cannot overwrite the canonical input')
    result=run_saved_analysis(args.input)
    args.output_prefix.parent.mkdir(parents=True,exist_ok=True)
    for suffix,content in (('.json',json.dumps(result,default=json_default,indent=2)),('.md',render_analysis(result)),('_paired.csv',paired_csv(result))):
        path=Path(str(args.output_prefix)+suffix)
        if path.resolve()==args.input.resolve():
            raise ValueError('cannot overwrite the canonical input')
        path.write_text(content+'\n',encoding='utf-8')
        print(path)
    print('Reconciled counts:',result['counts'])
    print('Matched pairs:',result['paired']['ALL']['n'])


if __name__=='__main__':
    main()
