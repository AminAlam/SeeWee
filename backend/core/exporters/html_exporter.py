from __future__ import annotations

import json
from typing import Any

from core.document_model import Document
from core.entry_schemas import normalize_entry
from core.markdown_utils import process_entry_markdown, process_profile_markdown


def _safe_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _normalize_items_for_html(doc: Document) -> list[dict]:
    """Normalize all items using the schema registry and process markdown for HTML."""
    sections = []
    for s in doc.sections:
        items = []
        for i in s.items:
            normalized = normalize_entry(i.entry_type, i.data or {})
            # Process markdown fields for HTML output
            normalized = process_entry_markdown(normalized, target='html')
            data_html = process_entry_markdown(i.data or {}, target='html')
            items.append({
                "entry_id": i.entry_id,
                "entry_type": i.entry_type,
                "tags": i.tags,
                "data": data_html,
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
          li.innerHTML = h;
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
          li.innerHTML = h;
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
          li.innerHTML = h;
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
          li.innerHTML = h;
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
          li.innerHTML = h;
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
        li.innerHTML = h;
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
    Modern responsive CV website - Bootstrap-style fluid layout.
    Clean, professional design optimized for all screen sizes.
    """
    # Process profile markdown for HTML
    processed_profile = process_profile_markdown(profile or {}, target='html')
    
    links = processed_profile.get("links") or {}
    personal = processed_profile.get("personal") or {}
    content = processed_profile.get("content") or {}

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

    # Build social links as icon buttons
    social_links = []
    if email:
        social_links.append(f'<a href="mailto:{email}" class="social-btn" title="Email"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg></a>')
    if github:
        social_links.append(f'<a href="{github}" target="_blank" class="social-btn" title="GitHub"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg></a>')
    if linkedin:
        social_links.append(f'<a href="{linkedin}" target="_blank" class="social-btn" title="LinkedIn"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg></a>')
    if scholar:
        social_links.append(f'<a href="{scholar}" target="_blank" class="social-btn" title="Google Scholar"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M5.242 13.769L0 9.5 12 0l12 9.5-5.242 4.269C17.548 11.249 14.978 9.5 12 9.5c-2.977 0-5.548 1.748-6.758 4.269zM12 10a7 7 0 1 0 0 14 7 7 0 0 0 0-14z"/></svg></a>')
    if twitter:
        social_links.append(f'<a href="{twitter}" target="_blank" class="social-btn" title="X/Twitter"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg></a>')
    if website:
        social_links.append(f'<a href="{website}" target="_blank" class="social-btn" title="Website"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg></a>')

    social_html = "\n        ".join(social_links)
    
    # Contact info for header
    contact_parts = []
    if email:
        contact_parts.append(f'<a href="mailto:{email}">{email}</a>')
    if phone:
        contact_parts.append(f'<span>{phone}</span>')
    if address:
        contact_parts.append(f'<span>{address}</span>')
    contact_html = ' <span class="sep">•</span> '.join(contact_parts)

    # Build navigation from sections
    nav_items = []
    for s in sections:
        if s["items"]:
            nav_items.append(f'<a href="#{s["id"]}" class="nav-pill">{s["title"]}</a>')
    nav_html = "\n        ".join(nav_items)

    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{full_name} - CV</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
      :root {{
      --bg: #f0f4f8;
      --bg-card: #ffffff;
      --text: #1a202c;
      --text-secondary: #4a5568;
      --text-muted: #718096;
      --accent: #4f46e5;
      --accent-light: #818cf8;
      --accent-bg: rgba(79, 70, 229, 0.08);
      --border: #e2e8f0;
      --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
      --shadow: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.04);
      --shadow-lg: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.04);
      --radius: 12px;
      --radius-lg: 16px;
    }}
    
    html {{ scroll-behavior: smooth; }}
    
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      font-size: 15px;
      -webkit-font-smoothing: antialiased;
    }}
    
    /* Container system - Bootstrap-like */
    .container {{
      width: 100%;
      margin: 0 auto;
      padding: 0 16px;
    }}
    @media (min-width: 576px) {{ .container {{ max-width: 540px; padding: 0 20px; }} }}
    @media (min-width: 768px) {{ .container {{ max-width: 720px; }} }}
    @media (min-width: 992px) {{ .container {{ max-width: 960px; }} }}
    @media (min-width: 1200px) {{ .container {{ max-width: 1140px; }} }}
    @media (min-width: 1400px) {{ .container {{ max-width: 1320px; }} }}
    
    .container-fluid {{ width: 100%; padding: 0 16px; }}
    @media (min-width: 768px) {{ .container-fluid {{ padding: 0 32px; }} }}
    
    /* Header */
    .header {{
      background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
      color: white;
      padding: 48px 0 80px;
      position: relative;
      overflow: hidden;
    }}
    
    .header::before {{
      content: '';
      position: absolute;
      top: 0; right: 0; bottom: 0; left: 0;
      background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
      opacity: 0.5;
    }}
    
    .header-content {{
      position: relative;
      z-index: 1;
    }}
    
    .profile-section {{
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 20px;
    }}
    
    @media (min-width: 768px) {{
      .profile-section {{
        flex-direction: row;
        text-align: left;
        gap: 32px;
      }}
    }}
    
    .avatar {{
      width: 120px;
      height: 120px;
      border-radius: 50%;
      background: linear-gradient(135deg, #f472b6 0%, #a78bfa 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 42px;
      font-weight: 800;
      color: white;
      text-transform: uppercase;
      flex-shrink: 0;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      border: 4px solid rgba(255,255,255,0.2);
    }}
    
    .avatar img {{
      width: 100%;
      height: 100%;
      border-radius: 50%;
      object-fit: cover;
    }}
    
    .profile-info {{ flex: 1; }}
    
    .name {{
      font-size: 32px;
      font-weight: 800;
      letter-spacing: -0.5px;
      margin-bottom: 4px;
    }}
    
    @media (min-width: 768px) {{
      .name {{ font-size: 40px; }}
    }}
    
    .tagline {{
      font-size: 16px;
      color: rgba(255,255,255,0.75);
      font-weight: 500;
      margin-bottom: 16px;
    }}
    
    .contact-row {{
      font-size: 13px;
      color: rgba(255,255,255,0.7);
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 8px;
    }}
    
    @media (min-width: 768px) {{
      .contact-row {{ justify-content: flex-start; }}
    }}
    
    .contact-row a {{
      color: rgba(255,255,255,0.9);
      text-decoration: none;
      transition: color 0.2s;
    }}
    
    .contact-row a:hover {{ color: white; text-decoration: underline; }}
    .contact-row .sep {{ opacity: 0.4; }}
    
    .social-row {{
      display: flex;
      gap: 8px;
      margin-top: 16px;
      justify-content: center;
    }}
    
    @media (min-width: 768px) {{
      .social-row {{ justify-content: flex-start; }}
    }}
    
    .social-btn {{
      width: 40px;
      height: 40px;
      border-radius: 10px;
      background: rgba(255,255,255,0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      color: rgba(255,255,255,0.8);
      transition: all 0.2s;
      backdrop-filter: blur(4px);
    }}
    
    .social-btn:hover {{
      background: rgba(255,255,255,0.2);
      color: white;
      transform: translateY(-2px);
    }}
    
    /* Navigation */
    .nav-bar {{
      background: var(--bg-card);
      position: sticky;
      top: 0;
      z-index: 100;
      border-bottom: 1px solid var(--border);
      box-shadow: var(--shadow-sm);
      margin-top: -48px;
    }}
    
    .nav-inner {{
      display: flex;
      gap: 6px;
      padding: 12px 0;
      overflow-x: auto;
      scrollbar-width: none;
      -ms-overflow-style: none;
    }}
    
    .nav-inner::-webkit-scrollbar {{ display: none; }}
    
    .nav-pill {{
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-secondary);
      text-decoration: none;
      white-space: nowrap;
      transition: all 0.2s;
      background: transparent;
    }}
    
    .nav-pill:hover {{
      background: var(--accent-bg);
      color: var(--accent);
    }}
    
    /* Main Content */
    .main {{
      padding: 32px 0 64px;
    }}
    
    .bio {{
      font-size: 16px;
      line-height: 1.8;
      color: var(--text-secondary);
      padding: 24px;
      background: var(--bg-card);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow);
      margin-bottom: 32px;
      border-left: 4px solid var(--accent);
    }}
    
    section {{
      margin-bottom: 40px;
    }}
    
    h2 {{
      font-size: 22px;
      font-weight: 700;
      color: var(--text);
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    
    h2::before {{
      content: '';
      width: 4px;
      height: 24px;
      background: var(--accent);
      border-radius: 2px;
    }}
    
    /* Entry Grid */
    .entry-grid {{
      display: grid;
      gap: 16px;
      grid-template-columns: 1fr;
    }}
    
    @media (min-width: 768px) {{
      .entry-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    
    @media (min-width: 1200px) {{
      .entry-grid.cols-3 {{ grid-template-columns: repeat(3, 1fr); }}
    }}
    
    .entry {{
      background: var(--bg-card);
      border-radius: var(--radius);
      padding: 20px;
      box-shadow: var(--shadow-sm);
      border: 1px solid var(--border);
      transition: all 0.2s ease;
      display: flex;
      flex-direction: column;
    }}
    
    .entry:hover {{
      box-shadow: var(--shadow);
      border-color: var(--accent-light);
      transform: translateY(-2px);
    }}
    
    .entry-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 8px;
    }}
    
    .entry-title {{
      font-weight: 700;
      font-size: 15px;
      color: var(--text);
      flex: 1;
    }}
    
    .entry-title a {{
      color: var(--accent);
      text-decoration: none;
    }}
    
    .entry-title a:hover {{ text-decoration: underline; }}
    
    .entry-date {{
      font-size: 11px;
      font-weight: 600;
      color: var(--accent);
      background: var(--accent-bg);
      padding: 4px 10px;
      border-radius: 12px;
      white-space: nowrap;
      flex-shrink: 0;
    }}
    
    .entry-subtitle {{
      font-size: 13px;
      color: var(--text-secondary);
      margin-bottom: 8px;
      font-weight: 500;
    }}
    
    .entry-meta {{
      font-size: 12px;
      color: var(--text-muted);
      margin-bottom: 8px;
    }}
    
    .entry-body {{
      font-size: 13px;
      color: var(--text-secondary);
      line-height: 1.6;
      flex: 1;
    }}
    
    ul {{
      margin: 8px 0 0 0;
      padding-left: 18px;
    }}
    
    li {{
      margin: 4px 0;
      color: var(--text-secondary);
      font-size: 13px;
      line-height: 1.5;
    }}
    
    /* Skills Grid */
    .skill-grid {{
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    }}
    
    .skill-row {{
      background: var(--bg-card);
      padding: 16px 20px;
      border-radius: var(--radius);
      box-shadow: var(--shadow-sm);
      border: 1px solid var(--border);
      transition: all 0.2s;
    }}
    
    .skill-row:hover {{
      border-color: var(--accent-light);
      box-shadow: var(--shadow);
    }}
    
    .skill-category {{
      font-weight: 700;
      color: var(--accent);
      font-size: 13px;
      display: block;
      margin-bottom: 6px;
    }}
    
    .skill-items {{
      color: var(--text-secondary);
      font-size: 13px;
      line-height: 1.6;
    }}
    
    /* Publications */
    .pub-entry {{
      background: var(--bg-card);
      border-radius: var(--radius);
      padding: 20px;
      box-shadow: var(--shadow-sm);
      border: 1px solid var(--border);
      margin-bottom: 12px;
      transition: all 0.2s;
    }}
    
    .pub-entry:hover {{
      border-color: var(--accent-light);
      box-shadow: var(--shadow);
    }}
    
    .pub-title {{
      font-weight: 700;
      color: var(--text);
      font-size: 15px;
      margin-bottom: 6px;
    }}
    
    .pub-title a {{
      color: var(--accent);
      text-decoration: none;
    }}
    
    .pub-title a:hover {{ text-decoration: underline; }}
    
    .pub-meta {{
      font-size: 13px;
      color: var(--text-muted);
      font-style: italic;
    }}
    
    /* Languages */
    .lang-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }}
    
    .lang-item {{
      background: var(--bg-card);
      padding: 14px 20px;
      border-radius: var(--radius);
      box-shadow: var(--shadow-sm);
      border: 1px solid var(--border);
      min-width: 140px;
      transition: all 0.2s;
    }}
    
    .lang-item:hover {{
      border-color: var(--accent-light);
      transform: translateY(-2px);
    }}
    
    .lang-name {{
      font-weight: 700;
      color: var(--text);
      font-size: 14px;
    }}
    
    .lang-level {{
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
    }}
    
    /* Footer */
    .footer {{
      text-align: center;
      padding: 32px 0;
      font-size: 12px;
      color: var(--text-muted);
      border-top: 1px solid var(--border);
    }}
    
    /* Print styles */
    @media print {{
      .nav-bar {{ display: none; }}
      .header {{ padding: 24px 0; }}
      .entry, .skill-row, .pub-entry, .lang-item {{ box-shadow: none; border: 1px solid #ddd; }}
      }}
    </style>
  </head>
  <body>
  <header class="header">
    <div class="container header-content">
      <div class="profile-section">
        <div class="avatar">
          {"<img src='" + avatar + "' alt='" + full_name + "'>" if avatar else full_name[:2] if full_name else "CV"}
        </div>
        <div class="profile-info">
          <h1 class="name">{full_name}</h1>
          <p class="tagline">{tagline}</p>
          <div class="contact-row">{contact_html}</div>
          <div class="social-row">
            {social_html}
          </div>
        </div>
      </div>
    </div>
  </header>
  
  <nav class="nav-bar">
    <div class="container">
      <div class="nav-inner">
        {nav_html}
      </div>
    </div>
  </nav>
  
  <main class="main">
    <div class="container">
      {"<div class='bio'>" + summary + "</div>" if summary else ""}
        <div id="root"></div>
    </div>
      </main>
  
  <footer class="footer">
    <div class="container">
      Generated by SeeWee CV Manager
    </div>
  </footer>

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
    """JavaScript for modern responsive CV rendering."""
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
    const dateStr = n._dates || d.dates || "";
    if (dateStr) {
      const date = document.createElement("span");
      date.className = "entry-date";
      date.textContent = dateStr;
      header.appendChild(date);
    }
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
          li.innerHTML = h;
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
    const dateStr = n._dates || d.dates || [d.start_date, d.end_date].filter(Boolean).join(" - ");
    if (dateStr) {
      const date = document.createElement("span");
      date.className = "entry-date";
      date.textContent = dateStr;
      header.appendChild(date);
    }
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
          li.innerHTML = h;
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
    const dateStr = n._dates || d.dates || "";
    if (dateStr) {
      const date = document.createElement("span");
      date.className = "entry-date";
      date.textContent = dateStr;
      header.appendChild(date);
    }
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
          li.innerHTML = h;
          ul.appendChild(li);
        }
      });
      div.appendChild(ul);
    }
    return div;
  }
  
  // PUBLICATION
  if (type === "publication") {
    div.className = "pub-entry";
    const titleDiv = document.createElement("div");
    titleDiv.className = "pub-title";
    const pubTitle = n.title || d.title || "Publication";
    if (n.link || d.link) {
      const a = document.createElement("a");
      a.href = n.link || d.link;
      a.textContent = pubTitle;
      a.target = "_blank";
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
    const items = n.skill_list || n.items || d.skill_list || d.items || [];
    if (items.length) {
      div.innerHTML = '<span class="skill-category">' + category + '</span><span class="skill-items">' + items.join(", ") + '</span>';
    } else if (n.name || d.name) {
      const level = n.level || d.level;
      div.innerHTML = '<span class="skill-category">' + (n.name || d.name) + '</span>' + (level ? '<span class="skill-items">' + level + '</span>' : '');
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
    const dateStr = n.date || d.date || d.year || "";
    if (dateStr) {
      const date = document.createElement("span");
      date.className = "entry-date";
      date.textContent = dateStr;
      header.appendChild(date);
    }
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
    const dateStr = n._dates || d.dates || "";
    if (dateStr) {
      const date = document.createElement("span");
      date.className = "entry-date";
      date.textContent = dateStr;
      header.appendChild(date);
    }
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
          li.innerHTML = h;
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
    const dateStr = n.date || d.date || "";
    if (dateStr) {
      const date = document.createElement("span");
      date.className = "entry-date";
      date.textContent = dateStr;
      header.appendChild(date);
    }
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
    const dateStr = n.date || d.date || "";
    if (dateStr) {
      const date = document.createElement("span");
      date.className = "entry-date";
      date.textContent = dateStr;
      header.appendChild(date);
    }
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
    div.innerHTML = '<div class="lang-name">' + name + '</div>' + (prof ? '<div class="lang-level">' + prof + '</div>' : '');
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
  const dateStr = d.dates || d.date || n._dates || "";
  if (dateStr) {
    const date = document.createElement("span");
    date.className = "entry-date";
    date.textContent = dateStr;
    header.appendChild(date);
  }
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
        li.innerHTML = h;
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
    
    // Skills - use skill grid
    if (s.id === "skills" || s.items[0]?.entry_type === "skill") {
      const grid = document.createElement("div");
      grid.className = "skill-grid";
      s.items.forEach(item => grid.appendChild(renderEntry(item, s.id)));
      section.appendChild(grid);
    }
    // Languages - use flex grid
    else if (s.id === "languages" || s.items[0]?.entry_type === "language") {
      const grid = document.createElement("div");
      grid.className = "lang-grid";
      s.items.forEach(item => grid.appendChild(renderEntry(item, s.id)));
      section.appendChild(grid);
    }
    // Publications - linear list
    else if (s.id === "publications" || s.items[0]?.entry_type === "publication") {
      s.items.forEach(item => section.appendChild(renderEntry(item, s.id)));
    }
    // Default - responsive 2-column grid
    else {
      const grid = document.createElement("div");
      grid.className = "entry-grid";
      // Use 3-col for certifications, awards
      if (s.id === "certifications" || s.id === "awards" || 
          s.items[0]?.entry_type === "certification" || s.items[0]?.entry_type === "award") {
        grid.classList.add("cols-3");
      }
      s.items.forEach(item => grid.appendChild(renderEntry(item, s.id)));
      section.appendChild(grid);
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
          li.innerHTML = h;
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
          li.innerHTML = h;
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
          li.innerHTML = h;
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
          li.innerHTML = h;
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
          li.innerHTML = h;
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
        li.innerHTML = h;
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
