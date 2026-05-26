# Test-Claude

<p align="center">
  <b>Claude Skill & SPSS Modeler Automation Toolkit</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/IBM%20SPSS%20Modeler-18.5-blue" alt="IBM SPSS Modeler 18.5">
  <img src="https://img.shields.io/badge/Python-Modeler%20API-yellow" alt="Python Modeler API">
  <img src="https://img.shields.io/badge/CLEM-SPSS%20Expressions-green" alt="CLEM">
  <img src="https://img.shields.io/badge/Claude-Skills-purple" alt="Claude Skills">
</p>

---

## Overview

**Test-Claude** is a practical repository for building Claude skills and reusable Python examples for **IBM SPSS Modeler**.

The purpose of this project is to help Claude work more effectively as a data science assistant inside SPSS Modeler by providing structured documentation, verified syntax examples, reusable stream patterns, and Python automation scripts.

This repository focuses on:

- data preparation
- customer segmentation
- predictive modeling
- SPSS Modeler stream automation
- CLEM expression examples
- reusable Claude skill documentation

---

## Project Purpose

This repository is designed to support data scientists, analysts, and AI assistants working with IBM SPSS Modeler.

It helps Claude understand how to generate, review, and troubleshoot SPSS Modeler streams using Python scripting and CLEM expressions.

The Markdown files act as Claude skill/reference documents, while the Python files provide practical stream-building examples.

---

## Repository Contents

| File | Description |
|---|---|
| `01.transactions.py` | Python example for preparing retail transaction data and creating customer-level KPIs |
| `02.transactions-segmentation.py` | Python example for customer segmentation using transaction behavior and K-Means clustering |
| `03.predictive-modeling.py` | Python example for predictive modeling, including mobile churn target creation and CHAID modeling |
| `Clem-expressions.md` | Reference guide for CLEM expressions used in SPSS Modeler |
| `Merge+Append.md` | Documentation for merge and append node patterns |
| `Nodes-types.md` | Reference notes for SPSS Modeler node types and verified rules |
| `Stream-parameters.md` | Guide for stream parameters in SPSS Modeler |
| `Stream-patterns.md` | Reusable patterns for building SPSS Modeler streams |

---

## Main Features

### Data Preparation

The repository includes examples for building data preparation streams, including:

- loading source data
- filtering valid records
- handling missing values
- deriving new fields
- creating date-based features
- aggregating transaction data
- creating customer-level KPIs

### Customer Segmentation

The segmentation example demonstrates how to prepare customer data for clustering and profiling.

It includes:

- customer behavior aggregation
- active customer filtering
- K-Means clustering setup
- cluster profiling
- comparison with overall averages

### Predictive Modeling

The predictive modeling example demonstrates a churn modeling workflow.

It includes:

- observation-window logic
- churn-label creation
- database source usage
- merge logic for target creation
- CHAID model setup
- model evaluation using gains analysis

### Claude Skill Documentation

The Markdown files are intended to be used as structured references for Claude.

They help Claude generate more accurate SPSS Modeler scripts by documenting:

- verified syntax
- node patterns
- CLEM examples
- merge and append behavior
- stream parameter usage
- common stream design patterns

---

## Technology Stack

| Technology | Purpose |
|---|---|
| IBM SPSS Modeler | Visual data mining and machine learning platform |
| Python | Stream scripting and automation |
| Modeler API | Programmatic creation of SPSS Modeler nodes and streams |
| CLEM | Expression language used inside SPSS Modeler |
| Markdown | Documentation and Claude skill reference files |
| Claude | AI assistant used for generating and improving SPSS Modeler workflows |

---

## How to Use This Repository

### 1. Clone the repository

```bash
git clone https://github.com/evinampk/Test-Claude.git
