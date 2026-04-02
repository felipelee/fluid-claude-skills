# Contributing to Fluid Skills

Thanks for contributing! This guide covers how to add or modify skills.

## Skill Structure

Each skill lives in its own directory under `skills/`:

```
skills/
  my-skill/
    SKILL.md              # Required — main skill file
    references/           # Optional — supplementary docs
      api-reference.md
    assets/               # Optional — templates, examples
```

## Creating a New Skill

### 1. Name your skill

- Use kebab-case: `fluid-product-import`, `fluid-theme-setup`
- Prefix with `fluid-` for platform-specific skills
- Keep it short and descriptive

### 2. Create the directory and SKILL.md

```bash
mkdir -p skills/my-skill-name
```

### 3. Add required frontmatter

```yaml
---
name: my-skill-name
description: >-
  Describe when this skill should be used. Include trigger phrases
  and keywords that Claude should match on.
metadata:
  version: 1.0.0
---
```

**Frontmatter rules:**
- `name` must match the directory name exactly
- `name`: 1-64 characters, lowercase letters, numbers, and hyphens only
- `description`: 1-1024 characters, include trigger conditions
- `metadata.version`: semantic versioning

### 4. Write the skill body

Good skills include:
- Clear step-by-step instructions
- API endpoint references with request/response examples
- Schema definitions with required vs optional fields
- Common pitfalls and error handling patterns
- Code examples that can be used as templates

Keep SKILL.md under 500 lines where possible. Move detailed reference material to `references/`. Exception: orchestration/API-reference skills (like `fluid-full-import`) that need all endpoints and step details in a single context can exceed this limit.

### 5. Update the README

Add your skill to the appropriate category table in `README.md`.

## Quality Checklist

Before submitting:

- [ ] `name` in frontmatter matches directory name
- [ ] Description clearly explains when to use the skill
- [ ] Instructions are actionable (not just documentation)
- [ ] API endpoints and field names are accurate
- [ ] Code examples are correct and minimal
- [ ] No sensitive credentials or API keys included
- [ ] SKILL.md is under 500 lines
- [ ] README.md skill table is updated

## Pull Request Process

1. Fork the repo
2. Create a feature branch: `feature/skill-name`
3. Add your skill following the structure above
4. Submit a PR with a description of what the skill does and when it's useful

## Updating Existing Skills

- Bump the `metadata.version` when making changes
- Keep backward compatibility — don't rename fields users may reference
- Note breaking changes in your PR description
