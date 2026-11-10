#!/usr/bin/env python3
"""Create and verify the approval gates used by this video skill."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


STATE_FILE = ".video-skill-state.json"
PLACEHOLDER = "<!-- VIDEO_SKILL_CONTENT_DRAFT: replace this marker before confirmation -->"
CONTENT_FILES = ("CONTENT_BRIEF.md", "FACT_CHECK.md", "STORYBOARD.md")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def atomic_json_write(path: Path, data: dict) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def state_path(output: Path) -> Path:
    return output / STATE_FILE


def load_state(output: Path) -> dict:
    path = state_path(output)
    if not path.is_file():
        fail(f"missing {STATE_FILE}; run init first")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {STATE_FILE}: {exc}")


def initial_documents(topic: str) -> dict[str, str]:
    return {
        "CONTENT_BRIEF.md": f"""# {topic}｜内容策划单

{PLACEHOLDER}

## 主题、受众与一句话目标

## 钩子与待回答的问题

## 核心拆解与贯穿对象

## 中段知识节点、例子与边界

## 结尾

## 时长、音乐、语言、声音与交付

## 待确认项
""",
        "FACT_CHECK.md": f"""# {topic}｜事实核对清单

{PLACEHOLDER}

| 编号/片中位置 | 拟用写法 | 依据与适用范围 | 来源链接及日期 | 素材/授权状态 | 核实状态 |
|---|---|---|---|---|---|
""",
        "STORYBOARD.md": f"""# {topic}｜风格无关分镜

{PLACEHOLDER}

| 段落/作用 | 时间码或暂定占比 | 画面对象与解释动作 | 衔接方式 | 中文字幕 | 英文字幕（可选） | 音乐/音效提示 | 事实编号 |
|---|---|---|---|---|---|---|---|
""",
    }


def cmd_init(args: argparse.Namespace) -> None:
    output = Path(args.output).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    for name, content in initial_documents(args.topic).items():
        path = output / name
        if path.exists():
            continue
        path.write_text(content, encoding="utf-8")
        created.append(name)

    path = state_path(output)
    if not path.exists():
        atomic_json_write(
            path,
            {
                "schema_version": 1,
                "topic": args.topic,
                "created_at": now_iso(),
                "content": {"confirmed": False, "evidence": None, "confirmed_at": None},
                "style": {"selected": None, "evidence": None, "confirmed_at": None},
                "sample": {"confirmed": False, "evidence": None, "confirmed_at": None},
            },
        )
        created.append(STATE_FILE)
    print(json.dumps({"output": str(output), "created": created}, ensure_ascii=False))


def validate_content_files(output: Path) -> None:
    problems: list[str] = []
    for name in CONTENT_FILES:
        path = output / name
        if not path.is_file():
            problems.append(f"missing {name}")
            continue
        text = path.read_text(encoding="utf-8")
        if PLACEHOLDER in text:
            problems.append(f"{name} still contains the draft marker")
        if len(text.strip()) < 200:
            problems.append(f"{name} is too short to be a filled content document")
    if problems:
        fail("; ".join(problems))


def cmd_confirm_content(args: argparse.Namespace) -> None:
    output = Path(args.output).expanduser().resolve()
    validate_content_files(output)
    state = load_state(output)
    state["content"] = {
        "confirmed": True,
        "evidence": args.evidence.strip(),
        "confirmed_at": now_iso(),
    }
    atomic_json_write(state_path(output), state)
    print("content gate recorded")


def cmd_record_style(args: argparse.Namespace) -> None:
    output = Path(args.output).expanduser().resolve()
    state = load_state(output)
    if not state.get("content", {}).get("confirmed"):
        fail("content gate is not confirmed")
    state["style"] = {
        "selected": args.style.strip(),
        "evidence": args.evidence.strip(),
        "confirmed_at": now_iso(),
    }
    atomic_json_write(state_path(output), state)
    print("style gate recorded")


def cmd_confirm_sample(args: argparse.Namespace) -> None:
    output = Path(args.output).expanduser().resolve()
    state = load_state(output)
    if not state.get("style", {}).get("selected"):
        fail("style gate is not confirmed")
    state["sample"] = {
        "confirmed": True,
        "evidence": args.evidence.strip(),
        "confirmed_at": now_iso(),
    }
    atomic_json_write(state_path(output), state)
    print("sample gate recorded")


def cmd_check(args: argparse.Namespace) -> None:
    output = Path(args.output).expanduser().resolve()
    state = load_state(output)
    validate_content_files(output)
    if not state.get("content", {}).get("confirmed"):
        fail("cannot enter style stage: content gate is not confirmed")
    if args.next in {"sample", "full"} and not state.get("style", {}).get("selected"):
        fail(f"cannot enter {args.next} stage: style gate is not confirmed")
    if args.next == "full" and not state.get("sample", {}).get("confirmed"):
        fail("cannot enter full stage: sample gate is not confirmed")
    print(f"gate check passed for next stage: {args.next}")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create content-stage files without overwriting existing files")
    init.add_argument("--output", required=True)
    init.add_argument("--topic", required=True)
    init.set_defaults(func=cmd_init)

    confirm_content = sub.add_parser("confirm-content", help="record explicit approval of the content plan")
    confirm_content.add_argument("--output", required=True)
    confirm_content.add_argument("--evidence", required=True)
    confirm_content.set_defaults(func=cmd_confirm_content)

    record_style = sub.add_parser("record-style", help="record the user's explicit style selection")
    record_style.add_argument("--output", required=True)
    record_style.add_argument("--style", required=True)
    record_style.add_argument("--evidence", required=True)
    record_style.set_defaults(func=cmd_record_style)

    confirm_sample = sub.add_parser("confirm-sample", help="record explicit approval of the complete sample")
    confirm_sample.add_argument("--output", required=True)
    confirm_sample.add_argument("--evidence", required=True)
    confirm_sample.set_defaults(func=cmd_confirm_sample)

    check = sub.add_parser("check", help="verify prerequisites for the requested next stage")
    check.add_argument("--output", required=True)
    check.add_argument("--next", choices=("style", "sample", "full"), required=True)
    check.set_defaults(func=cmd_check)
    return root


def main() -> None:
    args = parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
