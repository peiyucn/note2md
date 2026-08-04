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
import html
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# Windows 终端 GBK 编码兼容：强制 stdout 使用 UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ONENOTE_NS = "http://schemas.microsoft.com/office/onenote/2013/onenote"
ET.register_namespace("", ONENOTE_NS)
NS = {"one": ONENOTE_NS}

# ---------- helpers ----------

def _safe_name(name: str) -> str:
    """Replace filesystem-unsafe characters."""
    name = name.replace("\n", "").replace("\r", "")
    return re.sub(r'[\\/:*?"<>|]', "_", name)


def _text_in_subtree(element: ET.Element) -> str:
    """Collect all text from <one:T> descendants, stripping OneNote inline HTML spans."""
    parts = []
    for t in element.iter(f"{{{ONENOTE_NS}}}T"):
        if t.text:
            parts.append(t.text)
    raw = "".join(parts)
    # Strip OneNote inline HTML spans (e.g. <span style='...' lang=...>text</span>)
    raw = re.sub(r"<[^>]+>", "", raw)
    return html.unescape(raw)


def _strip_html(text: str) -> str:
    """Remove HTML tags from text (used for OneNote inline formatting)."""
    return re.sub(r"<[^>]+>", "", text)


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

    # If this OE has container children (Table, OEChildren), it's just a wrapper;
    # skip its own text and only recurse into children
    for child in children:
        child_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if child_tag in ("Table", "OEChildren"):
            for c in children:
                lines.extend(_convert_oe_tree(c, depth))
            return lines

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
                # Process each OE within the cell separately to preserve line breaks
                oe_texts = []
                for oe in cell.findall(f"one:OEChildren/one:OE", NS):
                    t = _text_in_subtree(oe).strip()
                    if t:
                        oe_texts.append(t)
                # Join with HTML <br> for line breaks within cells
                cells.append(" <br> ".join(oe_texts))
            # Skip empty rows (all cells empty)
            if any(c for c in cells):
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
    # Prefer page name attribute (clean, no formatting cruft)
    title = page_meta.get("name", "").strip()
    # Fallback: extract from Title OE subtree
    if not title:
        title_oe = root.find(f".//one:Title/one:OE", NS)
        if title_oe is not None:
            title = _text_in_subtree(title_oe).strip()
    # Last resort: filename
    if not title:
        title = xml_path.stem

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

    # Process all top-level OEs (avoid double-processing with a single XPath)
    seen_ids = set()
    for oe in root.findall(f".//one:Outline/one:OEChildren/one:OE", NS):
        oe_id = oe.get("objectID", "")
        if oe_id not in seen_ids:
            seen_ids.add(oe_id)
            body_lines.extend(_convert_oe_tree(oe))
    # Also process direct page OEs (outside Outline)
    page_elem = root.find(f"one:Page", NS) or root
    for oe_children in page_elem.findall(f"one:OEChildren", NS):
        for oe in oe_children.findall(f"one:OE", NS):
            oe_id = oe.get("objectID", "")
            if oe_id not in seen_ids:
                seen_ids.add(oe_id)
                body_lines.extend(_convert_oe_tree(oe))

    body = _clean_markdown("\n".join(body_lines))
    body = html.unescape(body)
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
    for xml_file in sorted(xml_dir.rglob("*.xml")):
        # Preserve the full relative hierarchy: Notebook/SectionGroup*/Section/page.xml
        rel = xml_file.relative_to(xml_dir)
        target_dir = notes_dir.joinpath(*rel.parts[:-1])
        target_dir.mkdir(parents=True, exist_ok=True)

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
