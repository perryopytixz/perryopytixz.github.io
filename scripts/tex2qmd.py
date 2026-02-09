#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AI辅助生成的代码
"""
将 LaTeX (.tex) 文件转换为 Quarto Markdown (.qmd) 文件。由 AI 生成。

支持的 LaTeX 环境:
- 公式环境: equation, align, etc. (包括 \label 和 \eqref 引用)
- 定理环境: theorem, lemma, proposition, corollary, definition, example, remark, proof
- 图片: \includegraphics 路径转换
"""

import os
import sys
import re
import subprocess
import shutil

# ==========================================
# 定理环境映射表
# LaTeX 环境名 -> Quarto callout 类型和中文标题
# ==========================================
THEOREM_ENVS = {
    'theorem':     {'type': 'thm', 'title': '定理', 'title_en': 'Theorem'},
    'lemma':       {'type': 'lem', 'title': '引理', 'title_en': 'Lemma'},
    'proposition': {'type': 'prp', 'title': '命题', 'title_en': 'Proposition'},
    'corollary':   {'type': 'cor', 'title': '推论', 'title_en': 'Corollary'},
    'definition':  {'type': 'def', 'title': '定义', 'title_en': 'Definition'},
    'example':     {'type': 'exm', 'title': '例', 'title_en': 'Example'},
    'remark':      {'type': 'rem', 'title': '注', 'title_en': 'Remark'},
    'assumption':  {'type': 'asm', 'title': '假设', 'title_en': 'Assumption'},
    'conjecture':  {'type': 'cnj', 'title': '猜想', 'title_en': 'Conjecture'},
    'exercise':    {'type': 'exr', 'title': '练习', 'title_en': 'Exercise'},
}

# Proof 环境特殊处理（不需要编号）
PROOF_ENV = 'proof'


def convert_tex_to_qmd(tex_file_path, lang='zh'):
    if not os.path.exists(tex_file_path):
        print(f"Error: File not found: {tex_file_path}")
        return

    # 1. 准备输出文件名
    dirname = os.path.dirname(tex_file_path)
    basename = os.path.basename(tex_file_path)
    name_without_ext = os.path.splitext(basename)[0]
    clean_name = name_without_ext.replace(" ", "-")
    qmd_file_path = os.path.join(dirname, f"{clean_name}.qmd")

    print(f"Processing: {tex_file_path} -> {qmd_file_path}")

    # 2. 读取 LaTeX 内容 (仅用于提取元数据)
    with open(tex_file_path, 'r', encoding='utf-8') as f:
        raw_tex_content = f.read()

    # 3. 提取元数据
    title_match = re.search(r'\\title\{(.*?)\}', raw_tex_content, re.DOTALL)
    author_match = re.search(r'\\author\{(.*?)\}', raw_tex_content, re.DOTALL)
    
    title = title_match.group(1) if title_match else clean_name
    author = author_match.group(1) if author_match else "Perry"
    date = "last-modified"

    # 提取参考文献
    bib_match = re.search(r'\\bibliography\{(.*?)\}', raw_tex_content)
    bib_resource_match = re.search(r'\\addbibresource\{(.*?)\}', raw_tex_content)
    
    bib_files = []
    if bib_match:
        # \bibliography 可能包含逗号分隔的多个文件
        files = bib_match.group(1).split(',')
        for f in files:
            f = f.strip()
            if not f.endswith('.bib'):
                f += '.bib'
            bib_files.append(f)
            
    if bib_resource_match:
        f = bib_resource_match.group(1).strip()
        if f not in bib_files:
            bib_files.append(f)

    # 提取 bibliographystyle (仅供参考)
    style_match = re.search(r'\\bibliographystyle\{(.*?)\}', raw_tex_content)
    bib_style = style_match.group(1) if style_match else None

    # 4. 预处理 LaTeX 内容
    # 提取 document 环境内的内容
    body_match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', raw_tex_content, re.DOTALL)
    body_content = body_match.group(1) if body_match else raw_tex_content

    # 5. 使用 Pandoc 转换为 Markdown
    if shutil.which("quarto"):
        command = ['quarto', 'pandoc']
    elif shutil.which("pandoc"):
        command = ['pandoc']
    else:
        print("Error: Neither 'quarto' nor 'pandoc' found in PATH.")
        return

    try:
        # 使用 -t markdown-raw_tex 以保留 \label 等原始命令，方便后续处理
        process = subprocess.Popen(
            command + ['-f', 'latex', '-t', 'markdown-raw_tex', '--wrap=none'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        md_output, stderr = process.communicate(input=body_content)
        
        if process.returncode != 0:
            print(f"Pandoc Warning: {stderr}")
            if not md_output:
                return

    except Exception as e:
        print(f"Execution Error: {e}")
        return

    # ==========================================
    # 6. 针对 Pandoc 输出的修复
    # ==========================================

    # 辅助函数：清理 Label ID (冒号转连字符，确保 eq- 开头)
    def clean_label_id(label):
        clean = label.replace(':', '-')
        if not clean.startswith('eq-'):
            if clean.startswith('eq'):
                clean = 'eq-' + clean[2:]
            else:
                clean = 'eq-' + clean
        return clean

    def clean_figure_id(label):
        clean = label.strip().replace(':', '-')
        if clean.startswith('fig-'):
            return clean
        if clean.startswith('fig') and len(clean) > 3 and clean[3] in ['-', '_']:
            return 'fig-' + clean[4:]
        return f'fig-{clean}'

    # A. 修复公式块中的 label
    # Pandoc 输出: $$ \label{eq:foo} ... $$
    # 目标: $$ ... $$ {#eq-foo}
    
    def fix_math_block(match):
        content = match.group(1)
        # 寻找 \label{...}
        label_match = re.search(r'\\label\{([^}]+)\}', content)
        label_str = ""
        if label_match:
            raw_label = label_match.group(1)
            label_str = f" {{#{clean_label_id(raw_label)}}}"
            # 删除 \label{...}
            content = content.replace(label_match.group(0), "")
        
        return f"$${content.strip()}$${label_str}"

    # 匹配 $$ ... $$ 块
    md_output = re.sub(r'\$\$(.*?)\$\$', fix_math_block, md_output, flags=re.DOTALL)

    # B. 修复引用
    # 情况 1: Pandoc 生成的复杂链接 [\[eq:foo\]](#eq:foo){...}
    md_output = re.sub(r'\[\\?\[(.*?)\\?\]\]\(#.*?\)\{.*?\}', lambda m: f"@{clean_label_id(m.group(1))}", md_output)
    
    # 情况 2: 残留的 \eqref{eq:foo}
    md_output = re.sub(r'\\eqref\{([^}]+)\}', lambda m: f"@{clean_label_id(m.group(1))}", md_output)
    
    # 情况 3: 残留的 \ref{eq:foo}
    md_output = re.sub(r'\\ref\{([^}]+)\}', lambda m: f"@{clean_label_id(m.group(1))}", md_output)

    # C. 清理 Abstract 标题 (Pandoc 可能会给它加 {.unnumbered})
    md_output = md_output.replace(r'{#abstract .unnumbered}', '')

    # D. 处理定理环境
    # LaTeX: \begin{theorem}[名称]\label{thm:foo} 内容 \end{theorem}
    # Quarto: ::: {#thm-foo .callout-note title="定理 (名称)"} \n 内容 \n :::
    
    def convert_theorem_env(match):
        env_name = match.group(1)  # theorem, lemma, etc.
        options = match.group(2) or ""  # [可选的名称]
        content = match.group(3)
        
        if env_name not in THEOREM_ENVS:
            return match.group(0)  # 不识别的环境，保持原样
        
        env_info = THEOREM_ENVS[env_name]
        env_type = env_info['type']
        env_title = env_info['title'] if lang == 'zh' else env_info['title_en']
        
        # 提取 label
        label_match = re.search(r'\\label\{([^}]+)\}', content)
        label_id = ""
        if label_match:
            raw_label = label_match.group(1)
            # 清理 label: thm:foo -> thm-foo
            clean = raw_label.replace(':', '-')
            # 确保有正确的前缀
            if not clean.startswith(f'{env_type}-'):
                if clean.startswith(env_type):
                    clean = f'{env_type}-{clean[len(env_type):]}'
                else:
                    clean = f'{env_type}-{clean}'
            label_id = clean
            # 删除 \label{...}
            content = content.replace(label_match.group(0), "")
        
        # 提取可选名称 [名称]
        opt_name = ""
        if options:
            opt_name = options.strip('[]').strip()
        
        # 构建标题
        if opt_name:
            title_str = f'{env_title} ({opt_name})'
        else:
            title_str = env_title
        
        # 构建 Quarto div
        if label_id:
            header = f'::: {{#{label_id}}}'
        else:
            header = f'::: {{{env_type}}}'
        
        # 清理内容前后空白
        content = content.strip()
        
        return f'{header}\n## {title_str}\n\n{content}\n:::'
    
    # 匹配定理环境: \begin{theorem}[可选名称] ... \end{theorem}
    for env_name in THEOREM_ENVS.keys():
        pattern = rf'\\begin\{{{env_name}\}}(\[[^\]]*\])?(.*?)\\end\{{{env_name}\}}'
        md_output = re.sub(pattern, convert_theorem_env, md_output, flags=re.DOTALL)
    
    # E. 处理 proof 环境
    def convert_proof_env(match):
        options = match.group(1) or ""
        content = match.group(2).strip()
        
        proof_title = "证明" if lang == 'zh' else "Proof"
        if options:
            opt_name = options.strip('[]').strip()
            proof_title = f"{proof_title} ({opt_name})"
        
        return f'::: {{.proof}}\n## {proof_title}\n\n{content}\n:::'
    
    pattern = rf'\\begin\{{{PROOF_ENV}\}}(\[[^\]]*\])?(.*?)\\end\{{{PROOF_ENV}\}}'
    md_output = re.sub(pattern, convert_proof_env, md_output, flags=re.DOTALL)

    # F. 处理定理引用
    # \ref{thm:foo} -> @thm-foo
    # \cref{thm:foo} -> @thm-foo (cleveref 包的引用)
    # \autoref{thm:foo} -> @thm-foo (hyperref 包的引用)
    
    def clean_theorem_ref(label):
        """清理定理引用标签"""
        clean = label.replace(':', '-')
        return clean
    
    # \cref{...} 和 \autoref{...}
    md_output = re.sub(r'\\cref\{([^}]+)\}', lambda m: f"@{clean_theorem_ref(m.group(1))}", md_output)
    md_output = re.sub(r'\\autoref\{([^}]+)\}', lambda m: f"@{clean_theorem_ref(m.group(1))}", md_output)
    md_output = re.sub(r'\\Cref\{([^}]+)\}', lambda m: f"@{clean_theorem_ref(m.group(1))}", md_output)
    
    # 注意: \ref{} 已在前面的公式引用部分处理，但这里再处理一次确保覆盖定理引用
    # 只处理非 eq 开头的引用（eq 开头的已经处理过了）
    def fix_non_eq_ref(match):
        label = match.group(1)
        if label.startswith('eq'):
            return f"@{clean_label_id(label)}"
        else:
            return f"@{clean_theorem_ref(label)}"
    
    md_output = re.sub(r'\\ref\{([^}]+)\}', fix_non_eq_ref, md_output)

    # G. 处理图片路径
    # \includegraphics[options]{path} -> ![](path)
    # Pandoc 应该已经处理了大部分，但可能有残留
    
    def convert_includegraphics(match):
        options = match.group(1) or ""
        path = match.group(2)
        
        # 清理路径
        # 移除可能的 {} 包裹
        path = path.strip('{}')
        
        # 处理常见的路径格式
        # 1. 移除 figures/, images/, img/ 等前缀（如果需要）
        # 2. 添加扩展名（如果没有）
        
        # 检查是否有扩展名
        if not re.search(r'\.\w+$', path):
            # 没有扩展名，尝试常见格式
            for ext in ['.png', '.jpg', '.jpeg', '.pdf', '.svg']:
                # 这里只是添加一个默认扩展名，实际文件可能需要手动确认
                pass
            # 默认不添加，保持原样让用户手动处理
        
        # 提取宽度参数
        width_match = re.search(r'width=([0-9.]+)\\?(textwidth|linewidth|columnwidth)?', options)
        width_str = ""
        if width_match:
            width_val = float(width_match.group(1))
            width_unit = width_match.group(2) or "textwidth"
            # 转换为百分比
            width_percent = int(width_val * 100)
            width_str = f'{{width="{width_percent}%"}}'
        
        return f'![]({path}){width_str}'
    
    # 匹配 \includegraphics[...]{...} 或 \includegraphics{...}
    md_output = re.sub(
        r'\\includegraphics\s*(?:\[([^\]]*)\])?\s*\{([^}]+)\}',
        convert_includegraphics,
        md_output
    )
    
    # H. 清理图片环境 (figure)
    # Pandoc 可能留下 \begin{figure} ... \end{figure}
    # 简单处理：提取 caption 和 label
    
    def convert_figure_env(match):
        content = match.group(1)
        
        # 提取 caption
        caption_match = re.search(r'\\caption\{([^}]+)\}', content)
        caption = caption_match.group(1) if caption_match else ""
        
        # 提取 label
        label_match = re.search(r'\\label\{([^}]+)\}', content)
        label = ""
        if label_match:
            raw_label = label_match.group(1)
            label = clean_figure_id(raw_label)
        
        # 提取图片（已经转换过的 ![](path) 格式）
        img_match = re.search(r'!\[([^\]]*)\]\(([^)]+)\)(\{[^}]*\})?', content)
        if img_match:
            img_alt = img_match.group(1)
            img_path = img_match.group(2)
            img_opts = img_match.group(3) or ""

            # 若图片本身已有 ID，做兼容兜底
            inline_label_match = re.search(r'#([^\s}]+)', img_opts)
            if inline_label_match and not label:
                label = clean_figure_id(inline_label_match.group(1))

            # 清理已有 ID，避免重复
            opts_inner = img_opts.strip()[1:-1].strip() if img_opts else ""
            if opts_inner:
                opts_inner = re.sub(r'#\S+', '', opts_inner).strip()

            # 构建 Quarto 图片格式
            attr_parts = []
            if label:
                attr_parts.append(f'#{label}')
            if opts_inner:
                attr_parts.append(opts_inner)

            attr_str = f'{{{" ".join(attr_parts)}}}' if attr_parts else ""
            alt_text = caption if caption else img_alt
            return f'![{alt_text}]({img_path}){attr_str}'
        
        # 如果没找到图片，返回原内容
        return content
    
    md_output = re.sub(
        r'\\begin\{figure\}.*?(.*?)\\end\{figure\}',
        convert_figure_env,
        md_output,
        flags=re.DOTALL
    )

    # I. 修复 Pandoc 的图编号写法（fig:foo -> fig-foo）
    md_output = re.sub(
        r'\{#fig:([^\s}]+)',
        lambda m: '{#' + clean_figure_id('fig:' + m.group(1)),
        md_output
    )

    # J. 将 Pandoc 生成的图引用链接统一为 Quarto 交叉引用语法
    md_output = re.sub(
        r'\[[^\]]*\]\(#(fig[:\-][^)]+)\)\{[^}]*reference-type="[^"]+"[^}]*\}',
        lambda m: f'@{clean_figure_id(m.group(1))}',
        md_output
    )

    # K. 移除第一个标题 (如果它和 YAML title 重复)
    # 简单的启发式：如果第一行是 # Title，且 Title 与 YAML title 相似，则移除
    lines = md_output.lstrip().split('\n')
    if lines and lines[0].startswith('# '):
        # 这里直接移除第一个 H1 标题，因为 Quarto 会自动显示 YAML 中的 title
        md_output = '\n'.join(lines[1:])

    # 7. 组装最终内容
    yaml_header = f"""---
title: "{title}"
author: "{author}"
date: {date}
lang: {lang}
format: html
"""
    # 过滤掉 'references.bib'，因为它已经在 _quarto.yml 中全局配置了
    # 这可以防止路径问题（例如在 notes/ 子目录中寻找 references.bib）
    local_bib_files = [f for f in bib_files if f != 'references.bib']

    if local_bib_files:
        if len(local_bib_files) == 1:
             yaml_header += f"bibliography: {local_bib_files[0]}\n"
        else:
             yaml_header += "bibliography:\n"
             for f in local_bib_files:
                 yaml_header += f"  - {f}\n"

    if bib_style:
        yaml_header += f"# bibliographystyle: {bib_style} (注意: Quarto 使用 CSL，而不是 BibTeX 样式)\n"

    yaml_header += "---\n\n"
    final_content = yaml_header + md_output

    # 8. 写入文件
    with open(qmd_file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"Success! Created {qmd_file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/tex2qmd.py <path_to_tex_file_or_directory> [lang]")
        print("  lang: 'zh' (中文, 默认) or 'en' (English)")
        sys.exit(1)

    target = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else 'zh'
    
    if lang not in ['zh', 'en']:
        print(f"Warning: Unsupported language '{lang}', using 'zh' as default.")
        lang = 'zh'
    
    if os.path.isfile(target):
        convert_tex_to_qmd(target, lang)
    elif os.path.isdir(target):
        for root, dirs, files in os.walk(target):
            for file in files:
                if file.endswith(".tex"):
                    convert_tex_to_qmd(os.path.join(root, file), lang)
