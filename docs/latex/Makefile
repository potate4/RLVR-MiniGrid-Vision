# Makefile for RLVR Survey Paper LaTeX Compilation
# Usage:
#   make          - Compile the PDF
#   make clean    - Remove auxiliary files
#   make cleanall - Remove all generated files including PDF
#   make view     - Open the PDF (platform-specific)

# Main document name (without .tex extension)
MAIN = rlvr_survey

# LaTeX compiler
LATEX = pdflatex
BIBTEX = bibtex

# Compiler flags
LATEXFLAGS = -interaction=nonstopmode -halt-on-error

# PDF viewer (change based on your system)
# Linux: xdg-open, evince, okular
# macOS: open
# Windows: start
VIEWER = xdg-open

# Source files
TEX_FILES = $(MAIN).tex
BIB_FILES = $(MAIN).bib

# Generated files
PDF = $(MAIN).pdf
AUX = $(MAIN).aux
BBL = $(MAIN).bbl
BLG = $(MAIN).blg
LOG = $(MAIN).log
OUT = $(MAIN).out
TOC = $(MAIN).toc

# Auxiliary files to clean
AUX_FILES = $(AUX) $(BBL) $(BLG) $(LOG) $(OUT) $(TOC) \
            $(MAIN).lof $(MAIN).lot $(MAIN).synctex.gz \
            $(MAIN).fls $(MAIN).fdb_latexmk

.PHONY: all clean cleanall view help

# Default target
all: $(PDF)

# Compile the PDF
$(PDF): $(TEX_FILES) $(BIB_FILES)
	@echo "===================================="
	@echo "Compiling LaTeX document..."
	@echo "===================================="
	$(LATEX) $(LATEXFLAGS) $(MAIN)
	@echo ""
	@echo "===================================="
	@echo "Processing bibliography..."
	@echo "===================================="
	-$(BIBTEX) $(MAIN)
	@echo ""
	@echo "===================================="
	@echo "Second LaTeX pass..."
	@echo "===================================="
	$(LATEX) $(LATEXFLAGS) $(MAIN)
	@echo ""
	@echo "===================================="
	@echo "Final LaTeX pass..."
	@echo "===================================="
	$(LATEX) $(LATEXFLAGS) $(MAIN)
	@echo ""
	@echo "===================================="
	@echo "Compilation complete!"
	@echo "Output: $(PDF)"
	@echo "===================================="

# Quick compile (single pass, no bibliography)
quick:
	@echo "Quick compile (single pass)..."
	$(LATEX) $(LATEXFLAGS) $(MAIN)
	@echo "Done! (May have unresolved references)"

# Clean auxiliary files
clean:
	@echo "Cleaning auxiliary files..."
	rm -f $(AUX_FILES)
	@echo "Clean complete!"

# Clean everything including PDF
cleanall: clean
	@echo "Removing PDF..."
	rm -f $(PDF)
	@echo "All clean!"

# View the PDF
view: $(PDF)
	@echo "Opening PDF..."
	$(VIEWER) $(PDF) &

# Check for missing packages
check:
	@echo "Checking LaTeX installation..."
	@which $(LATEX) > /dev/null || (echo "ERROR: pdflatex not found!" && exit 1)
	@which $(BIBTEX) > /dev/null || (echo "ERROR: bibtex not found!" && exit 1)
	@echo "LaTeX installation OK!"

# Count words (approximate, from PDF)
wordcount: $(PDF)
	@echo "Approximate word count:"
	@pdftotext $(PDF) - | wc -w

# Show compilation stats
stats: $(PDF)
	@echo "===================================="
	@echo "Document Statistics"
	@echo "===================================="
	@echo "PDF size: $$(du -h $(PDF) | cut -f1)"
	@echo "PDF pages: $$(pdfinfo $(PDF) | grep Pages | awk '{print $$2}')"
	@echo "Approx words: $$(pdftotext $(PDF) - | wc -w)"
	@echo "LaTeX lines: $$(wc -l $(MAIN).tex | awk '{print $$1}')"
	@echo "BibTeX entries: $$(grep -c '^@' $(MAIN).bib)"
	@echo "===================================="

# Help target
help:
	@echo "===================================="
	@echo "RLVR Survey Paper - Makefile Help"
	@echo "===================================="
	@echo ""
	@echo "Available targets:"
	@echo "  make         - Compile the PDF (full process)"
	@echo "  make quick   - Quick compile (single pass)"
	@echo "  make clean   - Remove auxiliary files"
	@echo "  make cleanall- Remove all generated files"
	@echo "  make view    - Open the PDF"
	@echo "  make check   - Check LaTeX installation"
	@echo "  make stats   - Show document statistics"
	@echo "  make help    - Show this help message"
	@echo ""
	@echo "Typical workflow:"
	@echo "  1. Edit $(MAIN).tex"
	@echo "  2. Run 'make'"
	@echo "  3. Run 'make view' to see result"
	@echo "  4. Run 'make clean' to tidy up"
	@echo ""
	@echo "For issues, see README.md"
	@echo "===================================="

# Watch for changes and auto-compile (requires entr or inotifywait)
watch:
	@echo "Watching for changes..."
	@echo "Press Ctrl+C to stop"
	@while true; do \
		inotifywait -e modify $(TEX_FILES) $(BIB_FILES) 2>/dev/null || \
		(echo "Install inotify-tools for file watching" && exit 1); \
		make quick; \
	done

# Alternative: use latexmk if available
latexmk:
	@echo "Using latexmk..."
	latexmk -pdf -pdflatex="$(LATEX) $(LATEXFLAGS)" $(MAIN)

# Continuous preview with latexmk
preview:
	@echo "Starting continuous preview..."
	latexmk -pdf -pvc -pdflatex="$(LATEX) $(LATEXFLAGS)" $(MAIN)




