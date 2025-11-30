# Deep Research Crew — Phase 1 MVP

A CrewAI-powered research system that performs end-to-end evidence-driven research with multimodal evidence gathering, claim extraction, fact-checking, and reproducible outputs.

## 🎯 What It Does

The Deep Research Crew automates the research process:

1. **Discovers** relevant sources based on your research query
2. **Extracts** structured information from PDFs and web pages
3. **Identifies** factual claims with full provenance tracking
4. **Verifies** claims against external academic databases
5. **Generates** comprehensive research reports with confidence scores

## 🏗️ Architecture

### Phase 1 MVP Agents

- **Research Lead**: Orchestrates the research process and synthesizes findings
- **Literature Miner**: Extracts structured data from PDFs and web pages
- **Claim Verifier**: Fact-checks claims using Semantic Scholar and other sources
- **Report Composer**: Creates comprehensive Markdown reports

### Custom Tools

- **PDFParserTool**: Extracts sections, citations, and metadata from academic papers
- **WebScraperTool**: Scrapes web content with HTML cleaning
- **ClaimExtractorTool**: Identifies numerical, comparative, and experimental claims
- **FactCheckerTool**: Verifies claims against academic databases
- **ReportGeneratorTool**: Creates structured research reports

## 📦 Installation

1. **Clone and navigate to the project**:
   ```bash
   cd latest_ai_development
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

## 🚀 Usage

### Quick Start

Run the default research query:

```bash
python -m latest_ai_development.main
```

This will research "efficacy of transformer models for natural language processing" and generate a report.

### Custom Research Query

Edit `src/latest_ai_development/main.py` and modify the `inputs` dictionary:

```python
inputs = {
    'query': 'your research question here',
    'start_date': '2020-01-01',
    'end_date': '2024-12-31',
    'sources': 'papers, web',
    'max_docs': 10
}
```

### Using the CLI

```bash
# Run research
latest_ai_development

# Or use the run_crew command
run_crew
```

## 📊 Output

The system generates:

- **research_report.md**: Comprehensive research report with:
  - Executive summary
  - Research statistics
  - Claims analysis (grouped by confidence level)
  - Source documentation
  - Full provenance tracking

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Required
OPENAI_API_KEY=your_openai_key_here

# Optional
SEMANTIC_SCHOLAR_API_KEY=optional
CROSSREF_EMAIL=your_email@example.com
MAX_DOCUMENTS=50
MAX_CLAIMS_PER_DOCUMENT=20
```

### Agent Configuration

Agents are configured in `src/latest_ai_development/config/agents.yaml`:

- Roles and goals
- Backstories for prompting
- Tool assignments

### Task Configuration

Tasks are defined in `src/latest_ai_development/config/tasks.yaml`:

- Task descriptions
- Expected outputs
- Agent assignments
- Dependencies

## 📁 Project Structure

```
latest_ai_development/
├── src/latest_ai_development/
│   ├── config/
│   │   ├── agents.yaml          # Agent definitions
│   │   └── tasks.yaml           # Task definitions
│   ├── models/
│   │   ├── claim.py             # Claim, Evidence, Provenance models
│   │   ├── document.py          # Document, Section, Citation models
│   │   └── research.py          # ResearchQuery, ResearchResult models
│   ├── tools/
│   │   ├── ingestion/
│   │   │   ├── pdf_parser.py    # PDF parsing tool
│   │   │   └── web_scraper.py   # Web scraping tool
│   │   ├── analysis/
│   │   │   ├── claim_extractor.py  # Claim extraction
│   │   │   └── fact_checker.py     # Fact-checking
│   │   └── output/
│   │       └── report_generator.py # Report generation
│   ├── crew.py                  # Crew orchestration
│   └── main.py                  # Entry point
├── pyproject.toml               # Dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

## 🎓 How It Works

### 1. Discovery Phase
The Research Lead analyzes your query and creates a research plan with specific questions and source priorities.

### 2. Literature Mining
The Literature Miner uses PDFParserTool and WebScraperTool to extract structured content from documents.

### 3. Claim Extraction
Claims are identified using pattern matching and LLM-based analysis, with full provenance tracking.

### 4. Fact-Checking
The Claim Verifier searches Semantic Scholar and other academic databases to find supporting or contradicting evidence.

### 5. Report Generation
The Report Composer synthesizes all findings into a comprehensive Markdown report with confidence scores.

## 🔍 Example Output

```markdown
# Deep Research Report: efficacy of transformer models

## Executive Summary
This report analyzes 10 documents and extracts 25 claims...

## Research Statistics
- Documents Found: 50
- Documents Processed: 10
- Claims Extracted: 25
- Verified Claims: 18
- Contradicted Claims: 2

## Claims Analysis

### ✅ Verified Claims

#### claim_001
> Transformer models reduce error by 30% on dataset Y

**Type**: numerical
**Confidence**: verified
**Evidence**:
1. ✓ Paper shows 28-32% improvement...
   - Source: https://arxiv.org/...
```

## 🚧 Future Phases

### Phase 2: Data Analysis
- Data Engineer agent for ETL
- ML Analyst for pattern discovery
- Statistical analysis tools

### Phase 3: Multimodal
- Video Watcher for YouTube analysis
- Social Media Miner for X/Reddit
- News Crawler for large-scale scraping

### Phase 4: Governance
- Ethics Officer for compliance
- Ops Agent for monitoring
- PII detection and redaction

## 📝 License

This project is part of the Deep Research Crew system.

## 🤝 Contributing

To extend the system:

1. Add new tools in `src/latest_ai_development/tools/`
2. Define new agents in `config/agents.yaml`
3. Create tasks in `config/tasks.yaml`
4. Wire them in `crew.py`

See `DEEP_RESEARCH_CREW_PLAN.md` for the full architecture and roadmap.
