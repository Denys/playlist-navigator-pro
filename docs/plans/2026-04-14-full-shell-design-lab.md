# Full Shell Design Lab Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a standalone HTML shell prototype with a live right-side parameter panel for evaluating new UI directions quickly.

**Architecture:** Use a single self-contained HTML file with inline CSS and JavaScript. The page will expose a token-driven shell layout and update CSS custom properties in real time based on preset selection and slider changes.

**Tech Stack:** HTML, CSS custom properties, vanilla JavaScript

---

### Task 1: Scaffold the standalone evaluation artifact

**Files:**
- Create: `docs/prototypes/full-shell-design-lab.html`

**Step 1: Create the prototype file skeleton**

Add a full HTML document with:
- root shell container
- left rail
- top header
- main content grid
- right-side design panel

**Step 2: Add tokenized CSS variables**

Define CSS variables for:
- canvas and surface colors
- text colors
- accent and secondary colors
- blur, glow, radius, density, and motion values

**Step 3: Add initial mock content**

Add enough representative shell content to judge:
- navigation hierarchy
- action prominence
- list/table readability
- panel balance

### Task 2: Implement live design controls

**Files:**
- Modify: `docs/prototypes/full-shell-design-lab.html`

**Step 1: Add preset definitions**

Create JavaScript preset objects for:
- Current Green
- Mineral Glass
- Graphite Ice

**Step 2: Add control bindings**

Wire sliders, toggles, and preset buttons to CSS variables for:
- hue shift
- accent intensity
- blur
- glow
- radius
- density
- motion

**Step 3: Add compare-oriented affordances**

Support quick evaluation with:
- visible preset state
- reset button
- concise token labels

### Task 3: Verify artifact usability

**Files:**
- Verify: `docs/prototypes/full-shell-design-lab.html`

**Step 1: Open and inspect the file**

Check:
- layout renders at desktop width
- control panel changes the shell immediately
- contrast remains readable
- shell remains visually coherent after extreme slider values

**Step 2: Sanity-check mobile/compact behavior**

Check that the shell stacks or compresses sensibly at narrower widths.

**Step 3: Document delivery**

Report:
- created file path
- recommended preset
- any limitations of the standalone prototype
