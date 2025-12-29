# KAIROS Clinical OS

**KAIROS** is a Next-Gen Clinical Operating System designed to automate the lifecycle of clinical trials using Agentic AI.

## ⏳ Seize the Timeline

KAIROS helps Clinical Research Organizations (CROs) and Pharmas cut 40% of their operational overhead by deploying AI agents for:
- **Design**: Protocol writing & auditing.
- **Build**: UAT script generation.
- **Clean**: Data query automation.
- **Translate**: Medical translation with back-translation audit.
- **File**: TMF classification.

## Modules

- **The Workbench**: Core tools for clinical operations.
- **Collaboration Hub**: Project management and chat.
- **Secretary (Meeting AI)**: Automated minutes and specialized action items.

## Setup

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   streamlit run app_ui.py
   ```

## Deployment

Deploy to Google Cloud Run:
```bash
./deploy.sh
```
