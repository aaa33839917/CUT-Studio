# CUT 工作室 · 官网

CUT 工作室的官方网站。

- 线上地址：https://aaa33839917.github.io/CUT-Studio/
- 托管：GitHub Pages（同账号的第二个 Pages 站，与 `Deep-Space-Web` 互不影响）

## 状态

**建设中。** 目前只有一个占位页，正式内容待 CUT 工作室提供。

## 内容怎么改（2026-10-02 起：页面由内容生成，别手改 HTML）

原来 `index.html` 是**手写**的 —— 改一句简介、加一台服务器都得动 HTML。现在拆成三份：

| 文件 | 作用 |
|---|---|
| `content/schema.json` | **哪些内容可以改**（字段、类型、分组）。加字段只改这里，控制台会自动出表单 |
| `content/values.json` | **当前的值**（唯一的真源；内容就改这里） |
| `_build/index.template.html` | 版式（占位符 `{{...}}`） |
| `_build/render.py` | 生成器：读上面两份 + 模板 → 写出 `index.html` |
| `index.html` | **生成产物，别手改**（下次生成会覆盖） |

改法（任选）：

```bash
# ① 推荐：综合平台里点着改（表单照着 schema 自动生成，服务器列表能加/删条目）
#    控制台 → 官网管理 → 切到「CUT 工作室官网」→ 内容管理 →
#    http://192.168.3.100:18080/content?site=cut&token=…
# ② 或者直接改 content/values.json，然后：
python3 _build/render.py          # 生成 index.html
python3 _build/render.py --check  # 只核对页面与内容是否一致（不一致退出 1）
```

安全：所有文本都按 HTML 转义（内容里写 `<script>` 也只会显示成字），
链接只允许 `http(s)://` 或站内相对路径（`javascript:`、`data:` 一律丢掉，实测过）。
控制台保存前会先备份到 `content/.backup/`（保留最近 20 份）。
