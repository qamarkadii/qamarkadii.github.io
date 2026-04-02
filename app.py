from __future__ import annotations

import html
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
CONTENT_PATH = BASE_DIR / "content.json"


def load_content() -> dict[str, object]:
    return json.loads(CONTENT_PATH.read_text(encoding="utf-8"))


def save_content(content: dict[str, object]) -> None:
    CONTENT_PATH.write_text(json.dumps(content, indent=2), encoding="utf-8")


def render_tag_list(tags: list[str]) -> str:
    return "".join(f'<li>{html.escape(tag)}</li>' for tag in tags)


def render_home(content: dict[str, object]) -> str:
    personal = content["personal"]
    mouse_glow_script = """
<script>
(() => {
    if (window.matchMedia("(pointer: coarse)").matches) {
        return;
    }

    const glow = document.querySelector("[data-mouse-glow]");
    if (!glow) {
        return;
    }

    let targetX = window.innerWidth * 0.5;
    let targetY = window.innerHeight * 0.3;
    let currentX = targetX;
    let currentY = targetY;

    document.body.classList.add("has-mouse-glow");

    window.addEventListener("mousemove", (event) => {
        targetX = event.clientX;
        targetY = event.clientY;
    });

    document.querySelectorAll("a, button, .project-card, .panel, .hero-copy, .hero-panel").forEach((node) => {
        node.addEventListener("mouseenter", () => glow.classList.add("is-strong"));
        node.addEventListener("mouseleave", () => glow.classList.remove("is-strong"));
    });

    const tick = () => {
        currentX += (targetX - currentX) * 0.12;
        currentY += (targetY - currentY) * 0.12;
        glow.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
        requestAnimationFrame(tick);
    };

    glow.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
    tick();
})();
</script>
"""
    stats = "".join(
        f"""
        <article class="stat-card">
            <span>{html.escape(item["value"])}</span>
            <p>{html.escape(item["label"])}</p>
        </article>
        """
        for item in content["stats"]
    )
    education = "".join(
        f"""
        <article class="education-card">
            <div class="section-chip">{html.escape(item["period"])}</div>
            <h3>{html.escape(item["institution"])}</h3>
            <p class="education-degree">{html.escape(item["degree"])}</p>
            <p>{html.escape(item["details"])}</p>
        </article>
        """
        for item in content["education"]
    )
    experience = "".join(
        f"""
        <article class="timeline-card">
            <div class="timeline-meta">
                <span>{html.escape(item["period"])}</span>
                <span>{html.escape(item["location"])}</span>
            </div>
            <h3>{html.escape(item["role"])}</h3>
            <p class="timeline-company">{html.escape(item["company"])}</p>
            <p>{html.escape(item["summary"])}</p>
            <ul class="bullet-list">
                {''.join(f"<li>{html.escape(point)}</li>" for point in item["highlights"])}
            </ul>
            <ul class="tag-list">{render_tag_list(item["stack"])}</ul>
        </article>
        """
        for item in content["experience"]
    )
    projects = "".join(
        f"""
        <article class="project-card">
            <div class="project-top">
                <span class="section-chip">{html.escape(item["kind"])}</span>
                <span class="project-status">{html.escape(item["status"])}</span>
            </div>
            <h3>{html.escape(item["name"])}</h3>
            <p>{html.escape(item["description"])}</p>
            <ul class="tag-list">{render_tag_list(item["stack"])}</ul>
            <div class="project-links">
                <a href="{html.escape(item["link"])}" target="_blank" rel="noreferrer">Project Link</a>
            </div>
        </article>
        """
        for item in content["projects"]
    )
    future_projects = "".join(
        f"""
        <article class="future-card">
            <div class="section-chip">Future Build</div>
            <h3>{html.escape(item["name"])}</h3>
            <p>{html.escape(item["description"])}</p>
            <p class="future-goal">Goal: {html.escape(item["goal"])}</p>
        </article>
        """
        for item in content["future_projects"]
    )
    skills = "".join(
        f"""
        <article class="skill-card">
            <h3>{html.escape(group["category"])}</h3>
            <ul class="tag-list">{render_tag_list(group["items"])}</ul>
        </article>
        """
        for group in content["skills"]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(personal["name"])} | Portfolio</title>
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
    <div class="mouse-glow" data-mouse-glow></div>
    <div class="site-bg"></div>
    <header class="topbar">
        <a class="brand" href="/">QA</a>
        <nav>
            <a href="#about">About</a>
            <a href="#experience">Experience</a>
            <a href="#projects">Projects</a>
            <a href="#contact">Contact</a>
            <a href="/edit">Edit</a>
        </nav>
    </header>

    <main class="shell">
        <section class="hero">
            <div class="hero-copy">
                <p class="eyebrow">{html.escape(personal["tagline"])}</p>
                <h1>{html.escape(personal["headline"])}</h1>
                <p class="lead">{html.escape(personal["summary"])}</p>
                <div class="hero-actions">
                    <a class="button button-primary" href="#projects">View Projects</a>
                    <a class="button button-secondary" href="#contact">Contact Me</a>
                </div>
            </div>
            <aside class="hero-panel">
                <p class="hero-label">Now</p>
                <h2>{html.escape(personal["name"])}</h2>
                <p>{html.escape(personal["role"])}</p>
                <p>{html.escape(personal["location"])}</p>
                <ul class="contact-list compact">
                    <li><span>Email</span><a href="mailto:{html.escape(personal["email"])}">{html.escape(personal["email"])}</a></li>
                    <li><span>Phone</span><a href="tel:{html.escape(personal["phone"])}">{html.escape(personal["phone"])}</a></li>
                    <li><span>LinkedIn</span><a href="{html.escape(personal["linkedin"])}" target="_blank" rel="noreferrer">Open</a></li>
                    <li><span>GitHub</span><a href="{html.escape(personal["github"])}" target="_blank" rel="noreferrer">Open</a></li>
                </ul>
            </aside>
        </section>

        <section class="stats-grid">
            {stats}
        </section>

        <section class="section" id="about">
            <div class="section-heading">
                <p class="eyebrow">Profile</p>
                <h2>Personal CV, built like a product.</h2>
            </div>
            <div class="about-grid">
                <article class="panel">
                    <p>{html.escape(personal["about"])}</p>
                </article>
                <article class="panel">
                    <h3>Highlights</h3>
                    <ul class="bullet-list">
                        {''.join(f"<li>{html.escape(point)}</li>" for point in personal["highlights"])}
                    </ul>
                </article>
            </div>
        </section>

        <section class="section">
            <div class="section-heading">
                <p class="eyebrow">Education</p>
                <h2>School and university journey.</h2>
            </div>
            <div class="education-grid">
                {education}
            </div>
        </section>

        <section class="section" id="experience">
            <div class="section-heading">
                <p class="eyebrow">Experience</p>
                <h2>Work that shows range and direction.</h2>
            </div>
            <div class="timeline">
                {experience}
            </div>
        </section>

        <section class="section">
            <div class="section-heading">
                <p class="eyebrow">Skills</p>
                <h2>What I use to build.</h2>
            </div>
            <div class="skills-grid">
                {skills}
            </div>
        </section>

        <section class="section" id="projects">
            <div class="section-heading">
                <p class="eyebrow">Selected Work</p>
                <h2>Projects, shipped and in progress.</h2>
            </div>
            <div class="project-grid">
                {projects}
            </div>
        </section>

        <section class="section">
            <div class="section-heading">
                <p class="eyebrow">Roadmap</p>
                <h2>Future projects I want to build next.</h2>
            </div>
            <div class="future-grid">
                {future_projects}
            </div>
        </section>

        <section class="section" id="contact">
            <div class="section-heading">
                <p class="eyebrow">Contact</p>
                <h2>Let people reach you directly.</h2>
            </div>
            <article class="panel contact-panel">
                <ul class="contact-list">
                    <li><span>Name</span><strong>{html.escape(personal["name"])}</strong></li>
                    <li><span>Email</span><a href="mailto:{html.escape(personal["email"])}">{html.escape(personal["email"])}</a></li>
                    <li><span>Phone</span><a href="tel:{html.escape(personal["phone"])}">{html.escape(personal["phone"])}</a></li>
                    <li><span>Location</span><strong>{html.escape(personal["location"])}</strong></li>
                    <li><span>GitHub</span><a href="{html.escape(personal["github"])}" target="_blank" rel="noreferrer">{html.escape(personal["github"])}</a></li>
                    <li><span>LinkedIn</span><a href="{html.escape(personal["linkedin"])}" target="_blank" rel="noreferrer">{html.escape(personal["linkedin"])}</a></li>
                </ul>
            </article>
        </section>
    </main>
    {mouse_glow_script}
</body>
</html>
"""


def render_editor(content: dict[str, object], message: str = "") -> str:
    escaped_json = html.escape(json.dumps(content, indent=2))
    message_html = f'<p class="save-message">{html.escape(message)}</p>' if message else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Portfolio Content</title>
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body class="editor-body">
    <main class="editor-shell">
        <section class="editor-panel">
            <div class="section-heading">
                <p class="eyebrow">Editor</p>
                <h1>Edit your portfolio content</h1>
            </div>
            <p class="lead">Update the JSON below, save it, then refresh the homepage. You can change your name, bio, education, projects, experience, and future plans from one file.</p>
            {message_html}
            <form method="post" action="/edit">
                <textarea name="content_json" spellcheck="false">{escaped_json}</textarea>
                <div class="editor-actions">
                    <button class="button button-primary" type="submit">Save Changes</button>
                    <a class="button button-secondary" href="/">Back to Site</a>
                </div>
            </form>
        </section>
    </main>
</body>
</html>
"""


class PortfolioHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.respond_html(render_home(load_content()))
            return
        if parsed.path == "/edit":
            self.respond_html(render_editor(load_content()))
            return
        if parsed.path == "/static/styles.css":
            css = (STATIC_DIR / "styles.css").read_bytes()
            self.respond(css, "text/css; charset=utf-8")
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        form = parse_qs(body)

        if parsed.path != "/edit":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        raw_content = form.get("content_json", [""])[0]
        try:
            parsed_content = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(render_editor(load_content(), f"Invalid JSON: {exc.msg}").encode("utf-8"))
            return

        save_content(parsed_content)
        self.respond_html(render_editor(parsed_content, "Saved successfully."))

    def log_message(self, format: str, *args: object) -> None:
        return

    def respond_html(self, body: str) -> None:
        self.respond(body.encode("utf-8"), "text/html; charset=utf-8")

    def respond(self, body: bytes, content_type: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    if not CONTENT_PATH.exists():
        raise FileNotFoundError("content.json is missing.")
    server = ThreadingHTTPServer(("127.0.0.1", 8010), PortfolioHandler)
    print("Portfolio site running at http://127.0.0.1:8010")
    server.serve_forever()


if __name__ == "__main__":
    main()
