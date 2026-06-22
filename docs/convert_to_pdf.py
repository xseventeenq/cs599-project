#!/usr/bin/env python3
"""
将 CS599_大作业报告.md 转换为带书签跳转的 PDF
使用 fpdf2（纯 Python，无需系统依赖）
"""

import re, os
from fpdf import FPDF

# ── 字体 ──────────────────────────────────────────────────────
FONT_DIR = r"C:\Windows\Fonts"
FONT_SONG = os.path.join(FONT_DIR, "simsun.ttc")
FONT_HEI  = os.path.join(FONT_DIR, "simhei.ttf")
FONT_MONO = os.path.join(FONT_DIR, "consola.ttf")

# ── 读取 MD ───────────────────────────────────────────────────
md_path = r"D:\SoftWare\VSCode\code\cs599-project\docs\CS599_大作业报告.md"
with open(md_path, "r", encoding="utf-8") as f:
    raw = f.read()

# ── 解析 Markdown 为元素 ──────────────────────────────────────

class MD:
    __slots__ = ('typ', 'txt', 'lv', 'ext')
    def __init__(self, typ, txt='', lv=0, ext=None):
        self.typ = typ; self.txt = txt; self.lv = lv; self.ext = ext or {}

def parse_md(text):
    """解析 MD 文本为元素列表"""
    lines = text.split('\n')
    els = []
    i = 0
    while i < len(lines):
        ln = lines[i]

        if ln.strip() == '':
            els.append(MD('gap'))
            i += 1; continue

        # 标题
        m = re.match(r'^(#{1,6})\s+(.+?)\s*$', ln)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            aid = ''
            am = re.search(r'\{#([\w-]+)\}', title)
            if am:
                aid = am.group(1)
                title = re.sub(r'\s*\{#[\w-]+\}', '', title).strip()
            els.append(MD('h', title, level, {'aid': aid}))
            i += 1; continue

        # 水平线
        if re.match(r'^-{3,}\s*$', ln) or re.match(r'^\*{3,}\s*$', ln):
            els.append(MD('hr'))
            i += 1; continue

        # 代码块
        if ln.startswith('```'):
            lang = ln[3:].strip()
            cl = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                cl.append(lines[i]); i += 1
            i += 1
            els.append(MD('code', '\n'.join(cl), ext={'lang': lang}))
            continue

        # 表格
        if ln.strip().startswith('|') and ln.strip().endswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                rows.append(cells)
                i += 1
            rows = [r for r in rows if not all(re.match(r'^[-:]+$', c) for c in r)]
            els.append(MD('table', ext={'rows': rows}))
            continue

        # 无序列表
        if re.match(r'^\s*[-*+]\s+', ln):
            items = []
            while i < len(lines) and re.match(r'^\s*[-*+]\s+', lines[i]):
                items.append(re.sub(r'^\s*[-*+]\s+', '', lines[i]))
                i += 1
            els.append(MD('ul', ext={'items': items}))
            continue

        # 有序列表
        if re.match(r'^\s*\d+[.)]\s+', ln):
            items = []
            while i < len(lines) and re.match(r'^\s*\d+[.)]\s+', lines[i]):
                items.append(re.sub(r'^\s*\d+[.)]\s+', '', lines[i]))
                i += 1
            els.append(MD('ol', ext={'items': items}))
            continue

        # 块引用
        if ln.startswith('>'):
            ql = []
            while i < len(lines) and lines[i].startswith('>'):
                ql.append(lines[i][1:].strip())
                i += 1
            els.append(MD('quote', ' '.join(ql)))
            continue

        # 段落
        pl = []
        while i < len(lines) and lines[i].strip() != '' and not \
              (lines[i].startswith('```') or lines[i].startswith('|') or \
               re.match(r'^(#{1,6})\s', lines[i]) or \
               re.match(r'^\s*[-*+]\s+', lines[i]) or \
               re.match(r'^\s*\d+[.)]\s+', lines[i]) or \
               lines[i].startswith('>') or re.match(r'^-{3,}\s*$', lines[i])):
            pl.append(lines[i])
            i += 1
        if pl:
            els.append(MD('p', ' '.join(pl)))
        else:
            i += 1

    return els

elements = parse_md(raw)

# ── 内联清理 ──────────────────────────────────────────────────
def clean(t):
    t = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    t = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', t)
    t = re.sub(r'`([^`]+)`', r'\1', t)
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    t = re.sub(r'!\[.*?\]\([^)]+\)', '[图]', t)
    t = re.sub(r'<[^>]+>', '', t)
    return t

# ── PDF 类 ─────────────────────────────────────────────────────
class MPDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.add_font("S", "", FONT_SONG)
        self.add_font("H", "", FONT_HEI)
        self.add_font("M", "", FONT_MONO)
        self.set_auto_page_break(True, 20)

    def header(self):
        if self.page_no() > 1:
            self.set_font("H", "", 8)
            self.set_text_color(150,150,150)
            self.cell(0, 5, "CS599 · 大作业报告", align='C')
            self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("S", "", 8)
        self.set_text_color(150,150,150)
        self.cell(0, 10, f"— {self.page_no()} —", align='C')

    def put_heading(self, title, level, aid=''):
        sz = {1:18, 2:14, 3:12, 4:11, 5:10}.get(level, 12)
        clr = {1:(26,82,118), 2:(36,113,163), 3:(46,134,193)}.get(level, (0,0,0))
        self.set_font("H", "", sz)
        self.set_text_color(*clr)
        if level <= 2:
            self.ln(3)
        self.multi_cell(0, 7.5, clean(title))
        if level == 1:
            y = self.get_y()
            self.set_draw_color(*clr)
            self.set_line_width(0.5)
            self.line(10, y, 200, y)
        elif level == 2:
            y = self.get_y()
            self.set_draw_color(212,230,241)
            self.set_line_width(0.3)
            self.line(10, y, 200, y)
        self.ln(4)
        if level <= 3:
            self.start_section(clean(title), level - 1)

    def put_para(self, text, size=10.5):
        text = clean(text)
        if not text or text in ['---']:
            return
        self.set_font("S", "", size)
        self.set_text_color(51,51,51)
        self.multi_cell(0, 6.2, text)
        self.ln(1.5)

    def put_code(self, text, lang=''):
        self.ln(2)
        self.set_font("M", "", 7.5)
        self.set_text_color(40,40,40)
        for line in text.split('\n'):
            if self.get_y() > 272:
                self.add_page()
            y = self.get_y()
            self.set_draw_color(26,82,118)
            self.set_line_width(0.6)
            self.line(10, y, 10, y + 4)
            self.set_x(13)
            self.cell(0, 4, line[:130])
            self.ln()
        self.set_text_color(51,51,51)
        self.ln(3)

    def put_table(self, rows):
        self.ln(2)
        nc = max(len(r) for r in rows) if rows else 1
        cw = 190 / nc
        for ri, row in enumerate(rows):
            while len(row) < nc:
                row.append('')
            texts = [clean(c) for c in row]
            # 估算行高
            row_h = 7
            for ct in texts:
                lines_n = max(1, len(ct) * 3.5 / cw + 1)
                row_h = max(row_h, lines_n * 4.5 + 1)
            row_h = min(row_h, 35)
            if self.get_y() + row_h > 270:
                self.add_page()
            y0 = self.get_y()
            x0 = self.get_x()
            for ci, ct in enumerate(texts):
                x = x0 + ci * cw
                if ri == 0:
                    self.set_fill_color(26,82,118)
                    self.set_text_color(255,255,255)
                    self.set_font("H", "", 8)
                else:
                    bg = (245,247,250) if ri % 2 == 0 else (255,255,255)
                    self.set_fill_color(*bg)
                    self.set_text_color(51,51,51)
                    self.set_font("S", "", 8)
                self.set_draw_color(210,210,210)
                self.rect(x, y0, cw, row_h, style='DF')
                self.set_xy(x + 1.5, y0 + 1.5)
                display = ct[:int(cw*2)] if len(ct) > cw*2 else ct
                self.multi_cell(cw - 3, 4.5, display)
            self.set_y(y0 + row_h)
        self.ln(4)

    def put_list(self, items, ordered=False):
        self.ln(1)
        self.set_font("S", "", 10)
        self.set_text_color(51,51,51)
        for idx, it in enumerate(items):
            prefix = f"{idx + 1}. " if ordered else "• "
            self.cell(8, 5.5, prefix)
            self.multi_cell(172, 5.5, clean(it))
            self.ln(0.5)
        self.ln(2)

    def put_hr(self):
        self.ln(3)
        y = self.get_y()
        self.set_draw_color(200,200,200)
        self.set_line_width(0.3)
        self.line(10, y, 200, y)
        self.ln(5)

    def put_quote(self, text):
        self.ln(2)
        self.set_font("S", "", 9.5)
        self.set_text_color(100,100,100)
        self.set_x(15)
        self.multi_cell(175, 5.5, clean(text))
        self.ln(4)

# ── 构建 PDF ──────────────────────────────────────────────────
pdf = MPDF()
pdf.add_page()

# ═══ 封面 ═══
pdf.set_font("H", "", 24)
pdf.set_text_color(26,82,118)
pdf.ln(40)
pdf.cell(0, 15, "企业级应用软件设计与开发", align='C')
pdf.ln(18)
pdf.set_font("H", "", 20)
pdf.cell(0, 12, "课程大作业报告", align='C')
pdf.ln(30)

cover_info = [
    ("项目名称", "UAV-Mission-Agent"),
    ("", "面向多无人机任务分配的多智能体协作 Agent 系统"),
    ("方向", "方向一：Agentic AI 原生开发"),
    ("学号", "2025303021"),
    ("姓名", "熊谦"),
    ("专业", "计算机技术 / 软件工程"),
    ("指导教师", "戚欣"),
    ("提交日期", "2026 年 6 月 22 日"),
]
cw1, cw2 = 36, 118
sx = (210 - cw1 - cw2) / 2
pdf.set_font("S", "", 10)
pdf.set_text_color(51,51,51)
for lbl, val in cover_info:
    pdf.set_x(sx)
    if lbl:
        pdf.set_font("H", "", 10)
        pdf.set_fill_color(245,245,245)
        pdf.set_draw_color(200,200,200)
        pdf.cell(cw1, 9, lbl, border=1, fill=True, align='R')
    else:
        pdf.set_fill_color(245,245,245)
        pdf.set_draw_color(200,200,200)
        pdf.cell(cw1, 9, '', border=1, fill=True)
    pdf.set_font("S", "", 10)
    pdf.cell(cw2, 9, val, border=1)
    pdf.ln()
pdf.ln(40)
pdf.set_font("S", "", 9)
pdf.set_text_color(150,150,150)
pdf.cell(0, 8, "武汉理工大学  ·  计算机与人工智能学院", align='C')

# ═══ 内容 ═══
# 找到第一个正式内容标题 (选题背景)
start_idx = 0
for i, e in enumerate(elements):
    if e.typ == 'h' and '选题背景' in e.txt:
        start_idx = i
        break

pdf.add_page()

for e in elements[start_idx:]:
    if e.typ == 'gap':
        pdf.ln(2)
    elif e.typ == 'h':
        if e.lv == 1 and pdf.get_y() > 50:
            pdf.add_page()
        pdf.put_heading(e.txt, e.lv, e.ext.get('aid', ''))
    elif e.typ == 'p':
        pdf.put_para(e.txt)
    elif e.typ == 'code':
        pdf.put_code(e.txt, e.ext.get('lang', ''))
    elif e.typ == 'table':
        if e.ext.get('rows'):
            pdf.put_table(e.ext['rows'])
    elif e.typ == 'ul':
        if e.ext.get('items'):
            pdf.put_list(e.ext['items'])
    elif e.typ == 'ol':
        if e.ext.get('items'):
            pdf.put_list(e.ext['items'], ordered=True)
    elif e.typ == 'hr':
        pdf.put_hr()
    elif e.typ == 'quote':
        pdf.put_quote(e.txt)

# ── 保存 ──────────────────────────────────────────────────────
out = r"D:\SoftWare\VSCode\code\cs599-project\docs\CS599_大作业报告.pdf"
pdf.output(out)
print(f"✅ PDF 已生成：{out}")
print(f"   共 {pdf.page_no()} 页")
print(f"   在 PDF 阅读器中打开左侧「书签/大纲」面板即可点击跳转各章节")
