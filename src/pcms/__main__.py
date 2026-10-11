import argparse
import json

from .core import Ledger
from .demo import run_demo
from .bank_statement import stage_files
from .review import export_review_package, receive_review


def main():
    parser = argparse.ArgumentParser(description="PCMS synthetic ledger pilot and read-only bank staging")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="Run synthetic import-to-restatement demo in a new directory")
    demo.add_argument("--output", required=True)
    verify = commands.add_parser("verify", help="Verify history, evidence and snapshot reconstruction")
    verify.add_argument("ledger")
    report = commands.add_parser("report", help="Rebuild synthetic draft report")
    report.add_argument("ledger")
    report.add_argument("--as-of", required=True)
    bank = commands.add_parser("bank-stage", help="Read supported bank XLSX into private staging, never publish to ledger")
    bank.add_argument("files", nargs="+")
    bank.add_argument("--output", default="private-data/bank-staging")
    review = commands.add_parser("review-package", help="Prepare a verified owner-review input package")
    review.add_argument("batch")
    review.add_argument("--output", required=True)
    reply = commands.add_parser("review-return", help="Collect workbook responses as proposals, never approval")
    reply.add_argument("batch")
    reply.add_argument("workbook")
    reply.add_argument("--output", default="private-data/review-responses")
    web = commands.add_parser("serve", help="Open the local synthetic product trial")
    web.add_argument("--data", default=None)
    web.add_argument("--port", type=int, default=8787)
    web.add_argument("--p01", action="store_true", help="Run focused P01 bank trial in a separate data directory")
    args = parser.parse_args()
    if args.command == "serve":
        from .server import serve
        serve(args.data or ("private-data/p01-trial" if args.p01 else "private-data/product-demo"), args.port, p01=args.p01)
        return
    if args.command == "demo":
        result = run_demo(args.output)
    elif args.command == "verify":
        result = {"verified_events": Ledger(args.ledger).verify()}
    elif args.command == "bank-stage":
        result = stage_files(args.files, args.output)
    elif args.command == "review-package":
        result = export_review_package(args.batch, args.output)
    elif args.command == "review-return":
        result = receive_review(args.batch, args.workbook, args.output)
    else:
        result = Ledger(args.ledger).report(args.as_of)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
