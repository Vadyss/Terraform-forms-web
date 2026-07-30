/*import type { DeploymentConfig, ValidationErrors } from "../../types";
import { Toggle } from "../Toggle";
import { Select } from "../Select";

interface NetworkSectionProps {
  value: DeploymentConfig['networks'];
  onChange: (updates: Partial<DeploymentConfig['networks']>) => void;
  errors?: ValidationErrors['networks'];
}

const ipConfigOptions = [
  { value: 'dhcp', label: 'DHCP' },
  { value: 'static', label: 'Statická' },
];

export function NetworkSection({ value, onChange, errors }: NetworkSectionProps) {
    return (
        <div className="form-section">
            <h3>Sítě</h3>

            <Toggle
            checked={value.lan}
            onChange={(v) => onChange({ lan: v })}
            label="LAN"
            />

            {value.lan && (
            <div className="form-subsection">
                <div className="form-group">
                    <label>IP adresa LAN</label>
                    <input
                    value={value.lanIp}
                    onChange={(e) => onChange({ lanIp: e.target.value })}
                    />
                    {errors?.lanIp && <span className="field-error">{errors.lanIp}</span>}
                </div>
            </div>
            )}

            <Select
            label="IP konfigurace"
            value={value.ipConfig}
            options={ipConfigOptions}
            onChange={(v) => onChange({ ipConfig: v as 'dhcp' | 'static' })}
            />

            {value.ipConfig === 'static' && (
            <div className="form-subsection">
                <div className="form-group">
                    <label>Statická IP</label>
                    <input
                    value={value.staticIp}
                    onChange={(e) => onChange({ staticIp: e.target.value })}
                    />
                    {errors?.staticIp && <span className="field-error">{errors.staticIp}</span>}
                </div>
            </div>
            )}
        </div>
    );
}
    */