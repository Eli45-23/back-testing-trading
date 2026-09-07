"""Run the fixed offline First Hold feature/reference study, without live access."""
import json
from pathlib import Path

from spy_research.break_hold.first_hold_quality_service import run_quality_study
from spy_research.break_hold.first_hold_quality_reporting import render_decision,render_tables,feature_csv,executable_csv
from spy_research.break_hold.entry_timing_analysis import json_default


def main():
    result=run_quality_study()
    folder=Path('reports')
    outputs={
        'break_hold_first_hold_quality_analysis.json':json.dumps(result,default=json_default,indent=2),
        'break_hold_first_hold_quality_analysis.md':render_decision(result),
        'break_hold_first_hold_quality_tables.md':render_tables(result),
        'break_hold_first_hold_quality_features.csv':feature_csv(result),
        'break_hold_first_hold_quality_executable_pairs.csv':executable_csv(result),
    }
    for name,content in outputs.items():
        path=folder/name
        path.write_text(content+'\n',encoding='utf-8')
        print(path)
    print(result['counts'])


if __name__=='__main__':
    main()
