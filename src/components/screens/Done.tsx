import type { JobOutputs } from '../../types';

interface DoneProps {
  outputs: JobOutputs;
  onBackToDeployments?: () => void;
}

export function Done({ outputs, onBackToDeployments }: DoneProps) {
  return (
    <div>
      <div className="done-header">
        <span className="success-badge" aria-hidden="true" />
        <h2>Deployment dokončen</h2>
      </div>
      <div>
        <p className="output-label">IP</p>
        <div className="output-block">{outputs.ip}</div>
      </div>
      <div>
        <p className="output-label">ID prostředku</p>
        <div className="output-block">{outputs.resourceId}</div>
      </div>
      {onBackToDeployments && (
        <button className="back-to-deployments-btn" onClick={onBackToDeployments}>Zpět na seznam</button>
      )}
    </div>
  );
}
