---
title: "Scripts Documentation"
---

This folder contains automation scripts for the academic website.

## Workflow Overview

1. **Manual Step**: Use `tex2qmd.py` to convert your raw LaTeX notes into Quarto Markdown.
2. **Automated Step**: The `sync_deepseek.py` script runs automatically during deployment (or manually via `deploy.sh`) to translate content between English and Chinese.

---

## 1. LaTeX to Quarto Converter (`tex2qmd.py`)

**Run Mode**: Manual (Run locally when adding new notes)

This script automates the conversion of LaTeX documents (`.tex`) into Quarto Markdown (`.qmd`) format.

### Features

- **Automated Conversion**: Uses `quarto pandoc` to perform the core text conversion.
- **Math & Label Fixes**: Converts LaTeX `\label{...}` inside math blocks to Quarto's `{#eq-...}` syntax.
- **Theorem Environments**: Converts LaTeX theorem environments (`theorem`, `lemma`, `proposition`, `corollary`, `definition`, `example`, `remark`, `proof`, etc.) to Quarto's cross-referenceable format.
  - Supports `\label{thm:foo}` → `{#thm-foo}` for cross-referencing.
  - Supports `\ref{thm:foo}`, `\cref{thm:foo}`, `\autoref{thm:foo}` → `@thm-foo`.
- **Image Handling**: Converts `\includegraphics[width=0.8\textwidth]{path}` to Markdown image syntax with width attributes.
- **Citation Handling**: 
  - Converts `\cite{...}` to `[@...]`.
  - Detects `\bibliography{...}` and adds it to the YAML header.
  - **Smart Exclusion**: Automatically excludes `references.bib` from the YAML header if detected, as it is already configured globally in `_quarto.yml`.
  - **Local Bibliography**: If you use a separate `.bib` file (e.g., `mypaper.bib`) for a specific note, ensure it is in the **same directory** as your `.tex` file. The script will add it to the YAML header, applying it only to that note.
- **Filename Sanitization**: Replaces spaces in filenames with hyphens.
- **Language Support**: Generates theorem titles in Chinese (`zh`) or English (`en`).

### Usage

**Convert a single file:**

```bash
# Windows (default: Chinese titles)
python scripts/tex2qmd.py content/zh/notes/my-paper.tex

# Windows (English titles)
python scripts/tex2qmd.py content/en/notes/my-paper.tex en

# Linux/macOS
python3 scripts/tex2qmd.py content/en/notes/my-paper.tex en
```

**Convert all notes (recursive):**

```bash
# Windows (Chinese)
python scripts/tex2qmd.py content/zh/notes/

# Windows (English)
python scripts/tex2qmd.py content/en/notes/ en

# Linux/macOS
python3 scripts/tex2qmd.py content/en/notes/ en
```

### Supported Theorem Environments

| LaTeX Environment | Quarto ID Prefix | Chinese Title | English Title |
|-------------------|------------------|---------------|---------------|
| `theorem`         | `thm-`           | 定理          | Theorem       |
| `lemma`           | `lem-`           | 引理          | Lemma         |
| `proposition`     | `prp-`           | 命题          | Proposition   |
| `corollary`       | `cor-`           | 推论          | Corollary     |
| `definition`      | `def-`           | 定义          | Definition    |
| `example`         | `exm-`           | 例            | Example       |
| `remark`          | `rem-`           | 注            | Remark        |
| `assumption`      | `asm-`           | 假设          | Assumption    |
| `conjecture`      | `cnj-`           | 猜想          | Conjecture    |
| `exercise`        | `exr-`           | 练习          | Exercise      |
| `proof`           | (no ID)          | 证明          | Proof         |

### Example

**LaTeX Input:**

```latex
\begin{theorem}[Fermat's Last Theorem]\label{thm:fermat}
For $n > 2$, there are no positive integers $a, b, c$ such that $a^n + b^n = c^n$.
\end{theorem}

\begin{proof}
The proof is left as an exercise for the reader. See \ref{thm:fermat}.
\end{proof}
```

**Quarto Output:**

```markdown
::: {#thm-fermat}
## 定理 (Fermat's Last Theorem)

For $n > 2$, there are no positive integers $a, b, c$ such that $a^n + b^n = c^n$.
:::

::: {.proof}
## 证明

The proof is left as an exercise for the reader. See @thm-fermat.
:::
```

---

## 2. Automatic Translation (`sync_deepseek.py`)

**Run Mode**: Automated (Runs in GitHub Actions) / Manual (Preview)

This script uses the DeepSeek API to automatically translate content between Chinese (`content/zh`) and English (`content/en`).

### Feature

- **Bi-directional Sync**: Translates `zh` -> `en` and `en` -> `zh`.
- **Homepage Sync**: In addition to folder syncing, it automatically translates the root `index.qmd` (Chinese Homepage) to `content/en/index.qmd` (English Homepage).
- **Incremental Update**: Only translates files that are newer than their counterparts.
- **Manual Protection**: If you need to manually edit a translated file, you **MUST** remove the `<!-- Auto-generated ... -->` marker at the end of the file. Otherwise, your changes will be overwritten during the next sync.
- **YAML Aware**: Translates `title` and `description` in YAML headers while preserving structure.

### Prerequisites

- Set the `DEEPSEEK_API_KEY` environment variable (configured in GitHub Secrets).

### Usage

**Automated**: This script runs automatically via GitHub Actions whenever you push changes to the repository. You don't need to do anything.

**Manual (Preview)**: If you want to preview the translation results locally before pushing:

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="your-key-here"
python scripts/sync_deepseek.py

# Linux/macOS
export DEEPSEEK_API_KEY="your-key-here"
python3 scripts/sync_deepseek.py
```

---
---

## 脚本说明文档 (中文版)

本文件夹包含用于维护学术网站的自动化脚本。

## 工作流概览

1. **手动步骤**：使用 `tex2qmd.py` 将您的 LaTeX 笔记转换为 Quarto Markdown。
2. **自动步骤**：`sync_deepseek.py` 脚本会在 GitHub Actions 部署过程中（参考 `publish.yml`）自动运行，负责中英文内容的互译。

---

## 1. LaTeX 转 Quarto 转换器 (`tex2qmd.py`)

**运行方式**：手动运行（在添加新笔记时在本地执行）

此脚本用于自动将 LaTeX 文档 (`.tex`) 转换为 Quarto Markdown (`.qmd`) 格式。

### 功能

- **自动转换**：使用 `quarto pandoc` 进行核心文本转换。
- **数学公式与标签修复**：将数学块内的 `\label{...}` 转换为 Quarto 的 `{#eq-...}` 语法。
- **定理环境支持**：将 LaTeX 定理环境（`theorem`、`lemma`、`proposition`、`corollary`、`definition`、`example`、`remark`、`proof` 等）转换为 Quarto 可交叉引用的格式。
  - 支持 `\label{thm:foo}` → `{#thm-foo}` 用于交叉引用。
  - 支持 `\ref{thm:foo}`、`\cref{thm:foo}`、`\autoref{thm:foo}` → `@thm-foo`。
- **图片处理**：将 `\includegraphics[width=0.8\textwidth]{path}` 转换为带宽度属性的 Markdown 图片语法。
- **参考文献处理**：
  - 将 `\cite{...}` 转换为 `[@...]`。
  - 检测 `\bibliography{...}` 并将其添加到 YAML 头中。
  - **智能排除全局引用**：如果你的 `.tex` 文件引用了 `references.bib`（这是本网站的全局参考文献库），脚本会自动在 YAML 中忽略它，避免重复引用。
  - **支持独立引用**：如果你想为某篇笔记使用单独的 `.bib` 文件（例如 `mypaper.bib`），请确保该 `.bib` 文件与你的 `.tex` 文件在**同一目录**下。脚本会自动将其添加到 YAML 头中，仅对该篇笔记生效。
- **文件名清洗**：将文件名中的空格替换为连字符。
- **多语言支持**：定理标题支持中文（`zh`）或英文（`en`）。

### 用法

**转换单个文件:**

```bash
# Windows（默认生成中文标题）
python scripts/tex2qmd.py content/zh/notes/my-paper.tex

# Windows（生成英文标题）
python scripts/tex2qmd.py content/en/notes/my-paper.tex en

# Linux/macOS
python3 scripts/tex2qmd.py content/en/notes/my-paper.tex en
```

**一键转换所有笔记（递归扫描 notes 目录）:**

```bash
# Windows（中文）
python scripts/tex2qmd.py content/zh/notes/

# Windows（英文）
python scripts/tex2qmd.py content/en/notes/ en

# Linux/macOS
python3 scripts/tex2qmd.py content/en/notes/ en
```

### 支持的定理环境

| LaTeX 环境       | Quarto ID 前缀 | 中文标题 | 英文标题    |
|------------------|----------------|----------|-------------|
| `theorem`        | `thm-`         | 定理     | Theorem     |
| `lemma`          | `lem-`         | 引理     | Lemma       |
| `proposition`    | `prp-`         | 命题     | Proposition |
| `corollary`      | `cor-`         | 推论     | Corollary   |
| `definition`     | `def-`         | 定义     | Definition  |
| `example`        | `exm-`         | 例       | Example     |
| `remark`         | `rem-`         | 注       | Remark      |
| `assumption`     | `asm-`         | 假设     | Assumption  |
| `conjecture`     | `cnj-`         | 猜想     | Conjecture  |
| `exercise`       | `exr-`         | 练习     | Exercise    |
| `proof`          | (无编号)       | 证明     | Proof       |

### 示例

**LaTeX 输入:**

```latex
\begin{theorem}[费马大定理]\label{thm:fermat}
对于 $n > 2$，不存在正整数 $a, b, c$ 使得 $a^n + b^n = c^n$。
\end{theorem}

\begin{proof}
证明留作读者练习。参见 \ref{thm:fermat}。
\end{proof}
```

**Quarto 输出:**

```markdown
::: {#thm-fermat}
## 定理 (费马大定理)

对于 $n > 2$，不存在正整数 $a, b, c$ 使得 $a^n + b^n = c^n$。
:::

::: {.proof}
## 证明

证明留作读者练习。参见 @thm-fermat。
:::
```

---

## 2. 自动翻译脚本 (`sync_deepseek.py`)

**运行方式**：自动化（在 GitHub Actions 中通过 `publish.yml` 运行）/ 手动运行（预览）

此脚本使用 DeepSeek API 在中文目录 (`content/zh`) 和英文目录 (`content/en`) 之间自动同步翻译内容。

### 功能

- **双向同步**：支持中译英及英译中。
- **首页同步**：除了同步 content 目录外，还会自动将根目录的 `index.qmd`（中文首页）同步翻译到 `content/en/index.qmd`（英文首页）。
- **增量更新**：仅翻译比目标文件更新的源文件。
- **手动保护**：如果需要手动修改翻译后的文件，**必须**先删除文件末尾的 `<!-- Auto-generated ... -->` 标记，否则下次同步时修改会被覆盖。
- **YAML 识别**：翻译 YAML 头中的标题和描述，同时保持结构不变。

### 前置要求

- 设置 `DEEPSEEK_API_KEY` 环境变量（在 GitHub Secrets 中配置）。

### 用法

**自动运行**：当您将代码推送到 GitHub 时，该脚本会通过 GitHub Actions 自动运行，无需人工干预。

**手动运行（预览）**：如果您想在推送前提前查看翻译效果，可以在本地手动运行：

```bash
# Windows PowerShell 手动运行（需要 API Key）
$env:DEEPSEEK_API_KEY="your-key-here"
python scripts/sync_deepseek.py

# Linux/macOS 手动运行
export DEEPSEEK_API_KEY="your-key-here"
python3 scripts/sync_deepseek.py
```
