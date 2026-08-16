import { DataProvenance } from '../types/domain';

export interface MetricMetadata {
  id: string;
  label: string;
  unit: string;
  provenance: DataProvenance;
  description: string;
  formula?: string;
  validation?: (val: any) => boolean;
  formatter?: (val: any) => string;
}

export const MetricRegistry: Record<string, MetricMetadata> = {
  price: {
    id: 'price',
    label: 'Market Price',
    unit: '₹',
    provenance: 'LIVE',
    description: 'Latest traded price on the exchange.',
    validation: (v) => typeof v === 'number' && v > 0,
    formatter: (v) => v !== null && v !== undefined && !isNaN(v) ? `₹${v.toLocaleString()}` : '---'
  },
  conviction: {
    id: 'conviction',
    label: 'AI Conviction',
    unit: '%',
    provenance: 'AI GENERATED',
    description: 'Confidence level of the multi-agent consensus.',
    formula: 'Weighted average of 12 analytical agents.',
    validation: (v) => typeof v === 'number' && v >= 0 && v <= 100,
    formatter: (v) => v !== null && v !== undefined && !isNaN(v) ? `${Math.round(v)}%` : '---'
  },
  beta: {
    id: 'beta',
    label: 'Beta (1Y)',
    unit: '',
    provenance: 'CALCULATED',
    description: 'Sensitivity of asset returns compared to Nifty 50.',
    formula: 'Covariance(Asset, Market) / Variance(Market)',
    validation: (v) => typeof v === 'number',
    formatter: (v) => v !== null && v !== undefined && !isNaN(v) ? v.toFixed(2) : '---'
  },
  pcr: {
    id: 'pcr',
    label: 'Put-Call Ratio (OI)',
    unit: '',
    provenance: 'LIVE',
    description: 'Ratio of Put open interest to Call open interest.',
    formula: 'Total Put OI / Total Call OI',
    validation: (v) => typeof v === 'number' && v >= 0,
    formatter: (v) => v !== null && v !== undefined && !isNaN(v) ? v.toFixed(2) : '---'
  },
  sharpe: {
    id: 'sharpe',
    label: 'Sharpe Ratio',
    unit: '',
    provenance: 'CALCULATED',
    description: 'Risk-adjusted return relative to risk-free rate.',
    formula: '(Avg Return - RF) / Std Dev',
    validation: (v) => typeof v === 'number',
    formatter: (v) => v !== null && v !== undefined && !isNaN(v) ? v.toFixed(2) : '---'
  }
};

export const validateMetric = (id: string, value: any): { isValid: boolean; error?: string } => {
  const metric = MetricRegistry[id];
  if (!metric) return { isValid: true };

  if (value === null || value === undefined) return { isValid: false, error: 'Missing Data' };
  if (metric.validation && !metric.validation(value)) return { isValid: false, error: 'Invalid Value' };

  return { isValid: true };
};

export const formatMetric = (id: string, value: any): string => {
  const metric = MetricRegistry[id];
  if (!metric || value === null || value === undefined || (typeof value === 'number' && isNaN(value))) {
    return '---';
  }
  return metric.formatter ? metric.formatter(value) : String(value);
};
