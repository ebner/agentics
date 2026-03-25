# Research Profiles Reference

## Purpose
Reusable research configurations that save time on recurring research patterns.
Profiles define defaults for mode, domain, queries, and exclusions.

## Profile location (dual lookup)
Profiles are loaded from two locations, with project-local taking precedence:

1. **Project-local** (checked first): `./research-output/.research-profiles/<name>.yml`
2. **Global** (fallback): `~/.claude/deep-research-profiles/<name>.yml`

Project-local profiles override global ones of the same name.

## Profile schema

```yaml
# Example: security-audit.yml
name: security-audit
description: Security-focused research for code and architecture review

# Mode override (optional — if omitted, user is prompted as usual)
mode: deep

# Domain override (optional — if omitted, auto-detection is used)
domain: technology

# Custom sub-questions to always include (optional)
custom_sub_questions:
  - Known CVEs and security advisories
  - OWASP Top 10 relevance
  - Authentication and authorization patterns
  - Data protection and encryption practices

# Additional search queries to include (optional)
custom_queries:
  - "[topic] CVE vulnerability"
  - "[topic] security advisory"
  - "[topic] OWASP"
  - "[topic] penetration test results"

# Source preferences (optional)
preferred_sources:
  - "site:nvd.nist.gov"
  - "site:cve.mitre.org"
  - "site:owasp.org"

# Exclusions (optional)
exclusions:
  - marketing content
  - vendor comparison pages without methodology

# Report customization (optional)
report_sections:
  - Vulnerability Assessment
  - Attack Surface Analysis
  - Compliance Status
  - Remediation Recommendations
```

## Loading a profile

When the user specifies `--profile <name>` or says "use the [name] profile":

1. Search for `<name>.yml` in project-local directory first, then global
2. If not found, inform the user and list available profiles from both locations
3. If found, load the YAML and apply settings:
   - `mode`: skip mode selection prompt, use specified mode
   - `domain`: skip auto-detection, use specified domain
   - `custom_sub_questions`: add to the sub-questions generated in STEP 1
   - `custom_queries`: add to the queries planned in STEP 2
   - `preferred_sources`: add `site:` prefixes to query patterns
   - `exclusions`: add to exclusion criteria in STEP 1
   - `report_sections`: use as the section structure in STEP 7
4. Inform the user which profile was loaded and what settings it applies

## Listing available profiles

When the user asks "what profiles are available" or "list profiles":
1. Glob for `*.yml` in both profile directories
2. Read the `name` and `description` fields from each
3. Present as a formatted list

## Creating profiles

When the user asks to create a profile:
1. Ask for the profile name, description, and settings
2. Ask whether to save project-local or global
3. Write the YAML file to the chosen location
4. Confirm creation
