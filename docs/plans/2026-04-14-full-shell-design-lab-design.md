# Full Shell Design Lab Design

**Date:** 2026-04-14

**Purpose:** Create a fast evaluation artifact for a redesigned Playlist Navigator Pro shell without changing the production frontend.

## Scope

Build a standalone HTML prototype that models the full application shell:
- left navigation rail
- top command/header bar
- main dashboard canvas with representative cards, tables, and status panels
- right-side design lab panel with live visual controls

The artifact is for design evaluation, not functional product behavior.

## Visual Direction

The current green shell overuses emerald across background, accent, focus, and glow states. The prototype should shift to a cooler technical palette and reserve green for positive system states.

**Primary direction:** Mineral Glass
- Canvas: deep navy
- Surfaces: blue-charcoal glass panels
- Accent: electric blue
- Secondary accent: cyan/teal
- Success only: green

## Layout

### Left Rail
- compact brand block
- vertical navigation items
- clear active indicator
- separated utility section near the bottom

### Header
- current workspace/screen title
- search field
- compact KPI chips
- primary and secondary actions

### Main Area
- hero summary row
- playlist/indexing activity modules
- recent playlists or queue list
- analytics/status panel

This content should be realistic enough to judge hierarchy and density.

### Design Lab Panel
- preset switcher
- hue/accent sliders
- blur/glow sliders
- radius/density sliders
- motion toggle/intensity
- optional compare mode toggle

Changing controls should update the shell in real time through CSS custom properties.

## Interaction Model

- no backend calls
- no dependency on existing app state
- client-side preset switching only
- subtle motion and hover states to evaluate feel

## Deliverable

Create a self-contained HTML file under `docs/prototypes/` so it can be opened immediately for review and later ported into the main frontend if the direction is approved.
