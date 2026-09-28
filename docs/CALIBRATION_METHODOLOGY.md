# TradeMind AI — Probability Calibration Methodology

---

## 1. Calibration Framework

Raw machine learning model outputs (from ExtraTrees, GradientBoosting, or Neural Networks) often produce uncalibrated probability scores. TradeMindAI enforces **Venn-Abers Multiprobability Calibration** and **Inductive Conformal Prediction**.

---

## 2. Calibration Metrics

For every model deployment, probability outputs are evaluated using:
* **Brier Score**:
  $$\text{BS} = \frac{1}{N} \sum_{t=1}^N (f_t - y_t)^2$$
* **Log Loss**:
  $$\text{LogLoss} = -\frac{1}{N} \sum_{t=1}^N \left[ y_t \log f_t + (1 - y_t) \log(1 - f_t) \right]$$
* **Expected Calibration Error (ECE)**:
  $$\text{ECE} = \sum_{b=1}^M \frac{|B_b|}{N} | \text{acc}(B_b) - \text{conf}(B_b) |$$

---

## 3. Venn-Abers Lower-Bound Threshold

Signals classified as `PRIMARY` require a lower-bound Venn-Abers calibrated probability $p_{\text{lower}} \ge 0.70$, guaranteeing that published confidence levels are mathematically bounded against over-confidence.
