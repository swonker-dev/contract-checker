from __future__ import annotations

from html import escape


def icon(name: str, *, size: int = 16) -> str:
    """Small line icons using the stroke and dimensions from the ViWork brandbook."""
    paths = {
        "documents": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
        "library": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/><path d="M8 7h8M8 11h6"/>',
        "upload": '<path d="M12 16V4m-4 4 4-4 4 4M4 16v4h16v-4"/>',
    }
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        f'{paths[name]}</svg>'
    )


def render_page(title: str, content: str, script: str, *, active: str) -> str:
    """One shared ViWork shell for the standalone contract-checker screens."""
    navigation = []
    for key, href, label, symbol in (
        ("catalog", "/", "Проверка договоров", "documents"),
        ("regulations", "/regulations", "Нормативная база", "library"),
    ):
        current = ' aria-current="page"' if active == key else ""
        navigation.append(
            f'<a class="nav-item" href="{href}"{current}>'
            f'{icon(symbol)}<span>{label}</span></a>'
        )
    return f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} — ViWork</title>
  <link rel="icon" type="image/png" href="/static/viwork-logo.png">
  <link rel="stylesheet" href="/static/ui.css">
</head>
<body>
  <a class="skip-link" href="#main-content">Перейти к содержимому</a>
  <header class="portal-header">
    <div class="topbar">
      <img class="brand-logo" src="/static/viwork-logo.png" alt="ViWork" width="126" height="28">
      <span class="portal-name">Проверка договоров</span>
    </div>
  </header>
  <div class="portal-layout">
    <aside class="sidebar">
      <p class="nav-label">Документы</p>
      <nav aria-label="Основная навигация">{''.join(navigation)}</nav>
    </aside>
    <main class="page-content" id="main-content" tabindex="-1">
      {content}
    </main>
  </div>
  <script>{script}</script>
</body>
</html>'''
