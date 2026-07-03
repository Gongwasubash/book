## Goal
- Serve all Nepal government textbooks (Grade 1–10) with PDF as the primary view and markdown chapter content retained for AI tutoring features.

## Constraints & Preferences
- Every chapter click must show exact textbook content
- Nepali text must be proper Unicode Devanagari, no OCR garbage
- PDF opens by default when clicking a book; markdown chapter view and AI features still available via toggle
- PDF source: CDC CDN at `giwmscdnone.gov.np/media/pdf_upload/`

## Progress

### Done
- **PDF-first frontend** — `toc_webpage.html` now shows PDF embed as the default view when a book with a known PDF URL is selected. A toggle button ("PDF View" / "Chapter View") lets users switch between the full PDF and the markdown chapter content with AI features (MCQs, mind maps, exercises).
- **`/api/pdf-url` endpoint** — `server.py` now has a `get_pdf_url()` function that maps (class, subject) pairs to CDC CDN PDF URLs loaded from `book_pdf_map.json`. Returns `{"pdf_url": "https://...", "available": true}` or `{"available": false}`.
- **`book_pdf_map.json`** — curated mapping of 11 CDC content IDs to CDN PDF URLs, built by scraping textbook content pages that contain `var pdf = '...'` in their HTML. Includes Class 1 Nepali, Class 9 Math Nepali, Class 10 Social Studies, plus 8 supplementary subjects (Ayurveda, Yoga, Nitishasram, etc.).
- **Verified CDN PDF accessibility** — `webfetch` tool successfully retrieves 5+ MB PDFs from the CDN. Python `requests` has SSL/TLS handshake errors with the CDN host, but browsers (`<iframe>`) load them fine.
- **Class 7 Maths English headings fixed** — 21 `##` headings inserted at correct "Lesson" markers.
- **Single-chapter loading** — frontend loads one chapter at a time via `/api/chapter-content`.
- **Simplified body-text scanning** — aggressive scanning removed; corrupted files return 0 chapters.

### Current State
- 11 textbook PDF URLs discovered (mostly supplementary subjects plus Nepali 1, Math 9 Nepali, Social Studies 10)
- 78 core subject textbooks (Nepali, English, Math, Science for grades 1-10) still lack PDF URLs
- CDC website has no accessible textbook listing — `/category/textbook/` shows only notices, WordPress REST API is disabled, site search returns no textbook results
- Content IDs 1-500 scanned — no new textbook PDFs found beyond the 11 known
- Python `requests` fails on the CDN with SSL errors — use browser/iframe for PDF viewing

### Next Steps
1. **Manual PDF discovery for core subjects** — try CDC search for individual textbooks (e.g., `moecdc.gov.np/?s=english+class+6`), or manually inspect content pages at known textbook URLs. For each found content ID, add to `SUBJECT_TO_CONTENT` in `server.py` and verify the PDF URL via `_build_pdf_map.py`.
2. **Add more subject-to-content mappings** — update `SUBJECT_TO_CONTENT` dict in `server.py` as more PDF URLs are verified. Currently mapped: Class 1 Nepali, Class 9 Math Nepali, Class 9 Naturopath, Class 9 Yoga, Class 10 Social Studies.
3. **Test PDF embed across browsers** — verify the `<iframe>` PDF viewer works in Chrome, Firefox, Edge.
4. **Consider PDF.js for advanced features** — if users need search, page navigation, or text selection within PDFs, switch from native `<iframe>` to PDF.js for better control.
5. **Retry CDC elibrary** — `lib.moecdc.gov.np` was inaccessible previously; may become available.

## Key Files
- `server.py`: Flask backend — `/api/pdf-url` endpoint, PDF mapping via `get_pdf_url()`
- `toc_webpage.html`: Frontend — PDF/chapter view toggle, chapter loading, AI features
- `book_pdf_map.json`: 11 known content ID → CDN PDF URL mappings
- `cdc_pdf_map.json`: ~50 scraper entries (mostly notices, a few textbooks)
- `_build_pdf_map.py`: Script to scan CDC content IDs for textbook PDFs
