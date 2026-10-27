import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.ml.ablation_study import AblationStudyService

if __name__ == '__main__':
    print("=" * 70)
    print("MOIL MANGANESE INTELLIGENCE: SATELLITE & WEATHER ABLATION STUDY")
    print("=" * 70)
    results = AblationStudyService.run_ablation_study()
    print(f"\nStudy Summary:")
    print(results["summary_conclusion"])
    print("\nModel Comparison on Chronological Out-of-Time Test Set:")
    for m in results["model_comparison"]:
        print(f" - {m['model_name']}: Overall MAE={m['overall_mae']} t | Monsoon MAE={m['monsoon_mae']} t | WAPE={m['overall_wape_pct']}%")
    print("\nTop Predictive Features:")
    for f in results["feature_importances"][:6]:
        print(f" - {f['label']} ({f['category']}): {f['importance_pct']}%")
    print(f"\nMonsoon Accuracy Gain: +{results['monsoon_accuracy_gain']['mae_gain_tonnes']} t/day (+{results['monsoon_accuracy_gain']['mae_gain_pct']}%)")
    print("=" * 70)
