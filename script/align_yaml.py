import re
import glob
import unicodedata
from pathlib import Path


def split_elements(content: str) -> list[str]:
    """
    将字符串内容按逗号分割成元素列表，同时考虑括号和引号的嵌套情况。
    """
    elements = []
    current = []
    bracket_level = 0
    in_quote = False
    for char in content:
        if char == '"' and not in_quote:
            in_quote = True
        elif char == '"' and in_quote:
            in_quote = False
        elif char in ['[', '{', '('] and not in_quote:
            bracket_level += 1
        elif char in [']', '}', ')'] and not in_quote:
            bracket_level -= 1
        elif char == ',' and bracket_level == 0 and not in_quote:
            elements.append(''.join(current).strip())
            current = []
            continue
        current.append(char)
    if current:
        elements.append(''.join(current).strip())
    return elements


def get_display_width(s: str) -> int:
    """
    计算字符串的显示宽度，考虑中文字符和英文字符的宽度差异。
    """
    width = 0
    for char in s:
        if unicodedata.east_asian_width(char) in 'WF':
            width += 1.7
        else:
            width += 1
    return int(width)


def align_yaml_columns(_directory: Path):
    """
    对指定目录中的所有 YAML 文件进行列对齐。
    """
    pattern = re.compile(r'^(\s*)-\s\[(.*)]$')
    yaml_files = glob.glob(
        str(_directory / '**' / 'test_data.yaml'), recursive=True)
    print(f"Aligning columns in {len(yaml_files)} YAML files...")

    for file_path in yaml_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_block = []
        all_blocks = []

        # 解析文件中的块
        for line_num, line in enumerate(lines):
            line_stripped = line.rstrip()
            match = pattern.match(line_stripped)
            if match:
                indent, content = match.groups()
                elements = split_elements(content)
                current_block.append((line_num, indent, elements))
            else:
                if current_block:
                    all_blocks.append(current_block)
                    current_block = []
        if current_block:
            all_blocks.append(current_block)

        # 对齐每个块中的列
        for block in all_blocks:
            if not block:
                continue

            all_elements = [elem for _, _, elem in block]
            num_columns = max(len(elem)
                              for elem in all_elements) if all_elements else 0
            max_widths = [0] * num_columns if num_columns else []

            # 计算每列的最大宽度
            for row in all_elements:
                for j in range(len(row)):
                    max_widths[j] = max(
                        max_widths[j], get_display_width(row[j]))

            new_lines = []
            # 生成对齐后的新行
            for line_num, indent, elements in block:
                formatted = [elem.ljust(width - get_display_width(elem) + len(elem))
                             for elem, width in zip(elements, max_widths)]
                new_content = ', '.join(formatted)
                new_line = f"{indent}- [{new_content}]"
                new_lines.append((line_num, new_line))

            # 替换原文件中的行
            for line_num, new_line in new_lines:
                lines[line_num] = new_line + '\n'

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)


if __name__ == "__main__":
    rootdir = Path(__file__).parent.parent
    align_yaml_columns(rootdir / "testcases" / "api" / "api_test")
