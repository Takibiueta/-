#!/usr/bin/env python3
"""クラウドワークス案件の管理(フォルダ作成・状態変更・一覧)。標準ライブラリのみ。

  python3 crowdworks/cw.py new "案件タイトル" < 案件本文.txt   # 本文は標準入力
  python3 crowdworks/cw.py new "案件タイトル" --file 本文.txt [--url URL]
  python3 crowdworks/cw.py status <id> <状態> [--verdict GO|保留|見送り]
  python3 crowdworks/cw.py list [--all]
"""
import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JOBS = ROOT / "jobs"
TEMPLATE = ROOT / "templates" / "job.md"

STATES = [
    "screened", "proposed", "applied", "awarded", "working",
    "review", "delivered", "done", "lost", "skipped",
]
CLOSED = {"done", "lost", "skipped"}
VERDICTS = {"GO", "保留", "見送り"}


def read_meta(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta, text


def write_meta(path, updates):
    meta, text = read_meta(path)
    meta.update(updates)
    head = "\n".join(f"{k}: {v}" for k, v in meta.items())
    body = re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S)
    path.write_text(f"---\n{head}\n---\n{body}", encoding="utf-8")


def next_id():
    today = dt.date.today().strftime("%Y%m%d")
    n = len(list(JOBS.glob(f"{today}-*"))) + 1
    return f"{today}-{n:02d}"


def find_job(job_id):
    hits = sorted(JOBS.glob(f"{job_id}*"))
    if len(hits) != 1:
        sys.exit(f"案件が特定できません: {job_id}({len(hits)}件一致)")
    return hits[0] / "job.md"


def cmd_new(a):
    body = Path(a.file).read_text(encoding="utf-8") if a.file else sys.stdin.read()
    if not body.strip():
        sys.exit("案件本文が空です")
    job_id = next_id()
    d = JOBS / job_id
    (d / "deliverables").mkdir(parents=True)
    text = TEMPLATE.read_text(encoding="utf-8").format(
        id=job_id, title=a.title.replace("\n", " "),
        date=dt.date.today().isoformat(), body=body.strip(),
    )
    (d / "job.md").write_text(text, encoding="utf-8")
    if a.url:
        write_meta(d / "job.md", {"url": a.url})
    print(d.relative_to(ROOT.parent))


def cmd_status(a):
    if a.state not in STATES:
        sys.exit(f"状態は次のいずれか: {', '.join(STATES)}")
    if a.verdict and a.verdict not in VERDICTS:
        sys.exit(f"判定は次のいずれか: {', '.join(sorted(VERDICTS))}")
    path = find_job(a.id)
    updates = {"status": a.state}
    if a.verdict:
        updates["verdict"] = a.verdict
    write_meta(path, updates)
    print(f"{path.parent.name}: {a.state}")


def cmd_list(a):
    rows = []
    for p in sorted(JOBS.glob("*/job.md")):
        meta, _ = read_meta(p)
        if not a.all and meta.get("status") in CLOSED:
            continue
        rows.append((meta.get("id", p.parent.name), meta.get("status", "?"),
                     meta.get("verdict", ""), meta.get("title", "")))
    if not rows:
        print("案件はありません" + ("" if a.all else "(終了分は --all で表示)"))
        return
    for r in rows:
        print(f"{r[0]:<12} {r[1]:<10} {r[2]:<4} {r[3]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(required=True)

    p = sub.add_parser("new", help="案件フォルダを作る")
    p.add_argument("title")
    p.add_argument("--file")
    p.add_argument("--url", default="")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("status", help="状態を変える")
    p.add_argument("id")
    p.add_argument("state")
    p.add_argument("--verdict")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("list", help="一覧")
    p.add_argument("--all", action="store_true")
    p.set_defaults(func=cmd_list)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
