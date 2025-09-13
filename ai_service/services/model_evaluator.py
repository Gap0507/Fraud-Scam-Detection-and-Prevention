"""
Model Evaluator for SMS Scam Detection
Provides comprehensive evaluation metrics and testing capabilities
"""

import asyncio
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import logging

from services.sms_analyzer import SMSAnalyzer
from services.data_simulator import DataSimulator
from models.schemas import TestResult, EvaluationMetrics, ModelEvaluation

logger = logging.getLogger(__name__)

class ModelEvaluator:
    """Model evaluation and testing framework"""
    
    def __init__(self):
        self.sms_analyzer = None
        self.data_simulator = DataSimulator()
        self.evaluation_results = {}
    
    async def initialize(self):
        """Initialize the evaluator"""
        self.sms_analyzer = SMSAnalyzer()
        await self.sms_analyzer.initialize()
        logger.info("Model Evaluator initialized")
    
    async def evaluate_model(self, test_data: List[Dict[str, Any]], 
                           model_name: str = "SMS Analyzer") -> ModelEvaluation:
        """
        Evaluate model performance on test data
        Args:
            test_data: List of test messages with labels
            model_name: Name of the model being evaluated
        Returns:
            ModelEvaluation object with comprehensive results
        """
        logger.info(f"Starting evaluation of {model_name} on {len(test_data)} test samples")
        
        start_time = time.time()
        test_results = []
        
        # Run predictions on test data
        for i, item in enumerate(test_data):
            try:
                # Get prediction
                result = await self.sms_analyzer.analyze_sms(
                    item["message"], 
                    item.get("sender", "555-0123")
                )
                
                # Create test result
                test_result = TestResult(
                    message=item["message"],
                    expected_label=item["is_scam"],
                    predicted_label=result["is_scam"],
                    confidence=result["confidence"],
                    is_correct=result["is_scam"] == item["is_scam"],
                    risk_score=result["risk_score"],
                    triggers=result["triggers"]
                )
                
                test_results.append(test_result)
                
                # Log progress
                if (i + 1) % 100 == 0:
                    logger.info(f"Processed {i + 1}/{len(test_data)} samples")
                    
            except Exception as e:
                logger.error(f"Error processing sample {i}: {str(e)}")
                continue
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate metrics
        metrics = self._calculate_metrics(test_results)
        
        # Create evaluation object
        evaluation = ModelEvaluation(
            model_name=model_name,
            dataset_name="SMS Test Dataset",
            test_results=test_results,
            metrics=metrics,
            evaluation_timestamp=datetime.utcnow().isoformat(),
            total_test_time=total_time
        )
        
        logger.info(f"Evaluation completed in {total_time:.2f} seconds")
        logger.info(f"Accuracy: {metrics.accuracy:.4f}")
        logger.info(f"Precision: {metrics.precision:.4f}")
        logger.info(f"Recall: {metrics.recall:.4f}")
        logger.info(f"F1 Score: {metrics.f1_score:.4f}")
        
        return evaluation
    
    def _calculate_metrics(self, test_results: List[TestResult]) -> EvaluationMetrics:
        """Calculate evaluation metrics"""
        # Extract labels and predictions
        y_true = [result.expected_label for result in test_results]
        y_pred = [result.predicted_label for result in test_results]
        
        # Calculate basic metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        # Calculate confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # Calculate false positive and false negative rates
        tn, fp, fn, tp = cm.ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
        
        # Generate classification report
        class_report = classification_report(y_true, y_pred, output_dict=True)
        
        return EvaluationMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            false_positive_rate=fpr,
            false_negative_rate=fnr,
            confusion_matrix=cm.tolist(),
            classification_report=class_report
        )
    
    async def cross_validate(self, dataset: List[Dict[str, Any]], 
                           k_folds: int = 5) -> Dict[str, Any]:
        """
        Perform k-fold cross validation
        Args:
            dataset: Full dataset for cross validation
            k_folds: Number of folds
        Returns:
            Cross validation results
        """
        logger.info(f"Starting {k_folds}-fold cross validation")
        
        # Shuffle dataset
        import random
        random.shuffle(dataset)
        
        fold_size = len(dataset) // k_folds
        fold_results = []
        
        for fold in range(k_folds):
            logger.info(f"Processing fold {fold + 1}/{k_folds}")
            
            # Split data
            start_idx = fold * fold_size
            end_idx = start_idx + fold_size if fold < k_folds - 1 else len(dataset)
            
            test_fold = dataset[start_idx:end_idx]
            train_fold = dataset[:start_idx] + dataset[end_idx:]
            
            # Evaluate on test fold
            evaluation = await self.evaluate_model(test_fold, f"Fold {fold + 1}")
            fold_results.append(evaluation)
        
        # Calculate average metrics
        avg_metrics = self._calculate_average_metrics(fold_results)
        
        return {
            "k_folds": k_folds,
            "fold_results": fold_results,
            "average_metrics": avg_metrics,
            "std_metrics": self._calculate_std_metrics(fold_results)
        }
    
    def _calculate_average_metrics(self, fold_results: List[ModelEvaluation]) -> Dict[str, float]:
        """Calculate average metrics across folds"""
        metrics = ["accuracy", "precision", "recall", "f1_score", "false_positive_rate", "false_negative_rate"]
        
        avg_metrics = {}
        for metric in metrics:
            values = [getattr(fold.metrics, metric) for fold in fold_results]
            avg_metrics[metric] = np.mean(values)
        
        return avg_metrics
    
    def _calculate_std_metrics(self, fold_results: List[ModelEvaluation]) -> Dict[str, float]:
        """Calculate standard deviation of metrics across folds"""
        metrics = ["accuracy", "precision", "recall", "f1_score", "false_positive_rate", "false_negative_rate"]
        
        std_metrics = {}
        for metric in metrics:
            values = [getattr(fold.metrics, metric) for fold in fold_results]
            std_metrics[metric] = np.std(values)
        
        return std_metrics
    
    async def benchmark_performance(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Benchmark model performance
        Args:
            test_data: Test dataset
        Returns:
            Performance benchmarks
        """
        logger.info("Starting performance benchmark")
        
        # Test different batch sizes
        batch_sizes = [1, 5, 10, 20, 50]
        performance_results = {}
        
        for batch_size in batch_sizes:
            logger.info(f"Testing batch size: {batch_size}")
            
            # Create batches
            batches = [test_data[i:i + batch_size] for i in range(0, len(test_data), batch_size)]
            
            total_time = 0
            total_accuracy = 0
            batch_count = 0
            
            for batch in batches:
                start_time = time.time()
                
                # Process batch
                batch_results = []
                for item in batch:
                    result = await self.sms_analyzer.analyze_sms(item["message"], item.get("sender", "555-0123"))
                    batch_results.append(result)
                
                end_time = time.time()
                batch_time = end_time - start_time
                total_time += batch_time
                
                # Calculate accuracy for this batch
                correct = sum(1 for i, result in enumerate(batch_results) 
                            if result["is_scam"] == batch[i]["is_scam"])
                batch_accuracy = correct / len(batch) if batch else 0
                total_accuracy += batch_accuracy
                batch_count += 1
            
            # Calculate averages
            avg_time_per_batch = total_time / batch_count if batch_count > 0 else 0
            avg_accuracy = total_accuracy / batch_count if batch_count > 0 else 0
            avg_time_per_message = avg_time_per_batch / batch_size if batch_size > 0 else 0
            
            performance_results[batch_size] = {
                "avg_time_per_batch": avg_time_per_batch,
                "avg_time_per_message": avg_time_per_message,
                "avg_accuracy": avg_accuracy,
                "total_batches": batch_count
            }
        
        return performance_results
    
    async def generate_evaluation_report(self, evaluation: ModelEvaluation) -> str:
        """
        Generate a comprehensive evaluation report
        Args:
            evaluation: Model evaluation results
        Returns:
            Formatted evaluation report
        """
        report = f"""
# Model Evaluation Report

## Model Information
- **Model Name**: {evaluation.model_name}
- **Dataset**: {evaluation.dataset_name}
- **Evaluation Date**: {evaluation.evaluation_timestamp}
- **Total Test Time**: {evaluation.total_test_time:.2f} seconds

## Performance Metrics
- **Accuracy**: {evaluation.metrics.accuracy:.4f}
- **Precision**: {evaluation.metrics.precision:.4f}
- **Recall**: {evaluation.metrics.recall:.4f}
- **F1 Score**: {evaluation.metrics.f1_score:.4f}
- **False Positive Rate**: {evaluation.metrics.false_positive_rate:.4f}
- **False Negative Rate**: {evaluation.metrics.false_negative_rate:.4f}

## Confusion Matrix
```
                Predicted
Actual    False  True
False     {evaluation.metrics.confusion_matrix[0][0]:4d}  {evaluation.metrics.confusion_matrix[0][1]:4d}
True      {evaluation.metrics.confusion_matrix[1][0]:4d}  {evaluation.metrics.confusion_matrix[1][1]:4d}
```

## Detailed Classification Report
```
{evaluation.metrics.classification_report}
```

## Sample Results
"""
        
        # Add sample results
        correct_predictions = [r for r in evaluation.test_results if r.is_correct]
        incorrect_predictions = [r for r in evaluation.test_results if not r.is_correct]
        
        report += f"\n### Correct Predictions (Sample of 5)\n"
        for i, result in enumerate(correct_predictions[:5]):
            report += f"{i+1}. **Message**: {result.message[:100]}...\n"
            report += f"   **Expected**: {'Scam' if result.expected_label else 'Legitimate'}\n"
            report += f"   **Predicted**: {'Scam' if result.predicted_label else 'Legitimate'}\n"
            report += f"   **Confidence**: {result.confidence:.4f}\n"
            report += f"   **Risk Score**: {result.risk_score:.4f}\n\n"
        
        report += f"\n### Incorrect Predictions (Sample of 5)\n"
        for i, result in enumerate(incorrect_predictions[:5]):
            report += f"{i+1}. **Message**: {result.message[:100]}...\n"
            report += f"   **Expected**: {'Scam' if result.expected_label else 'Legitimate'}\n"
            report += f"   **Predicted**: {'Scam' if result.predicted_label else 'Legitimate'}\n"
            report += f"   **Confidence**: {result.confidence:.4f}\n"
            report += f"   **Risk Score**: {result.risk_score:.4f}\n\n"
        
        return report
    
    async def save_evaluation_results(self, evaluation: ModelEvaluation, filename: str):
        """Save evaluation results to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(evaluation.dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"Evaluation results saved to {filename}")
    
    async def load_evaluation_results(self, filename: str) -> ModelEvaluation:
        """Load evaluation results from file"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return ModelEvaluation(**data)
