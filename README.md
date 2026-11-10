# Opus 5.5 — 86 Styles in Motion

一个面向 Codex 的讲解视频制作 Skill：用户只需给出主题或已有口播，它会先核实事实、细化内容并等待确认，再从 86 种基础风格与 2 种扩展风格中选择视觉方向，制作约 20 秒 HTML 样片，获批后完成全片。

An explainer-video skill for Codex. Start with only a topic or existing narration; the workflow researches facts, develops and confirms the story, selects a visual style, produces an approximately 20-second HTML sample, and expands it into the complete film only after approval.

## 核心流程 / Workflow

1. **给出主题**：一句话即可，不要求用户先写脚本。
2. **事实研究与内容细化**：明确受众、目标、钩子、核心问题、解释结构、案例、边界、结尾和交付要求。
3. **确认内容**：先交付并确认 `CONTENT_BRIEF.md`、`FACT_CHECK.md` 和风格无关的 `STORYBOARD.md` 初稿。
4. **选择风格**：基于已确认内容，从完整风格索引中推荐三个有明显差异的方案，并展示原始参考图；也可以直接采用用户已指定的风格。
5. **约 20 秒 HTML 样片**：研究所选风格的图片、参考视频和源码，制作可播放、暂停、拖动和重播的连续动画样片。
6. **样片确认后制作全片**：沿用通过的视觉规范完成完整 HTML，检查时间轴、事实逻辑、动效、可读性与声音。
7. **按需导出 MP4**：HTML 是默认交付；只有用户要求时才导出视频文件。

内容确认先于风格确认，风格确认先于样片确认。未获得相应确认时，不提前扩展全片。

### 硬性门禁 / Deterministic Gates

关键确认不再只依赖长篇文字说明。新作品可用 `workflow_gate.py` 初始化三份内容文档并记录确认状态：

```sh
python scripts/workflow_gate.py init --output ../my-film --topic "My topic"
python scripts/workflow_gate.py confirm-content --output ../my-film --evidence "用户确认原话"
python scripts/workflow_gate.py check --output ../my-film --next style
```

`check --next style` 只有在 `CONTENT_BRIEF.md`、`FACT_CHECK.md`、`STORYBOARD.md` 已填实且内容确认已记录时才会通过。脚本还支持 `record-style`、`confirm-sample`，以及进入 `sample`、`full` 阶段前的检查。

## 风格库 / Style Library

- **#1–#86**：Futurepedia AI Style Atlas 的 86 种视觉风格，每种包含原始封面、两段参考视频、完整提示词、元数据与参考源码。
- **#87 口播类 / Talking Head**：适用于已有口播、人物小窗、精剪和人物旁解释动效。原声、字幕与精剪时间映射决定动画时序，不用自动文案替换原话。
- **#88 Vibe 知识讲解 / Vibe Knowledge Film**：包含 **C Nocturne / 夜曲** 与 **B Fable / 寓言** 两个子方案；只有选中该风格后才加载其导演方法、本地引擎和示例源码。

离线图库位于 `assets/gallery/index.html`，提供中英文名称、搜索、分类、原始示例图与参考视频。图库用于浏览参考，不替代内容确认或样片确认。

## 安装 / Install

需要 Codex、本地文件访问权限、Python 3.9+ 和可用于预览 HTML 的现代浏览器。部分作品可能需要额外的渲染或音视频工具。

```sh
git clone https://github.com/canwekissforever56-wq/claude-opus-5-5-video-style.git ~/.codex/skills/claude-opus-5-5-new
```

如果使用自定义 `CODEX_HOME`，请安装到其 `skills` 目录。目标文件夹已存在时，请先备份或使用其他目录，不要直接覆盖。

调用示例：

```text
$claude-opus-5-5-new 制作一支让普通人看懂 AI 为什么会出现幻觉的讲解视频
```

默认使用中文、16:9、面向普通观众；用户当次指定的语言、画幅、时长、声音和交付形式优先。

## 常用命令 / Utilities

在 Skill 根目录运行：

```sh
python scripts/atlas.py --list
python scripts/atlas.py --id 11
python scripts/atlas.py --id 87
python scripts/atlas.py --id 88
python scripts/atlas.py --verify
python scripts/gallery.py --output ../styles-gallery
```

- `atlas.py --list`：列出风格。
- `atlas.py --id <编号>`：定位指定风格的材料。
- `atlas.py --verify`：校验基础风格与扩展风格的文件和哈希。
- `gallery.py`：导出一份可独立打开的本地风格图库。

## 目录结构 / Files

- `SKILL.md`：核心制作流程、确认节点与跨回合续做规则。
- `agents/openai.yaml`：Codex 界面元数据与默认调用示例。
- `references/content-planning.md`：事实研究、内容策划与确认方法。
- `references/style-index.json`：86 种基础风格精简索引。
- `references/custom-style-index.json`：#87 与 #88 扩展风格索引。
- `references/style-selection.md`：风格图片展示与选择流程。
- `references/style-research.md`：选定风格后的素材研究方法。
- `references/motion-delivery.md`：样片与成片验收标准。
- `references/talking-head.md`：口播类制作指南。
- `references/vibe-knowledge-film.md`：Vibe 知识讲解专属指南。
- `scripts/`：阶段门禁、风格定位、图库导出与 Vibe 项目脚手架工具。
- `assets/atlas/`：86 种风格原始参考集合、来源与哈希清单。
- `assets/gallery/`：可离线浏览的风格图库。
- `assets/custom/talking-head/`：口播类参考、可编辑 HTML、预览视频与制作证据。
- `assets/custom/vibe-knowledge-film/`：本地引擎、字体、示例、播放器和授权文件。

## 口播类说明 / Talking Head

#87 基于阿朱本人已确认的 150 秒作品，包含可浏览成片参考、20.733 秒节选、完整可编辑 HTML 项目和历史剪辑/字幕证据。参考作品属于用户自制内容，不归因于 Opus 5.5。嵌入的第三方素材保留各自来源说明。

明确选择口播类后，可以跳过三风格推荐，但仍需先确认讲述目标、素材范围与剪辑边界，并在全片制作前确认约 20 秒样片。

## Vibe 知识讲解说明 / Vibe Knowledge Film

#88 集成 [HeyChengC/vibe-knowledge-film](https://github.com/HeyChengC/vibe-knowledge-film) 作为独立风格条目。夜曲适合抽象机制与知识拆解，寓言适合行为、角色和插画叙事。它不改变其他风格的制作规则。

可以用脚本创建自包含项目：

```sh
python scripts/new_vibe_film.py --output ../my-film/sample --world C --title "My topic"
```

使用 `--world B` 选择寓言，`--example` 复制带署名的原始参考，`--audio path/to/track.mp3` 导入本地音乐。示例项目和图库视频仅用于研究运动语言，不代表已经完成 MP4 导出。

## 来源与授权 / Credits

- 原始 86 种风格来自 [Futurepedia — AI Style Atlas](https://www.futurepedia.io/resources/ai-style-atlas/view)。
- 口播类参考由阿朱制作；第三方素材来源记录在 `assets/custom/talking-head/source/assets/sources.txt` 及嵌套示例的说明文件中。
- Vibe Knowledge Film 由 HeyChengC 制作；MIT License 与字体 OFL 文件保存在 `assets/custom/vibe-knowledge-film/`。
- 更完整的第三方说明见 `THIRD_PARTY_NOTICES.md`。

本地收录参考素材不等于获得对外再分发许可。使用与发布前请遵守各素材的原始授权条款。
