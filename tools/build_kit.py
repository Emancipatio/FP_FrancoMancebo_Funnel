"""Build the Right Hand Kit downloads from kit/right-hand-kit/.

Writes, into brief/:
  right-hand-kit.zip          skill for everyone (ends on Pareto's Right Hand Program)
  right-hand-kit-fitcall.zip  skill for qualified founders (ends on the Match Call booking page)
  prompt.txt / prompt-fitcall.txt  the same kit as one paste-in prompt for any AI chat
  kits/<style>-<contact>-<pace>[-fitcall].zip/.txt  the same, tuned to a Founder Working Style result

Run from the repo root: python3 tools/build_kit.py
"""
import json
import pathlib
import re
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "kit" / "right-hand-kit"
OUT = ROOT / "brief"

NEXT = {
    "": "Want someone to run this kit with you? Pareto Talent matches founders with a full-time, AI-trained Right Hand who owns these outcomes, not just tasks. See the Right Hand Program: https://paretotalent.com",
    "-fitcall": "Bring this kit to your 20-minute Right Hand Match Call: https://emancipatio.github.io/FP_FrancoMancebo_Funnel/book/ We'll turn it into your Right Hand's role and, if it's a fit, show you 3 hand-picked candidates within 24 hours. You owe nothing unless you're excited about one.",
}

FILES = ["SKILL.md", "references/playbooks.md", "references/kit-template.md"]
STYLES = json.loads((ROOT / "kit" / "styles.json").read_text(encoding="utf-8"))
KITS = OUT / "kits"


def style_md(style, contact, pace):
    st, c, p = STYLES["styles"][style], STYLES["contact"][contact], STYLES["pace"][pace]
    ty = STYLES["types"][style][pace]
    return "\n".join([
        "# My Founder Working Style",
        "",
        f"**{ty['name']}** ({st['axes']} · {p['label']} · {c['label']})",
        "",
        ty["line"],
        "",
        "## What I want from my Right Hand",
        *[f"- {x}" for x in st["rh"]],
        "",
        f"**SOP detail:** {st['sop']}",
        f"**Decide alone vs ask me:** {st['decide']}",
        f"**How to update me:** {c['update']}",
        f"**Drafts:** {p['drafts']}",
        "",
    ])


def read(rel):
    return (SRC / rel).read_text(encoding="utf-8")


def prompt(next_step, style_text=""):
    skill = read("SKILL.md")
    body = re.sub(r"\A---\n.*?\n---\n", "", skill, flags=re.S).replace("{{NEXT_STEP}}", next_step)
    body = body.replace("Read `references/playbooks.md` before Part 2 and `references/kit-template.md` before Part 3.",
                        "The playbooks for Part 2 and the kit template for Part 3 are at the end of this prompt.")
    body = body.replace("`references/playbooks.md`", "the PLAYBOOKS below").replace("`references/kit-template.md`", "the KIT TEMPLATE below")
    head = ("You are my Right Hand Kit by Pareto Talent. Follow these instructions for the whole chat. "
            "You can't see my inbox or calendar in this chat unless I paste them, so use the fallback questions in Part 1. "
            "Start now with the Start step.\n\n")
    if style_text:
        body = body.replace("`references/my-style.md`", "MY STYLE below")
        head += "MY STYLE (from the Founder Working Style quiz):\n\n" + style_text + "\n"
    return (head + body + "\n\n=== PLAYBOOKS ===\n\n" + read("references/playbooks.md")
            + "\n\n=== KIT TEMPLATE ===\n\n" + read("references/kit-template.md"))


def write_zip(path, next_step, style_text=""):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        files = [(rel, read(rel).replace("{{NEXT_STEP}}", next_step)) for rel in FILES]
        if style_text:
            files.append(("references/my-style.md", style_text))
        for rel, text in files:
            info = zipfile.ZipInfo(f"right-hand-kit/{rel}", date_time=(2026, 10, 6, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, text)


def main():
    KITS.mkdir(exist_ok=True)
    for suffix, next_step in NEXT.items():
        # No quiz taken: the generic kit.
        write_zip(OUT / f"right-hand-kit{suffix}.zip", next_step)
        (OUT / f"prompt{suffix}.txt").write_text(prompt(next_step), encoding="utf-8")
        # One kit per Founder Working Style result: kits/<style>-<contact>-<pace><suffix>.zip
        for style in STYLES["styles"]:
            for contact in STYLES["contact"]:
                for pace in STYLES["pace"]:
                    key = f"{style}-{contact}-{pace}{suffix}"
                    text = style_md(style, contact, pace)
                    write_zip(KITS / f"{key}.zip", next_step, text)
                    (KITS / f"{key}.txt").write_text(prompt(next_step, text), encoding="utf-8")
    print("built", len(list(KITS.glob("*.zip"))), "style kits +", len(list(OUT.glob("right-hand-kit*.zip"))), "generic")


if __name__ == "__main__":
    main()
