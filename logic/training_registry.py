import os

# Define the library of training videos available for each role.
# In a real app, this might come from a database or storage bucket.

TRAINING_REGISTRY = {
    "Protocol Writer": [
        {
            "title": "Protocol Writing 101: Structure & Standards",
            "filename": "protocol_writing_101.mp4",
            "description": "Learn the fundamentals of TransCelerate compliant protocol structure.",
            "duration": "12:30"
        },
        {
            "title": "Using the Zero-Draft Generator",
            "filename": "zero_draft_tutorial.mp4",
            "description": "A deep dive into using the AI drafting tool effectively.",
            "duration": "08:15"
        }
    ],
    "Medical Coder": [
        {
            "title": "Coding with MedDRA v26.0",
            "filename": "meddra_coding_guide.mp4",
            "description": "Best practices for selecting LLTs using the browser.",
            "duration": "15:45"
        },
        {
            "title": "Handling Uncodable Terms",
            "filename": "uncodable_terms.mp4",
            "description": "What to do when the AI returns low confidence scores.",
            "duration": "06:20"
        }
    ],
    "Clinical Data Manager": [
        {
            "title": "CDM Metrics Dashboard Tour",
            "filename": "cdm_dashboard_tour.mp4",
            "description": "Understanding the key performance indicators (KPIs) in the dashboard.",
            "duration": "10:00"
        },
        {
            "title": "Reconciliation: EDC vs Safety",
            "filename": "reconciliation_workflow.mp4",
            "description": "Step-by-step guide to running the reconciliation agent.",
            "duration": "14:10"
        }
    ],
    "CRA / Monitor": [
        {
            "title": "Remote SDV Best Practices",
            "filename": "remote_sdv_guide.mp4",
            "description": "How to perform source data verification remotely.",
            "duration": "18:20"
        },
        {
            "title": "Generating Trip Reports",
            "filename": "trip_report_gen.mp4",
            "description": "Using the voice-to-text feature for rapid reporting.",
            "duration": "05:50"
        }
    ],
    "CRC / Site Coord": [
        {
            "title": "Patient Visit Calculation",
            "filename": "visit_calc_tutorial.mp4",
            "description": "Ensure your patients never miss a window.",
            "duration": "04:30"
        },
        {
            "title": "Answering Queries in EDC",
            "filename": "answering_queries.mp4",
            "description": "How to respond to CDM queries effectively.",
            "duration": "09:45"
        }
    ],
    "Medical Monitor (Oncology)": [
        {
            "title": "RECIST 1.1 Criteria Overview",
            "filename": "recist_101.mp4",
            "description": "Standardized response criteria for solid tumors.",
            "duration": "22:00"
        },
        {
            "title": "Toxicity Grading (CTCAE v5.0)",
            "filename": "ctcae_grading.mp4",
            "description": "Accurate grading of adverse events in oncology.",
            "duration": "12:15"
        }
    ],
    "Admin": [
        {
            "title": "System Administration & Audit Logs",
            "filename": "admin_overview.mp4",
            "description": "Managing users and reviewing 21 CFR Part 11 logs.",
            "duration": "10:00"
        }
    ],
    "Protocol Reviewer": [
        {
            "title": "Protocol Audit Checklist",
            "filename": "protocol_audit_guide.mp4",
            "description": "How to stress-test a protocol draft for feasibility.",
            "duration": "14:20"
        }
    ],
    "Clinical QA / Auditor": [
        {
            "title": "eTMF Filing Standards (DIA Model)",
            "filename": "etmf_standards.mp4",
            "description": "Proper classification and metadata for TMF artifacts.",
            "duration": "11:50"
        }
    ],
    "Medical Researcher": [
        {
            "title": "Using Asclepius Agent",
            "filename": "asclepius_tutorial.mp4",
            "description": "How to query the medical knowledge base effectively.",
            "duration": "09:15"
        }
    ]
}

def get_videos_for_role(role):
    """Returns a list of video dictionaries for the specified role."""
    return TRAINING_REGISTRY.get(role, [])
