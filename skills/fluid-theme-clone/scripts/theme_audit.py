#!/usr/bin/env python3
"""
Fluid theme gold-star audit.

Scans .liquid section/block files for violations of the Fluid base theme's
"gold star" conventions documented in the wiki. Emits machine-readable output
(file:line: rule: message) so it can be wired into a hook.

Usage:
    audit.py PATH...                    # audit one or more files or dirs
    audit.py --since-commit              # audit only files changed since HEAD~1 (in a git repo)
    audit.py --diff                      # audit only files staged or modified vs HEAD
    audit.py --json                      # JSON output instead of human-readable
    audit.py --rules R1,R2               # run only the listed rules
    audit.py --quiet                     # only print when there are violations

Exit codes:
    0  no violations
    1  violations found
    2  invocation error (bad path, etc.)

The audit is conservative on purpose: each rule has a high signal-to-noise
ratio. False positives are worse than misses for this use case — a noisy
linter trains people to ignore it.

Rules implemented (each has a stable ID):

    GS001  Section schema must contain Section Shell + Container settings.
    GS002  Section-level color settings must use background_colors option group,
           not raw hex (covers `color` AND `color_background` types).
    GS003  Section-level fonts must use font_families option group, not
           font_picker.
    GS004  image_picker is only allowed for backgrounds or inside the canonical
           image block. Forbidden as a section-level content image or in
           non-image blocks.
    GS005  Visible headings must be richtext blocks (heading/eyebrow/subhead),
           not section-level text fields named heading/title.
    GS006  {% render %} must reference components/, never blocks/.
    GS007  Every block wrapper element must include {{ block.fluid_attributes }}
           inside a {% for block in section.blocks %} loop.
    GS008  Section schema must declare a non-empty presets array.
    GS009  Schema JSON must parse cleanly. (Builder shows "Unknown Section"
           silently on parse error.)
    GS010  Liquid scopes: don't read {{ section.settings.X }} outside a section
           context, don't read {{ block.settings.X }} outside a block loop.
    GS011  Unsupported schema types (number, paragraph, inline_richtext, video,
           video_url, color_scheme, color_scheme_group, page, liquid, metaobject,
           metaobject_list, article, article_list).
    GS012  visible_if on a setting should be paired with a matching {% if %}
           guard in the Liquid template.
    GS013  Whitespace-trimming dashes on {% for block %} / {% case block.type %}
           tags break the Fluid editor parser. (Dashes ARE safe in {%- style -%}.)
    GS014  `var(--clr-{{ section.settings.X }})` is a known anti-pattern: when
           the setting is empty it renders `var(--clr-)`, invalid CSS that
           silently kills the surrounding rule block (padding, border-radius
           included). Use `{{ section.settings.X | default: 'transparent' }}`.
    GS015  Section files must include {{ section.fluid_attributes }} on the
           root element so the visual editor can identify the section.
    GS016  {{ block.fluid_attributes }} must live on a <div> wrapper — never
           directly on <h1>-<h6>, <p>, <span>, or <a>.
    GS017  Use the canonical 767px / 991px breakpoints. 749px, 768px, 1023px
           are forbidden — they desync with every other section's transitions.
    GS018  Template files: {% layout 'theme' %} must be on the first
           non-blank line.
    GS019  Template schemas (with top-level `sections` + `order`) must NOT
           contain `blocks` data on a section instance — blocks come from the
           section's own `presets` array. Putting blocks in the template
           schema breaks fluid_attributes bindings.
    GS020  Fluid's link_list shape exposes `menu.menu_items` (not `menu.links`).
    GS021  `border` schema type ships a hex color picker — split into a
           `range` (0-10) for width plus a `select` with
           "options": "background_colors" for color.
    GS022  `range` settings must declare `min`, `max`, and `step`.
    GS023  Section files must contain a {% schema %} block (a section without a
           schema can't be added in the Builder).
    GS024  Section schemas must declare a non-empty `name` (the label shown
           in the Builder's "Add section" panel).
    GS025  `richtext` setting defaults must be wrapped in HTML tags — bare
           strings render unstyled and the WYSIWYG can't initialize them.
    GS026  Typo guard: `fluid_attribute` (singular) renders nothing. The
           correct accessor is `fluid_attributes` (plural).

Rules NOT implemented (would be too noisy or require deep cross-file knowledge):
    - "Hero intros must be richtext" — too dependent on intent
    - "Mobile-first responsive" — too style-dependent
    - "Title Case labels" — many false positives on technical terms
    - "position: sticky needs no overflow:hidden ancestor" — cross-file CSS check
    - "Default richtext should ship inline style=" — too style-dependent
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------- data types ----------


@dataclass
class Violation:
    file: str
    line: int
    rule: str
    message: str
    snippet: str = ""

    def to_human(self) -> str:
        return f"{self.file}:{self.line}: {self.rule}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "line": self.line,
            "rule": self.rule,
            "message": self.message,
            "snippet": self.snippet,
        }


@dataclass
class FileContext:
    """Pre-computed structure of a .liquid file: template half + schema half."""
    path: Path
    text: str
    lines: list[str] = field(default_factory=list)
    schema_text: str = ""           # raw text between {% schema %} and {% endschema %}
    schema_start_line: int = -1     # 1-indexed line of opening {% schema %}
    template_text: str = ""         # everything before {% schema %}
    template_end_line: int = -1     # 1-indexed last line of template half
    schema_obj: Any = None          # parsed JSON or None
    schema_parse_error: str = ""

    @property
    def is_section(self) -> bool:
        # sections live under a /sections/ directory
        return "/sections/" in str(self.path).replace(os.sep, "/")

    @property
    def is_block(self) -> bool:
        return "/blocks/" in str(self.path).replace(os.sep, "/")

    @property
    def is_component(self) -> bool:
        return "/components/" in str(self.path).replace(os.sep, "/")


# ---------- parsing ----------


SCHEMA_OPEN_RE = re.compile(r"\{%-?\s*schema\s*-?%\}")
SCHEMA_CLOSE_RE = re.compile(r"\{%-?\s*endschema\s*-?%\}")


def load_file(path: Path) -> FileContext:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")
    ctx = FileContext(path=path, text=text, lines=lines)

    open_m = SCHEMA_OPEN_RE.search(text)
    close_m = SCHEMA_CLOSE_RE.search(text)
    if open_m and close_m and close_m.start() > open_m.end():
        ctx.template_text = text[: open_m.start()]
        ctx.template_end_line = ctx.template_text.count("\n") + 1
        ctx.schema_text = text[open_m.end() : close_m.start()]
        ctx.schema_start_line = text[: open_m.start()].count("\n") + 1
        try:
            ctx.schema_obj = json.loads(ctx.schema_text)
        except json.JSONDecodeError as e:
            ctx.schema_parse_error = f"line {e.lineno}, col {e.colno}: {e.msg}"
    else:
        ctx.template_text = text

    return ctx


def line_of_offset(text: str, offset: int) -> int:
    """Convert a character offset within `text` to a 1-indexed line number."""
    return text.count("\n", 0, offset) + 1


def schema_line(ctx: FileContext, schema_offset: int) -> int:
    """Convert an offset within ctx.schema_text to an absolute 1-indexed line."""
    if ctx.schema_start_line < 1:
        return 1
    return ctx.schema_start_line + ctx.schema_text.count("\n", 0, schema_offset)


# ---------- helpers for walking the parsed schema ----------


def walk_settings(obj: Any, path: list[str] | None = None):
    """
    Yield (setting_dict, path) for every setting inside a parsed schema, including
    settings inside blocks and inside presets blocks (skipped — those are values, not specs).
    `path` is a list like ["settings", "0"] or ["blocks", "0", "settings", "3"]
    so the caller can describe location.
    """
    if path is None:
        path = []
    if isinstance(obj, dict):
        # top-level: visit "settings" array, "blocks" array
        if "settings" in obj and isinstance(obj["settings"], list):
            for i, s in enumerate(obj["settings"]):
                if isinstance(s, dict):
                    yield s, path + ["settings", str(i)]
        if "blocks" in obj and isinstance(obj["blocks"], list):
            for bi, b in enumerate(obj["blocks"]):
                if isinstance(b, dict) and "settings" in b and isinstance(b["settings"], list):
                    for i, s in enumerate(b["settings"]):
                        if isinstance(s, dict):
                            yield s, path + ["blocks", str(bi), "settings", str(i)]


def find_schema_setting_line(ctx: FileContext, setting_id: str | None, setting_type: str) -> int:
    """
    Best-effort: find the line of a setting in the schema by searching for its id
    or type. Falls back to the schema start line.
    """
    if ctx.schema_start_line < 1:
        return 1
    if setting_id:
        # search for "id": "<id>" inside schema_text
        m = re.search(r'"id"\s*:\s*"' + re.escape(setting_id) + r'"', ctx.schema_text)
        if m:
            return schema_line(ctx, m.start())
    # fall back: type
    m = re.search(r'"type"\s*:\s*"' + re.escape(setting_type) + r'"', ctx.schema_text)
    if m:
        return schema_line(ctx, m.start())
    return ctx.schema_start_line


# ---------- rules ----------

# Required IDs in Section Shell & Container, per wiki/schema-settings-reference.md
SECTION_SHELL_REQUIRED = {
    "section_padding",
    "section_border_radius",
    "background_color",
    "background_image",
    "section_border_width",
    "section_border_color",
}

CONTAINER_REQUIRED = {
    "container_max_width",
    "container_padding",
    "container_border_radius",
    "container_background_color",
    "container_background_image",
    "container_overlay_color",
    "container_overlay_opacity",
    "container_border_width",
    "container_border_color",
}

UNSUPPORTED_TYPES = {
    "number",
    "paragraph",
    "inline_richtext",
    "video",
    "video_url",
    "color_scheme",
    "color_scheme_group",
    "page",
    "liquid",
    "metaobject",
    "metaobject_list",
    "article",
    "article_list",
}

# Heading-ish IDs that should be richtext blocks rather than section-level text fields.
HEADING_LIKE_IDS = {
    "heading",
    "title",
    "subhead",
    "subheading",
    "eyebrow",
    "headline",
}

# Color-related IDs that should pull from background_colors option group.
COLOR_ID_HINTS = (
    "_color",
    "_background",
    "background_color",
)

# Where image_picker is allowed.
ALLOWED_IMAGE_PICKER_IDS = {"image", "background_image", "container_background_image"}

# Hex color regex
HEX_RE = re.compile(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$')

# HTML tags where {{ block.fluid_attributes }} must NOT live. The gold-star
# rule says "never directly on <h1>, <h2>, <p>, <span>, <a>", but the canonical
# button block intentionally puts fluid_attributes on the `<a>` itself (the
# anchor IS the entire block — there's no inner content to manage), so we
# don't flag <a>. The text-content tags below are where the editor's selection
# model genuinely breaks: rich text inside h1-h6/p/span can't be selected if
# the wrapper is the same element.
SEMANTIC_TAGS_FORBIDDING_FLUID_ATTRS = ("h1", "h2", "h3", "h4", "h5", "h6", "p", "span")

# Canonical breakpoints (do not flag): the base theme uses desktop-first
# 991px (tablet) and 767px (mobile). Forbidden alternatives:
FORBIDDEN_BREAKPOINTS = ("749", "768", "1023")


def rule_GS009_schema_parses(ctx: FileContext) -> list[Violation]:
    """Schema JSON must parse."""
    if ctx.schema_text and ctx.schema_parse_error:
        return [Violation(
            file=str(ctx.path),
            line=ctx.schema_start_line,
            rule="GS009",
            message=f"Schema JSON does not parse ({ctx.schema_parse_error}). The Builder will silently show 'Unknown Section'.",
        )]
    return []


def rule_GS001_section_shell_and_container(ctx: FileContext) -> list[Violation]:
    """Sections must include Section Shell + Container required settings."""
    if not ctx.is_section or ctx.schema_obj is None:
        return []

    # main_* sections are theme-owned (main_cart, main_navbar, main_footer,
    # main_product, etc.) — they don't ship the standard Section Shell + Container
    # because they wrap Fluid's built-in templates, not free-form merchant content.
    name = ctx.path.parent.name.lower()
    if name.startswith("main_"):
        return []

    settings = ctx.schema_obj.get("settings") or []
    declared_ids = {s.get("id") for s in settings if isinstance(s, dict) and s.get("id")}

    missing_shell = SECTION_SHELL_REQUIRED - declared_ids
    missing_container = CONTAINER_REQUIRED - declared_ids

    out = []
    if missing_shell:
        out.append(Violation(
            file=str(ctx.path),
            line=ctx.schema_start_line,
            rule="GS001",
            message=(
                "Section Shell is missing required settings: "
                + ", ".join(sorted(missing_shell))
                + ". Every section needs the standard 6-control Section Shell at the bottom."
            ),
        ))
    if missing_container:
        out.append(Violation(
            file=str(ctx.path),
            line=ctx.schema_start_line,
            rule="GS001",
            message=(
                "Container is missing required settings: "
                + ", ".join(sorted(missing_container))
                + ". Every section needs the standard 9-control Container header."
            ),
        ))
    return out


def rule_GS002_color_uses_option_group(ctx: FileContext) -> list[Violation]:
    """Section-level color settings must point at background_colors, not raw hex."""
    if not ctx.is_section or ctx.schema_obj is None:
        return []
    out = []
    settings = ctx.schema_obj.get("settings") or []
    for s in settings:
        if not isinstance(s, dict):
            continue
        sid = s.get("id", "")
        stype = s.get("type", "")
        # Only flag id/labels that smell like colors.
        if not any(h in sid for h in COLOR_ID_HINTS):
            continue
        # gradient_overlay / image_picker are layout types, exempt.
        # `border` is exempt here because GS021 owns it (split-into-width+color rule).
        if stype in {"gradient_overlay", "image_picker", "border"}:
            continue
        if stype in ("color", "color_background"):
            out.append(Violation(
                file=str(ctx.path),
                line=find_schema_setting_line(ctx, sid, stype),
                rule="GS002",
                message=(
                    f"Setting '{sid}' uses type '{stype}' (raw hex picker). Section-level "
                    "colors must be 'select' with \"options\": \"background_colors\" so "
                    "they stay theme-aware. `color_background` belongs only in "
                    "config/settings_schema.json, not section settings."
                ),
            ))
            continue
        if stype == "select":
            opts = s.get("options")
            default = s.get("default", "")
            # Allowed: options is the literal "background_colors"
            if opts == "background_colors":
                continue
            # Allowed: select with bespoke non-color options (e.g. background_position)
            if isinstance(opts, list) and not any(
                isinstance(o, dict) and isinstance(o.get("value"), str) and HEX_RE.match(o["value"])
                for o in opts
            ):
                continue
            # If default is a raw hex, that's a smell.
            if isinstance(default, str) and HEX_RE.match(default):
                out.append(Violation(
                    file=str(ctx.path),
                    line=find_schema_setting_line(ctx, sid, stype),
                    rule="GS002",
                    message=(
                        f"Setting '{sid}' has a hex default ({default}). Use "
                        "\"options\": \"background_colors\" with a CSS-var default "
                        "like 'var(--clr-primary)'."
                    ),
                ))
    return out


def rule_GS003_font_uses_option_group(ctx: FileContext) -> list[Violation]:
    """font_picker is theme-only. Section-level fonts must point at font_families."""
    if not ctx.is_section or ctx.schema_obj is None:
        return []
    out = []
    for setting, _ in walk_settings(ctx.schema_obj):
        sid = setting.get("id", "")
        stype = setting.get("type", "")
        if stype == "font_picker":
            out.append(Violation(
                file=str(ctx.path),
                line=find_schema_setting_line(ctx, sid, stype),
                rule="GS003",
                message=(
                    f"Setting '{sid}' uses font_picker, which only works in "
                    "config/settings_schema.json. At section/block level use "
                    "\"select\" with \"options\": \"font_families\" and a CSS-var "
                    "default like 'var(--ff-body)'."
                ),
            ))
    return out


def rule_GS004_image_picker_placement(ctx: FileContext) -> list[Violation]:
    """image_picker is only allowed in known background spots or in the canonical image block."""
    if ctx.schema_obj is None:
        return []

    # blocks/image is the canonical home — exempt entirely
    if ctx.is_block and ctx.path.parent.name == "image":
        return []

    out = []
    settings = ctx.schema_obj.get("settings") or []
    for s in settings:
        if not isinstance(s, dict):
            continue
        if s.get("type") == "image_picker":
            sid = s.get("id", "")
            if sid not in ALLOWED_IMAGE_PICKER_IDS:
                out.append(Violation(
                    file=str(ctx.path),
                    line=find_schema_setting_line(ctx, sid, "image_picker"),
                    rule="GS004",
                    message=(
                        f"Section-level image_picker '{sid}' is forbidden. Content "
                        "images must use a canonical 'image' block. Allowed ids at "
                        "section level: " + ", ".join(sorted(ALLOWED_IMAGE_PICKER_IDS))
                        + "."
                    ),
                ))

    # check inline blocks
    for bi, b in enumerate(ctx.schema_obj.get("blocks") or []):
        if not isinstance(b, dict):
            continue
        block_type = b.get("type", "")
        if block_type == "image":
            continue  # canonical image block — image_picker expected
        for s in b.get("settings") or []:
            if not isinstance(s, dict):
                continue
            if s.get("type") == "image_picker":
                sid = s.get("id", "")
                if sid in ALLOWED_IMAGE_PICKER_IDS:
                    continue
                out.append(Violation(
                    file=str(ctx.path),
                    line=find_schema_setting_line(ctx, sid, "image_picker"),
                    rule="GS004",
                    message=(
                        f"image_picker '{sid}' lives inside block '{block_type}'. "
                        "Inlining image_picker into a non-image block strips the "
                        "canonical aspect_ratio / fit / overlay / border controls. "
                        "Use a separate canonical 'image' block instead."
                    ),
                ))
    return out


def rule_GS005_heading_should_be_richtext_block(ctx: FileContext) -> list[Violation]:
    """Visible headings should be richtext blocks, not section-level text fields."""
    if not ctx.is_section or ctx.schema_obj is None:
        return []
    out = []
    settings = ctx.schema_obj.get("settings") or []
    for s in settings:
        if not isinstance(s, dict):
            continue
        sid = s.get("id", "")
        stype = s.get("type", "")
        if sid in HEADING_LIKE_IDS and stype in {"text", "textarea"}:
            out.append(Violation(
                file=str(ctx.path),
                line=find_schema_setting_line(ctx, sid, stype),
                rule="GS005",
                message=(
                    f"Section-level '{sid}' uses type '{stype}'. Visible intros "
                    "(eyebrow / heading / subhead) belong in richtext blocks so "
                    "the merchant can style them. Move this to a block of "
                    f"type '{sid}' with a single 'richtext' setting."
                ),
            ))
    return out


def rule_GS006_render_from_components_only(ctx: FileContext) -> list[Violation]:
    """{% render 'foo/...' %} where 'foo' is 'blocks' is invalid — only components/ is resolvable."""
    out = []
    # Find {% render 'something' %} or {% render "something" %}
    pattern = re.compile(r"\{%-?\s*render\s+['\"]([^'\"]+)['\"]")
    for m in pattern.finditer(ctx.template_text):
        target = m.group(1)
        if target.startswith("blocks/") or target.startswith("blocks "):
            out.append(Violation(
                file=str(ctx.path),
                line=line_of_offset(ctx.text, m.start()),
                rule="GS006",
                message=(
                    f"{{% render '{target}' %}} cannot resolve — render only finds "
                    "files in components/. Move the shared markup into "
                    "components/<name>/index.liquid and render from there."
                ),
            ))
    return out


def rule_GS007_block_loop_has_fluid_attributes(ctx: FileContext) -> list[Violation]:
    """Each {% for block in section.blocks %} body must include block.fluid_attributes somewhere."""
    out = []
    if not ctx.template_text:
        return out

    text = ctx.template_text
    # Track every for/endfor with proper nesting; only check loops that iterate
    # section.blocks directly. Filtered loops (`for block in eyebrow_blocks` after
    # `assign eyebrow_blocks = section.blocks | where: 'type', 'eyebrow'`) inherit
    # the obligation but are harder to track — we only flag the direct case to keep
    # noise low. The direct case is the most common authoring path anyway.
    token_re = re.compile(
        r"(\{%-?\s*for\s+(\w+)\s+in\s+section\.blocks(?:[^%]*)%\})|(\{%-?\s*for\s+\w+\s+in\s+[^%]+?%\})|(\{%-?\s*endfor\s*-?%\})",
        re.IGNORECASE,
    )
    # stack entries: (kind, loop_var, open_start, body_start)
    # kind = "section_blocks" | "other"
    stack: list[tuple[str, str, int, int]] = []
    for m in token_re.finditer(text):
        if m.group(1):  # for X in section.blocks
            stack.append(("section_blocks", m.group(2), m.start(), m.end()))
        elif m.group(3):  # other for
            stack.append(("other", "", m.start(), m.end()))
        elif m.group(4):  # endfor
            if not stack:
                continue
            kind, var, open_start, body_start = stack.pop()
            if kind == "section_blocks":
                body = text[body_start:m.start()]
                if "fluid_attributes" not in body:
                    out.append(Violation(
                        file=str(ctx.path),
                        line=line_of_offset(ctx.text, open_start),
                        rule="GS007",
                        message=(
                            f"Block loop '{{% for {var} in section.blocks %}}' has no "
                            f"{{{{ {var}.fluid_attributes }}}} on any wrapper. Without "
                            "it the block isn't clickable in the Builder iframe."
                        ),
                    ))
    return out


def rule_GS008_presets_required(ctx: FileContext) -> list[Violation]:
    """Sections need a non-empty presets array (otherwise they look broken when added)."""
    if not ctx.is_section or ctx.schema_obj is None:
        return []
    name = ctx.path.parent.name.lower()
    # main_* sections have fixed roles and don't need presets — they're auto-mounted
    if name.startswith("main_"):
        return []
    presets = ctx.schema_obj.get("presets")
    if presets is None or (isinstance(presets, list) and len(presets) == 0):
        return [Violation(
            file=str(ctx.path),
            line=ctx.schema_start_line,
            rule="GS008",
            message=(
                "Section schema has no 'presets' array. Without presets the section "
                "drops in empty and looks broken. Add one preset with realistic "
                "default content."
            ),
        )]
    return []


def rule_GS010_scope_consistency(ctx: FileContext) -> list[Violation]:
    """
    block.settings.X outside a block-loop body almost certainly indicates the wrong scope.
    A "block loop" here means any {% for block in <expr> %} (the loop variable is named
    `block`), since merchants commonly filter section.blocks first via `assign x =
    section.blocks | where: 'type', 'foo'` and then iterate `for block in x`.

    Tracks nesting properly so a {% for block in trust_blocks %} containing an
    inner {% for i in (1..n) %} still counts code after the inner loop as inside
    the outer block loop.

    Block files (blocks/*/index.liquid) are exempt: their entire body is the
    body of an implicit block iteration, so block.settings.* is always in scope
    inside them.
    """
    if ctx.is_block:
        return []
    out = []
    text = ctx.template_text

    # Tokenize all {% for ... %} and {% endfor %} occurrences in template order.
    token_re = re.compile(
        r"\{%-?\s*for\s+(\w+)\s+in\s+[^%]+?%\}|\{%-?\s*endfor\s*-?%\}",
        re.IGNORECASE,
    )
    block_loop_ranges: list[tuple[int, int]] = []
    # stack of (loop_var, start_offset_after_open)
    stack: list[tuple[str, int]] = []
    for m in token_re.finditer(text):
        if m.group(1):  # opening {% for VAR in ... %}
            stack.append((m.group(1), m.end()))
        else:  # endfor
            if not stack:
                continue
            var, start = stack.pop()
            if var == "block":
                block_loop_ranges.append((start, m.start()))

    def in_block_loop(offset: int) -> bool:
        return any(s <= offset < e for s, e in block_loop_ranges)

    block_ref_re = re.compile(r"(?<![A-Za-z0-9_])block\.settings\.[A-Za-z0-9_]+")
    for m in block_ref_re.finditer(text):
        if in_block_loop(m.start()):
            continue
        out.append(Violation(
            file=str(ctx.path),
            line=line_of_offset(ctx.text, m.start()),
            rule="GS010",
            message=(
                "Reference to block.settings.* outside a {% for block in ... %} loop. "
                "block.settings is only available inside a loop where the iterator is "
                "named `block`. If you meant the section-level value, use "
                "section.settings.* instead."
            ),
        ))
    return out


def rule_GS011_unsupported_types(ctx: FileContext) -> list[Violation]:
    """Catch types the Fluid render engine does not support."""
    if ctx.schema_obj is None:
        return []
    out = []
    for setting, _ in walk_settings(ctx.schema_obj):
        stype = setting.get("type", "")
        if stype in UNSUPPORTED_TYPES:
            sid = setting.get("id", "")
            out.append(Violation(
                file=str(ctx.path),
                line=find_schema_setting_line(ctx, sid, stype),
                rule="GS011",
                message=(
                    f"Setting '{sid}' uses unsupported type '{stype}'. The Fluid "
                    "render engine drops or errors on this type silently — see "
                    "the 'Not supported' table in fluid-theme-clone/references/"
                    "schema-settings-reference.md for the supported alternative."
                ),
            ))
    return out


def rule_GS012_visible_if_paired_with_template_guard(ctx: FileContext) -> list[Violation]:
    """
    visible_if hides a setting in the sidebar but the Liquid template still receives
    the value. Without a matching {% if %} guard, hidden state still renders.

    Heuristic: for each setting with visible_if referencing a boolean-looking flag
    (id prefix show_/has_/use_/enable_/is_) on either section.settings or
    block.settings, require an {% if/unless %} guard on the same scope+flag
    somewhere in the template.
    """
    if ctx.schema_obj is None:
        return []
    out = []
    flag_prefixes = ("show_", "has_", "use_", "enable_", "is_")
    cond_re = re.compile(r"\b(section|block)\.settings\.(\w+)")
    for setting, _ in walk_settings(ctx.schema_obj):
        cond = setting.get("visible_if")
        if not isinstance(cond, str):
            continue
        m = cond_re.search(cond)
        if not m:
            continue
        scope, flag = m.group(1), m.group(2)
        if not any(flag.startswith(p) for p in flag_prefixes):
            continue
        guard_re = re.compile(
            r"\{%-?\s*(?:if|unless)\s+" + scope + r"\.settings\." + re.escape(flag) + r"\b",
        )
        if guard_re.search(ctx.template_text):
            continue
        sid = setting.get("id", "")
        out.append(Violation(
            file=str(ctx.path),
            line=find_schema_setting_line(ctx, sid, setting.get("type", "")),
            rule="GS012",
            message=(
                f"Setting '{sid}' has visible_if depending on '{scope}.settings.{flag}', "
                f"but the template never guards on {{% if {scope}.settings.{flag} %}}. "
                "visible_if is UI-only — without the Liquid guard, the markup "
                "still renders even when the user 'hides' it."
            ),
        ))
    return out


def rule_GS013_no_dashes_in_block_iteration(ctx: FileContext) -> list[Violation]:
    """
    Whitespace-trimming dashes break Fluid's block-iteration parser.

    Per the canonical reference: dashes are forbidden on the {% for X in section.blocks %}
    opener and on {% case block.type %} — those are the parser entry points the editor
    relies on. Dashes inside {%- style -%} blocks are explicitly safe (CSS generation,
    not block rendering), so we don't touch them.
    """
    if not ctx.template_text:
        return []
    out = []
    patterns = [
        (
            re.compile(
                r"\{%-\s*for\s+\w+\s+in\s+section\.blocks\b[^%]*-?%\}|"
                r"\{%\s*for\s+\w+\s+in\s+section\.blocks\b[^%]*-%\}",
                re.IGNORECASE,
            ),
            "{% for X in section.blocks %}",
        ),
        (
            re.compile(
                r"\{%-\s*case\s+block\.type\b[^%]*-?%\}|"
                r"\{%\s*case\s+block\.type\b[^%]*-%\}",
                re.IGNORECASE,
            ),
            "{% case block.type %}",
        ),
    ]
    for pat, label in patterns:
        for m in pat.finditer(ctx.template_text):
            out.append(Violation(
                file=str(ctx.path),
                line=line_of_offset(ctx.text, m.start()),
                rule="GS013",
                message=(
                    f"{label} uses a whitespace-trimming dash: `{m.group(0).strip()}`. "
                    "Dashes here break the Fluid editor parser — block iteration tags "
                    "must use plain {% %} (no dashes). Dashes ARE safe inside "
                    "{%- style -%} blocks (CSS generation, not block rendering)."
                ),
                snippet=m.group(0),
            ))
    return out


def rule_GS014_no_var_clr_wrapping(ctx: FileContext) -> list[Violation]:
    """
    `var(--clr-{{ section.settings.X }})` is the single most expensive footgun in the
    base theme — when the setting is empty it renders `var(--clr-)`, invalid CSS that
    silently kills the entire surrounding rule block (padding, border-radius, the
    works). The `background_colors` option group already returns CSS values like
    `var(--clr-primary)` or `transparent`, so the value should be inlined directly.
    """
    if not ctx.template_text:
        return []
    out = []
    pattern = re.compile(
        r"var\(\s*--[\w-]+-\s*\{\{\s*(?:section|block)\.settings\.\w+",
        re.IGNORECASE,
    )
    for m in pattern.finditer(ctx.template_text):
        out.append(Violation(
            file=str(ctx.path),
            line=line_of_offset(ctx.text, m.start()),
            rule="GS014",
            message=(
                "Anti-pattern: wrapping a settings value in `var(--clr-{{ ... }})`. "
                "When the setting is empty this renders `var(--clr-)` — invalid CSS "
                "that silently kills the entire rule block (padding, border-radius "
                "included). The `background_colors` option group already returns CSS "
                "values; use `{{ section.settings.X | default: 'transparent' }}` "
                "directly."
            ),
            snippet=m.group(0),
        ))
    return out


def rule_GS015_section_root_fluid_attributes(ctx: FileContext) -> list[Violation]:
    """Section files must include {{ section.fluid_attributes }} somewhere on the root."""
    if not ctx.is_section or not ctx.template_text:
        return []
    # main_* sections are Fluid-controlled / theme-owned and don't always follow
    # the standard section shell pattern (e.g. main_cart wraps Fluid's cart shell,
    # main_page is a thin content host).
    if ctx.path.parent.name.lower().startswith("main_"):
        return []
    if "section.fluid_attributes" in ctx.template_text:
        return []
    # Skip empty / placeholder section files
    if not ctx.template_text.strip():
        return []
    return [Violation(
        file=str(ctx.path),
        line=1,
        rule="GS015",
        message=(
            "Section file does not include {{ section.fluid_attributes }} anywhere. "
            "Without it the visual editor cannot identify or manage this section. "
            "Add it to the outermost <section> element: "
            "`<section class=\"...\" {{ section.fluid_attributes }}>`."
        ),
    )]


def rule_GS016_block_fluid_attributes_on_div(ctx: FileContext) -> list[Violation]:
    """
    {{ block.fluid_attributes }} must live on a <div> wrapper, never directly on
    a semantic element (h1-h6, p, span, a). Attaching it to those elements
    breaks the editor's selection model on rich text and links.
    """
    if not ctx.template_text:
        return []
    out = []
    seen = set()  # de-dup if regex matches overlap
    for tag in SEMANTIC_TAGS_FORBIDDING_FLUID_ATTRS:
        pattern = re.compile(
            r"<" + re.escape(tag) + r"\b[^>]*?\{\{\s*\w+\.fluid_attributes\s*\}\}[^>]*?>",
            re.IGNORECASE | re.DOTALL,
        )
        for m in pattern.finditer(ctx.template_text):
            if m.start() in seen:
                continue
            seen.add(m.start())
            snippet = m.group(0).replace("\n", " ").strip()
            if len(snippet) > 140:
                snippet = snippet[:137] + "..."
            out.append(Violation(
                file=str(ctx.path),
                line=line_of_offset(ctx.text, m.start()),
                rule="GS016",
                message=(
                    f"`block.fluid_attributes` is on <{tag}>. Move it to a <div> "
                    "wrapper. Attaching it to a semantic element (h1-h6, p, span, a) "
                    "breaks the editor's selection model on rich text and links."
                ),
                snippet=snippet,
            ))
    return out


def rule_GS017_canonical_breakpoints(ctx: FileContext) -> list[Violation]:
    """
    The base theme standardizes on 991px (tablet) and 767px (mobile). 749px,
    768px, and 1023px are forbidden — they desync this section's responsive
    transitions from the rest of the theme by ~1px and produce jumpy layout
    boundaries when scrolling between sections at those widths.
    """
    if not ctx.template_text:
        return []
    out = []
    # Match a forbidden breakpoint inside a media query feature, e.g.
    # `@media (max-width: 768px)` or `@media screen and (min-width: 1023px) and ...`
    for bp in FORBIDDEN_BREAKPOINTS:
        pattern = re.compile(
            r"@media\b[^{]*?\(\s*(?:min|max)-width\s*:\s*" + bp + r"px\b",
            re.IGNORECASE,
        )
        for m in pattern.finditer(ctx.template_text):
            out.append(Violation(
                file=str(ctx.path),
                line=line_of_offset(ctx.text, m.start()),
                rule="GS017",
                message=(
                    f"Non-canonical breakpoint @{bp}px. The base theme standardizes on "
                    "767px (mobile) and 991px (tablet). Other sections will transition "
                    f"layouts at 991/767, this one at {bp} — the result is a jumpy "
                    "layout boundary when scrolling between sections at those widths."
                ),
            ))
    return out


def rule_GS018_template_layout_first_line(ctx: FileContext) -> list[Violation]:
    """
    Template files: `{% layout 'theme' %}` must be the first non-blank line.

    Heuristic: any file containing a `{% layout %}` directive is a template
    file. Anything (HTML, comments, other tags) before that directive breaks
    layout resolution.
    """
    if not ctx.template_text:
        return []
    layout_re = re.compile(r"\{%-?\s*layout\s+['\"][^'\"]+['\"]\s*-?%\}")
    m = layout_re.search(ctx.template_text)
    if not m:
        return []
    pre = ctx.template_text[: m.start()]
    if not pre.strip():
        return []  # layout is on the first non-blank line — good
    return [Violation(
        file=str(ctx.path),
        line=line_of_offset(ctx.text, m.start()),
        rule="GS018",
        message=(
            "{% layout 'theme' %} is not on the first non-blank line of this template. "
            "Layout directives must come first — anything before them (HTML, comments, "
            "Liquid tags) breaks layout resolution."
        ),
    )]


def rule_GS019_template_schema_no_blocks(ctx: FileContext) -> list[Violation]:
    """
    Template schemas (the page-level schemas with top-level `sections` + `order`)
    must NOT include `blocks` data on a section instance. Block data comes from
    the section's own `presets` array — putting blocks in the template schema
    breaks fluid_attributes bindings, so merchants can't select or edit those
    blocks in the visual editor.
    """
    if ctx.schema_obj is None or not isinstance(ctx.schema_obj, dict):
        return []
    sections = ctx.schema_obj.get("sections")
    if not isinstance(sections, dict):
        return []  # not a template schema
    out = []
    for sid, sdef in sections.items():
        if not isinstance(sdef, dict):
            continue
        if "blocks" not in sdef:
            continue
        # Find the line of "blocks": within this section instance for a precise pointer
        line = ctx.schema_start_line
        m = re.search(
            r'"' + re.escape(sid) + r'"\s*:\s*\{(?:[^{}]|\{[^{}]*\})*?"blocks"',
            ctx.schema_text,
            re.DOTALL,
        )
        if m:
            blocks_offset = m.group(0).rfind('"blocks"')
            line = schema_line(ctx, m.start() + max(blocks_offset, 0))
        out.append(Violation(
            file=str(ctx.path),
            line=line,
            rule="GS019",
            message=(
                f"Template schema for section instance '{sid}' contains 'blocks'. Block "
                "data must come from the section's own `presets` array, NOT the template "
                "schema. Putting blocks here breaks fluid_attributes bindings — the "
                "merchant cannot select or edit those blocks in the visual editor."
            ),
        ))
    return out


def rule_GS020_menu_uses_menu_items(ctx: FileContext) -> list[Violation]:
    """Fluid's link_list shape exposes `menu.menu_items` — `.links` doesn't exist."""
    if not ctx.template_text:
        return []
    out = []
    # Only flag `.links` on a variable that smells like a menu.
    pattern = re.compile(r"\b([\w.]*menu[\w.]*?)\.links\b", re.IGNORECASE)
    for m in pattern.finditer(ctx.template_text):
        out.append(Violation(
            file=str(ctx.path),
            line=line_of_offset(ctx.text, m.start()),
            rule="GS020",
            message=(
                f"`{m.group(0)}` — Fluid's link_list shape uses `menu.menu_items`, not "
                "`.links`. Each item exposes `.url` and `.title`. See "
                "components/navbar_primary_nav for the canonical iteration."
            ),
            snippet=m.group(0),
        ))
    return out


def rule_GS021_no_border_type(ctx: FileContext) -> list[Violation]:
    """
    The native `border` schema type ships a hex color picker that breaks the
    theme-driven color rule. Split it into a `range` (0-10px) for width plus
    a `select` with "options": "background_colors" for color — the same
    pattern Section Shell + Container use for `section_border_*` and
    `container_border_*`.
    """
    if ctx.schema_obj is None:
        return []
    out = []
    for setting, _ in walk_settings(ctx.schema_obj):
        if setting.get("type") != "border":
            continue
        sid = setting.get("id", "")
        out.append(Violation(
            file=str(ctx.path),
            line=find_schema_setting_line(ctx, sid, "border"),
            rule="GS021",
            message=(
                f"Setting '{sid}' uses type 'border'. The `border` type bundles a hex "
                "color picker which breaks the theme-driven color rule. Split into two "
                "settings: `range` (min:0, max:10, step:1, unit:px) for width, and "
                "`select` with \"options\": \"background_colors\" for color. Mirrors "
                "the Section Shell `section_border_width` + `section_border_color` "
                "pattern."
            ),
        ))
    return out


def rule_GS022_range_has_bounds(ctx: FileContext) -> list[Violation]:
    """`range` settings must declare min, max, and step."""
    if ctx.schema_obj is None:
        return []
    out = []
    for setting, _ in walk_settings(ctx.schema_obj):
        if setting.get("type") != "range":
            continue
        sid = setting.get("id", "")
        missing = [k for k in ("min", "max", "step") if k not in setting]
        if not missing:
            continue
        out.append(Violation(
            file=str(ctx.path),
            line=find_schema_setting_line(ctx, sid, "range"),
            rule="GS022",
            message=(
                f"Setting '{sid}' is type 'range' but missing: "
                + ", ".join(missing)
                + ". `range` requires min, max, and step or the editor cannot render "
                "the slider."
            ),
        ))
    return out


def rule_GS023_section_has_schema(ctx: FileContext) -> list[Violation]:
    """Section files must contain a {% schema %} block."""
    if not ctx.is_section:
        return []
    # main_* sections may legitimately omit schemas (they wrap built-in templates).
    if ctx.path.parent.name.lower().startswith("main_"):
        return []
    if ctx.schema_text or ctx.schema_obj is not None:
        return []
    if not ctx.text.strip():
        return []
    return [Violation(
        file=str(ctx.path),
        line=1,
        rule="GS023",
        message=(
            "Section file has no {% schema %} block. Without a schema the section "
            "cannot be added in the Builder — it won't even appear in the picker. "
            "Add {% schema %}{ \"name\": \"...\", \"settings\": [], \"blocks\": [], "
            "\"presets\": [...] }{% endschema %} at the bottom of the file."
        ),
    )]


def rule_GS024_schema_has_name(ctx: FileContext) -> list[Violation]:
    """Section schemas must declare a non-empty `name`."""
    if not ctx.is_section or ctx.schema_obj is None:
        return []
    # Template schemas (top-level `sections` + `order`) don't have a `name` field.
    if isinstance(ctx.schema_obj, dict) and isinstance(ctx.schema_obj.get("sections"), dict):
        return []
    if ctx.path.parent.name.lower().startswith("main_"):
        return []
    name = ctx.schema_obj.get("name") if isinstance(ctx.schema_obj, dict) else None
    if isinstance(name, str) and name.strip():
        return []
    return [Violation(
        file=str(ctx.path),
        line=ctx.schema_start_line,
        rule="GS024",
        message=(
            "Section schema is missing a non-empty `name`. The Builder uses this "
            "string as the section's label in the 'Add section' picker — without "
            "it the section appears as an unlabeled entry that's hard to identify."
        ),
    )]


def rule_GS025_richtext_default_html_wrapped(ctx: FileContext) -> list[Violation]:
    """`richtext` defaults must be wrapped in HTML tags so the WYSIWYG can render them."""
    if ctx.schema_obj is None:
        return []
    out = []
    for setting, _ in walk_settings(ctx.schema_obj):
        if setting.get("type") not in ("richtext", "rich_text"):
            continue
        default = setting.get("default")
        if not isinstance(default, str) or not default.strip():
            continue
        # Acceptable: contains an HTML tag.
        if re.search(r"<[a-zA-Z][^>]*>", default):
            continue
        sid = setting.get("id", "")
        out.append(Violation(
            file=str(ctx.path),
            line=find_schema_setting_line(ctx, sid, setting.get("type", "")),
            rule="GS025",
            message=(
                f"richtext setting '{sid}' has a default that isn't wrapped in HTML "
                f"tags ({default!r}). The WYSIWYG can't initialize bare strings — "
                "they render unstyled and the merchant can't restyle them inline. "
                "Wrap in a tag, e.g. \"<h2>Default heading</h2>\" or \"<p>...</p>\"."
            ),
        ))
    return out


def rule_GS026_fluid_attribute_typo(ctx: FileContext) -> list[Violation]:
    """
    `fluid_attribute` (singular) is a typo. The accessor is `fluid_attributes`
    (plural). The singular form silently renders nothing — the editor can't
    select the section/block but no error is raised.
    """
    if not ctx.template_text:
        return []
    out = []
    # Match `.fluid_attribute` NOT followed by `s` and NOT preceded by alphanumeric
    # (so we don't false-positive on user-defined identifiers).
    pattern = re.compile(r"(?<![A-Za-z0-9_])(\w+\.fluid_attribute)(?!s)\b")
    for m in pattern.finditer(ctx.template_text):
        out.append(Violation(
            file=str(ctx.path),
            line=line_of_offset(ctx.text, m.start()),
            rule="GS026",
            message=(
                f"`{m.group(1)}` looks like a typo — the correct accessor is "
                "`fluid_attributes` (plural). The singular form renders nothing "
                "silently, so the section/block becomes invisible to the editor "
                "without any error."
            ),
            snippet=m.group(0),
        ))
    return out


ALL_RULES = [
    ("GS009", rule_GS009_schema_parses),
    ("GS001", rule_GS001_section_shell_and_container),
    ("GS002", rule_GS002_color_uses_option_group),
    ("GS003", rule_GS003_font_uses_option_group),
    ("GS004", rule_GS004_image_picker_placement),
    ("GS005", rule_GS005_heading_should_be_richtext_block),
    ("GS006", rule_GS006_render_from_components_only),
    ("GS007", rule_GS007_block_loop_has_fluid_attributes),
    ("GS008", rule_GS008_presets_required),
    ("GS010", rule_GS010_scope_consistency),
    ("GS011", rule_GS011_unsupported_types),
    ("GS012", rule_GS012_visible_if_paired_with_template_guard),
    ("GS013", rule_GS013_no_dashes_in_block_iteration),
    ("GS014", rule_GS014_no_var_clr_wrapping),
    ("GS015", rule_GS015_section_root_fluid_attributes),
    ("GS016", rule_GS016_block_fluid_attributes_on_div),
    ("GS017", rule_GS017_canonical_breakpoints),
    ("GS018", rule_GS018_template_layout_first_line),
    ("GS019", rule_GS019_template_schema_no_blocks),
    ("GS020", rule_GS020_menu_uses_menu_items),
    ("GS021", rule_GS021_no_border_type),
    ("GS022", rule_GS022_range_has_bounds),
    ("GS023", rule_GS023_section_has_schema),
    ("GS024", rule_GS024_schema_has_name),
    ("GS025", rule_GS025_richtext_default_html_wrapped),
    ("GS026", rule_GS026_fluid_attribute_typo),
]

KNOWN_RULE_IDS = {rid for rid, _ in ALL_RULES}


# ---------- driver ----------


def gather_files(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        if p.is_dir():
            for sub in p.rglob("*.liquid"):
                if sub.is_file():
                    out.append(sub)
        elif p.is_file() and p.suffix == ".liquid":
            out.append(p)
    return sorted(set(out))


def git_changed_files(mode: str) -> list[Path]:
    """Return changed .liquid files relative to current repo."""
    if mode == "since-commit":
        cmd = ["git", "diff", "--name-only", "HEAD~1..HEAD"]
    else:  # diff
        cmd = ["git", "diff", "--name-only", "HEAD"]
    try:
        out = subprocess.check_output(cmd, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    files = [Path(line.strip()) for line in out.splitlines() if line.strip().endswith(".liquid")]
    return [p for p in files if p.exists()]


def audit_file(ctx: FileContext, enabled_rules: set[str] | None) -> list[Violation]:
    out: list[Violation] = []
    for rid, fn in ALL_RULES:
        if enabled_rules is not None and rid not in enabled_rules:
            continue
        try:
            out.extend(fn(ctx))
        except Exception as e:
            out.append(Violation(
                file=str(ctx.path),
                line=1,
                rule=rid,
                message=f"audit rule crashed (this is a bug in the audit script, not your theme): {e}",
            ))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Fluid theme gold-star audit")
    ap.add_argument("paths", nargs="*", help="Files or directories to audit")
    ap.add_argument("--since-commit", action="store_true", help="Audit files changed in the last commit (HEAD~1..HEAD)")
    ap.add_argument("--diff", action="store_true", help="Audit files modified vs HEAD")
    ap.add_argument("--json", action="store_true", help="Emit JSON output")
    ap.add_argument("--rules", help="Comma-separated rule ids to run (default: all)")
    ap.add_argument("--quiet", action="store_true", help="Only print when there are violations")
    args = ap.parse_args(argv)

    if args.since_commit and args.diff:
        print("error: --since-commit and --diff are mutually exclusive", file=sys.stderr)
        return 2

    if args.since_commit:
        files = git_changed_files("since-commit")
    elif args.diff:
        files = git_changed_files("diff")
    else:
        if not args.paths:
            ap.print_help(sys.stderr)
            return 2
        files = gather_files([Path(p) for p in args.paths])

    if not files:
        if not args.quiet:
            print("audit: no .liquid files to check")
        return 0

    enabled = None
    if args.rules:
        enabled = {r.strip() for r in args.rules.split(",") if r.strip()}
        unknown = enabled - KNOWN_RULE_IDS
        if unknown:
            print(
                f"error: unknown rule id(s): {', '.join(sorted(unknown))}. "
                f"Known rules: {', '.join(sorted(KNOWN_RULE_IDS))}",
                file=sys.stderr,
            )
            return 2

    all_violations: list[Violation] = []
    for f in files:
        try:
            ctx = load_file(f)
        except OSError as e:
            print(f"audit: cannot read {f}: {e}", file=sys.stderr)
            continue
        all_violations.extend(audit_file(ctx, enabled))

    # Stable, human-friendly ordering: by file, then line, then rule id.
    all_violations.sort(key=lambda v: (v.file, v.line, v.rule))

    if args.json:
        print(json.dumps({
            "files_checked": len(files),
            "violations": [v.to_dict() for v in all_violations],
        }, indent=2))
    else:
        if not all_violations and not args.quiet:
            print(f"audit: ok — {len(files)} file(s) checked, 0 violations")
        for v in all_violations:
            print(v.to_human())
        if all_violations:
            # Per-rule rollup so a noisy single rule is obvious at a glance.
            rule_counts: dict[str, int] = {}
            for v in all_violations:
                rule_counts[v.rule] = rule_counts.get(v.rule, 0) + 1
            rollup = ", ".join(
                f"{rid}:{rule_counts[rid]}"
                for rid in sorted(rule_counts, key=lambda r: (-rule_counts[r], r))
            )
            print(
                f"\naudit: {len(all_violations)} violation(s) across "
                f"{len(files)} file(s) [{rollup}]",
                file=sys.stderr,
            )

    return 1 if all_violations else 0


if __name__ == "__main__":
    sys.exit(main())
