#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services import (  # noqa: E402
    evaluate_generated_course_json,
    evaluate_generated_course_markdown,
    run_pdf_course_generation_benchmark,
    save_report_json,
    write_flat_report_csv,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate PDF course generation quality for summary, generated QAs, and generated quiz. "
            "The evaluator can either run the generator first or score an existing generated markdown file."
        )
    )
    parser.add_argument("--pdf", required=True, help="Path to the source PDF.")
    parser.add_argument(
        "--reference-markdown",
        help="Optional gold/reference course markdown used for benchmark alignment.",
    )
    parser.add_argument(
        "--generated-markdown",
        help="Evaluate an existing generated course markdown instead of running the generator again.",
    )
    parser.add_argument(
        "--course-json",
        help="Evaluate a JSON file with summary, questions.qa_list, and quiz instead of markdown.",
    )
    parser.add_argument(
        "--response-language",
        default="en",
        choices=["en", "de"],
        help="Language used for keyword handling and generator prompts.",
    )
    parser.add_argument(
        "--llm-model",
        help="LLM model name for benchmark mode. If omitted, the backend default is used.",
    )
    parser.add_argument("--qa-count", type=int, default=5, help="Expected/generated QA count.")
    parser.add_argument(
        "--quiz-question-count",
        type=int,
        default=3,
        help="Expected/generated quiz item count.",
    )
    parser.add_argument(
        "--quiz-option-count",
        type=int,
        default=3,
        help="Expected/generated option count per MCQ item.",
    )
    parser.add_argument(
        "--misconception-count",
        type=int,
        default=2,
        help="Expected/generated misconception count.",
    )
    parser.add_argument("--output-json", help="Optional path to save the full JSON report.")
    parser.add_argument("--output-csv", help="Optional path to save a flattened one-row CSV report.")
    return parser


async def _run(args: argparse.Namespace) -> dict:
    if args.course_json:
        return evaluate_generated_course_json(
            pdf_path=args.pdf,
            generated_course_json_path=args.course_json,
            reference_markdown_path=args.reference_markdown,
            response_language=args.response_language,
            expected_qa_count=args.qa_count,
            expected_quiz_question_count=args.quiz_question_count,
            expected_quiz_option_count=args.quiz_option_count,
            expected_misconception_count=args.misconception_count,
        )

    if args.generated_markdown:
        return evaluate_generated_course_markdown(
            pdf_path=args.pdf,
            generated_markdown_path=args.generated_markdown,
            reference_markdown_path=args.reference_markdown,
            response_language=args.response_language,
            expected_qa_count=args.qa_count,
            expected_quiz_question_count=args.quiz_question_count,
            expected_quiz_option_count=args.quiz_option_count,
            expected_misconception_count=args.misconception_count,
        )

    return await run_pdf_course_generation_benchmark(
        pdf_path=args.pdf,
        reference_markdown_path=args.reference_markdown,
        response_language=args.response_language,
        llm_model_name=args.llm_model,
        qa_count=args.qa_count,
        quiz_question_count=args.quiz_question_count,
        quiz_option_count=args.quiz_option_count,
        misconception_count=args.misconception_count,
    )


async def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    report = await _run(args)

    if args.output_json:
        save_report_json(report, args.output_json)
    if args.output_csv:
        write_flat_report_csv(report, args.output_csv)

    if not args.output_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    overall = (report.get("overall") or {}).get("score")
    summary_score = (report.get("summary") or {}).get("score")
    qa_score = (report.get("qa") or {}).get("score")
    quiz_score = (report.get("quiz") or {}).get("score")
    misconception_score = (report.get("misconceptions") or {}).get("score")
    print(
        f"overall_score={overall} summary_score={summary_score} "
        f"qa_score={qa_score} quiz_score={quiz_score} "
        f"misconceptions_score={misconception_score}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
