import numpy as np
from sklearn.metrics import root_mean_squared_error, mean_absolute_percentage_error, r2_score, accuracy_score, \
    precision_score, recall_score, f1_score


def available_evaluation_metrics() -> dict:
    """
    Get a dictionary of available evaluation metrics with their descriptions.

    Returns:
        metrics: Dictionary with evaluation metrics as keys and their descriptions as values
    """
    metrics = {
        'rmse': 'Root Mean Squared Error (RMSE)',
        'mape': 'Mean Absolute Percentage Error (MAPE)',
        'r2_score': 'R-squared Score (R2 Score)',
        'information_ratio': 'Information Ratio (IR)',
        'accuracy': 'Accuracy',
        'precision': 'Precision',
        'recall': 'Recall',
        'f1_score': 'F1 Score'
    }
    return metrics


def accumulative_returns(returns) -> list:
    """
    Calculate the accumulative returns.

    Arguments:
        returns: Returns

    Returns:
        accumulative_returns: Accumulative returns
    """
    return np.cumprod(1 + np.array(returns)) - 1


def information_ratio(strategy_returns, benchmark_returns=None) -> float:
    """
    Calculate the Information Ratio (IR).

    Arguments:
        strategy_returns: Strategy returns
        benchmark_returns: Benchmark returns

    Returns:
        IR: Information Ratio (IR)
    """
    if benchmark_returns is None:
        benchmark_returns = np.zeros(len(strategy_returns))

    return ((np.mean(strategy_returns) - np.mean(benchmark_returns)) / np.std(strategy_returns)) if np.std(
        strategy_returns) != 0 else 0


def generate_scores_from_returns(true_returns, predicted_returns) -> dict:
    """
    Generate scores from true and predicted returns.

    Arguments:
        true_returns: True returns
        predicted_returns: Predicted returns

    Returns:
        scores: Dictionary with scores for the specified metrics
    """

    true_labels = [1 if val > 0 else 0 for val in true_returns]
    predicted_labels = [1 if val > 0 else 0 for val in predicted_returns]

    strategy_returns = np.array(true_returns) * np.array(predicted_labels)
    scores = {}
    available_metrics = available_evaluation_metrics()
    for metric in available_metrics:
        if metric == 'rmse':
            scores[metric] = root_mean_squared_error(true_returns, predicted_returns)
        elif metric == 'mape':
            scores[metric] = mean_absolute_percentage_error(true_returns, predicted_returns)
        elif metric == 'r2_score':
            scores[metric] = r2_score(true_returns, predicted_returns)
        elif metric == 'information_ratio':
            scores[metric] = information_ratio(strategy_returns)
        elif metric == 'accuracy':
            scores[metric] = accuracy_score(true_labels, predicted_labels)
        elif metric == 'precision':
            scores[metric] = precision_score(true_labels, predicted_labels, zero_division=0)
        elif metric == 'recall':
            scores[metric] = recall_score(true_labels, predicted_labels, zero_division=0)
        elif metric == 'f1_score':
            scores[metric] = f1_score(true_labels, predicted_labels, zero_division=0)

    return scores
