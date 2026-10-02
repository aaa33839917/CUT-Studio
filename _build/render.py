#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CUT 工作室官网 · 内容生成器（2026-10-02 新增）

为什么要有它：这张页面原来是**手写的**（85 行 HTML），改一句话就要动 HTML，
而官网内容经常要改（新服务器上线、版本号、简介、联系方式）。
⇒ 把"会变的内容"抽出来放到 `content/values.json`，页面由本脚本生成：

    content/schema.json   —— **哪些内容可以改**（控制台据此自动出表单；加字段不用改控制台）
    content/values.json   —— 当前的值（唯一的真源）
    _build/index.template.html —— 版式（占位符 {{...}}）
    index.html            —— 生成产物（**不要手改**，会被覆盖）

用法：
    python3 _build/render.py            # 生成 index.html
    python3 _build/render.py --check    # 只核对：index.html 与内容是否一致（不一致退出 1）
    python3 _build/render.py --dry-run  # 只打印会生成什么，不写盘

★ 安全：所有文本都走 html.escape（内容里写 <script> 也不会变成标签）；
  链接只允许 http(s):// 或站内相对路径（不许 javascript: 之类）。
"""
import argparse
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCHEMA = os.path.join(ROOT, "content", "schema.json")
VALUES = os.path.join(ROOT, "content", "values.json")
TEMPLATE = os.path.join(HERE, "index.template.html")
OUT = os.path.join(ROOT, "index.html")

TAG_CLASS = {"live": "live", "dev": "dev"}


def die(msg, code=2):
    print("❌ %s" % msg, file=sys.stderr)
    sys.exit(code)


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:                                        # noqa: BLE001
        die("读不了 %s：%s" % (path, e))


def safe_url(u):
    """链接白名单：http(s) / 站内相对路径。别的（javascript:、data:）一律丢掉。"""
    u = (u or "").strip()
    if not u:
        return ""
    if re.match(r"^https?://", u) or (u.startswith("/") or re.match(r"^[A-Za-z0-9_./#?=&-]+$", u) and ":" not in u):
        return u
    return ""


def servers_html(items):
    out = []
    for it in (items or []):
        if not isinstance(it, dict):
            continue
        name = html.escape(str(it.get("name") or "").strip())
        ver = html.escape(str(it.get("ver") or "").strip())
        desc = html.escape(str(it.get("desc") or "").strip())
        tag = str(it.get("tag") or "dev").strip()
        tag_class = TAG_CLASS.get(tag, "dev")
        tag_text = "已开放" if tag_class == "live" else "开发中"
        url = safe_url(it.get("url"))
        label = html.escape(str(it.get("link_label") or "前往 →").strip())
        inner = (
            '      <div class="top">\n'
            '        <span class="nm">%s</span>\n'
            '        <span class="ver">%s</span>\n'
            '        <span class="tag %s">%s</span>\n'
            '      </div>\n'
            '      <div class="desc">%s</div>\n' % (name, ver, tag_class, tag_text, desc)
        )
        if url:
            out.append('    <a class="srv" href="%s">\n%s      <div class="go">%s</div>\n    </a>\n'
                       % (html.escape(url, quote=True), inner, label))
        else:
            out.append('    <div class="srv disabled">\n%s    </div>\n' % inner)
    return "".join(out)


def build():
    schema = load_json(SCHEMA)
    values = load_json(VALUES)
    tpl = open(TEMPLATE, encoding="utf-8").read()

    # 收集 schema 里声明过的字段（没声明的值不往页面里塞 —— 免得手滑把内部字段渲染出去）
    flat = []
    lists = set()
    for g in (schema.get("groups") or []):
        for f in (g.get("fields") or []):
            if f.get("type") == "list":
                lists.add(f["key"])
            else:
                flat.append(f["key"])

    out = tpl
    out = out.replace("{{servers_html}}", servers_html(values.get("servers")))
    for k in flat:
        v = values.get(k, "")
        # 多行文本：行内换行按 HTML 处理（两行之间不额外加 <br>，与原页面一致：段内换行=空格）
        text = html.escape(str(v))
        out = out.replace("{{%s}}" % k, text)

    left = sorted(set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", out)))
    if left:
        print("   ⚠️ 模板里还有没被值填上的占位符：%s（schema 里声明了吗？）" % "、".join(left))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只核对 index.html 与内容是否一致")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    html_out = build()
    old = open(OUT, encoding="utf-8").read() if os.path.isfile(OUT) else ""
    if html_out == old:
        print("   ✅ 官网首页已是最新（与 content/values.json 一致），未改动任何字节")
        return 0
    if a.check:
        print("   ❌ index.html 与 content/values.json 不一致（跑 python3 _build/render.py 同步）")
        return 1
    if a.dry_run:
        print("   [dry] 会更新 index.html（%d 字节 → %d 字节）" % (len(old.encode()), len(html_out.encode())))
        return 0
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(html_out)
    os.replace(tmp, OUT)
    print("   ✅ 已生成 index.html（由 content/values.json + _build/index.template.html 生成，别手改页面）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
