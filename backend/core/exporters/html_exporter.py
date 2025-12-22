from __future__ import annotations

import json
from typing import Any

from core.document_model import Document
from core.entry_schemas import normalize_entry


def _safe_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _normalize_items_for_html(doc: Document) -> list[dict]:
    """Normalize all items using the schema registry for consistent rendering."""
    sections = []
    for s in doc.sections:
        items = []
        for i in s.items:
            normalized = normalize_entry(i.entry_type, i.data or {})
            items.append({
                "entry_id": i.entry_id,
                "entry_type": i.entry_type,
                "tags": i.tags,
                "data": i.data,
                "normalized": normalized,
            })
        sections.append({
            "id": s.id,
            "title": s.title,
            "items": items,
        })
    return sections


def render_html_bundle(doc: Document) -> dict[str, str]:
    """
    Returns a dict of filename -> content for a static HTML CV viewer.
    """
    sections = _normalize_items_for_html(doc)
    doc_json = _safe_json({
        "variant_id": doc.variant_id,
        "generated_at": doc.generated_at.isoformat(),
        "sections": sections,
    })

    index_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SeeWee CV</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: 'Source Serif 4', Georgia, serif;
      margin: 0;
      background: #fafafa;
      color: #1a1a1a;
      line-height: 1.6;
    }}
    .container {{
      max-width: 850px;
      margin: 0 auto;
      padding: 40px 32px;
      background: #fff;
      min-height: 100vh;
      box-shadow: 0 0 40px rgba(0,0,0,0.08);
    }}
    header {{
      text-align: center;
      margin-bottom: 32px;
      padding-bottom: 24px;
      border-bottom: 2px solid #1a1a1a;
    }}
    h1 {{
      margin: 0;
      font-size: 28px;
      font-weight: 700;
      letter-spacing: 0.5px;
    }}
    .contact {{
      margin-top: 12px;
      font-size: 14px;
      color: #444;
    }}
    .contact a {{
      color: #2563eb;
      text-decoration: none;
    }}
    .contact a:hover {{
      text-decoration: underline;
    }}
    section {{
      margin: 28px 0;
    }}
    h2 {{
      font-size: 16px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      border-bottom: 1px solid #ddd;
      padding-bottom: 8px;
      margin: 0 0 16px 0;
      color: #1a1a1a;
    }}
    .entry {{
      margin: 16px 0;
      text-align: justify;
    }}
    .entry-header {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 4px;
    }}
    .entry-title {{
      font-weight: 700;
      font-size: 15px;
      color: #1a1a1a;
    }}
    .entry-date {{
      font-size: 13px;
      color: #666;
      font-style: italic;
      white-space: nowrap;
    }}
    .entry-subtitle {{
      font-size: 14px;
      color: #444;
      margin-bottom: 6px;
    }}
    .entry-meta {{
      font-size: 13px;
      color: #666;
      margin-bottom: 6px;
    }}
    .entry-body {{
      font-size: 14px;
      color: #333;
      text-align: justify;
    }}
    ul {{
      margin: 8px 0 0 0;
      padding-left: 20px;
    }}
    li {{
      margin: 4px 0;
      text-align: justify;
    }}
    .skill-row {{
      margin: 8px 0;
    }}
    .skill-category {{
      font-weight: 600;
      color: #1a1a1a;
    }}
    .skill-items {{
      color: #333;
    }}
    .pub-title {{
      font-weight: 600;
    }}
    .pub-meta {{
      font-size: 13px;
      color: #555;
      font-style: italic;
    }}
    .tags {{
      font-size: 11px;
      color: #888;
      margin-top: 4px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Curriculum Vitae</h1>
      <div class="contact" id="contact"></div>
    </header>
    <main id="root"></main>
  </div>
  <script>
    window.SEEWEE_DOC = {doc_json};
  </script>
  <script src="./app.js"></script>
</body>
</html>
"""

    app_js = r"""
function renderEntry(item, sectionId) {
  const d = item.data || {};
  const n = item.normalized || d;
  const type = item.entry_type || "";
  
  const div = document.createElement("div");
  div.className = "entry";
  
  // EXPERIENCE
  if (type === "experience") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("span");
    title.className = "entry-title";
    title.textContent = n.role || d.role || d.title || "Position";
    if (n.lead) title.textContent += " / " + n.lead;
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n._dates || d.dates || "";
    header.appendChild(date);
    div.appendChild(header);
    
    const subtitle = document.createElement("div");
    subtitle.className = "entry-subtitle";
    const parts = [n.company || d.company || d.org, n.location || d.location].filter(Boolean);
    subtitle.textContent = parts.join(", ");
    if (parts.length) div.appendChild(subtitle);
    
    const highlights = n.highlights || d.highlights || [];
    if (highlights.length) {
      const ul = document.createElement("ul");
      highlights.forEach(h => {
        if (h && h.trim()) {
          const li = document.createElement("li");
          li.textContent = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // EDUCATION
  if (type === "education") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("span");
    title.className = "entry-title";
    title.textContent = n.school || d.school || d.institution || "Institution";
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n._dates || d.dates || [d.start_date, d.end_date].filter(Boolean).join(" - ");
    header.appendChild(date);
    div.appendChild(header);
    
    const subtitle = document.createElement("div");
    subtitle.className = "entry-subtitle";
    const degreeParts = [n.degree || d.degree];
    if (n.gpa || d.gpa) degreeParts.push("GPA: " + (n.gpa || d.gpa));
    subtitle.textContent = degreeParts.filter(Boolean).join(" | ");
    div.appendChild(subtitle);
    
    if (n.honors || d.honors) {
      const honors = document.createElement("div");
      honors.className = "entry-meta";
      honors.style.fontStyle = "italic";
      honors.textContent = n.honors || d.honors;
      div.appendChild(honors);
    }
    
    const highlights = n.highlights || d.highlights || [];
    if (highlights.length) {
      const ul = document.createElement("ul");
      highlights.forEach(h => {
        if (h && h.trim()) {
          const li = document.createElement("li");
          li.textContent = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // PROJECT
  if (type === "project") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("span");
    title.className = "entry-title";
    const name = n.name || d.name || d.title || "Project";
    if (n.link || d.link) {
      const a = document.createElement("a");
      a.href = n.link || d.link;
      a.textContent = name;
      a.target = "_blank";
      title.appendChild(a);
    } else {
      title.textContent = name;
    }
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n._dates || d.dates || "";
    header.appendChild(date);
    div.appendChild(header);
    
    const techStack = n.tech_stack || d.tech_stack || [];
    if (techStack.length) {
      const tech = document.createElement("div");
      tech.className = "entry-meta";
      tech.innerHTML = "<strong>Tech:</strong> " + techStack.join(", ");
      div.appendChild(tech);
    }
    
    const highlights = n.highlights || d.highlights || [];
    if (highlights.length) {
      const ul = document.createElement("ul");
      highlights.forEach(h => {
        if (h && h.trim()) {
          const li = document.createElement("li");
          li.textContent = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // PUBLICATION
  if (type === "publication") {
    const titleDiv = document.createElement("div");
    titleDiv.className = "pub-title";
    titleDiv.textContent = n.title || d.title || "Publication";
    div.appendChild(titleDiv);
    
    const metaParts = [];
    if (n.authors || d.authors) metaParts.push(n.authors || d.authors);
    if (n.venue || d.venue) metaParts.push(n.venue || d.venue);
    if (n.year || d.year) metaParts.push(n.year || d.year);
    if (metaParts.length) {
      const meta = document.createElement("div");
      meta.className = "pub-meta";
      meta.textContent = metaParts.join(" — ");
      div.appendChild(meta);
    }
    
    const links = [];
    if (n.link || d.link) links.push('<a href="' + (n.link || d.link) + '" target="_blank">[Link]</a>');
    if (n.doi || d.doi) links.push('<a href="https://doi.org/' + (n.doi || d.doi) + '" target="_blank">[DOI]</a>');
    if (links.length) {
      const linkDiv = document.createElement("div");
      linkDiv.innerHTML = links.join(" ");
      div.appendChild(linkDiv);
    }
    return div;
  }
  
  // SKILL
  if (type === "skill") {
    div.className = "skill-row";
    const category = n.category || d.category || n.name || d.name || "Skills";
    const items = n.skill_list || n.items || d.skill_list || d.items || [];
    if (items.length) {
      div.innerHTML = '<span class="skill-category">' + category + ':</span> <span class="skill-items">' + items.join(", ") + '</span>';
    } else if (n.name || d.name) {
      const level = n.level || d.level;
      div.innerHTML = '<span class="skill-category">' + (n.name || d.name) + '</span>' + (level ? ' <span class="skill-items">(' + level + ')</span>' : '');
    }
    return div;
  }
  
  // AWARD
  if (type === "award") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("span");
    title.className = "entry-title";
    title.textContent = n.title || d.title || d.name || "Award";
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n.date || d.date || d.year || "";
    header.appendChild(date);
    div.appendChild(header);
    
    if (n.issuer || d.issuer) {
      const issuer = document.createElement("div");
      issuer.className = "entry-subtitle";
      issuer.textContent = n.issuer || d.issuer;
      div.appendChild(issuer);
    }
    
    if (n.description || d.description) {
      const desc = document.createElement("div");
      desc.className = "entry-body";
      desc.textContent = n.description || d.description;
      div.appendChild(desc);
    }
    
    const highlights = n.highlights || d.highlights || [];
    if (highlights.length) {
      const ul = document.createElement("ul");
      highlights.forEach(h => {
        if (h && h.trim()) {
          const li = document.createElement("li");
          li.textContent = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // VOLUNTEERING
  if (type === "volunteering") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("span");
    title.className = "entry-title";
    title.textContent = n.role || d.role || d.title || "Role";
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n._dates || d.dates || "";
    header.appendChild(date);
    div.appendChild(header);
    
    if (n.organization || d.organization) {
      const org = document.createElement("div");
      org.className = "entry-subtitle";
      org.textContent = n.organization || d.organization;
      div.appendChild(org);
    }
    
    const highlights = n.highlights || d.highlights || [];
    if (highlights.length) {
      const ul = document.createElement("ul");
      highlights.forEach(h => {
        if (h && h.trim()) {
          const li = document.createElement("li");
          li.textContent = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // CERTIFICATION
  if (type === "certification") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("span");
    title.className = "entry-title";
    const name = n.name || d.name || d.title || "Certification";
    if (n.link || d.link) {
      const a = document.createElement("a");
      a.href = n.link || d.link;
      a.textContent = name;
      a.target = "_blank";
      title.appendChild(a);
    } else {
      title.textContent = name;
    }
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n.date || d.date || "";
    header.appendChild(date);
    div.appendChild(header);
    
    if (n.issuer || d.issuer) {
      const issuer = document.createElement("div");
      issuer.className = "entry-subtitle";
      issuer.textContent = n.issuer || d.issuer;
      div.appendChild(issuer);
    }
    return div;
  }
  
  // TALK
  if (type === "talk") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("span");
    title.className = "entry-title";
    title.textContent = n.title || d.title || d.name || "Talk";
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n.date || d.date || "";
    header.appendChild(date);
    div.appendChild(header);
    
    const eventParts = [n.event || d.event, n.location || d.location].filter(Boolean);
    if (eventParts.length) {
      const event = document.createElement("div");
      event.className = "entry-subtitle";
      event.textContent = eventParts.join(", ");
      div.appendChild(event);
    }
    
    if (n.link || d.link) {
      const link = document.createElement("div");
      link.innerHTML = '<a href="' + (n.link || d.link) + '" target="_blank">[Slides/Recording]</a>';
      div.appendChild(link);
    }
    return div;
  }
  
  // LANGUAGE
  if (type === "language") {
    div.className = "skill-row";
    const name = n.name || d.name || d.language || "Language";
    const prof = n.proficiency || d.proficiency || d.level || "";
    div.innerHTML = '<span class="skill-category">' + name + '</span>' + (prof ? ': <span class="skill-items">' + prof + '</span>' : '');
    return div;
  }
  
  // REFERENCE
  if (type === "reference") {
    const title = document.createElement("div");
    title.className = "entry-title";
    title.textContent = n.name || d.name || "Reference";
    div.appendChild(title);
    
    const details = [];
    if (n.title || d.title) details.push(n.title || d.title);
    if (n.organization || d.organization) details.push(n.organization || d.organization);
    if (details.length) {
      const detailDiv = document.createElement("div");
      detailDiv.className = "entry-subtitle";
      detailDiv.textContent = details.join(", ");
      div.appendChild(detailDiv);
    }
    
    const contact = [];
    if (n.email || d.email) contact.push(n.email || d.email);
    if (n.phone || d.phone) contact.push(n.phone || d.phone);
    if (contact.length) {
      const contactDiv = document.createElement("div");
      contactDiv.className = "entry-meta";
      contactDiv.textContent = contact.join(" | ");
      div.appendChild(contactDiv);
    }
    return div;
  }
  
  // FALLBACK - generic rendering
  const header = document.createElement("div");
  header.className = "entry-header";
  const title = document.createElement("span");
  title.className = "entry-title";
  title.textContent = d.title || d.role || d.name || d.header || type;
  header.appendChild(title);
  const date = document.createElement("span");
  date.className = "entry-date";
  date.textContent = d.dates || d.date || n._dates || "";
  header.appendChild(date);
  div.appendChild(header);
  
  const org = d.org || d.organization || d.company || d.subheader || "";
  if (org) {
    const subtitle = document.createElement("div");
    subtitle.className = "entry-subtitle";
    subtitle.textContent = org;
    div.appendChild(subtitle);
  }
  
  const highlights = d.highlights || d.bullets || [];
  if (highlights.length) {
    const ul = document.createElement("ul");
    highlights.forEach(h => {
      if (h && h.trim()) {
        const li = document.createElement("li");
        li.textContent = h;
        ul.appendChild(li);
      }
    });
    div.appendChild(ul);
  }
  
  return div;
}

function render() {
  const root = document.getElementById("root");
  const doc = window.SEEWEE_DOC;
  root.innerHTML = "";
  
  (doc.sections || []).forEach(s => {
    if (!s.items || s.items.length === 0) return;
    
    const section = document.createElement("section");
    const h2 = document.createElement("h2");
    h2.textContent = s.title;
    section.appendChild(h2);
    
    s.items.forEach(item => {
      section.appendChild(renderEntry(item, s.id));
    });
    
    root.appendChild(section);
  });
}

render();
"""

    return {"index.html": index_html, "app.js": app_js}


def render_academicpages_like_preview(doc: Document, profile: dict[str, Any]) -> str:
    """
    Academic Pages style website - sidebar with profile, main content with sections.
    Modern, clean web design for personal academic/professional homepage.
    """
    links = (profile or {}).get("links") or {}
    personal = (profile or {}).get("personal") or {}
    content = (profile or {}).get("content") or {}

    full_name = personal.get("full_name", "Your Name")
    tagline = content.get("tagline", "Researcher & Engineer")
    summary = content.get("summary", "")
    avatar = personal.get("avatar", "")

    sections = _normalize_items_for_html(doc)
    doc_json = _safe_json({
        "variant_id": doc.variant_id,
        "generated_at": doc.generated_at.isoformat(),
        "sections": sections,
    })

    email = links.get("email", "")
    phone = links.get("phone", "")
    address = links.get("address", "")
    github = links.get("github", "")
    linkedin = links.get("linkedin", "")
    website = links.get("website", "")
    twitter = links.get("twitter", "")
    scholar = links.get("scholar", "")

    # Build social links
    social_links = []
    if email:
        social_links.append(f'<a href="mailto:{email}" class="social-link"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg><span>{email}</span></a>')
    if github:
        social_links.append(f'<a href="{github}" target="_blank" class="social-link"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg><span>GitHub</span></a>')
    if linkedin:
        social_links.append(f'<a href="{linkedin}" target="_blank" class="social-link"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg><span>LinkedIn</span></a>')
    if scholar:
        social_links.append(f'<a href="{scholar}" target="_blank" class="social-link"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M5.242 13.769L0 9.5 12 0l12 9.5-5.242 4.269C17.548 11.249 14.978 9.5 12 9.5c-2.977 0-5.548 1.748-6.758 4.269zM12 10a7 7 0 1 0 0 14 7 7 0 0 0 0-14z"/></svg><span>Scholar</span></a>')
    if twitter:
        social_links.append(f'<a href="{twitter}" target="_blank" class="social-link"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg><span>X/Twitter</span></a>')
    if website:
        social_links.append(f'<a href="{website}" target="_blank" class="social-link"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg><span>Website</span></a>')
    if phone:
        social_links.append(f'<div class="social-link"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg><span>{phone}</span></div>')
    if address:
        social_links.append(f'<div class="social-link"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg><span>{address}</span></div>')

    social_html = "\n".join(social_links)

    # Build navigation from sections
    nav_items = []
    for s in sections:
        if s["items"]:
            nav_items.append(f'<a href="#{s["id"]}" class="nav-link">{s["title"]}</a>')
    nav_html = "\n".join(nav_items)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{full_name}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    :root {{
      --bg-primary: #f8fafc;
      --bg-sidebar: #1e293b;
      --bg-card: #ffffff;
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #64748b;
      --text-sidebar: #e2e8f0;
      --text-sidebar-muted: #94a3b8;
      --accent: #3b82f6;
      --accent-hover: #2563eb;
      --border: #e2e8f0;
      --shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
      --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
    }}
    
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg-primary);
      color: var(--text-primary);
      line-height: 1.6;
      font-size: 15px;
    }}
    
    .layout {{
      display: grid;
      grid-template-columns: 300px 1fr;
      min-height: 100vh;
    }}
    
    /* Sidebar */
    .sidebar {{
      background: var(--bg-sidebar);
      color: var(--text-sidebar);
      padding: 40px 28px;
      position: sticky;
      top: 0;
      height: 100vh;
      overflow-y: auto;
    }}
    
    .avatar {{
      width: 140px;
      height: 140px;
      border-radius: 50%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      margin: 0 auto 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 48px;
      font-weight: 700;
      color: white;
      text-transform: uppercase;
    }}
    
    .avatar img {{
      width: 100%;
      height: 100%;
      border-radius: 50%;
      object-fit: cover;
    }}
    
    .name {{
      font-size: 24px;
      font-weight: 700;
      text-align: center;
      margin-bottom: 8px;
    }}
    
    .tagline {{
      font-size: 14px;
      color: var(--text-sidebar-muted);
      text-align: center;
      margin-bottom: 28px;
    }}
    
    .social-links {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 32px;
      padding-bottom: 28px;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    
    .social-link {{
      display: flex;
      align-items: center;
      gap: 12px;
      color: var(--text-sidebar-muted);
      text-decoration: none;
      font-size: 13px;
      transition: color 0.2s;
    }}
    
    .social-link:hover {{
      color: var(--text-sidebar);
    }}
    
    .social-link svg {{
      flex-shrink: 0;
      opacity: 0.7;
    }}
    
    .social-link span {{
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    
    .nav {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    
    .nav-link {{
      display: block;
      padding: 10px 14px;
      color: var(--text-sidebar-muted);
      text-decoration: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      transition: all 0.2s;
    }}
    
    .nav-link:hover {{
      background: rgba(255,255,255,0.08);
      color: var(--text-sidebar);
    }}
    
    /* Main Content */
    .main {{
      padding: 48px 56px;
      max-width: 900px;
    }}
    
    .bio {{
      font-size: 16px;
      line-height: 1.8;
      color: var(--text-secondary);
      margin-bottom: 48px;
      padding: 24px 28px;
      background: var(--bg-card);
      border-radius: 12px;
      box-shadow: var(--shadow);
      border-left: 4px solid var(--accent);
    }}
    
    section {{
      margin-bottom: 48px;
    }}
    
    h2 {{
      font-size: 20px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 2px solid var(--border);
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    
    .entry {{
      background: var(--bg-card);
      border-radius: 10px;
      padding: 20px 24px;
      margin-bottom: 16px;
      box-shadow: var(--shadow);
      transition: box-shadow 0.2s;
    }}
    
    .entry:hover {{
      box-shadow: var(--shadow-lg);
    }}
    
    .entry-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
      margin-bottom: 8px;
    }}
    
    .entry-title {{
      font-weight: 600;
      font-size: 16px;
      color: var(--text-primary);
    }}
    
    .entry-title a {{
      color: var(--accent);
      text-decoration: none;
    }}
    
    .entry-title a:hover {{
      text-decoration: underline;
    }}
    
    .entry-date {{
      font-size: 13px;
      color: var(--text-muted);
      white-space: nowrap;
      background: var(--bg-primary);
      padding: 4px 10px;
      border-radius: 20px;
    }}
    
    .entry-subtitle {{
      font-size: 14px;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }}
    
    .entry-meta {{
      font-size: 13px;
      color: var(--text-muted);
      margin-bottom: 8px;
    }}
    
    .entry-body {{
      font-size: 14px;
      color: var(--text-secondary);
      line-height: 1.7;
    }}
    
    ul {{
      margin: 10px 0 0 0;
      padding-left: 20px;
    }}
    
    li {{
      margin: 6px 0;
      color: var(--text-secondary);
      font-size: 14px;
      line-height: 1.6;
    }}
    
    .skill-grid {{
      display: grid;
      gap: 12px;
    }}
    
    .skill-row {{
      background: var(--bg-card);
      padding: 14px 18px;
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}
    
    .skill-category {{
      font-weight: 600;
      color: var(--accent);
      margin-right: 8px;
    }}
    
    .skill-items {{
      color: var(--text-secondary);
    }}
    
    .pub-title {{
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 4px;
    }}
    
    .pub-meta {{
      font-size: 13px;
      color: var(--text-muted);
      font-style: italic;
    }}
    
    .lang-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }}
    
    .lang-item {{
      background: var(--bg-card);
      padding: 12px 18px;
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}
    
    .lang-name {{
      font-weight: 600;
      color: var(--text-primary);
    }}
    
    .lang-level {{
      font-size: 13px;
      color: var(--text-muted);
    }}
    
    /* Responsive */
    @media (max-width: 900px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
      .sidebar {{
        position: relative;
        height: auto;
        padding: 32px 24px;
      }}
      .main {{
        padding: 32px 24px;
      }}
    }}
  </style>
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <div class="avatar">
        {"<img src='" + avatar + "' alt='" + full_name + "'>" if avatar else full_name[:2]}
      </div>
      <h1 class="name">{full_name}</h1>
      <p class="tagline">{tagline}</p>
      
      <div class="social-links">
        {social_html}
      </div>
      
      <nav class="nav">
        {nav_html}
      </nav>
    </aside>
    
    <main class="main">
      {"<div class='bio'>" + summary + "</div>" if summary else ""}
      <div id="root"></div>
    </main>
  </div>
  
  <script>
    window.SEEWEE_DOC = {doc_json};
  </script>
  <script>
{_get_academicpages_render_script()}
  </script>
</body>
</html>
"""
    return html


def _get_academicpages_render_script() -> str:
    """JavaScript for Academic Pages style rendering."""
    return r"""
function renderEntry(item, sectionId) {
  const d = item.data || {};
  const n = item.normalized || d;
  const type = item.entry_type || "";
  
  const div = document.createElement("div");
  div.className = "entry";
  
  // EXPERIENCE
  if (type === "experience") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("div");
    title.className = "entry-title";
    title.textContent = n.role || d.role || d.title || "Position";
    if (n.lead) title.textContent += " / " + n.lead;
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n._dates || d.dates || "";
    header.appendChild(date);
    div.appendChild(header);
    
    const parts = [n.company || d.company || d.org, n.location || d.location].filter(Boolean);
    if (parts.length) {
      const subtitle = document.createElement("div");
      subtitle.className = "entry-subtitle";
      subtitle.textContent = parts.join(" • ");
      div.appendChild(subtitle);
    }
    
    const highlights = n.highlights || d.highlights || [];
    if (highlights.length) {
      const ul = document.createElement("ul");
      highlights.forEach(h => {
        if (h && h.trim()) {
          const li = document.createElement("li");
          li.textContent = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // EDUCATION
  if (type === "education") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("div");
    title.className = "entry-title";
    title.textContent = n.degree || d.degree || "Degree";
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n._dates || d.dates || [d.start_date, d.end_date].filter(Boolean).join(" - ");
    header.appendChild(date);
    div.appendChild(header);
    
    const subtitle = document.createElement("div");
    subtitle.className = "entry-subtitle";
    const schoolParts = [n.school || d.school || d.institution];
    if (n.gpa || d.gpa) schoolParts.push("GPA: " + (n.gpa || d.gpa));
    subtitle.textContent = schoolParts.filter(Boolean).join(" • ");
    div.appendChild(subtitle);
    
    if (n.honors || d.honors) {
      const honors = document.createElement("div");
      honors.className = "entry-meta";
      honors.textContent = n.honors || d.honors;
      div.appendChild(honors);
    }
    
    const highlights = n.highlights || d.highlights || [];
    if (highlights.length) {
      const ul = document.createElement("ul");
      highlights.forEach(h => {
        if (h && h.trim()) {
          const li = document.createElement("li");
          li.textContent = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // PROJECT
  if (type === "project") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("div");
    title.className = "entry-title";
    const name = n.name || d.name || d.title || "Project";
    if (n.link || d.link) {
      const a = document.createElement("a");
      a.href = n.link || d.link;
      a.textContent = name;
      a.target = "_blank";
      title.appendChild(a);
    } else {
      title.textContent = name;
    }
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n._dates || d.dates || "";
    if (date.textContent) header.appendChild(date);
    div.appendChild(header);
    
    const techStack = n.tech_stack || d.tech_stack || [];
    if (techStack.length) {
      const tech = document.createElement("div");
      tech.className = "entry-meta";
      tech.innerHTML = "<strong>Stack:</strong> " + techStack.join(", ");
      div.appendChild(tech);
    }
    
    const highlights = n.highlights || d.highlights || [];
    if (highlights.length) {
      const ul = document.createElement("ul");
      highlights.forEach(h => {
        if (h && h.trim()) {
          const li = document.createElement("li");
          li.textContent = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // PUBLICATION
  if (type === "publication") {
    const titleDiv = document.createElement("div");
    titleDiv.className = "pub-title";
    const pubTitle = n.title || d.title || "Publication";
    if (n.link || d.link) {
      const a = document.createElement("a");
      a.href = n.link || d.link;
      a.textContent = pubTitle;
      a.target = "_blank";
      a.style.color = "var(--accent)";
      titleDiv.appendChild(a);
    } else {
      titleDiv.textContent = pubTitle;
    }
    div.appendChild(titleDiv);
    
    const metaParts = [];
    if (n.authors || d.authors) metaParts.push(n.authors || d.authors);
    if (n.venue || d.venue) metaParts.push(n.venue || d.venue);
    if (n.year || d.year) metaParts.push(n.year || d.year);
    if (metaParts.length) {
      const meta = document.createElement("div");
      meta.className = "pub-meta";
      meta.textContent = metaParts.join(" — ");
      div.appendChild(meta);
    }
    return div;
  }
  
  // SKILL
  if (type === "skill") {
    div.className = "skill-row";
    const category = n.category || d.category || n.name || d.name || "Skills";
    const items = n.items || d.items || [];
    if (items.length) {
      div.innerHTML = '<span class="skill-category">' + category + ':</span><span class="skill-items">' + items.join(", ") + '</span>';
    } else if (n.name || d.name) {
      const level = n.level || d.level;
      div.innerHTML = '<span class="skill-category">' + (n.name || d.name) + '</span>' + (level ? ' <span class="skill-items">(' + level + ')</span>' : '');
    }
    return div;
  }
  
  // AWARD
  if (type === "award") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("div");
    title.className = "entry-title";
    title.textContent = n.title || d.title || d.name || "Award";
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n.date || d.date || d.year || "";
    if (date.textContent) header.appendChild(date);
    div.appendChild(header);
    
    if (n.issuer || d.issuer) {
      const issuer = document.createElement("div");
      issuer.className = "entry-subtitle";
      issuer.textContent = n.issuer || d.issuer;
      div.appendChild(issuer);
    }
    
    if (n.description || d.description) {
      const desc = document.createElement("div");
      desc.className = "entry-body";
      desc.textContent = n.description || d.description;
      div.appendChild(desc);
    }
    return div;
  }
  
  // VOLUNTEERING
  if (type === "volunteering") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("div");
    title.className = "entry-title";
    title.textContent = n.role || d.role || d.title || "Role";
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n._dates || d.dates || "";
    if (date.textContent) header.appendChild(date);
    div.appendChild(header);
    
    if (n.organization || d.organization) {
      const org = document.createElement("div");
      org.className = "entry-subtitle";
      org.textContent = n.organization || d.organization;
      div.appendChild(org);
    }
    
    const highlights = n.highlights || d.highlights || [];
    if (highlights.length) {
      const ul = document.createElement("ul");
      highlights.forEach(h => {
        if (h && h.trim()) {
          const li = document.createElement("li");
          li.textContent = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // CERTIFICATION
  if (type === "certification") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("div");
    title.className = "entry-title";
    const name = n.name || d.name || d.title || "Certification";
    if (n.link || d.link) {
      const a = document.createElement("a");
      a.href = n.link || d.link;
      a.textContent = name;
      a.target = "_blank";
      title.appendChild(a);
    } else {
      title.textContent = name;
    }
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n.date || d.date || "";
    if (date.textContent) header.appendChild(date);
    div.appendChild(header);
    
    if (n.issuer || d.issuer) {
      const issuer = document.createElement("div");
      issuer.className = "entry-subtitle";
      issuer.textContent = n.issuer || d.issuer;
      div.appendChild(issuer);
    }
    return div;
  }
  
  // TALK
  if (type === "talk") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("div");
    title.className = "entry-title";
    const talkTitle = n.title || d.title || d.name || "Talk";
    if (n.link || d.link) {
      const a = document.createElement("a");
      a.href = n.link || d.link;
      a.textContent = talkTitle;
      a.target = "_blank";
      title.appendChild(a);
    } else {
      title.textContent = talkTitle;
    }
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n.date || d.date || "";
    if (date.textContent) header.appendChild(date);
    div.appendChild(header);
    
    const eventParts = [n.event || d.event, n.location || d.location].filter(Boolean);
    if (eventParts.length) {
      const event = document.createElement("div");
      event.className = "entry-subtitle";
      event.textContent = eventParts.join(" • ");
      div.appendChild(event);
    }
    return div;
  }
  
  // LANGUAGE
  if (type === "language") {
    div.className = "lang-item";
    const name = n.name || d.name || d.language || "Language";
    const prof = n.proficiency || d.proficiency || d.level || "";
    div.innerHTML = '<span class="lang-name">' + name + '</span>' + (prof ? '<br><span class="lang-level">' + prof + '</span>' : '');
    return div;
  }
  
  // REFERENCE
  if (type === "reference") {
    const title = document.createElement("div");
    title.className = "entry-title";
    title.textContent = n.name || d.name || "Reference";
    div.appendChild(title);
    
    const details = [];
    if (n.title || d.title) details.push(n.title || d.title);
    if (n.organization || d.organization) details.push(n.organization || d.organization);
    if (details.length) {
      const detailDiv = document.createElement("div");
      detailDiv.className = "entry-subtitle";
      detailDiv.textContent = details.join(", ");
      div.appendChild(detailDiv);
    }
    
    const contact = [];
    if (n.email || d.email) contact.push(n.email || d.email);
    if (n.phone || d.phone) contact.push(n.phone || d.phone);
    if (contact.length) {
      const contactDiv = document.createElement("div");
      contactDiv.className = "entry-meta";
      contactDiv.textContent = contact.join(" | ");
      div.appendChild(contactDiv);
    }
    return div;
  }
  
  // FALLBACK
  const header = document.createElement("div");
  header.className = "entry-header";
  const title = document.createElement("div");
  title.className = "entry-title";
  title.textContent = d.title || d.role || d.name || d.header || type;
  header.appendChild(title);
  const date = document.createElement("span");
  date.className = "entry-date";
  date.textContent = d.dates || d.date || n._dates || "";
  if (date.textContent) header.appendChild(date);
  div.appendChild(header);
  
  const org = d.org || d.organization || d.company || d.subheader || "";
  if (org) {
    const subtitle = document.createElement("div");
    subtitle.className = "entry-subtitle";
    subtitle.textContent = org;
    div.appendChild(subtitle);
  }
  
  const highlights = d.highlights || d.bullets || [];
  if (highlights.length) {
    const ul = document.createElement("ul");
    highlights.forEach(h => {
      if (h && h.trim()) {
        const li = document.createElement("li");
        li.textContent = h;
        ul.appendChild(li);
      }
    });
    div.appendChild(ul);
  }
  
  return div;
}

function render() {
  const root = document.getElementById("root");
  const doc = window.SEEWEE_DOC;
  root.innerHTML = "";
  
  (doc.sections || []).forEach(s => {
    if (!s.items || s.items.length === 0) return;
    
    const section = document.createElement("section");
    section.id = s.id;
    const h2 = document.createElement("h2");
    h2.textContent = s.title;
    section.appendChild(h2);
    
    // Special handling for skills - use grid
    if (s.id === "skills") {
      const grid = document.createElement("div");
      grid.className = "skill-grid";
      s.items.forEach(item => {
        grid.appendChild(renderEntry(item, s.id));
      });
      section.appendChild(grid);
    }
    // Special handling for languages - use flex grid
    else if (s.id === "languages") {
      const grid = document.createElement("div");
      grid.className = "lang-grid";
      s.items.forEach(item => {
        grid.appendChild(renderEntry(item, s.id));
      });
      section.appendChild(grid);
    }
    else {
      s.items.forEach(item => {
        section.appendChild(renderEntry(item, s.id));
      });
    }
    
    root.appendChild(section);
  });
}

render();
"""


def _get_render_script() -> str:
    return r"""
function renderEntry(item, sectionId) {
  const d = item.data || {};
  const n = item.normalized || d;
  const type = item.entry_type || "";
  
  const div = document.createElement("div");
  div.className = "entry";
  
  // EXPERIENCE
  if (type === "experience") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("span");
    title.className = "entry-title";
    title.textContent = n.role || d.role || d.title || "Position";
    if (n.lead) title.textContent += " / " + n.lead;
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n._dates || d.dates || "";
    header.appendChild(date);
    div.appendChild(header);
    
    const subtitle = document.createElement("div");
    subtitle.className = "entry-subtitle";
    const parts = [n.company || d.company || d.org, n.location || d.location].filter(Boolean);
    subtitle.textContent = parts.join(", ");
    if (parts.length) div.appendChild(subtitle);
    
    const highlights = n.highlights || d.highlights || [];
    if (highlights.length) {
      const ul = document.createElement("ul");
      highlights.forEach(h => {
        if (h && h.trim()) {
          const li = document.createElement("li");
          li.textContent = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // EDUCATION
  if (type === "education") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("span");
    title.className = "entry-title";
    title.textContent = n.school || d.school || d.institution || "Institution";
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n._dates || d.dates || [d.start_date, d.end_date].filter(Boolean).join(" - ");
    header.appendChild(date);
    div.appendChild(header);
    
    const subtitle = document.createElement("div");
    subtitle.className = "entry-subtitle";
    const degreeParts = [n.degree || d.degree];
    if (n.gpa || d.gpa) degreeParts.push("GPA: " + (n.gpa || d.gpa));
    subtitle.textContent = degreeParts.filter(Boolean).join(" | ");
    div.appendChild(subtitle);
    
    if (n.honors || d.honors) {
      const honors = document.createElement("div");
      honors.className = "entry-meta";
      honors.style.fontStyle = "italic";
      honors.textContent = n.honors || d.honors;
      div.appendChild(honors);
    }
    
    const highlights = n.highlights || d.highlights || [];
    if (highlights.length) {
      const ul = document.createElement("ul");
      highlights.forEach(h => {
        if (h && h.trim()) {
          const li = document.createElement("li");
          li.textContent = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // PROJECT
  if (type === "project") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("span");
    title.className = "entry-title";
    const name = n.name || d.name || d.title || "Project";
    if (n.link || d.link) {
      const a = document.createElement("a");
      a.href = n.link || d.link;
      a.textContent = name;
      a.target = "_blank";
      title.appendChild(a);
    } else {
      title.textContent = name;
    }
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n._dates || d.dates || "";
    header.appendChild(date);
    div.appendChild(header);
    
    const techStack = n.tech_stack || d.tech_stack || [];
    if (techStack.length) {
      const tech = document.createElement("div");
      tech.className = "entry-meta";
      tech.innerHTML = "<strong>Tech:</strong> " + techStack.join(", ");
      div.appendChild(tech);
    }
    
    const highlights = n.highlights || d.highlights || [];
    if (highlights.length) {
      const ul = document.createElement("ul");
      highlights.forEach(h => {
        if (h && h.trim()) {
          const li = document.createElement("li");
          li.textContent = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // PUBLICATION
  if (type === "publication") {
    const titleDiv = document.createElement("div");
    titleDiv.className = "pub-title";
    titleDiv.textContent = n.title || d.title || "Publication";
    div.appendChild(titleDiv);
    
    const metaParts = [];
    if (n.authors || d.authors) metaParts.push(n.authors || d.authors);
    if (n.venue || d.venue) metaParts.push(n.venue || d.venue);
    if (n.year || d.year) metaParts.push(n.year || d.year);
    if (metaParts.length) {
      const meta = document.createElement("div");
      meta.className = "pub-meta";
      meta.textContent = metaParts.join(" — ");
      div.appendChild(meta);
    }
    
    const links = [];
    if (n.link || d.link) links.push('<a href="' + (n.link || d.link) + '" target="_blank">[Link]</a>');
    if (n.doi || d.doi) links.push('<a href="https://doi.org/' + (n.doi || d.doi) + '" target="_blank">[DOI]</a>');
    if (links.length) {
      const linkDiv = document.createElement("div");
      linkDiv.innerHTML = links.join(" ");
      div.appendChild(linkDiv);
    }
    return div;
  }
  
  // SKILL
  if (type === "skill") {
    div.className = "skill-row";
    const category = n.category || d.category || n.name || d.name || "Skills";
    const items = n.skill_list || n.items || d.skill_list || d.items || [];
    if (items.length) {
      div.innerHTML = '<span class="skill-category">' + category + ':</span> <span class="skill-items">' + items.join(", ") + '</span>';
    } else if (n.name || d.name) {
      const level = n.level || d.level;
      div.innerHTML = '<span class="skill-category">' + (n.name || d.name) + '</span>' + (level ? ' <span class="skill-items">(' + level + ')</span>' : '');
    }
    return div;
  }
  
  // AWARD
  if (type === "award") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("span");
    title.className = "entry-title";
    title.textContent = n.title || d.title || d.name || "Award";
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n.date || d.date || d.year || "";
    header.appendChild(date);
    div.appendChild(header);
    
    if (n.issuer || d.issuer) {
      const issuer = document.createElement("div");
      issuer.className = "entry-subtitle";
      issuer.textContent = n.issuer || d.issuer;
      div.appendChild(issuer);
    }
    
    if (n.description || d.description) {
      const desc = document.createElement("div");
      desc.className = "entry-body";
      desc.textContent = n.description || d.description;
      div.appendChild(desc);
    }
    
    const highlights = n.highlights || d.highlights || [];
    if (highlights.length) {
      const ul = document.createElement("ul");
      highlights.forEach(h => {
        if (h && h.trim()) {
          const li = document.createElement("li");
          li.textContent = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // VOLUNTEERING
  if (type === "volunteering") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("span");
    title.className = "entry-title";
    title.textContent = n.role || d.role || d.title || "Role";
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n._dates || d.dates || "";
    header.appendChild(date);
    div.appendChild(header);
    
    if (n.organization || d.organization) {
      const org = document.createElement("div");
      org.className = "entry-subtitle";
      org.textContent = n.organization || d.organization;
      div.appendChild(org);
    }
    
    const highlights = n.highlights || d.highlights || [];
    if (highlights.length) {
      const ul = document.createElement("ul");
      highlights.forEach(h => {
        if (h && h.trim()) {
          const li = document.createElement("li");
          li.textContent = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // CERTIFICATION
  if (type === "certification") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("span");
    title.className = "entry-title";
    const name = n.name || d.name || d.title || "Certification";
    if (n.link || d.link) {
      const a = document.createElement("a");
      a.href = n.link || d.link;
      a.textContent = name;
      a.target = "_blank";
      title.appendChild(a);
    } else {
      title.textContent = name;
    }
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n.date || d.date || "";
    header.appendChild(date);
    div.appendChild(header);
    
    if (n.issuer || d.issuer) {
      const issuer = document.createElement("div");
      issuer.className = "entry-subtitle";
      issuer.textContent = n.issuer || d.issuer;
      div.appendChild(issuer);
    }
    return div;
  }
  
  // TALK
  if (type === "talk") {
    const header = document.createElement("div");
    header.className = "entry-header";
    const title = document.createElement("span");
    title.className = "entry-title";
    title.textContent = n.title || d.title || d.name || "Talk";
    header.appendChild(title);
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = n.date || d.date || "";
    header.appendChild(date);
    div.appendChild(header);
    
    const eventParts = [n.event || d.event, n.location || d.location].filter(Boolean);
    if (eventParts.length) {
      const event = document.createElement("div");
      event.className = "entry-subtitle";
      event.textContent = eventParts.join(", ");
      div.appendChild(event);
    }
    
    if (n.link || d.link) {
      const link = document.createElement("div");
      link.innerHTML = '<a href="' + (n.link || d.link) + '" target="_blank">[Slides/Recording]</a>';
      div.appendChild(link);
    }
    return div;
  }
  
  // LANGUAGE
  if (type === "language") {
    div.className = "skill-row";
    const name = n.name || d.name || d.language || "Language";
    const prof = n.proficiency || d.proficiency || d.level || "";
    div.innerHTML = '<span class="skill-category">' + name + '</span>' + (prof ? ': <span class="skill-items">' + prof + '</span>' : '');
    return div;
  }
  
  // REFERENCE
  if (type === "reference") {
    const title = document.createElement("div");
    title.className = "entry-title";
    title.textContent = n.name || d.name || "Reference";
    div.appendChild(title);
    
    const details = [];
    if (n.title || d.title) details.push(n.title || d.title);
    if (n.organization || d.organization) details.push(n.organization || d.organization);
    if (details.length) {
      const detailDiv = document.createElement("div");
      detailDiv.className = "entry-subtitle";
      detailDiv.textContent = details.join(", ");
      div.appendChild(detailDiv);
    }
    
    const contact = [];
    if (n.email || d.email) contact.push(n.email || d.email);
    if (n.phone || d.phone) contact.push(n.phone || d.phone);
    if (contact.length) {
      const contactDiv = document.createElement("div");
      contactDiv.className = "entry-meta";
      contactDiv.textContent = contact.join(" | ");
      div.appendChild(contactDiv);
    }
    return div;
  }
  
  // FALLBACK - generic rendering
  const header = document.createElement("div");
  header.className = "entry-header";
  const title = document.createElement("span");
  title.className = "entry-title";
  title.textContent = d.title || d.role || d.name || d.header || type;
  header.appendChild(title);
  const date = document.createElement("span");
  date.className = "entry-date";
  date.textContent = d.dates || d.date || n._dates || "";
  header.appendChild(date);
  div.appendChild(header);
  
  const org = d.org || d.organization || d.company || d.subheader || "";
  if (org) {
    const subtitle = document.createElement("div");
    subtitle.className = "entry-subtitle";
    subtitle.textContent = org;
    div.appendChild(subtitle);
  }
  
  const highlights = d.highlights || d.bullets || [];
  if (highlights.length) {
    const ul = document.createElement("ul");
    highlights.forEach(h => {
      if (h && h.trim()) {
        const li = document.createElement("li");
        li.textContent = h;
        ul.appendChild(li);
      }
    });
    div.appendChild(ul);
  }
  
  return div;
}

function render() {
  const root = document.getElementById("root");
  const doc = window.SEEWEE_DOC;
  root.innerHTML = "";
  
  (doc.sections || []).forEach(s => {
    if (!s.items || s.items.length === 0) return;
    
    const section = document.createElement("section");
    const h2 = document.createElement("h2");
    h2.textContent = s.title;
    section.appendChild(h2);
    
    s.items.forEach(item => {
      section.appendChild(renderEntry(item, s.id));
    });
    
    root.appendChild(section);
  });
}

render();
"""
