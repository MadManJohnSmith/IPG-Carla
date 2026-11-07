# Lab evidence — location, sensitivity, publication gate

The evidence for this project is kept outside the repository, under
`~/Documents/research/`:

| Path | Contents |
|---|---|
| `ipg-carla-lab/notebooklm/` | 26 NotebookLM items (papers, notes, links), one `.md` each, plus `INDEX.md` |
| `ipg-carla-lab/machine-configs/` | 35 rig photos + 1 video, with `INDEX.md` (34/35 classified) |
| `ipg-carla-lab/README.md`, `HANDOFF.md` | Index and handoff for the lab material |
| `gemini-chats/` | Three shared Gemini chats (77/53/30 turns) and their attachments |
| `gemini-chats/attachments/REVIEW.md` | Per-image sensitivity review (visual, 15 images) |

## Why it is not in this repo

The material contains lab identifiers and captures that must not be published:

- a handwritten credential note;
- hostname, local account and machine paths;
- a hardware serial number;
- `ipconfig` output with real IPs and MACs;
- BitLocker state, licence dialogs and software inventory.

The public repo must stay free of all of it. `research/` is gitignored as a
guard.

## Publication gate

Nothing from the evidence folders goes into a public repo, a chat or a
presentation without redaction and Alan's explicit confirmation. A redacted
file still needs the confirmation.

Per-image detail: `gemini-chats/attachments/REVIEW.md` (5 of 15 must not be
published, 4 require redaction, 6 have no identifiers) and
`machine-configs/INDEX.md` (rig photos: do not publish).

## If the evidence is missing

If the machine was restored and `~/Documents/research/` is gone, ask Alan for
the backup. The 7 PDFs are public papers and can be re-downloaded from their
publishers; the notes, photos and chats cannot be regenerated.
