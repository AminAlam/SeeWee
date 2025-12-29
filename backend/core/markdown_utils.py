"""
Markdown conversion utilities for CV exports.

Converts Markdown to:
- LaTeX (for PDF generation)
- HTML (for web preview and bundle)
- Plain text (for LinkedIn and other plain text exports)
"""

from __future__ import annotations

import re
import html
from typing import Any

import markdown
import mistune


# =============================================================================
# MARKDOWN TO HTML
# =============================================================================

_md_to_html = markdown.Markdown(
    extensions=['extra', 'smarty', 'sane_lists'],
    output_format='html5'
)


def md_to_html(text: str) -> str:
    """Convert Markdown to HTML."""
    if not text:
        return ""
    _md_to_html.reset()
    result = _md_to_html.convert(text)
    return result


def md_to_html_inline(text: str) -> str:
    """Convert Markdown to HTML, stripping outer <p> tags for inline use."""
    if not text:
        return ""
    result = md_to_html(text)
    # Strip outer <p>...</p> if it's a single paragraph
    result = result.strip()
    if result.startswith('<p>') and result.endswith('</p>') and result.count('<p>') == 1:
        result = result[3:-4]
    return result


# =============================================================================
# MARKDOWN TO PLAIN TEXT
# =============================================================================

def md_to_plain(text: str) -> str:
    """Convert Markdown to plain text (strip all formatting)."""
    if not text:
        return ""
    
    # Convert to HTML first, then strip tags
    html_text = md_to_html(text)
    
    # Decode HTML entities
    plain = html.unescape(html_text)
    
    # Remove HTML tags
    plain = re.sub(r'<[^>]+>', '', plain)
    
    # Clean up whitespace
    plain = re.sub(r'\n\s*\n', '\n\n', plain)
    plain = plain.strip()
    
    return plain


# =============================================================================
# MARKDOWN TO LATEX
# =============================================================================

class LaTeXRenderer(mistune.HTMLRenderer):
    """Custom Mistune renderer that outputs LaTeX instead of HTML."""
    
    def text(self, text: str) -> str:
        return _escape_latex(text)
    
    def emphasis(self, text: str) -> str:
        return f'\\textit{{{text}}}'
    
    def strong(self, text: str) -> str:
        return f'\\textbf{{{text}}}'
    
    def strikethrough(self, text: str) -> str:
        return f'\\sout{{{text}}}'
    
    def codespan(self, text: str) -> str:
        # Escape for texttt
        escaped = text.replace('\\', '\\textbackslash{}')
        escaped = escaped.replace('{', '\\{').replace('}', '\\}')
        escaped = escaped.replace('_', '\\_').replace('%', '\\%')
        escaped = escaped.replace('$', '\\$').replace('#', '\\#')
        escaped = escaped.replace('&', '\\&').replace('~', '\\textasciitilde{}')
        escaped = escaped.replace('^', '\\textasciicircum{}')
        return f'\\texttt{{{escaped}}}'
    
    def link(self, text: str, url: str, title: str | None = None) -> str:
        # Escape URL special chars for LaTeX
        safe_url = url.replace('%', '\\%').replace('#', '\\#').replace('&', '\\&')
        safe_url = safe_url.replace('_', '\\_')
        return f'\\href{{{safe_url}}}{{{text}}}'
    
    def image(self, text: str, url: str, title: str | None = None) -> str:
        # Skip images in LaTeX (or could include if needed)
        return f'[Image: {text}]'
    
    def linebreak(self) -> str:
        return ' \\\\\n'
    
    def newline(self) -> str:
        return '\n'
    
    def paragraph(self, text: str) -> str:
        return f'{text}\n\n'
    
    def heading(self, text: str, level: int, **attrs: Any) -> str:
        # For CV entries, headings become bold text
        if level == 1:
            return f'\\textbf{{\\large {text}}}\n\n'
        elif level == 2:
            return f'\\textbf{{{text}}}\n\n'
        else:
            return f'\\textbf{{{text}}} '
    
    def block_code(self, code: str, info: str | None = None) -> str:
        escaped = _escape_latex(code)
        return f'\\begin{{verbatim}}\n{code}\\end{{verbatim}}\n\n'
    
    def block_quote(self, text: str) -> str:
        return f'\\begin{{quote}}\n{text}\\end{{quote}}\n\n'
    
    def list(self, body: str, ordered: bool, **attrs: Any) -> str:
        env = 'enumerate' if ordered else 'itemize'
        return f'\\begin{{{env}}}\n{body}\\end{{{env}}}\n'
    
    def list_item(self, text: str, **attrs: Any) -> str:
        # Remove trailing newlines from text for cleaner output
        text = text.strip()
        return f'\\item {text}\n'
    
    def thematic_break(self) -> str:
        return '\\vspace{0.5em}\\hrule\\vspace{0.5em}\n\n'


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters."""
    if not text:
        return ""
    
    # Order matters - backslash first
    replacements = [
        ('\\', '\\textbackslash{}'),
        ('{', '\\{'),
        ('}', '\\}'),
        ('$', '\\$'),
        ('#', '\\#'),
        ('%', '\\%'),
        ('&', '\\&'),
        ('_', '\\_'),
        ('~', '\\textasciitilde{}'),
        ('^', '\\textasciicircum{}'),
    ]
    
    for old, new in replacements:
        text = text.replace(old, new)
    
    return text


# Create the LaTeX markdown parser
_latex_renderer = LaTeXRenderer()
_md_to_latex = mistune.create_markdown(renderer=_latex_renderer)


def md_to_latex(text: str) -> str:
    """Convert Markdown to LaTeX."""
    if not text:
        return ""
    result = _md_to_latex(text)
    # Clean up extra newlines
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result.strip()


def md_to_latex_inline(text: str) -> str:
    """Convert Markdown to LaTeX for inline use (no paragraph breaks)."""
    if not text:
        return ""
    result = md_to_latex(text)
    # Remove paragraph breaks for inline use
    result = result.replace('\n\n', ' ').replace('\n', ' ')
    return result.strip()


# =============================================================================
# BATCH PROCESSING FOR ENTRY DATA
# =============================================================================

# Fields that should be treated as markdown
MARKDOWN_FIELDS = {
    # Common fields
    'description', 'summary', 'notes', 'bio', 'about',
    # Bullet/highlight fields (each item is markdown)
    'highlights', 'bullets', 'responsibilities', 'achievements',
    # Honor/award descriptions
    'honors', 'citation',
    # Other rich text fields
    'abstract', 'content',
}

# Fields that are lists where each item should be markdown-processed
LIST_MARKDOWN_FIELDS = {'highlights', 'bullets', 'responsibilities', 'achievements'}


def process_entry_markdown(data: dict[str, Any], target: str = 'html') -> dict[str, Any]:
    """
    Process markdown fields in entry data for the specified target format.
    
    Args:
        data: Entry data dictionary
        target: 'html', 'latex', or 'plain'
    
    Returns:
        New dictionary with markdown fields converted
    """
    if not data:
        return data
    
    if target == 'html':
        converter = md_to_html_inline
        list_converter = md_to_html_inline
    elif target == 'latex':
        converter = md_to_latex_inline
        list_converter = md_to_latex_inline
    else:  # plain
        converter = md_to_plain
        list_converter = md_to_plain
    
    result = {}
    for key, value in data.items():
        if key in LIST_MARKDOWN_FIELDS and isinstance(value, list):
            # Process each item in the list
            result[key] = [list_converter(item) if isinstance(item, str) else item for item in value]
        elif key in MARKDOWN_FIELDS and isinstance(value, str):
            result[key] = converter(value)
        else:
            result[key] = value
    
    return result


def process_profile_markdown(profile: dict[str, Any], target: str = 'html') -> dict[str, Any]:
    """Process markdown fields in profile data."""
    if not profile:
        return profile
    
    if target == 'html':
        converter = md_to_html_inline
    elif target == 'latex':
        converter = md_to_latex_inline
    else:
        converter = md_to_plain
    
    result = dict(profile)
    
    # Process content section
    if 'content' in result and isinstance(result['content'], dict):
        content = dict(result['content'])
        for field in ['summary', 'bio', 'tagline']:
            if field in content and isinstance(content[field], str):
                content[field] = converter(content[field])
        result['content'] = content
    
    return result

