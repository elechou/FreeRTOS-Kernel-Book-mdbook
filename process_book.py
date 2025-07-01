

import os
import re

def sanitize_filename(name):
    """Converts a heading title to a safe filename, keeping the full number."""
    section_number_match = re.search(r'^(\d+(\.\d+)*)\s*', name)
    section_number = section_number_match.group(1) if section_number_match else ''

    title_part = re.sub(r'^\d+(\.\d+)*\s*', '', name).strip()
    title_part = re.sub(r'[\s/]', '-', title_part)
    title_part = re.sub(r'[^a-zA-Z0-9\-]', '', title_part).lower()

    if section_number:
        return f"{section_number}-{title_part}.md"
    else:
        return f"{title_part}.md"

def process_chapters():
    """
    Splits chapter files into a new directory structure without modifying originals,
    corrects image paths, and generates a new SUMMARY.md file with clean titles.
    """
    src_dir = 'src'
    if not os.path.isdir(src_dir):
        print(f"Error: '{src_dir}' directory not found.")
        return

    chapter_files = sorted([f for f in os.listdir(src_dir) if f.startswith('ch') and f.endswith('.md')])

    summary_lines = ["# Summary\n"]
    summary_lines.append(f"[Mastering the FreeRTOS™ Real Time Kernel](booktitle.md)")
    summary_lines.append(f"[List of Abbreviations](abbreviations.md)\n")

    part_titles = {
        1: "# Getting Started",
        3: "# Core Kernel Concepts",
        5: "# Kernel Objects and Communication",
        11: "# Advanced Topics"
    }

    # Regex to find and replace image blocks for centering and newlines
    # Captures: (1) full block, (2) image path, (3) figure number, (4) caption text
    figure_block_pattern = re.compile(
        r'(\* \* \*\s*\n\s*!\[\]\((.*?)\)\s*\n\s*\*\*\*Figure\s*(\d+(?:\.\d+)*)\*\*\*\s*(.*?)\s*\n\s*\* \* \*)',
        re.DOTALL
    )

    def replace_figure_block(match):
        image_path = match.group(2)
        figure_number = match.group(3)
        caption_text = match.group(4)

        # Construct the new HTML block with centering and newline after image
        return f"""<div align=\"center\">\n<img src=\"{image_path}\" alt=\"Figure {figure_number} {caption_text}\"/>\n\n***Figure {figure_number}*** *{caption_text}*\n</div>"""

    for filename in chapter_files:
        chapter_num_match = re.search(r'ch(\d+)', filename)
        if not chapter_num_match:
            continue
        chapter_num = int(chapter_num_match.group(1))

        if chapter_num in part_titles:
            summary_lines.append(f"{part_titles[chapter_num]}")

        chapter_dir_name = f'ch{chapter_num:02d}'
        chapter_path = os.path.join(src_dir, chapter_dir_name)
        os.makedirs(chapter_path, exist_ok=True)

        with open(os.path.join(src_dir, filename), 'r', encoding='utf-8') as f:
            content = f.read()

        sections = re.split(r'(\n##\s+.*)', content)

        intro_content = sections[0].strip()
        # Correct image paths for the intro file: from 'media/' to '../media/'
        intro_content_corrected = re.sub(r'\(media/', '(../media/', intro_content)
        # Apply centering and newline for image blocks in intro content
        intro_content_final = figure_block_pattern.sub(replace_figure_block, intro_content_corrected)

        readme_path = os.path.join(chapter_path, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(intro_content_final)

        h1_match = re.search(r'^#\s*(.*)', intro_content)
        chapter_title_full = h1_match.group(1).strip() if h1_match else f"Chapter {chapter_num}"

        chapter_title_clean = re.sub(r'^\d+\s*', '', chapter_title_full).strip()
        summary_lines.append(f"- [{chapter_title_clean}]({chapter_dir_name}/README.md)")

        for i in range(1, len(sections), 2):
            heading_line = sections[i].strip()
            body = sections[i+1].strip()

            heading_text_full = heading_line.replace("##", "").strip()

            full_section_content = f"{heading_line}\n\n{body}"
            # Correct image paths for sub-section files: from 'media/' to '../media/'
            full_section_content_corrected = re.sub(r'\(media/', '(../media/', full_section_content)
            # Apply centering and newline for image blocks in sub-section content
            full_section_content_final = figure_block_pattern.sub(replace_figure_block, full_section_content_corrected)

            new_filename = sanitize_filename(heading_text_full)
            new_filepath = os.path.join(chapter_path, new_filename)

            with open(new_filepath, 'w', encoding='utf-8') as f:
                f.write(full_section_content_final)

            heading_text_clean = re.sub(r'^\d+(\.\d+)*\s*', '', heading_text_full).strip()
            summary_lines.append(f"  - [{heading_text_clean}]({chapter_dir_name}/{new_filename})")

        summary_lines.append("")

    summary_filepath = os.path.join(src_dir, 'SUMMARY.md')
    with open(summary_filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines))

    print("Processing complete.")
    print(f"New directory structure created in '{src_dir}'.")
    print("Original chapter files remain unmodified.")
    print(f"New 'SUMMARY.md' has been generated in '{src_dir}' with clean titles.")

if __name__ == "__main__":
    process_chapters()
