"""Build the Right Hand Kit downloads from kit/right-hand-kit/.

Writes, into brief/:
  right-hand-kit.zip          skill for everyone (ends on Pareto's Right Hand Program)
  right-hand-kit-fitcall.zip  skill for qualified founders (ends on the Fit Call booking page)
  prompt.txt / prompt-fitcall.txt  the same kit as one paste-in prompt for any AI chat

Run from the repo root: python3 tools/build_kit.py
"""
import pathlib
import re
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "kit" / "right-hand-kit"
OUT = ROOT / "brief"

NEXT = {
    "": "Want someone to run this kit with you? Pareto Talent matches founders with a full-time, AI-trained Right Hand who owns these outcomes, not just tasks. See the Right Hand Program: https://paretotalent.com",
    "-fitcall": "Bring this kit to your 20-minute Right Hand Fit Call: https://emancipatio.github.io/FP_FrancoMancebo_Funnel/book/ We'll turn it into your Right Hand's role and, if it's a fit, show you 3 hand-picked candidates within 24 hours. You owe nothing unless you're excited about one.",
}

FILES = ["SKILL.md", "references/playbooks.md", "references/kit-template.md"]


def read(rel):
    return (SRC / rel).read_text(encoding="utf-8")


def prompt(next_step):
    skill = read("SKILL.md")
    body = re.sub(r"\A---\n.*?\n---\n", "", skill, flags=re.S).replace("{{NEXT_STEP}}", next_step)
    body = body.replace("Read `references/playbooks.md` before Part 2 and `references/kit-template.md` before Part 3.",
                        "The playbooks for Part 2 and the kit template for Part 3 are at the end of this prompt.")
    body = body.replace("`references/playbooks.md`", "the PLAYBOOKS below").replace("`references/kit-template.md`", "the KIT TEMPLATE below")
    head = ("You are my Right Hand Kit by Pareto Talent. Follow these instructions for the whole chat. "
            "You can't see my inbox or calendar in this chat unless I paste them, so use the fallback questions in Part 1. "
            "Start now with the Start step.\n\n")
    return (head + body + "\n\n=== PLAYBOOKS ===\n\n" + read("references/playbooks.md")
            + "\n\n=== KIT TEMPLATE ===\n\n" + read("references/kit-template.md"))


def main():
    for suffix, next_step in NEXT.items():
        with zipfile.ZipFile(OUT / f"right-hand-kit{suffix}.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for rel in FILES:
                text = read(rel).replace("{{NEXT_STEP}}", next_step)
                info = zipfile.ZipInfo(f"right-hand-kit/{rel}", date_time=(2026, 10, 6, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info, text)
        (OUT / f"prompt{suffix}.txt").write_text(prompt(next_step), encoding="utf-8")
    print("built", sorted(p.name for p in OUT.glob("*kit*.zip")), sorted(p.name for p in OUT.glob("prompt*.txt")))


if __name__ == "__main__":
    main()
