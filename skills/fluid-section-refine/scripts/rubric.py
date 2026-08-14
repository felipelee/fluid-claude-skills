#!/usr/bin/env python3
"""
Turn the theme's schema-reference page into a usable rubric.

The page is the best standard we have — every entry carries a rendered preview,
the exact schema snippet to copy, the Liquid accessor, and a tip. But it is
~175 KB of Liquid. Loading it whole to refine one section is wasteful and
mostly irrelevant.

This pulls out just the cards you need.

Usage (from the theme root):
    rubric.py --list                     compact index of every card
    rubric.py --card pattern-media-tag   one card, in full
    rubric.py --category patterns        every card in a category
    rubric.py --for-section sections/hero_section/index.liquid
                                         only the cards that section touches

`--for-section` is the one to reach for: it reads the section's schema, finds
every setting type and canonical block it uses, and returns the matching cards
plus the always-applicable patterns. That is the rubric to refine against.

Add --json for machine-readable output.
"""
import argparse
import html
import json
import os
import re
import sys

DEFAULT_PAGE = 'sections/schema_reference/index.liquid'

# Patterns that apply to every section regardless of what settings it declares.
ALWAYS = [
    'pattern-section-shell',
    'pattern-css-assets',
    'pattern-media-tag',
    'pattern-canonical-block-primacy',
]


def load_cards(page):
    src = open(page, encoding='utf-8').read()
    m = re.search(r'\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}', src, re.S)
    if not m:
        sys.exit(f'no {{% schema %}} block in {page}')
    schema = json.loads(m.group(1))
    presets = schema.get('presets') or []
    if not presets:
        sys.exit(f'{page} has no presets — nothing to extract')
    out = []
    for b in presets[0].get('blocks', []):
        st = b.get('settings', {})
        if st.get('anchor_id'):
            out.append(st)
    return out


def clean(s):
    """Snippets are stored HTML-escaped so they render as code in the page."""
    if not s:
        return ''
    return html.unescape(s).replace('\\"', '"')


def strip_html(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', clean(s))).strip()


def render(card, verbose=True):
    L = []
    L.append(f"### {card.get('control_name')}   [{card.get('anchor_id')}]")
    L.append(f"category: {card.get('category')}"
             + (f"   returns: {strip_html(card.get('returns_label'))}" if card.get('returns_label') else ''))
    if verbose:
        d = strip_html(card.get('description'))
        if d:
            L.append('')
            L.append(d)
        for f, label in (('schema_snippet', card.get('schema_label') or 'Schema'),
                         ('schema_snippet_2', card.get('schema_snippet_2_label') or 'Schema (cont.)')):
            if card.get(f):
                L.append('')
                L.append(f'{strip_html(label)}:')
                L.append('```json')
                L.append(clean(card[f]))
                L.append('```')
        if card.get('liquid_snippet'):
            L.append('')
            L.append(f"{strip_html(card.get('liquid_label') or 'Liquid')}:")
            L.append('```liquid')
            L.append(clean(card['liquid_snippet']))
            L.append('```')
        if card.get('tip'):
            kind = (card.get('tip_kind') or 'tip').upper()
            L.append('')
            L.append(f"{kind} — {strip_html(card.get('tip_label') or '')}")
            L.append(strip_html(card['tip']))
    return '\n'.join(L)


def types_used(section_path):
    """Every setting type and block type the section declares."""
    src = open(section_path, encoding='utf-8').read()
    m = re.search(r'\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}', src, re.S)
    if not m:
        return set(), set()
    try:
        schema = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        sys.exit(f'{section_path}: schema JSON does not parse ({e}) — fix that first')
    settings, blocks = set(), set()

    def walk(node):
        if isinstance(node, dict):
            for s in node.get('settings') or []:
                if isinstance(s, dict) and s.get('type'):
                    settings.add(s['type'])
            for b in node.get('blocks') or []:
                if isinstance(b, dict) and b.get('type'):
                    blocks.add(b['type'])
                walk(b)
        elif isinstance(node, list):
            for n in node:
                walk(n)

    walk(schema)
    for b in schema.get('blocks') or []:
        walk(b)
    return settings, blocks


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('--page', default=DEFAULT_PAGE)
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--card')
    ap.add_argument('--category')
    ap.add_argument('--for-section')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    if not os.path.exists(a.page):
        sys.exit(f'reference page not found: {a.page}\n'
                 'Run from the theme root, or pass --page. A theme without this page '
                 'has no rubric — refine against skills/fluid-theme-clone/references/ instead.')

    cards = load_cards(a.page)
    by_anchor = {c['anchor_id']: c for c in cards}

    if a.list:
        if a.json:
            print(json.dumps([{k: c.get(k) for k in ('anchor_id', 'category', 'control_name')}
                              for c in cards], indent=2))
            return
        cur = None
        for c in cards:
            if c.get('category') != cur:
                cur = c.get('category')
                print(f'\n--- {cur.upper()} ---')
            print(f"  {c.get('anchor_id'):34} {c.get('control_name')}")
        print(f'\n{len(cards)} cards')
        return

    if a.card:
        c = by_anchor.get(a.card)
        if not c:
            sys.exit(f'no card {a.card!r}. Try --list.')
        print(json.dumps(c, indent=2) if a.json else render(c))
        return

    if a.category:
        sel = [c for c in cards if c.get('category') == a.category]
        if not sel:
            cats = sorted({c.get('category') for c in cards})
            sys.exit(f'no cards in {a.category!r}. Categories: {", ".join(cats)}')
        print(json.dumps(sel, indent=2) if a.json
              else '\n\n'.join(render(c) for c in sel))
        return

    if a.for_section:
        settings, blocks = types_used(a.for_section)
        wanted, why = [], {}
        for anchor in ALWAYS:
            if anchor in by_anchor:
                wanted.append(anchor); why[anchor] = 'always applies'
        for c in cards:
            anchor, name = c['anchor_id'], c.get('control_name', '')
            # a card matches if its control_name names a type the section uses
            names = {n.strip() for n in re.split(r'[·,/]', name)}
            hit = names & settings
            if hit and anchor not in wanted:
                wanted.append(anchor); why[anchor] = f"section uses setting type: {', '.join(sorted(hit))}"
        if a.json:
            print(json.dumps({'section': a.for_section,
                              'setting_types': sorted(settings),
                              'block_types': sorted(blocks),
                              'cards': [by_anchor[w] for w in wanted]}, indent=2))
            return
        print(f'# Rubric for {a.for_section}')
        print(f'# setting types used: {", ".join(sorted(settings)) or "(none)"}')
        print(f'# block types used  : {", ".join(sorted(blocks)) or "(none)"}')
        print(f'# {len(wanted)} of {len(cards)} cards apply\n')
        for w in wanted:
            print(f'<!-- {why[w]} -->')
            print(render(by_anchor[w]))
            print()
        return

    ap.print_help()


if __name__ == '__main__':
    main()
