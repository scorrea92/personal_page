#!/usr/bin/env python3
import re, pathlib

index = pathlib.Path('index.html')
html = index.read_text(encoding='utf-8', errors='ignore')
medium = pathlib.Path('medium_section.html').read_text(encoding='utf-8', errors='ignore').strip() + "\n"

# Remove existing medium section if present
html = re.sub(r"\n<!-- Medium Posts \(auto-generated[\s\S]*?<section class=\"colorlib-blog\" data-section=\"medium\">[\s\S]*?</section>\n", "\n", html, flags=re.S)

# Insert after Experience section (data-section="experience") closing </section>
pat = re.compile(r"(<section class=\"colorlib-experience\" data-section=\"experience\">[\s\S]*?</section>)\n", re.S)
m = pat.search(html)
if not m:
    raise SystemExit('Could not find experience section to insert after')

insert_at = m.end(1)
html = html[:insert_at] + "\n\n" + medium + html[insert_at:]

# Add nav item after Experience
nav_pat = re.compile(r"(<li><a href=\"#\" data-nav-section=\"experience\">Experience</a></li>)")
if nav_pat.search(html) and 'data-nav-section="medium"' not in html:
    html = nav_pat.sub(r"\1\n\t\t\t\t\t\t\t<li><a href=\"#\" data-nav-section=\"medium\">Medium</a></li>", html, count=1)

index.write_text(html, encoding='utf-8')
print('inserted medium section')
