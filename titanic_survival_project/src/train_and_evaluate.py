import os
import joblib
from pprint import pprint

try:
    from .data_processing import load_data, prepare_X_y
    from .pipeline import build_preprocessor, get_models, evaluate_models
except Exception:
    from titanic_survival_project.src.data_processing import load_data, prepare_X_y
    from titanic_survival_project.src.pipeline import build_preprocessor, get_models, evaluate_models


def _project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def main(data_path=None):
    df = load_data(data_path)
    X, y = prepare_X_y(df)

    numeric_features = ['Age', 'Fare', 'FamilySize', 'SharedTicketCount', 'NormalizedFare', 'FamilyCohesion']
    categorical_features = ['Pclass', 'Sex', 'Embarked', 'HonorificCode', 'IsAlone', 'CabinFlag']

    preprocessor = build_preprocessor(numeric_features, categorical_features, with_novel=True)
    models = get_models()

    print('Evaluating models with cross-validation...')
    results = evaluate_models(X, y, preprocessor, models)
    pprint(results)

    best_name = max(results.keys(), key=lambda n: results[n]['f1'])
    print('\nBest model by CV f1:', best_name)

    from sklearn.pipeline import Pipeline
    best_clf = models[best_name]
    pipeline = Pipeline(steps=[('pre', preprocessor), ('clf', best_clf)])
    pipeline.fit(X, y)

    models_dir = os.path.join(_project_root(), 'models')
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, f'{best_name}_pipeline.joblib')
    joblib.dump(pipeline, model_path)
    print('Saved best pipeline to', model_path)


if __name__ == '__main__':
    main()
