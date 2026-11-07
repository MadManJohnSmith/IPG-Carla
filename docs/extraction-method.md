# Reproducing the NotebookLM extraction

This is the method that worked on 2026-11-07 against the current "Gemini
Notebook" UI. It is recorded because the naive approaches fail silently: they
return the sources sidebar instead of the document.

## Setup

- Use the in-app browser (`browser-use:control-browser`, backend `iab`) with a
  dedicated tab. The page must be rendered; plain HTTP returns a shell.
- Do not use Escape, `back()`, or screenshots to navigate: they leave the page
  on `about:blank` or in the chat view, and screenshots can time out.

## Opening an item

- Click `button.source-stretched-button`, the first child of
  `.single-source-container`, via `evaluate`. The visible `.source-title` is
  `aria-hidden` and is not the click target. Coordinate clicks were unreliable
  because the list reflows and the point lands on the previous row.
- **PDFs and web pages:** the viewer replaces the list inside `.source-panel`.
  Read the text from `labs-tailwind-doc-viewer` inside `source-viewer`. Discard
  `source-guide-container`; that is the generated summary, not the document.
- **Notes:** the click opens the note in the Studio panel. Read
  `labs-tailwind-doc-viewer` inside `note-editor`; the title is in
  `input.note-header__editable-title`.
- There is no back button for PDF/URL viewers: reload the tab to restore the
  list before opening the next one.

## Validation

Reject a capture that contains `side_nav` or starts with
`Sources` / `sort` / `Select all`: it is the sidebar, not the document. Every
valid file starts with `# <title>` and has its own text.

## Where the output lives

`~/Documents/research/ipg-carla-lab/notebooklm/`, one `.md` per item plus
`INDEX.md` with the inventory, method and caveats. That folder is sensitive and
must not be committed.
