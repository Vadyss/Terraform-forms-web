interface ErrorScreenProps {
  error: string;
  onBackToDeployments?: () => void;
}

export function ErrorScreen({ error, onBackToDeployments }: ErrorScreenProps) {
  return (
    <div className="card">
      <div className="error-header">
        <span className="error-icon" aria-hidden="true" />
        <h2>Deployment selhal</h2>
      </div>
      <p className="error-box">{error}</p>
      {onBackToDeployments && (
        <button className="back-to-deployments-btn" onClick={onBackToDeployments}>Zpět na seznam</button>
      )}
    </div>
  );
}
