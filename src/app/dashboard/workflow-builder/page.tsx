'use client';

import IntelligentWorkflowBuilder from '@/components/IntelligentWorkflowBuilder';

export default function WorkflowBuilderPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="py-8">
        <IntelligentWorkflowBuilder />
      </div>
    </div>
  );
}
