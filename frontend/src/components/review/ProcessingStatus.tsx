import * as React from 'react';
import { PipelineProgress } from './PipelineProgress';

interface ProcessingStatusProps {
  status: 'idle' | 'processing' | 'success' | 'error';
  currentStep: number;
}

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  status,
  currentStep,
}) => {
  return <PipelineProgress status={status} currentStep={currentStep} />;
};
