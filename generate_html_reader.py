import json
import re

with open(r"d:\聯合大學\專題\本傳續寫\parsed_data.json", "r", encoding="utf-8") as f:
    chapters = json.load(f)

# Helper to clean titles
def clean_title(title):
    # Remove markdown bold/italic asterisks from titles
    title = re.sub(r"\*+", "", title)
    return title.strip()

# Helper to process paragraphs into HTML
def format_inline(text):
    # First bold
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    # Highlight / code
    text = re.sub(r"`(.*?)`", r"<code>\1</code>", text)
    # Clean any leftover dangling asterisks
    text = re.sub(r"(?<!\w)\*(?!\w)", "", text)
    return text

def process_paragraph(text):
    text = text.strip()
    if not text:
        return ""
    
    # Check if this is an order dispatch block
    if text.startswith('【訂單來源：') or text.startswith('【派送物品：') or text.startswith('【配送地址：') or text.startswith('【訂單備註：'):
        return f'<div class="terminal-line">{format_inline(text)}</div>'
    
    # Check if system announcement or achievement
    if text.startswith('【叮！') or text.startswith('【恭喜') or text.startswith('【系統公告') or text.startswith('【⚠️') or text.startswith('【 ❌'):
        return f'<div class="system-alert-box">{format_inline(text)}</div>'

    # Check for group chat message in epilogue
    if text.startswith('• **') and '：' in text:
        match = re.match(r'^• \*\*(.*?)\*\*：(.*)$', text)
        if match:
            sender = match.group(1).strip()
            msg = match.group(2).strip()
            
            avatar_icon = "👤"
            badge_class = "default"
            if "溫青" in sender or "青青" in sender:
                avatar_icon = "🐯"
                badge_class = "tiger"
            elif "劉" in sender or "契約" in sender:
                avatar_icon = "⚖️"
                badge_class = "law"
            elif "安" in sender or "護理" in sender:
                avatar_icon = "🌿"
                badge_class = "heal"
            elif "宛辭" in sender or "媽咪" in sender:
                avatar_icon = "👶"
                badge_class = "mom"
            elif "願初" in sender:
                avatar_icon = "🪷"
                badge_class = "guanyin"
            elif "宮廟" in sender:
                avatar_icon = "🏮"
                badge_class = "temple"
            elif "風火輪" in sender:
                avatar_icon = "🔧"
                badge_class = "mechanic"

            return f'''<div class="chat-bubble-wrap {badge_class}">
                <div class="chat-avatar">{avatar_icon}</div>
                <div class="chat-bubble-content">
                    <div class="chat-sender">{sender}</div>
                    <div class="chat-bubble-text">{format_inline(msg)}</div>
                </div>
            </div>'''

    # Regular paragraph
    if (text.startswith('「') and text.endswith('」')) or (text.startswith('『') and text.endswith('』')):
        return f'<p class="dialogue-para">{format_inline(text)}</p>'
    
    return f'<p class="body-para">{format_inline(text)}</p>'

# Group paragraphs into logical blocks (like dispatch terminals)
def render_section_content(content_lines):
    html_out = []
    in_terminal = False
    terminal_buf = []

    for line in content_lines:
        line_s = line.strip()
        if not line_s:
            if in_terminal:
                html_out.append('<div class="terminal-card"><div class="terminal-header"><span class="terminal-dot red"></span><span class="terminal-dot yellow"></span><span class="terminal-dot green"></span><span class="terminal-title">✦ 祈心宮・神識終端派工單 ✦</span></div><div class="terminal-body">' + "".join(terminal_buf) + '</div></div>')
                terminal_buf = []
                in_terminal = False
            continue

        if line_s.startswith('【訂單來源：') or line_s.startswith('【派送物品：') or line_s.startswith('【配送地址：') or line_s.startswith('【訂單備註：'):
            in_terminal = True
            terminal_buf.append(f'<div class="terminal-row">{format_inline(line_s)}</div>')
        else:
            if in_terminal:
                html_out.append('<div class="terminal-card"><div class="terminal-header"><span class="terminal-dot red"></span><span class="terminal-dot yellow"></span><span class="terminal-dot green"></span><span class="terminal-title">✦ 祈心宮・神識終端派工單 ✦</span></div><div class="terminal-body">' + "".join(terminal_buf) + '</div></div>')
                terminal_buf = []
                in_terminal = False
            html_out.append(process_paragraph(line_s))

    if in_terminal:
        html_out.append('<div class="terminal-card"><div class="terminal-header"><span class="terminal-dot red"></span><span class="terminal-dot yellow"></span><span class="terminal-dot green"></span><span class="terminal-title">✦ 祈心宮・神識終端派工單 ✦</span></div><div class="terminal-body">' + "".join(terminal_buf) + '</div></div>')

    return "\n".join(html_out)

# Clean all chapter and section titles
for ch in chapters:
    ch['title'] = clean_title(ch['title'])
    for sec in ch['sections']:
        sec['title'] = clean_title(sec['title'])

# Build HTML
total_words = sum(len(line) for ch in chapters for sec in ch['sections'] for line in sec['content'])
est_read_min = round(total_words / 450)

html_template = f'''<!DOCTYPE html>
<html lang="zh-TW" data-theme="dark-cyber">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <title>騎蹟到府 | 現代神話輕小說・正傳全集</title>
    <meta name="description" content="臺灣現代神話輕小說《騎蹟到府》：當截稿地獄的漫畫家誤飲孟婆忘情水，騎上八卦噴射機車，穿梭大疫街頭傳遞神明祝福與人間微光。">
    <meta property="og:title" content="騎蹟到府 | 現代神話輕小說・正傳全集">
    <meta property="og:description" content="臺灣現代神話輕小說《騎蹟到府》・原創正傳完結篇 在線極致體驗閱讀器">
    <meta property="og:type" content="book">
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=Inter:wght@400;500;600;700&family=Noto+Sans+TC:wght@300;400;500;700&family=Noto+Serif+TC:wght@400;600;700;900&family=Orbitron:wght@700&display=swap" rel="stylesheet">

    <style>
        :root {{
            --font-serif: 'Noto Serif TC', serif;
            --font-sans: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --font-kai: 'DFKai-SB', 'BiauKai', 'Noto Serif TC', serif;
            
            --current-font: var(--font-serif);
            --content-font-size: 18px;
            --content-line-height: 1.95;
            --content-max-width: 760px;
            --ui-font: 'Inter', var(--font-sans);
        }}

        /* Theme: Cyber Temple Dark (Default) */
        [data-theme="dark-cyber"] {{
            --bg-body: #0a0e17;
            --bg-surface: #111827;
            --bg-surface-glass: rgba(17, 24, 39, 0.85);
            --bg-elevated: #1e293b;
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-accent: rgba(56, 189, 248, 0.3);
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-gold: #f59e0b;
            --accent-cyan: #38bdf8;
            --accent-crimson: #f43f5e;
            --card-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.7);
            --glow-color: rgba(56, 189, 248, 0.15);
            --terminal-bg: #030712;
            --terminal-border: #1e293b;
        }}

        /* Theme: Warm Eye-care Paper */
        [data-theme="paper-warm"] {{
            --bg-body: #f8f4eb;
            --bg-surface: #efe8d8;
            --bg-surface-glass: rgba(239, 232, 216, 0.9);
            --bg-elevated: #e6dcbe;
            --border-subtle: rgba(90, 70, 45, 0.12);
            --border-accent: rgba(180, 83, 9, 0.35);
            --text-primary: #382c1e;
            --text-secondary: #6e5c46;
            --text-muted: #9c8a73;
            --accent-gold: #b45309;
            --accent-cyan: #0284c7;
            --accent-crimson: #be123c;
            --card-shadow: 0 4px 20px rgba(60, 45, 20, 0.08);
            --glow-color: rgba(180, 83, 9, 0.08);
            --terminal-bg: #e5dbc4;
            --terminal-border: #ccbe9f;
        }}

        /* Theme: Pure Daylight Clean */
        [data-theme="light-clean"] {{
            --bg-body: #f8fafc;
            --bg-surface: #ffffff;
            --bg-surface-glass: rgba(255, 255, 255, 0.9);
            --bg-elevated: #f1f5f9;
            --border-subtle: #e2e8f0;
            --border-accent: #cbd5e1;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-muted: #94a3b8;
            --accent-gold: #d97706;
            --accent-cyan: #0284c7;
            --accent-crimson: #e11d48;
            --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            --glow-color: rgba(2, 132, 199, 0.06);
            --terminal-bg: #f8fafc;
            --terminal-border: #e2e8f0;
        }}

        /* Theme: OLED Pitch Black */
        [data-theme="midnight-ink"] {{
            --bg-body: #000000;
            --bg-surface: #0a0a0a;
            --bg-surface-glass: rgba(10, 10, 10, 0.9);
            --bg-elevated: #171717;
            --border-subtle: #262626;
            --border-accent: #eab308;
            --text-primary: #e5e5e5;
            --text-secondary: #a3a3a3;
            --text-muted: #737373;
            --accent-gold: #eab308;
            --accent-cyan: #38bdf8;
            --accent-crimson: #fb7185;
            --card-shadow: none;
            --glow-color: rgba(234, 179, 8, 0.1);
            --terminal-bg: #050505;
            --terminal-border: #262626;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
        }}

        html {{
            scroll-behavior: smooth;
            font-size: 16px;
        }}

        body {{
            background-color: var(--bg-body);
            color: var(--text-primary);
            font-family: var(--ui-font);
            min-height: 100vh;
            line-height: 1.6;
            transition: background-color 0.3s ease, color 0.3s ease;
            overflow-x: hidden;
        }}

        /* Top Progress Bar */
        #top-progress-bar {{
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            width: 0%;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-gold));
            z-index: 1000;
            transition: width 0.1s ease;
            box-shadow: 0 0 8px var(--accent-cyan);
        }}

        /* Header Bar */
        header.app-header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: var(--bg-surface-glass);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-subtle);
            z-index: 900;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 1.25rem;
            transition: transform 0.3s ease, background-color 0.3s ease;
        }}

        header.app-header.hidden {{
            transform: translateY(-100%);
        }}

        .brand-title-wrap {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            cursor: pointer;
        }}

        .brand-badge {{
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: linear-gradient(135deg, var(--accent-gold), var(--accent-crimson));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            box-shadow: 0 2px 10px rgba(245, 158, 11, 0.3);
        }}

        .brand-text h1 {{
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: var(--text-primary);
            font-family: var(--font-serif);
        }}

        .brand-text span {{
            font-size: 0.72rem;
            color: var(--text-muted);
            letter-spacing: 0.03em;
        }}

        .header-actions {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .header-btn {{
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            color: var(--text-primary);
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 1.05rem;
            transition: all 0.2s ease;
        }}

        .header-btn:hover {{
            background: var(--accent-gold);
            color: #000;
            border-color: var(--accent-gold);
            transform: translateY(-1px);
        }}

        .progress-pill {{
            font-size: 0.78rem;
            font-weight: 600;
            color: var(--accent-gold);
            background: var(--bg-elevated);
            padding: 0.3rem 0.65rem;
            border-radius: 20px;
            border: 1px solid var(--border-subtle);
        }}

        /* Main Container */
        main.reader-container {{
            max-width: var(--content-max-width);
            margin: 0 auto;
            padding: 90px 1.5rem 120px 1.5rem;
            transition: max-width 0.3s ease;
        }}

        /* Hero Banner */
        .novel-hero {{
            text-align: center;
            padding: 3rem 1rem 4rem 1rem;
            margin-bottom: 2.5rem;
            border-bottom: 1px solid var(--border-subtle);
            position: relative;
        }}

        .novel-hero::after {{
            content: "☯";
            position: absolute;
            bottom: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-body);
            padding: 0 15px;
            color: var(--accent-gold);
            font-size: 1.2rem;
        }}

        .hero-tag {{
            display: inline-block;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.15em;
            color: var(--accent-cyan);
            background: rgba(56, 189, 248, 0.12);
            padding: 0.25rem 0.8rem;
            border-radius: 30px;
            margin-bottom: 1rem;
            text-transform: uppercase;
        }}

        .hero-title {{
            font-family: var(--font-serif);
            font-size: 2.5rem;
            font-weight: 900;
            letter-spacing: 0.08em;
            margin-bottom: 0.6rem;
            background: linear-gradient(135deg, var(--text-primary) 40%, var(--accent-gold));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .hero-author {{
            font-size: 0.95rem;
            color: var(--text-secondary);
            margin-bottom: 1.2rem;
        }}

        .hero-meta-grid {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1.5rem;
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .meta-pill {{
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }}

        /* Chapter Headings */
        .chapter-block {{
            margin-bottom: 4.5rem;
        }}

        .chapter-header {{
            margin: 3.5rem 0 2rem 0;
            padding: 1.5rem;
            background: var(--bg-surface);
            border-radius: 16px;
            border-left: 4px solid var(--accent-gold);
            box-shadow: var(--card-shadow);
            position: relative;
        }}

        .chapter-header h2 {{
            font-family: var(--font-serif);
            font-size: 1.6rem;
            font-weight: 800;
            color: var(--text-primary);
            letter-spacing: 0.05em;
        }}

        .section-header {{
            margin: 2.8rem 0 1.5rem 0;
            padding-bottom: 0.6rem;
            border-bottom: 1px dashed var(--border-subtle);
        }}

        .section-header h3 {{
            font-family: var(--font-serif);
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--accent-cyan);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .section-header h3::before {{
            content: "✦";
            font-size: 0.9rem;
            color: var(--accent-gold);
        }}

        /* Reader Content Text */
        .section-content {{
            font-family: var(--current-font);
            font-size: var(--content-font-size);
            line-height: var(--content-line-height);
            letter-spacing: 0.02em;
            color: var(--text-primary);
        }}

        p.body-para {{
            margin-bottom: 1.45em;
            text-align: justify;
            text-indent: 2em;
        }}

        p.dialogue-para {{
            margin-bottom: 1.45em;
            text-align: justify;
            color: var(--text-primary);
            font-weight: 500;
        }}

        p code, span code {{
            background: var(--bg-elevated);
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            font-size: 0.9em;
            color: var(--accent-cyan);
            border: 1px solid var(--border-subtle);
        }}

        strong {{
            color: var(--accent-gold);
            font-weight: 700;
        }}

        /* Terminal Order Card */
        .terminal-card {{
            background: var(--terminal-bg);
            border: 1px solid var(--terminal-border);
            border-radius: 12px;
            margin: 2rem 0;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
            font-family: var(--ui-font);
        }}

        .terminal-header {{
            background: var(--bg-elevated);
            padding: 0.6rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .terminal-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        .terminal-dot.red {{ background: #f43f5e; }}
        .terminal-dot.yellow {{ background: #f59e0b; }}
        .terminal-dot.green {{ background: #10b981; }}

        .terminal-title {{
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-left: 0.5rem;
            letter-spacing: 0.05em;
        }}

        .terminal-body {{
            padding: 1.2rem 1.4rem;
            font-size: 0.95rem;
            line-height: 1.7;
            color: var(--accent-cyan);
        }}

        .terminal-row {{
            margin-bottom: 0.4rem;
        }}
        .terminal-row:last-child {{
            margin-bottom: 0;
        }}

        /* System Alert Box */
        .system-alert-box {{
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.35);
            border-left: 4px solid var(--accent-gold);
            padding: 1rem 1.25rem;
            border-radius: 10px;
            margin: 1.8rem 0;
            font-size: 0.95rem;
            color: var(--text-primary);
            line-height: 1.7;
        }}

        /* Chat UI in Epilogue */
        .chat-bubble-wrap {{
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            margin: 1rem 0;
            padding: 0.6rem 0.8rem;
            border-radius: 12px;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            transition: transform 0.2s ease;
        }}

        .chat-bubble-wrap:hover {{
            transform: translateX(3px);
            border-color: var(--border-accent);
        }}

        .chat-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: var(--bg-elevated);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            flex-shrink: 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }}

        .chat-bubble-content {{
            flex: 1;
        }}

        .chat-sender {{
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--accent-gold);
            margin-bottom: 0.25rem;
        }}

        .chat-bubble-text {{
            font-size: 0.95rem;
            color: var(--text-primary);
            line-height: 1.6;
        }}

        /* TOC Drawer (Sidebar) */
        .drawer-overlay {{
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(4px);
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }}

        .drawer-overlay.active {{
            opacity: 1;
            pointer-events: auto;
        }}

        .toc-drawer {{
            position: fixed;
            top: 0;
            left: 0;
            bottom: 0;
            width: 320px;
            max-width: 85vw;
            background: var(--bg-surface);
            border-right: 1px solid var(--border-subtle);
            z-index: 1010;
            transform: translateX(-100%);
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            flex-direction: column;
            box-shadow: 10px 0 40px rgba(0, 0, 0, 0.5);
        }}

        .toc-drawer.active {{
            transform: translateX(0);
        }}

        .drawer-header {{
            padding: 1.25rem;
            border-bottom: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .drawer-header h3 {{
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .close-btn {{
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 1.3rem;
            cursor: pointer;
        }}

        .toc-list {{
            padding: 1rem 0.75rem;
            overflow-y: auto;
            flex: 1;
        }}

        .toc-item-ch {{
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--accent-gold);
            padding: 0.6rem 0.75rem;
            border-radius: 8px;
            margin-top: 0.5rem;
            cursor: pointer;
            display: block;
            text-decoration: none;
            transition: background 0.15s ease;
        }}

        .toc-item-ch:hover {{
            background: var(--bg-elevated);
        }}

        .toc-item-sec {{
            font-size: 0.88rem;
            color: var(--text-secondary);
            padding: 0.45rem 0.75rem 0.45rem 1.6rem;
            border-radius: 6px;
            display: block;
            text-decoration: none;
            transition: all 0.15s ease;
            position: relative;
        }}

        .toc-item-sec:hover {{
            color: var(--accent-cyan);
            background: var(--bg-elevated);
        }}

        .toc-item-sec.active {{
            color: var(--accent-cyan);
            font-weight: 600;
            background: rgba(56, 189, 248, 0.1);
        }}

        .toc-item-sec.active::before {{
            content: "";
            position: absolute;
            left: 0.8rem;
            top: 50%;
            transform: translateY(-50%);
            width: 4px;
            height: 14px;
            border-radius: 2px;
            background: var(--accent-cyan);
        }}

        /* Settings Modal / Drawer */
        .settings-drawer {{
            position: fixed;
            top: 0;
            right: 0;
            bottom: 0;
            width: 320px;
            max-width: 85vw;
            background: var(--bg-surface);
            border-left: 1px solid var(--border-subtle);
            z-index: 1010;
            transform: translateX(100%);
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            flex-direction: column;
            box-shadow: -10px 0 40px rgba(0, 0, 0, 0.5);
            padding: 1.25rem;
            overflow-y: auto;
        }}

        .settings-drawer.active {{
            transform: translateX(0);
        }}

        .setting-group {{
            margin-bottom: 1.5rem;
        }}

        .setting-label {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 0.6rem;
            display: block;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .theme-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
        }}

        .theme-btn {{
            padding: 0.6rem 0.4rem;
            border-radius: 8px;
            border: 1px solid var(--border-subtle);
            background: var(--bg-elevated);
            color: var(--text-primary);
            font-size: 0.82rem;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.35rem;
            transition: all 0.15s ease;
        }}

        .theme-btn.active {{
            border-color: var(--accent-gold);
            background: rgba(245, 158, 11, 0.15);
            color: var(--accent-gold);
        }}

        .font-switch-wrap {{
            display: flex;
            gap: 0.4rem;
        }}

        .font-btn {{
            flex: 1;
            padding: 0.5rem 0.2rem;
            border-radius: 8px;
            border: 1px solid var(--border-subtle);
            background: var(--bg-elevated);
            color: var(--text-primary);
            font-size: 0.82rem;
            cursor: pointer;
            text-align: center;
        }}

        .font-btn.active {{
            border-color: var(--accent-cyan);
            color: var(--accent-cyan);
            font-weight: 600;
        }}

        .slider-wrap {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .slider-wrap input[type="range"] {{
            flex: 1;
            accent-color: var(--accent-gold);
        }}

        .slider-val {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--accent-gold);
            width: 40px;
            text-align: right;
        }}

        /* Floating Controls (Bottom) */
        .floating-bar {{
            position: fixed;
            bottom: 1.5rem;
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-surface-glass);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border-subtle);
            padding: 0.4rem 0.6rem;
            border-radius: 30px;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            z-index: 800;
            transition: transform 0.3s ease, opacity 0.3s ease;
        }}

        .floating-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 0.5rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.35rem;
            transition: all 0.2s ease;
        }}

        .floating-btn:hover, .floating-btn.active {{
            color: var(--text-primary);
            background: var(--bg-elevated);
        }}

        /* Resume Toast */
        .toast-resume {{
            position: fixed;
            bottom: 5.5rem;
            left: 50%;
            transform: translateX(-50%) translateY(30px);
            background: var(--bg-surface);
            border: 1px solid var(--accent-gold);
            padding: 0.85rem 1.25rem;
            border-radius: 14px;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.6);
            display: flex;
            align-items: center;
            gap: 1rem;
            z-index: 950;
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            max-width: 90vw;
        }}

        .toast-resume.show {{
            opacity: 1;
            pointer-events: auto;
            transform: translateX(-50%) translateY(0);
        }}

        .toast-text {{
            font-size: 0.88rem;
            color: var(--text-primary);
        }}

        .toast-btn {{
            background: var(--accent-gold);
            color: #000;
            border: none;
            padding: 0.4rem 0.8rem;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 700;
            cursor: pointer;
        }}

        /* Footer Info */
        footer.reader-footer {{
            text-align: center;
            padding: 3rem 1rem;
            border-top: 1px solid var(--border-subtle);
            color: var(--text-muted);
            font-size: 0.85rem;
        }}

        footer.reader-footer a {{
            color: var(--accent-cyan);
            text-decoration: none;
        }}

        /* Responsive Mobile Styles */
        @media (max-width: 640px) {{
            :root {{
                --content-font-size: 17px;
                --content-line-height: 1.85;
            }}
            main.reader-container {{
                padding: 75px 1.1rem 100px 1.1rem;
            }}
            .hero-title {{
                font-size: 2rem;
            }}
            .chapter-header {{
                padding: 1.1rem;
            }}
            .chapter-header h2 {{
                font-size: 1.35rem;
            }}
            .section-header h3 {{
                font-size: 1.15rem;
            }}
            .floating-bar {{
                bottom: 1rem;
                padding: 0.3rem 0.5rem;
            }}
            .floating-btn span {{
                display: none;
            }}
        }}
    </style>
</head>
<body>

    <!-- Progress Indicator -->
    <div id="top-progress-bar"></div>

    <!-- Header Navigation -->
    <header class="app-header" id="app-header">
        <div class="brand-title-wrap" id="btn-home">
            <div class="brand-badge">☯</div>
            <div class="brand-text">
                <h1>騎蹟到府</h1>
                <span>現代神話輕小說・正傳</span>
            </div>
        </div>
        <div class="header-actions">
            <div class="progress-pill" id="header-progress-val">0%</div>
            <button class="header-btn" id="btn-open-toc" title="章節目錄">📑</button>
            <button class="header-btn" id="btn-open-settings" title="閱讀設定">⚙️</button>
        </div>
    </header>

    <!-- Main Content Reader -->
    <main class="reader-container" id="reader-content">
        
        <!-- Novel Hero -->
        <div class="novel-hero">
            <span class="hero-tag">Taiwan Urban Fantasy</span>
            <h1 class="hero-title">騎蹟到府</h1>
            <p class="hero-author">作者：眾神守衛隊 ｜ 現代神話輕小說正傳</p>
            <div class="hero-meta-grid">
                <div class="meta-pill">📖 5 大篇章</div>
                <div class="meta-pill">⚡ 約 {total_words:,} 字</div>
                <div class="meta-pill">⏳ 閱讀約 {est_read_min} 分鐘</div>
            </div>
        </div>

        <!-- Rendered Chapters -->
'''

# Generate chapters HTML
for ch_idx, ch in enumerate(chapters):
    html_template += f'''
        <!-- Chapter {ch_idx+1}: {ch['title']} -->
        <article class="chapter-block" id="{ch['id']}">
            <div class="chapter-header">
                <h2>{ch['title']}</h2>
            </div>
    '''
    for sec_idx, sec in enumerate(ch['sections']):
        sec_content_html = render_section_content(sec['content'])
        html_template += f'''
            <section class="section-block" id="{sec['id']}">
                <div class="section-header">
                    <h3>{sec['title']}</h3>
                </div>
                <div class="section-content">
                    {sec_content_html}
                </div>
            </section>
        '''
    html_template += '</article>\n'

html_template += f'''
    </main>

    <!-- Footer -->
    <footer class="reader-footer">
        <p>《騎蹟到府》現代神話輕小說 正傳完結篇</p>
        <p style="margin-top: 0.3rem;">神明公關：誰是績優股 原創宇宙企劃 ｜ GitHub Pages 部署版</p>
    </footer>

    <!-- Bottom Floating Quick Action Bar -->
    <div class="floating-bar" id="floating-bar">
        <button class="floating-btn" id="float-btn-toc">📑 <span>章節目錄</span></button>
        <button class="floating-btn" id="float-btn-theme">🎨 <span>更換主題</span></button>
        <button class="floating-btn" id="float-btn-font-plus">A+ <span>放大</span></button>
        <button class="floating-btn" id="float-btn-font-minus">A- <span>縮小</span></button>
        <button class="floating-btn" id="float-btn-top">⬆️ <span>頂部</span></button>
    </div>

    <!-- Drawer Overlay -->
    <div class="drawer-overlay" id="drawer-overlay"></div>

    <!-- Table of Contents Drawer -->
    <div class="toc-drawer" id="toc-drawer">
        <div class="drawer-header">
            <h3>📑 章節目錄</h3>
            <button class="close-btn" id="btn-close-toc">✕</button>
        </div>
        <div class="toc-list" id="toc-list">
'''

for ch in chapters:
    html_template += f'<a href="#{ch["id"]}" class="toc-item-ch" data-target="{ch["id"]}">{ch["title"]}</a>\n'
    for sec in ch['sections']:
        html_template += f'<a href="#{sec["id"]}" class="toc-item-sec" data-target="{sec["id"]}">{sec["title"]}</a>\n'

html_template += '''
        </div>
    </div>

    <!-- Settings Drawer -->
    <div class="settings-drawer" id="settings-drawer">
        <div class="drawer-header">
            <h3>⚙️ 閱讀個人化設定</h3>
            <button class="close-btn" id="btn-close-settings">✕</button>
        </div>
        
        <!-- Theme Setting -->
        <div class="setting-group" style="margin-top: 1rem;">
            <span class="setting-label">背景主題配色</span>
            <div class="theme-grid">
                <button class="theme-btn active" data-set-theme="dark-cyber">🌙 賽博神宮</button>
                <button class="theme-btn" data-set-theme="paper-warm">📜 護眼宣紙</button>
                <button class="theme-btn" data-set-theme="light-clean">☀️ 晨曦素雅</button>
                <button class="theme-btn" data-set-theme="midnight-ink">🌌 純黑極夜</button>
            </div>
        </div>

        <!-- Font Family Setting -->
        <div class="setting-group">
            <span class="setting-label">字體切換</span>
            <div class="font-switch-wrap">
                <button class="font-btn active" data-set-font="serif">宋體 (經典)</button>
                <button class="font-btn" data-set-font="sans">黑體 (現代)</button>
                <button class="font-btn" data-set-font="kai">楷體 (古風)</button>
            </div>
        </div>

        <!-- Font Size Slider -->
        <div class="setting-group">
            <span class="setting-label">字體大小</span>
            <div class="slider-wrap">
                <input type="range" id="slider-font-size" min="15" max="25" value="18" step="1">
                <span class="slider-val" id="val-font-size">18px</span>
            </div>
        </div>

        <!-- Line Height Slider -->
        <div class="setting-group">
            <span class="setting-label">段落行距</span>
            <div class="slider-wrap">
                <input type="range" id="slider-line-height" min="1.6" max="2.3" value="1.95" step="0.05">
                <span class="slider-val" id="val-line-height">1.95</span>
            </div>
        </div>

        <!-- Content Width Slider -->
        <div class="setting-group">
            <span class="setting-label">版面寬度</span>
            <div class="slider-wrap">
                <input type="range" id="slider-max-width" min="620" max="920" value="760" step="20">
                <span class="slider-val" id="val-max-width">760px</span>
            </div>
        </div>

        <!-- Reset Button -->
        <button id="btn-reset-settings" style="width: 100%; padding: 0.6rem; background: var(--bg-elevated); border: 1px solid var(--border-subtle); color: var(--text-muted); border-radius: 8px; font-size: 0.85rem; cursor: pointer; margin-top: 1rem;">恢復預設排版</button>
    </div>

    <!-- Resume Reading Toast -->
    <div class="toast-resume" id="toast-resume">
        <div class="toast-text">
            <span>📍 發現上次閱讀進度 (<span id="resume-percent">0%</span>)</span>
        </div>
        <button class="toast-btn" id="btn-resume-jump">前往</button>
    </div>

    <!-- Interactive Script -->
    <script>
        (function() {
            // State
            const state = {
                theme: localStorage.getItem('novel_theme') || 'dark-cyber',
                fontFamily: localStorage.getItem('novel_font') || 'serif',
                fontSize: parseInt(localStorage.getItem('novel_font_size') || '18'),
                lineHeight: parseFloat(localStorage.getItem('novel_line_height') || '1.95'),
                maxWidth: parseInt(localStorage.getItem('novel_max_width') || '760'),
                lastScrollY: parseInt(localStorage.getItem('novel_scroll_y') || '0'),
                lastPercent: parseInt(localStorage.getItem('novel_scroll_percent') || '0')
            };

            // DOM elements
            const htmlEl = document.documentElement;
            const topBar = document.getElementById('top-progress-bar');
            const progressVal = document.getElementById('header-progress-val');
            const appHeader = document.getElementById('app-header');
            const drawerOverlay = document.getElementById('drawer-overlay');
            const tocDrawer = document.getElementById('toc-drawer');
            const settingsDrawer = document.getElementById('settings-drawer');
            const toastResume = document.getElementById('toast-resume');
            const resumePercent = document.getElementById('resume-percent');

            // Sliders
            const sliderFontSize = document.getElementById('slider-font-size');
            const valFontSize = document.getElementById('val-font-size');
            const sliderLineHeight = document.getElementById('slider-line-height');
            const valLineHeight = document.getElementById('val-line-height');
            const sliderMaxWidth = document.getElementById('slider-max-width');
            const valMaxWidth = document.getElementById('val-max-width');

            // Apply Settings
            function applySettings() {
                htmlEl.setAttribute('data-theme', state.theme);
                
                // Font family
                if (state.fontFamily === 'serif') {
                    document.documentElement.style.setProperty('--current-font', 'var(--font-serif)');
                } else if (state.fontFamily === 'sans') {
                    document.documentElement.style.setProperty('--current-font', 'var(--font-sans)');
                } else {
                    document.documentElement.style.setProperty('--current-font', 'var(--font-kai)');
                }

                // Font size & line height & max width
                document.documentElement.style.setProperty('--content-font-size', state.fontSize + 'px');
                document.documentElement.style.setProperty('--content-line-height', state.lineHeight);
                document.documentElement.style.setProperty('--content-max-width', state.maxWidth + 'px');

                // Update UI controls
                document.querySelectorAll('[data-set-theme]').forEach(btn => {
                    btn.classList.toggle('active', btn.getAttribute('data-set-theme') === state.theme);
                });

                document.querySelectorAll('[data-set-font]').forEach(btn => {
                    btn.classList.toggle('active', btn.getAttribute('data-set-font') === state.fontFamily);
                });

                sliderFontSize.value = state.fontSize;
                valFontSize.textContent = state.fontSize + 'px';
                sliderLineHeight.value = state.lineHeight;
                valLineHeight.textContent = state.lineHeight;
                sliderMaxWidth.value = state.maxWidth;
                valMaxWidth.textContent = state.maxWidth + 'px';

                // Save to localStorage
                localStorage.setItem('novel_theme', state.theme);
                localStorage.setItem('novel_font', state.fontFamily);
                localStorage.setItem('novel_font_size', state.fontSize);
                localStorage.setItem('novel_line_height', state.lineHeight);
                localStorage.setItem('novel_max_width', state.maxWidth);
            }

            // Scroll Handler & Progress Tracking
            let lastScroll = window.scrollY;
            let scrollTimeout = null;

            function onScroll() {
                const scrollY = window.scrollY;
                const docHeight = document.documentElement.scrollHeight - window.innerHeight;
                const percent = docHeight > 0 ? Math.min(100, Math.round((scrollY / docHeight) * 100)) : 0;

                topBar.style.width = percent + '%';
                progressVal.textContent = percent + '%';

                // Header auto-hide
                if (scrollY > 150 && scrollY > lastScroll) {
                    appHeader.classList.add('hidden');
                } else {
                    appHeader.classList.remove('hidden');
                }
                lastScroll = scrollY;

                // Save progress debounced
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {
                    localStorage.setItem('novel_scroll_y', scrollY);
                    localStorage.setItem('novel_scroll_percent', percent);
                    highlightActiveTOC();
                }, 150);
            }

            window.addEventListener('scroll', onScroll, { passive: true });

            // Highlight Active Section in TOC
            function highlightActiveTOC() {
                const sections = document.querySelectorAll('.section-block, .chapter-block');
                const scrollPos = window.scrollY + 120;
                let activeId = '';

                sections.forEach(sec => {
                    if (sec.offsetTop <= scrollPos) {
                        activeId = sec.id;
                    }
                });

                if (activeId) {
                    document.querySelectorAll('.toc-item-sec').forEach(item => {
                        item.classList.toggle('active', item.getAttribute('data-target') === activeId);
                    });
                }
            }

            // Drawer Handlers
            function openTOC() {
                drawerOverlay.classList.add('active');
                tocDrawer.classList.add('active');
                settingsDrawer.classList.remove('active');
                highlightActiveTOC();
            }

            function openSettings() {
                drawerOverlay.classList.add('active');
                settingsDrawer.classList.add('active');
                tocDrawer.classList.remove('active');
            }

            function closeDrawers() {
                drawerOverlay.classList.remove('active');
                tocDrawer.classList.remove('active');
                settingsDrawer.classList.remove('active');
            }

            document.getElementById('btn-open-toc').onclick = openTOC;
            document.getElementById('float-btn-toc').onclick = openTOC;
            document.getElementById('btn-close-toc').onclick = closeDrawers;

            document.getElementById('btn-open-settings').onclick = openSettings;
            document.getElementById('float-btn-theme').onclick = () => {
                const themes = ['dark-cyber', 'paper-warm', 'light-clean', 'midnight-ink'];
                const nextIdx = (themes.indexOf(state.theme) + 1) % themes.length;
                state.theme = themes[nextIdx];
                applySettings();
            };
            document.getElementById('btn-close-settings').onclick = closeDrawers;
            drawerOverlay.onclick = closeDrawers;

            // TOC click jumps
            document.querySelectorAll('#toc-list a').forEach(link => {
                link.addEventListener('click', (e) => {
                    closeDrawers();
                });
            });

            // Quick font size buttons
            document.getElementById('float-btn-font-plus').onclick = () => {
                if (state.fontSize < 25) {
                    state.fontSize += 1;
                    applySettings();
                }
            };
            document.getElementById('float-btn-font-minus').onclick = () => {
                if (state.fontSize > 15) {
                    state.fontSize -= 1;
                    applySettings();
                }
            };
            document.getElementById('float-btn-top').onclick = () => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            };
            document.getElementById('btn-home').onclick = () => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            };

            // Settings events
            document.querySelectorAll('[data-set-theme]').forEach(btn => {
                btn.onclick = () => {
                    state.theme = btn.getAttribute('data-set-theme');
                    applySettings();
                };
            });

            document.querySelectorAll('[data-set-font]').forEach(btn => {
                btn.onclick = () => {
                    state.fontFamily = btn.getAttribute('data-set-font');
                    applySettings();
                };
            });

            sliderFontSize.oninput = (e) => {
                state.fontSize = parseInt(e.target.value);
                applySettings();
            };
            sliderLineHeight.oninput = (e) => {
                state.lineHeight = parseFloat(e.target.value);
                applySettings();
            };
            sliderMaxWidth.oninput = (e) => {
                state.maxWidth = parseInt(e.target.value);
                applySettings();
            };

            document.getElementById('btn-reset-settings').onclick = () => {
                state.theme = 'dark-cyber';
                state.fontFamily = 'serif';
                state.fontSize = 18;
                state.lineHeight = 1.95;
                state.maxWidth = 760;
                applySettings();
            };

            // Resume Reading Toast
            if (state.lastScrollY > 300 && state.lastPercent > 2) {
                resumePercent.textContent = state.lastPercent + '%';
                toastResume.classList.add('show');

                document.getElementById('btn-resume-jump').onclick = () => {
                    window.scrollTo({ top: state.lastScrollY, behavior: 'smooth' });
                    toastResume.classList.remove('show');
                };

                setTimeout(() => {
                    toastResume.classList.remove('show');
                }, 8000);
            }

            // Init
            applySettings();
            onScroll();
        })();
    </script>
</body>
</html>
'''

with open(r"d:\聯合大學\專題\本傳續寫\index.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("Rebuilt index.html with clean titles without raw asterisks! Size:", len(html_template))
