from __future__ import annotations

import argparse
import json

from kvocab_core.analyzer import Analyzer
from kvocab_core.database import init_db
from kvocab_core.schemas import AnalyzeRequest, Strictness


def main() -> None:
    parser = argparse.ArgumentParser(description="K-Vocab Guard CLI analyzer")
    parser.add_argument("--level", default="2A")
    parser.add_argument("--unit", "--lesson", dest="lesson", default="2-1")
    parser.add_argument("--text", required=True)
    parser.add_argument("--strictness", default="balanced", choices=["loose", "balanced", "strict"])
    args = parser.parse_args()

    factory = init_db()
    with factory() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text=args.text,
                target_level=args.level,
                target_lesson=args.lesson,
                strictness=Strictness(args.strictness),
            )
        )

    out = result.model_dump()
    for issue in out.get("issues", []):
        from kvocab_core.status_labels import status_label_ko

        issue["status_label_ko"] = status_label_ko(issue["status"])
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
