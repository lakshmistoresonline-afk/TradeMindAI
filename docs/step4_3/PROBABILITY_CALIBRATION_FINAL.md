# Step 4.3.1 Probability Calibration Final

## Calibration Metrics
- **Brier Score**: 0.2709
- **Log Loss**: 0.7378

## Reliability Analysis
|   Mean Predicted Value |   Fraction of Positives |
|-----------------------:|------------------------:|
|               0.55992  |                0.489939 |
|               0.649769 |                0.491777 |
|               0.71499  |                0.498775 |

## Conclusion
The model demonstrates a systematic over-confidence or lack of calibration, as the realized win rate remains around 49-50% regardless of the predicted probability (which ranges from 0.52 to 0.80+). This suggests the model output is better suited as a **ranking score** rather than a true probability.

> [!IMPORTANT]
> The current threshold of 0.52 is effectively a ranking filter. Future optimization should prioritize **Isotonic Regression** or **Platt Scaling** to align predicted probabilities with actual outcomes.
