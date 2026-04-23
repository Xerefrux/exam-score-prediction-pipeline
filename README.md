# Student Exam Score Predictor — End-to-End ML Pipeline

A production-style machine learning application that predicts a student's
mathematics score based on demographic and academic background factors.
Built with a modular MLOps pipeline architecture and deployed as a live
web application on Render.

🔗 **Live Demo:** https://exam-score-predictor-2kuh.onrender.com/predictdata

---

## What This Project Does

Given inputs like a student's gender, parental education level, lunch type,
test preparation course status, and scores in reading and writing, the app
predicts their likely mathematics score. More importantly, the project
demonstrates how to build a maintainable, production-ready ML system —
not just a one-off Jupyter notebook.

The goal was to simulate how a real data science team would structure a
project: with clearly separated pipeline stages, reusable components,
proper exception handling, logging, and a live web interface that anyone
can interact with.

---

## Architecture Overview

The project is structured as a modular pipeline with three distinct stages
that run sequentially during training, and a separate inference pipeline
that runs at prediction time.

**Stage 1 — Data Ingestion** reads the raw dataset, performs an 80/20
train-test split, and saves the resulting files to an `artifacts/` directory.
Persisting the splits ensures that the exact same data partitioning is
traceable and reproducible across runs.

**Stage 2 — Data Transformation** builds a `scikit-learn` preprocessing
pipeline using `ColumnTransformer`. Numerical features receive median
imputation (to handle missing values robustly) followed by standard
scaling. Categorical features receive most-frequent imputation, one-hot
encoding, and then standard scaling. Critically, the fitted preprocessor
object is serialized to disk as `preprocessor.pkl` so that identical
transformations are applied at inference time — a common source of
*training-serving skew* that this design avoids by design.

**Stage 3 — Model Training** trains 8 regression models in a single
automated sweep: Linear Regression, Decision Tree, Random Forest, Gradient
Boosting, XGBoost, CatBoost, K-Nearest Neighbors, and AdaBoost.
Hyperparameter tuning is performed on each using `GridSearchCV` with
5-fold cross-validation. The best-performing model by R² score on the
held-out test set is automatically selected and saved as `model.pkl`.

**Inference Pipeline** — When a user submits the web form, the app loads
the pre-trained `model.pkl` and `preprocessor.pkl` artifacts from disk,
applies the same preprocessing transformations to the new input, and
returns a predicted score — all without retraining anything.

---

## Tech Stack

- **ML & Data:** scikit-learn, XGBoost, CatBoost, pandas, NumPy
- **Web App:** Flask with Gunicorn (production WSGI server)
- **Deployment:** Render (free tier, auto-deploys from GitHub)
- **Engineering:** Custom exception handling with full traceback details,
  timestamped rotating file logger, object serialization with `dill`

---

## Key Engineering Decisions

**Modular pipeline over monolithic notebooks.** Each stage of the ML
workflow is a self-contained class with its own configuration dataclass.
This makes it straightforward to swap out components — for example,
changing the model set or adding a new preprocessing step — without
touching unrelated code.

**Automated model selection.** Rather than manually picking a model,
`GridSearchCV` evaluates all candidates systematically. The pipeline
selects the winner based on test R², making experimentation reproducible
and the selection process auditable.

**Strict separation of training and inference.** The `PredictPipeline`
class loads serialized artifacts at inference time, ensuring the production
app applies identical transformations to those used during training. This
is a critical correctness property that many beginner projects overlook.

**OS-agnostic file paths.** All file paths are constructed using
`os.path.join()` rather than hardcoded strings, ensuring the project
runs correctly on both Windows (development) and Linux (production server).

---

## Results

| Model | R² Score |
|---|---|
| Best Model (auto-selected) | **0.8804332983749565** |

The best model explains approximately **[X]%** of the variance in student
math scores on the held-out test set.

> To see which model won and view the full comparison, run the training
> pipeline locally — the model evaluation scores are printed to the
> console during training.

---

## Running Locally

```bash
# 1. Clone the repository
git clone https://github.com/Xerefrux/exam-score-prediction-pipeline.git
cd exam-score-prediction-pipeline

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the training pipeline to generate model artifacts
python src/components/data_ingestion.py

# 4. Start the Flask app
python application.py
```

Then navigate to `http://localhost:5000` in your browser and use the
prediction form.

---

## Project Structure
├── data/
│   └── stud.csv                    # Raw dataset
├── src/
│   ├── components/
│   │   ├── data_ingestion.py       # Reads, splits, and saves raw data
│   │   ├── data_transformation.py  # Builds and fits preprocessing pipeline
│   │   └── model_trainer.py        # Trains, tunes, and selects best model
│   ├── pipeline/
│   │   └── predict_pipeline.py     # Loads artifacts and runs inference
│   ├── exception.py                # Custom exception with traceback details
│   ├── logger.py                   # Timestamped rotating file logger
│   └── utils.py                    # Shared helpers: save/load objects,
│                                   # evaluate and compare models
├── templates/
│   └── home.html                   # Flask prediction form (HTML)
├── artifacts/                      # Auto-generated during training:
│   ├── model.pkl                   #   Serialized best model
│   ├── preprocessor.pkl            #   Serialized preprocessing pipeline
│   ├── train.csv                   #   Training split
│   └── test.csv                    #   Test split
├── application.py                  # Flask app entry point (WSGI)
├── Procfile                        # Render start command
└── requirements.txt                # Python dependencies

---

## Deployment

This project is deployed on **Render** using their free web service tier,
with automatic re-deployment triggered on every push to the `main` branch.

The `Procfile` at the project root instructs Render to serve the app using
Gunicorn, a production-grade WSGI server, rather than Flask's built-in
development server which is not suitable for real traffic.

> **Note:** On Render's free tier, the app spins down after 15 minutes of
> inactivity and takes approximately 30 seconds to wake up on the next
> request. This is expected behaviour for free hosting and does not affect
> functionality.

---

## Dataset

The dataset used is the [Students Performance in Exams](https://www.kaggle.com/datasets/spscientist/students-performance-in-exams)
dataset from Kaggle, containing 1,000 student records with the following
features: gender, race/ethnicity, parental level of education, lunch type,
test preparation course status, reading score, and writing score.

The prediction target is the student's **math score**.