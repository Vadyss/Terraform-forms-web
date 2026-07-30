/*import type { DeploymentConfig, ValidationErrors } from "../../types";
import { Toggle } from "../Toggle";

interface NetworkConnectionSectionProps {
  value: DeploymentConfig['networkConnection'];
  onChange: (updates: Partial<DeploymentConfig['networkConnection']>) => void;
  errors?: ValidationErrors['networkConnection'];
}

export function NetworkConnectionSection({ value, onChange, errors }: NetworkConnectionSectionProps) {
  return (
    <div className="form-section">
      <h3>Síťové připojení</h3>

        <div className="form-row">
            <div className="form-group">
                <label>Název</label>
                <input
                    value={value.name}
                    onChange={(e) => onChange({ name: e.target.value })}
                />
                {errors?.name && <span className="field-error">{errors.name}</span>}
            </div>

            <div className="form-group">
                <label>Subnet</label>
                <input
                    value={value.subnet}
                    onChange={(e) => onChange({ subnet: e.target.value })}
                />
                {errors?.subnet && <span className="field-error">{errors.subnet}</span>}
            </div>
        </div>

        <div className="form-row">
            <Toggle
                checked={value.portSecurity}
                onChange={(v) => onChange({ portSecurity: v })}
                label="Port security"
            />

            <Toggle
                checked={value.internet}
                onChange={(v) => onChange({ internet: v })}
                label="Připojení k internetu"
            />
        </div>
    </div>
  );
}
  */