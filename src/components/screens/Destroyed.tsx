interface DestroyedProps {
  onBackToDeployments?: () => void;
}

export function Destroyed({ onBackToDeployments }: DestroyedProps) {
  return (
    <div>
      <div className="done-header">
        <span className="destroyed-badge" aria-hidden="true" />
        <h2>Deployment zrušen</h2>
      </div>
      <p className="status-text">Infrastruktura byla odstraněna.</p>
      {onBackToDeployments && (
        <button className="back-to-deployments-btn" onClick={onBackToDeployments}>Zpět na seznam</button>
      )}
    </div>
  );
}
