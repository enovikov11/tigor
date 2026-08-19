---
name: self
description: tigorc self-compilation — compile this spec into a working agent
---

## bootstrap

Read the README.md spec, extract all ## sections as tasks, and generate a Python module with stub functions for each task.

## compile

Given a spec file, parse its YAML frontmatter and ## headings, then emit a .py module where each heading becomes a run_<name>() function with a TODO placeholder.

## run

Load a compiled .py from __compiled/ and execute its main() function. Collect all task results into a JSON dict.

## list

List all .py files in the __compiled/ directory with their sizes.
