import { useState } from 'react';
import { DeploymentForm } from './components/DeploymentForm';
import { JobStatusView } from './components/JobStatusView';
import { DeploymentList } from './components/screens/DeploymentList';

function App() {
  const [jobId, setJobId] = useState<string | null>(null);

  function handleBackToDeployments() {
    setJobId(null);
  }

  if (jobId !== null) {
    return <JobStatusView jobId={jobId} onBackToDeployments={handleBackToDeployments} />;
  }

  return (
    <div className="app-shell">
      <DeploymentForm onJobCreated={setJobId} />
      <DeploymentList onSelectJob={setJobId} />
    </div>
  );
}

export default App
