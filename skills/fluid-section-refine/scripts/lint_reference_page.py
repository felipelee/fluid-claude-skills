#!/usr/bin/env python3
"""
Lint what the schema-reference page TEACHES.

`fluid theme lint --json` validates the page's own schema. It does not look
inside `schema_snippet` — the copy-paste code the page hands developers. A bad
snippet there is worse than a bad section: it propagates by hand into every
section someone builds from it.

This is exactly how `{ "type": "paragraph" }` reached five sections of the base
theme. The page taught it; developers copied it; the validator rejected all six
resulting schemas.

Usage (from the theme root):
    python3 lint_reference_page.py [path/to/schema_reference/index.liquid]

Exit code 0 = clean, 1 = findings.
"""
import json
import re
import subprocess
import sys
import html

DEFAULT_PAGE = 'sections/schema_reference/index.liquid'


def canonical_types(theme_root='.'):
    """Ask the real validator for the authoritative type list.

    Quirk worth knowing: `fluid theme lint --json` only emits
    `validSettingTypes` when it has errors to report. On a clean theme the
    payload is just {"ok":true,...,"files":[]} and there is no list to read.
    That is not a failure — it just means we fall back to the bundled copy.
    """
    try:
        out = subprocess.run(
            ['fluid', 'theme', 'lint', '--json'],
            cwd=theme_root, capture_output=True, text=True, timeout=120,
        ).stdout
        payload = json.loads(out)
        types = payload.get('validSettingTypes')
        if types:
            return set(types), 'fluid theme lint --json (live)'
        note = ('bundled list — validator emits validSettingTypes only alongside '
                'errors, and the theme is currently clean')
    except Exception as e:
        note = f'bundled list — could not reach the validator ({type(e).__name__})'
    # Fallback: the list as of fluid-cli-theme-dev 0.1.40. Prefer the live
    # validator — this copy goes stale the moment the engine adds a type.
    return set("""text plaintext rich_text richtext textarea html html_textarea url
        range number select radio checkbox color color_background font font_picker
        image image_picker video_picker media_picker text_alignment media_fit
        corner_radius padding border gradient_overlay header product products
        collection collections category categories blog posts post enrollment
        enrollments enrollment_pack forms media variant link_list product_list
        products_list collection_list collections_list category_list categories_list
        posts_list enrollment_list enrollments_list blog_list blogs_list post_list
        enrollment_packs_list""".split()), note


def unescape(s):
    """Snippets are stored HTML-escaped so they render as code in the page."""
    return html.unescape(s).replace('\\"', '"')


# a setting object is one that carries `id` or `content`; blocks carry `name`
SETTING_OBJ = re.compile(
    r'\{[^{}]*?"type"\s*:\s*"([a-z_]+)"[^{}]*?"(?:id|content)"\s*:',
    re.S,
)


def main():
    page = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PAGE
    src = open(page, encoding='utf-8').read()
    m = re.search(r'\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}', src, re.S)
    if not m:
        print(f'FAIL  no {{% schema %}} block in {page}')
        return 1
    schema = json.loads(m.group(1))

    presets = schema.get('presets') or []
    cards = presets[0].get('blocks', []) if presets else []
    valid, source = canonical_types()

    findings = []
    checked = 0
    for c in cards:
        st = c.get('settings', {})
        anchor = st.get('anchor_id', '?')
        name = st.get('control_name', '?')
        for field in ('schema_snippet', 'schema_snippet_2'):
            snip = st.get(field)
            if not snip:
                continue
            checked += 1
            for t in SETTING_OBJ.findall(unescape(snip)):
                if t not in valid:
                    findings.append((anchor, name, field, t))

    print(f'Reference page : {page}')
    print(f'Type list from : {source}  ({len(valid)} types)')
    print(f'Cards          : {len(cards)}')
    print(f'Snippets linted: {checked}')
    print()

    if not findings:
        print('CLEAN — every setting type taught by the page is valid.')
        return 0

    print(f'{len(findings)} INVALID SETTING TYPE(S) TAUGHT:')
    for anchor, name, field, t in findings:
        print(f'  [{anchor}] {name}')
        print(f'      {field} teaches "type": "{t}" — rejected by the validator')
        if t == 'paragraph':
            print('      fix: use "header" (same `content` field, no `id`)')
    print()
    print('Anyone copying these snippets writes a schema that fails `fluid theme push`.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
