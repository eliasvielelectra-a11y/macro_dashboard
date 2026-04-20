from __future__ import annotations

import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 1.0rem;
                padding-bottom: 2rem;
                max-width: 1500px;
            }

            .header-framing-line {
                font-size: 0.90rem;
                color: #6b7280;
                margin-top: 0.25rem;
                margin-bottom: 0.6rem;
            }

            .badge-strip {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
                margin-top: 0.35rem;
                margin-bottom: 1.2rem;
            }

            .dashboard-badge {
                display: inline-block;
                padding: 0.22rem 0.55rem;
                border-radius: 999px;
                font-size: 0.72rem;
                font-weight: 700;
                border: 1px solid rgba(128, 128, 128, 0.25);
            }

            .badge-tag { background: rgba(15, 23, 42, 0.04); }
            .badge-frequency { background: rgba(59, 130, 246, 0.08); }
            .badge-source { background: rgba(107, 114, 128, 0.08); }
            .badge-status { background: rgba(16, 185, 129, 0.08); }
            .badge-default { background: rgba(128, 128, 128, 0.08); }

            .section-header-wrap {
                margin-top: 0.6rem;
                margin-bottom: 0.7rem;
            }

            .section-header-title {
                font-size: 1.15rem;
                font-weight: 800;
                margin-bottom: 0.15rem;
            }

            .section-header-subtitle {
                font-size: 0.86rem;
                color: #6b7280;
            }

            .card-header {
                margin-bottom: 0.45rem;
            }

            .card-title {
                font-size: 0.95rem;
                font-weight: 800;
                margin-bottom: 0.25rem;
            }

            .card-badges {
                display: flex;
                flex-wrap: wrap;
                gap: 0.35rem;
                margin-bottom: 0.25rem;
            }

            .card-subtitle {
                font-size: 0.76rem;
                color: #6b7280;
                line-height: 1.25;
            }

            .card-main-value {
                font-size: 1.45rem;
                font-weight: 800;
                line-height: 1.05;
                margin-top: 0.15rem;
                margin-bottom: 0.2rem;
            }

            .card-secondary {
                font-size: 0.83rem;
                font-weight: 700;
                margin-bottom: 0.15rem;
            }

            .card-meta {
                font-size: 0.74rem;
                color: #6b7280;
                margin-bottom: 0.3rem;
            }

            .card-note {
                font-size: 0.72rem;
                color: #6b7280;
                margin-top: 0.35rem;
                line-height: 1.25;
            }

            div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stMarkdownContainer"] .card-header) {
                margin-bottom: 0.5rem;
            }

            .card-chart-placeholder {
                font-size: 0.75rem;
                color: #9ca3af;
                padding-top: 0.75rem;
            }

            .positive { color: #16a34a; }
            .negative { color: #dc2626; }
            .neutral  { color: #6b7280; }

            .assessment-main-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 0.2rem;
                margin-bottom: 0.35rem;
            }

            .assessment-level {
                font-size: 1.15rem;
                font-weight: 800;
            }

            .assessment-direction {
                font-size: 0.78rem;
                font-weight: 700;
                color: #6b7280;
            }

            .assessment-reason {
                font-size: 0.80rem;
                line-height: 1.3;
                color: #374151;
            }

            .assessment-low { border-left: 4px solid #16a34a; }
            .assessment-medium { border-left: 4px solid #f59e0b; }
            .assessment-high { border-left: 4px solid #dc2626; }

            .transmission-flow {
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                align-items: center;
                margin-bottom: 0.8rem;
                line-height: 1.4;
            }

            .flow-node {
                border: 1px solid rgba(128,128,128,0.20);
                border-radius: 999px;
                padding: 0.4rem 0.7rem;
                font-size: 0.8rem;
                font-weight: 700;
                background: rgba(128,128,128,0.04);
            }

            .flow-arrow {
                font-weight: 900;
                color: #6b7280;
            }

            .transmission-bucket {
                border: 1px solid rgba(128,128,128,0.16);
                border-radius: 14px;
                padding: 0.7rem;
                min-height: 110px;
            }

            .transmission-bucket-title {
                font-size: 0.86rem;
                font-weight: 800;
                margin-bottom: 0.25rem;
            }

            .transmission-bucket-text {
                font-size: 0.77rem;
                color: #4b5563;
                line-height: 1.3;
            }

            .insight-bar {
                border: 1px solid rgba(128,128,128,0.14);
                border-radius: 14px;
                padding: 0.7rem 0.8rem;
                display: flex;
                align-items: flex-start;
                gap: 0.7rem;
                margin-top: 0.2rem;
                margin-bottom: 0.8rem;
                background: rgba(128,128,128,0.03);
            }

            .insight-bar-text {
                font-size: 0.84rem;
                line-height: 1.35;
            }

            .commentary-list ul {
                margin: 0.3rem 0 0 1rem;
                padding: 0;
            }

            .commentary-list li {
                margin-bottom: 0.35rem;
                font-size: 0.80rem;
                line-height: 1.3;
            }

            .scenario-grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 0.18rem;
                font-size: 0.80rem;
                margin-top: 0.35rem;
                margin-bottom: 0.45rem;
            }

            .scenario-highlight {
                min-height: 1.4rem;
                margin-bottom: 0.2rem;
            }

            .scenario-note {
                font-size: 0.75rem;
                line-height: 1.3;
                margin-top: 0.2rem;
            }

            .scenario-note.secondary {
                color: #6b7280;
            }

            .scenario-label-strip {
                display: flex;
                gap: 0.6rem;
                flex-wrap: wrap;
                margin-top: 0.35rem;
                margin-bottom: 0.8rem;
            }

            .scenario-strip-label {
                font-size: 0.75rem;
                font-weight: 700;
                color: #4b5563;
                border: 1px dashed rgba(128,128,128,0.22);
                border-radius: 999px;
                padding: 0.25rem 0.55rem;
            }

            .policy-response-box {
                border: 1px solid rgba(128,128,128,0.16);
                border-radius: 14px;
                padding: 0.75rem;
                min-height: 120px;
            }

            .policy-response-title {
                font-size: 0.86rem;
                font-weight: 800;
                margin-bottom: 0.25rem;
            }

            .policy-response-text {
                font-size: 0.77rem;
                color: #4b5563;
                line-height: 1.3;
            }

            .policy-metric-row,
            .stat-panel-row {
                display: flex;
                justify-content: space-between;
                gap: 0.6rem;
                margin-top: 0.35rem;
                font-size: 0.80rem;
            }

            .policy-metric-label,
            .stat-panel-label {
                color: #4b5563;
            }

            .policy-metric-value,
            .stat-panel-value {
                font-weight: 800;
            }

            .header-controls-card {
                border: 1px solid rgba(128, 128, 128, 0.16);
                border-radius: 14px;
                padding: 0.7rem 0.8rem;
                font-size: 0.82rem;
                line-height: 1.35;
            }

            .empty-chart-note {
                font-size: 0.75rem;
                color: #9ca3af;
                padding: 0.4rem 0.2rem 0.2rem 0.2rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
