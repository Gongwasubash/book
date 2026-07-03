## Goal
- Serve all Nepal government textbooks (Grade 1–10) with PDF as the primary view and markdown chapter content retained for AI tutoring features.

## Constraints & Preferences
- Every chapter click must show exact textbook content
- Nepali text must be proper Unicode Devanagari, no OCR garbage
- PDF opens by default when clicking a book; markdown chapter view and AI features still available via toggle
- PDF source: CDC CDN at `giwmscdnone.gov.np/media/pdf_upload/`

## Progress

### Done
- **PDF.js canvas viewer** — replaced native `<iframe>` with PDF.js canvas renderer (`loadPdfViewer`, `pdfRenderPage`) for consistent cross-browser behavior; navigation bar with prev/next, page input, zoom controls
- **Fixed page jump system** — replaced `pdfPageTarget`/`pdfPendingTarget` with `pdfJumpRequest = { pk, rawTblPage }` that defers all page-number calculation until the PDF document is loaded and its page-label offset is known
- **Offset detection integrated** — `detectPdfOffsetOnce()` runs inside `loadPdfViewer()` after PDF opens, sets `pdfScale` auto-fit, then `resolvePdfJump()` calculates the target page from raw TOC page + detected offset; guaranteed to have offset before page is rendered
- **Duplicate-load guard** — `pdfLoadingPk` prevents starting a second `pdfjsLib.getDocument()` when user clicks chapters while PDF is still loading
- **Chapter click in PDF mode** — clicking a chapter no longer forcibly switches to markdown chapter view; if the chapter has no page data in TOC_TABLES, the PDF stays open at the current page and just highlights the sidebar entry
- **Preserve current page** — `resolvePdfJump()` no longer resets to page 1 when no jump request is active; re-rendering the PDF viewer keeps the user's current page
- **`/api/pdf-url` Netlify function** — `functions/pdf-url.js` returns PDF URL from pre-built `functions/pdf_lookup.json` (54 textbook mappings); `netlify.toml` updated with redirect
- **Pushed to GitHub** — `origin` at `https://github.com/Gongwasubash/book.git`
- **Batch TOC extraction from 43 unique PDFs** — used `pdfjs-dist` to download every PDF, detect page-label offset, extract outline/bookmarks, and fall back to text extraction from first 100 pages; results saved to `_toc_extracted.json`
- **Discovered ~30 new PDF URLs** — found via EducateNepal blog and Pragyapath site (Grade 7–10 CDN links including Science Technology English, Social Studies, Health PE)
- **All 87 books now have TOC entries** — auto-generated `addTOC()` calls from `addChapters()` data for the 39 books missing chapter listings; every book in INDEX now has at least a basic chapter table (without page numbers)
- **Hardcoded Mistral API key removed** — `functions/chat.js` now reads `MISTRAL_API_KEY` from environment only

### Current State
- **87 books in INDEX**, all with TOC entries (22 with page numbers, 65 without)
- **54 PDF URLs** mapped in `pdf_lookup.json` (covering 38/87 books)
- **16 books** are Fully Functional (PDF + TOC with page numbers → chapter-click jumps to correct PDF page)
- **22 books** have PDFs and TOC entries but no page numbers (PDF viewable, chapter navigation works with no page jump)
- **16 books** have PDFs but no TOC page numbers (PDF viewable)
- **33 books** have no PDF URL at all (markdown-only, no PDF viewing)
- PDF text extraction from _toc_extracted.json returned 0 usable text for all PDFs (Preeti font issues for Nepali, no embedded text layer for English)
- CDC website has no accessible textbook listing — `/category/textbook/` shows only notices, WordPress REST API is disabled
- Python `requests` fails on the CDN with SSL errors — use browser/iframe for PDF viewing

### Next Steps
1. **Add page numbers manually** — 38 books with PDFs need page numbers extracted from printed TOC pages; requires opening each PDF, reading the Devanagari/Arabic page numbers, and typing them into `addTOC()` entries in `toc_webpage.html`
2. **Deploy to Netlify** — requires `netlify login` or `NETLIFY_AUTH_TOKEN`; set `GROQ_API_KEY` and `MISTRAL_API_KEY` as Netlify environment variables for AI chat feature
3. **Discover more PDF URLs** — for the 33 books still missing PDFs, try CDC elibrary (`lib.moecdc.gov.np/elibrary`) or other sources
4. **Test PDF chapter-click → correct page** for the 16 fully functional books
5. **Test across browsers** — verify PDF.js viewer works in Chrome, Firefox, Edge

## Key Files
- `toc_webpage.html`: Frontend — PDF.js canvas viewer, chapter list, AI cards, sidebar, TOC_TABLES, page-jump queueing
- `functions/pdf-url.js`: Netlify function serving `/api/pdf-url` endpoint
- `functions/chat.js`: Netlify function for AI chat (Groq/Mistral with fallback)
- `functions/pdf_lookup.json`: Pre-built mapping of 54 `"Class N|Subject Name"` → CDN PDF URL
- `netlify.toml`: Redirects `/api/pdf-url` → `/.netlify/functions/pdf-url`
- `server.py`: Flask backend for local development (AI chat, chapter content)
- `book_pdf_map.json`: Source PDF URL data from CDC CDN scraping (200+ content IDs, most with `no pdf`)
- `_toc_extracted.json`: Extracted outline and page-text data from all PDFs for TOC_TABLES generation
- `_gen_toc_entries.mjs`: Script to generate addTOC() calls from addChapters() data
