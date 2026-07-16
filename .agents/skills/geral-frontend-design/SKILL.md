---
name: geral-frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics.
license: Complete terms in LICENSE.txt
aliases: [geral-frontend-design]
tags: [skill, area-geral]
area: geral
version: 2.0.0
author: V4 Company · Peretto & Co
---

# geral-frontend-design

This skill guides creation of distinctive, production-grade frontend interfaces. When the context is V4 Company, apply the V4 Design System below. For other projects, follow the general Design Thinking process with creative freedom.

Always output a single, self-contained HTML file (or component code). No external dependencies except Google Fonts CDN.

---

## V4 Design System (default for V4 company work)

Use this whenever the output is for V4 Company, a V4 client, or any Peretto & Co internal project.

### Color Palette

```css
:root {
  /* Primary — Red */
  --v4-red:         #e50914;
  --v4-red-dark:    #b20710;
  --v4-red-darker:  #80050b;
  --v4-red-deep:    #400306;

  /* Secondary */
  --v4-gold:        #ffc02a;
  --v4-green:       #52cc5a;

  /* Light tones */
  --v4-white:       #ffffff;
  --v4-gray-100:    #e5e5e5;
  --v4-gray-200:    #cccccc;
  --v4-gray-300:    #b3b3b3;

  /* Dark tones */
  --v4-gray-700:    #333333;
  --v4-gray-800:    #262626;
  --v4-gray-900:    #1a1a1a;
  --v4-black:       #000000;
}
```

### Typography

| Level | Font | Weight | Size | Spacing |
|-------|------|--------|------|---------|
| H1 | Proxima Nova | ExtraBold | 72px | 58px |
| H2 | Proxima Nova | Bold | 60px | 58px |
| H3 | Proxima Nova | Regular | 22px | 29px |
| H4 | Proxima Nova | Light | 18px | 20px |
| Body | Montserrat | 300-600 | 16px | — |
| Display/CTA | Bebas Neue or Morganite | — | — | — |

Fallback (if Proxima Nova not available): use Montserrat for headings + body with appropriate weight hierarchy. Import from Google Fonts.

When generating standalone HTML, prefer Google Fonts-available families:
- **Montserrat** (body, 300-800 weights)
- **Barlow Condensed** (headings, 600-900 weights — condensed display feel similar to Bebas Neue)
- **JetBrains Mono** (data/KPI values, tables)

### Logo Usage

Logos live at repo root. Reference them as relative paths from the output file location:

**For client-facing documents:**
- `v4logo.png` — full V4 Company logo (light bg)
- `logo-v4-white.png` — V4 logo for dark backgrounds

**For internal / team documents:**
- `logo-peretto-red.png` — Peretto & Co logo (red variant, for light bg)
- `logo-peretto.png` — Peretto & Co logo (for dark bg, if available)

Place the logo prominently in the header/topbar and optionally in the hero section.

### Visual Direction

- **Dark-first**: default to dark backgrounds (`#0a0a0c`, `#1a1a1a`) with red (#e50914) as accent
- **Red topbar**: solid red bar at top with logo + section label in white uppercase
- **Gradients**: use `radial-gradient` with red at low opacity for atmospheric glow behind hero sections
- **Grid pattern**: subtle dot/grid overlay (`linear-gradient` 1px lines at 48px) on dark backgrounds for texture
- **Cards**: dark surfaces (`rgba(255,255,255,0.03)` bg, `rgba(255,255,255,0.06)` border), rounded corners
- **Data/KPIs**: large bold numbers with subtle labels below, optional colored top border
- **Tables**: dark header row, alternating rows, minimal borders
- **Selection**: `::selection { background: var(--v4-red); color: white; }`
- **CTAs**: red-filled buttons (`background: var(--v4-red)`), white text, rounded 12px

### Layout Conventions

- Topbar: `display:flex; justify-content:space-between;` with logo left, metadata right
- Hero: centered content with gradient background, label badge, large heading, subtitle
- Content sections: max-width ~900-1100px, centered with `margin: 0 auto`
- Grid: `grid-template-columns: 1fr 1fr` (or 1fr 1fr 1fr for KPIs), gap 20px
- Responsive: collapse to 1 column below 640-768px

### Reference Outputs

Good examples of the V4 visual identity in practice:
- `projetos/AEO-GEO/docs/templates/dashboard-auditoria.html`
- `gset-meta-ads-junho-2026.html`
- `consolidado-conserva-junho-2026.html`
- `nova-estrutura-campanhas-conserva-2026-q3.html`
- `projetos/infraestrutura/v4-automations/documentação/AI-OPS-APRESENTACAO-4.html`

---

## General Design Thinking (for non-V4 projects)

When the output is NOT for V4 Company, use creative freedom with the following process:

### Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

### Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. CSS-only for HTML. Motion library for React when available.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements.
- **Backgrounds & Visual Details**: Create atmosphere and depth. Gradient meshes, noise textures, geometric patterns, layered transparencies.

NEVER use generic AI-generated aesthetics (Inter, Roboto, purple gradients on white, predictable layouts).

Interpret creatively and make unexpected choices that feel genuinely designed for the context.
