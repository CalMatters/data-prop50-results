# AGENTS.md — Marimo Notebooks

Instructions for AI coding agents working with Marimo notebooks in this project. Marimo is a **reactive** Python notebook that differs significantly from Jupyter. Following these rules prevents broken notebooks and avoids common pitfalls.

---

## Core Constraints (Never Violate)

Marimo enforces three constraints via static analysis. Violations prevent cells from running.

### 1. No multiply defined variables

**Each global variable must be defined in exactly one cell.** If you add a new cell that defines `df`, and another cell already defines `df`, marimo will error.

- **Fix**: Use unique names, or encapsulate in a function with local variables
- **Local variables**: Prefix with `_` (e.g. `_temp`) — these are cell-local and cannot be referenced by other cells.
  - If another cell tries to read `_temp`, you will get a runtime `NameError`, even if the “defining” cell name starts with `_`.
- **Shared constants/config**: Use non-underscored names (e.g. `CONSTANT_VALUE` or `variable_value`) and `return` them from the defining cell, then list them as parameters in downstream cells.

Example (cell-local underscore variable is not readable elsewhere):
```python
@app.cell
def _():
    _value = 123
    return

@app.cell
def _():
    mo.md(_value)  # NameError: _value is cell-local
```

Example (shared value across cells):
```python
@app.cell
def _():
    value = 123
    return value

@app.cell
def _(tmp):
    mo.md(value)
```

### 2. No cycles

If cell A defines `a` and reads `b`, cell B cannot define `b` and read `a`. The dependency graph must be a DAG.

- **Fix**: Restructure so dependencies flow one way. Extract shared logic into a third cell that both depend on.

### 3. No `import *`

```python
# ❌ BAD
from pandas import *

# ✅ GOOD
import pandas as pd
# or
from pandas import DataFrame, read_csv
```

---

## Mutation Rules

**Marimo does not track object mutations.** Mutations like `list.append()`, `df["col"] = ...`, or `obj.attr = x` do **not** trigger reactive re-runs.

- **Never** define a variable in one cell and mutate it in another
- **Do** perform mutations in the same cell that defines the variable
- **Prefer** creating new variables over mutating (e.g. `extended = lst + [2]` instead of `lst.append(2)`)

---

## marimo.ui — Critical Differences from Jupyter Widgets

**Do not treat marimo.ui like Jupyter ipywidgets.** Marimo widgets are **reactive** — no callbacks, no observers, no manual re-runs.

### Correct usage pattern

1. **Assign to a global variable** — required for reactivity
2. **Display** by including it in the cell output (e.g. `slider` or `mo.md(f"Value: {slider}")`)
3. **Read value** via `.value` in another cell (e.g. `slider.value`)

```python
# Cell 1: create and display
slider = mo.ui.slider(0, 100)
slider

# Cell 2: use the value (auto re-runs when slider changes)
mo.md(f"Selected: {slider.value}")
```

### Common widget mistakes to avoid

| Mistake | Why it fails |
|---------|--------------|
| Using `on_change` / `on_click` for logic that should drive other cells | Use reactive references instead — reference the widget's `.value` in downstream cells |
| Creating widgets inside a loop without `mo.ui.array` / `mo.ui.dictionary` / `mo.ui.batch` | `on_change` handlers only work when the widget is bound to a global variable |
| Closure capturing loop variable in `on_change` | Use default arg: `lambda value, i=i: print(i)` not `lambda value: print(i)` |
| Expecting `ipywidgets`-style `.observe()` or callbacks | Marimo has no observers — use `.value` and reactive cells |

### Dynamic UI elements

For a dynamic number of widgets (e.g. from a loop), use:

- `mo.ui.array([...])` — list of widgets
- `mo.ui.dictionary({...})` — keyed widgets
- `mo.ui.batch(...)` — custom layout of widgets

---

## Cell structure (app.cell decorator)

Notebooks use `@app.cell` with functions. The function:

- **Parameters**: Variables this cell *reads* (dependencies)
- **Return**: Variables this cell *defines* (must match what other cells will reference)

```python
@app.cell
def _(pd, mo):  # reads pd, mo
    df = pd.DataFrame({"a": [1, 2, 3]})
    return df,  # defines df
```

- **Do not** add `mo` to return if you only use it for display (e.g. `mo.md(...)`) — only return variables that other cells need
- **Do** return every variable that other cells reference
- **Optional**: `@app.cell(hide_code=True)` for markdown/display-only cells

---

## anywidget (custom widgets)

When generating custom widgets with anywidget:

- Use vanilla JavaScript in `_esm`; do not forget `_css`
- Wrap for marimo: `widget = mo.ui.anywidget(OriginalAnywidget())`
- Keep CSS small; support light and dark mode
- Export the render function: `export default { render };`

---

## Other conventions

- **Run notebooks**: `uv run marimo edit <notebook>.py` (interactive) or `uv run <notebook>.py` (script)
- **Lint**: `marimo check` to catch constraint violations before running
- **Expensive cells**: Use `mo.stop()`, `mo.cache`, or disable cells to avoid accidental re-runs
- **Forms**: Use `mo.ui.form` when you want a submit button — access submitted value via `form.value`

---

## Quick reference: Jupyter vs Marimo

| Jupyter | Marimo |
|---------|--------|
| Run cells manually, any order | Cells run reactively based on variable dependencies |
| Delete cell → variables stay in memory | Delete cell → variables removed from memory |
| `ipywidgets` + `.observe()` / callbacks | `mo.ui` + reference `.value` in other cells |
| JSON `.ipynb` format | Pure Python `.py` format |
| Execution order = cell order | Execution order = DAG of variable references |
