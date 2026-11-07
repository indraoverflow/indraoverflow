#!/usr/bin/env python3
"""Generate the theme-aware AgentDiet banner used in the profile README.

Two SVGs, identical geometry, different palette, so the README can pick one with
<picture> + prefers-color-scheme. The bars animate with CSS transforms; the
final width lives in the attribute, so any renderer that ignores CSS still shows
the correct numbers.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

W, H = 1200, 300

DARK = {
    "bg": "#0a0b0d",
    "panel": "#101216",
    "line": "#ffffff1f",
    "grid": "#ffffff0d",
    "fg": "#f4f5f7",
    "muted": "#969ca5",
    "faint": "#7d848e",
    "accent": "#3ddc97",
    "warn": "#ff8a4c",
    "track": "#ffffff12",
}
LIGHT = {
    "bg": "#fcfcfb",
    "panel": "#ffffff",
    "line": "#0b0c0e1f",
    "grid": "#0b0c0e0f",
    "fg": "#0c0e11",
    "muted": "#545b65",
    "faint": "#6a717c",
    "accent": "#077a4d",
    "warn": "#b8511a",
    "track": "#0b0c0e14",
}

SANS = "'Inter','Segoe UI',system-ui,-apple-system,sans-serif"
MONO = "'JetBrains Mono','SFMono-Regular',ui-monospace,monospace"

CARD_X, CARD_Y, CARD_W, CARD_H = 644, 40, 512, 220
INNER = 28
BAR_W = CARD_W - INNER * 2
BEFORE, AFTER = 6770, 711
AFTER_W = round(BAR_W * AFTER / BEFORE, 1)


def bars(x, y, w, h, fill, delay):
    """Track plus a fill that grows from the left when CSS is available."""
    return f"""
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{{track}}"/>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{fill}"
          style="transform-origin:{x}px {y}px;animation:grow .9s cubic-bezier(.22,1,.36,1) {delay}s both"/>"""


def svg(p):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"
     aria-label="AgentDiet: measures the always-on context an AI coding agent loads. In a simulated repository, always-on tokens drop from 6,770 at grade C to 711 at grade A, an 89.5 percent reduction.">
  <defs>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="{p['grid']}" stroke-width="1"/>
    </pattern>
    <style>
      text {{ font-family: {SANS}; }}
      .mono {{ font-family: {MONO}; }}
      @keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
      @keyframes pulse {{ 0%,100% {{ opacity:.35; }} 50% {{ opacity:1; }} }}
      .dot {{ animation: pulse 2.4s ease-in-out infinite; }}
      @media (prefers-reduced-motion: reduce) {{
        .dot, rect[style] {{ animation: none !important; }}
      }}
    </style>
  </defs>

  <rect width="{W}" height="{H}" rx="18" fill="{p['bg']}"/>
  <rect width="{W}" height="{H}" rx="18" fill="url(#grid)" opacity=".75"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{p['line']}"/>

  <!-- mark: three instruction lines, the fat trimmed -->
  <g transform="translate(56,52)">
    <rect width="26" height="3.6" rx="1.8" fill="{p['fg']}"/>
    <rect y="7.4" width="17" height="3.6" rx="1.8" fill="{p['fg']}" opacity=".45"/>
    <rect y="14.8" width="9" height="3.6" rx="1.8" fill="{p['accent']}"/>
  </g>
  <text x="56" y="122" font-size="42" font-weight="600" letter-spacing="-1.6" fill="{p['fg']}">AgentDiet</text>

  <text x="56" y="162" font-size="17" fill="{p['muted']}">Measure the context your AI coding agent loads</text>
  <text x="56" y="186" font-size="17" fill="{p['muted']}">before you type a single word — then cut it.</text>

  <text x="56" y="228" font-size="12.5" fill="{p['faint']}" class="mono">go install github.com/qansaid/agentdiet@latest</text>

  <g class="mono">
    <circle cx="60" cy="256" r="3" fill="{p['accent']}" class="dot"/>
    <text x="72" y="260" font-size="11" fill="{p['faint']}">MIT · Go 1.22+ · single static binary · no account · no network calls</text>
  </g>

  <!-- report card -->
  <rect x="{CARD_X}" y="{CARD_Y}" width="{CARD_W}" height="{CARD_H}" rx="14" fill="{p['panel']}" stroke="{p['line']}"/>
  <text x="{CARD_X + INNER}" y="{CARD_Y + 34}" font-size="11" fill="{p['faint']}" class="mono" letter-spacing=".6">AGENT CONTEXT · ACME-PLATFORM</text>
  <rect x="{CARD_X + CARD_W - INNER - 74}" y="{CARD_Y + 19}" width="74" height="21" rx="5" fill="{p['warn']}" fill-opacity=".12" stroke="{p['warn']}" stroke-opacity=".45"/>
  <text x="{CARD_X + CARD_W - INNER - 61}" y="{CARD_Y + 34}" font-size="10.5" fill="{p['warn']}" class="mono">C → A</text>

  <text x="{CARD_X + INNER}" y="{CARD_Y + 72}" font-size="10.5" fill="{p['faint']}" class="mono">BEFORE</text>
  <text x="{CARD_X + CARD_W - INNER}" y="{CARD_Y + 74}" font-size="17" fill="{p['fg']}" class="mono" text-anchor="end">6,770</text>
  {bars(CARD_X + INNER, CARD_Y + 84, BAR_W, 8, p['warn'], 0.1)}

  <text x="{CARD_X + INNER}" y="{CARD_Y + 128}" font-size="10.5" fill="{p['faint']}" class="mono">AFTER</text>
  <text x="{CARD_X + CARD_W - INNER}" y="{CARD_Y + 130}" font-size="17" fill="{p['accent']}" class="mono" text-anchor="end">711</text>
  {bars(CARD_X + INNER, CARD_Y + 140, AFTER_W, 8, p['accent'], 0.35)}
  <line x1="{CARD_X + INNER + AFTER_W + 6}" y1="{CARD_Y + 144}" x2="{CARD_X + INNER + BAR_W}" y2="{CARD_Y + 144}"
        stroke="{p['track']}" stroke-width="1" stroke-dasharray="2 5"/>

  <text x="{CARD_X + INNER}" y="{CARD_Y + 176}" font-size="13" fill="{p['accent']}" class="mono">−89.5% always-on tokens</text>
  <text x="{CARD_X + INNER}" y="{CARD_Y + 200}" font-size="11" fill="{p['faint']}" class="mono">simulated repository · real report output</text>
</svg>
"""


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, palette in (("agentdiet-dark.svg", DARK), ("agentdiet-light.svg", LIGHT)):
        path = OUT / name
        body = svg(palette).replace("{track}", palette["track"])
        path.write_text(body, encoding="utf-8")
        print(f"wrote {path} ({len(body)} bytes)")


if __name__ == "__main__":
    main()
