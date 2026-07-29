"""
note2md — OneNote XML to Markdown Converter

Converts OneNote pages exported as XML (via export-onenote.ps1) into
structured Markdown files under notes/, preserving the Notebook → Section → Page hierarchy.

Usage:
    python convert-xml2md.py <xml_dir> [--output <notes_dir>]

Example:
    python convert-xml2md.py ./onenote_export
    python convert-xml2md.py ./onenote_export --output ./my_notes
"""

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

ONENOTE_NS = "http://schemas.microsoft.com/office/onenote/2013/onenote"
ET.register_namespace("", ONENOTE_NS)
NS = {"one": ONENOTE_NS}

# ---------- helpers ----------

def _safe_name(name: str) -> str:
    """Replace filesystem-unsafe characters."""
    return re.sub(r'[\\/:*?"<>|]', "_", name)


def _text_in_subtree(element: ET.Element) -> str:
    """Collect all text from <one:T> descendants, preserving order."""
    parts = []
    for t in element.iter(f"{{{ONENOTE_NS}}}T"):
        if t.text:
            parts.append(t.text)
    return "".join(parts)


def _is_list_item(elem: ET.Element) -> bool:
    """Check if an <one:OE> represents a bullet/number list item."""
    # List items have <one:List> child or <one:Tag> with list-related index
    return elem.find(f"one:List", NS) is not None or elem.find(f"one:Tag", NS) is not None


def _is_todo_item(elem: ET.Element) -> bool:
    """Check if an <one:OE> is a to-do / checkbox item."""
    tag = elem.find(f"one:Tag", NS)
    if tag is not None:
        idx = tag.get("index", "")
        return idx in ("0", "1", "2", "3")  # unchecked=0, checked=1
    return False


def _todo_checked(elem: ET.Element) -> bool:
    """Whether a to-do item is checked."""
    tag = elem.find(f"one:Tag", NS)
    return tag is not None and tag.get("index") == "1"


def _detect_heading_level(elem: ET.Element) -> int:
    """
    Heuristic heading detection from OneNote OE styles.
    OneNote uses quickStyleIndex / style attributes to mark headings.
    """
    # Check for explicit heading marker in style
    for attr_name in ("quickStyleIndex", "style"):
        val = elem.get(attr_name, "")
        if val and "heading" in val.lower():
            m = re.search(r"(\d+)", val)
            if m:
                return int(m.group(1))
    return 0


def _extract_images(elem: ET.Element) -> list[str]:
    """Extract image references from the page XML. (Placeholder — not yet implemented.)"""
    # Image extraction from OneNote XML is complex — pending implementation
    return []


# ---------- core conversion ----------

def _convert_oe_tree(element: ET.Element, depth: int = 0) -> list[str]:
    """
    Recursively convert an <one:OE> tree (OneNote paragraph) to Markdown.
    Returns a list of markdown lines.
    """
    lines = []

    # Skip empty / structural elements
    if element.tag == f"{{{ONENOTE_NS}}}Image":
        return []

    # Collect children that are meaningful
    children = list(element)

    # ---- HEADING ----
    heading_level = _detect_heading_level(element)
    if heading_level:
        text = _text_in_subtree(element).strip()
        prefix = "#" * min(heading_level, 6)
        lines.append(f"\n{prefix} {text}\n")
        return lines

    # ---- TO-DO / CHECKBOX ----
    if _is_todo_item(element):
        checked = _todo_checked(element)
        marker = "[x]" if checked else "[ ]"
        text = _text_in_subtree(element).strip()
        indent = "  " * depth
        lines.append(f"{indent}- {marker} {text}")
        # Process nested OE children (sub-items)
        for child in children:
            if child.tag == f"{{{ONENOTE_NS}}}OE":
                sub = _convert_oe_tree(child, depth + 1)
                lines.extend(sub)
        return lines

    # ---- BULLET / NUMBER LIST ----
    if _is_list_item(element):
        text = _text_in_subtree(element).strip()
        indent = "  " * depth
        lines.append(f"{indent}- {text}")
        for child in children:
            if child.tag == f"{{{ONENOTE_NS}}}OE":
                sub = _convert_oe_tree(child, depth + 1)
                lines.extend(sub)
        return lines

    # ---- TABLE ----
    if element.tag == f"{{{ONENOTE_NS}}}Table":
        rows = []
        for row_elem in element.findall(f"one:Row", NS):
            cells = []
            for cell in row_elem.findall(f"one:Cell", NS):
                cells.append(_text_in_subtree(cell).strip().replace("\n", " "))
            rows.append(cells)

        if not rows:
            return []

        # Build Markdown table
        col_count = max(len(r) for r in rows)
        # Header row
        header = "| " + " | ".join(rows[0][:col_count]) + " |"
        separator = "|" + "|".join([" --- " for _ in range(col_count)]) + "|"
        lines.append("")
        lines.append(header)
        lines.append(separator)
        for row in rows[1:]:
            padded = row + [""] * (col_count - len(row))
            lines.append("| " + " | ".join(padded[:col_count]) + " |")
        lines.append("")
        return lines

    # ---- IMAGE ----
    if element.tag == f"{{{ONENOTE_NS}}}Image":
        alt = element.get("alt", "image")
        lines.append(f"\n![{alt}](assets/{alt})\n")
        return lines

    # ---- PLAIN TEXT ----
    text = _text_in_subtree(element).strip()
    if text:
        indent = "  " * depth
        # Bold detection via font weight
        bold = element.get("bold") == "1"
        italic = element.get("italic") == "1"

        if bold and italic:
            text = f"***{text}***"
        elif bold:
            text = f"**{text}**"
        elif italic:
            text = f"*{text}*"

        lines.append(f"{indent}{text}")

    # Recurse into children that haven't been processed
    for child in children:
        if child.tag in (f"{{{ONENOTE_NS}}}OE", f"{{{ONENOTE_NS}}}Table", f"{{{ONENOTE_NS}}}Image"):
            lines.extend(_convert_oe_tree(child, depth))

    return lines


def convert_page_xml(xml_path: Path) -> tuple[dict, str]:
    """
    Convert a single OneNote page XML file to Markdown.

    Returns (frontmatter_dict, body_markdown).
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Extract page metadata
    page_meta = root.find(f"one:Page", NS)
    if page_meta is None:
        page_meta = root

    title = ""
    title_elem = root.find(f".//one:Title//one:T", NS)
    if title_elem is not None and title_elem.text:
        title = title_elem.text.strip()

    page_date = ""
    date_attr = page_meta.get("dateTime") or page_meta.get("lastModifiedTime", "")
    if date_attr:
        try:
            page_date = datetime.fromisoformat(date_attr.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except ValueError:
            page_date = date_attr[:10]  # fallback: take YYYY-MM-DD

    # If no title from metadata, use filename
    if not title:
        title = xml_path.stem

    # Build frontmatter
    frontmatter = {
        "date": page_date or datetime.now().strftime("%Y-%m-%d"),
        "type": "note",
        "title": title,
        "tags": [],
    }

    # Convert body
    body_lines = []
    if title:
        body_lines.append(f"# {title}\n")

    # Process all top-level OEs
    for oe in root.findall(f".//one:Outline//one:OEChildren/one:OE", NS):
        body_lines.extend(_convert_oe_tree(oe))
    for oe in root.findall(f".//one:OEChildren/one:OE", NS):
        body_lines.extend(_convert_oe_tree(oe))

    body = _clean_markdown("\n".join(body_lines))
    return frontmatter, body


def _clean_markdown(md: str) -> str:
    """Clean up generated Markdown."""
    # Collapse 3+ blank lines to 2
    md = re.sub(r"\n{3,}", "\n\n", md)
    # Remove trailing whitespace
    md = "\n".join(line.rstrip() for line in md.split("\n"))
    return md.strip() + "\n"


def _detect_type(page_name: str, content: str) -> str:
    """
    Heuristic: guess the note type from the page name and content patterns.
    Returns a type string (e.g. "meeting", "daily", "note").
    """
    lower = content.lower()
    if any(kw in page_name.lower() for kw in ["例会", "会议", "meeting", "review"]):
        return "meeting"
    if any(kw in page_name.lower() for kw in ["日记", "daily", "journal"]):
        return "daily"
    if any(kw in lower for kw in ["待办", "todo", "action item"]):
        return "task"
    return "note"


# ---------- main pipeline ----------

def convert_all(xml_dir: Path, notes_dir: Path):
    """
    Walk the exported XML directory and convert all pages to Markdown.
    """
    if not xml_dir.exists():
        print(f"Error: XML export directory not found: {xml_dir}")
        sys.exit(1)

    total = 0
    for nb_dir in sorted(xml_dir.iterdir()):
        if not nb_dir.is_dir():
            continue
        nb_name = nb_dir.name

        for sec_dir in sorted(nb_dir.iterdir()):
            if not sec_dir.is_dir():
                continue
            sec_name = sec_dir.name

            xml_files = sorted(sec_dir.glob("*.xml"))
            if not xml_files:
                continue

            # Create target directory
            target_dir = notes_dir / nb_name / sec_name
            target_dir.mkdir(parents=True, exist_ok=True)

            for xml_file in xml_files:
                try:
                    fm, body = convert_page_xml(xml_file)

                    # Detect type
                    fm["type"] = _detect_type(fm["title"], body)

                    # Build output
                    frontmatter_yaml = _format_frontmatter(fm)
                    md_path = target_dir / f"{_safe_name(fm['title'])}.md"

                    # Avoid overwrite
                    counter = 2
                    while md_path.exists():
                        md_path = target_dir / f"{_safe_name(fm['title'])}({counter}).md"
                        counter += 1

                    md_path.write_text(frontmatter_yaml + "\n" + body, encoding="utf-8")
                    total += 1

                except Exception as e:
                    print(f"  ✗ Failed: {xml_file.name} — {e}")

    print(f"\n✅ Converted {total} pages → {notes_dir.resolve()}")


def _format_frontmatter(fm: dict) -> str:
    """Format a dict as YAML frontmatter."""
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            if v:
                items = ", ".join(v)
                lines.append(f"{k}: [{items}]")
            else:
                lines.append(f"{k}: []")
        elif isinstance(v, str):
            if any(c in v for c in ':#{}[]&*!|>\'"@`,'):
                lines.append(f'{k}: "{v}"')
            else:
                lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Convert OneNote XML export to structured Markdown notes"
    )
    parser.add_argument(
        "xml_dir",
        help="Path to the OneNote XML export directory (from export-onenote.ps1)",
    )
    parser.add_argument(
        "--output", "-o",
        default="./notes",
        help="Output directory for Markdown notes (default: ./notes)",
    )
    args = parser.parse_args()

    xml_dir = Path(args.xml_dir).resolve()
    notes_dir = Path(args.output).resolve()

    print(f"Converting {xml_dir} → {notes_dir}")
    convert_all(xml_dir, notes_dir)


if __name__ == "__main__":
    main()
