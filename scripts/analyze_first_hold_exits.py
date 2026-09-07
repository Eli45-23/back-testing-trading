"""Run only the predeclared offline exit family; no broker or data-download calls."""
import json
from pathlib import Path
from spy_research.break_hold.exit_study import run_exit_study
from spy_research.break_hold.exit_study_reporting import render_tables,trade_csv
from spy_research.break_hold.entry_timing_analysis import json_default


def main():
    result=run_exit_study()
    outputs={'break_hold_exit_study.json':json.dumps(result,default=json_default,indent=2),
             'break_hold_exit_study_tables.md':render_tables(result),
             'break_hold_exit_study_trades.csv':trade_csv(result)}
    for name,content in outputs.items():
        path=Path('reports')/name;path.write_text(content+'\n');print(path)
    print(result['counts'])


if __name__=='__main__':main()
