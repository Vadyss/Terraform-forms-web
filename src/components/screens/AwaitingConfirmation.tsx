import type { JobPlan } from '../../types';

interface AwaitingConfirmationProps {
  plan: JobPlan;
  onConfirm: () => void;
}

function rizikaLabel(count: number): string {
  if (count === 1) return 'riziko';
  if (count >= 2 && count <= 4) return 'rizika';
  return 'rizik';
}

export function AwaitingConfirmation({ plan, onConfirm }: AwaitingConfirmationProps) {
  return (
    <div className="confirmation-panel">
      <h2>Plán</h2>
      <p>{plan.summary}</p>
      <div className="risk-header">
        <h3>Rizika</h3>
        <span className="risk-count">{plan.risks.length} {rizikaLabel(plan.risks.length)}</span>
      </div>
      <ul className="risk-list">
        {plan.risks.map((risk) => (
          <li className="risk-item" key={risk}>{risk}</li>
        ))}
      </ul>
      <button onClick={onConfirm}>Potvrdit</button>
    </div>
  );
}
