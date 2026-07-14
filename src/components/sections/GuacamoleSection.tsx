import type { DeploymentConfig, ValidationErrors } from "../../types";
import { useOptions } from "../../hooks/useOptions";
import { Toggle } from "../Toggle";
import { Select } from "../Select";

interface GuacamoleSectionProps {
    value: DeploymentConfig["guacamole"]
    onChange: (updates: Partial<DeploymentConfig['guacamole']>) => void;
    errors?: ValidationErrors['guacamole'];
}

export function GuacamoleSection({ value, onChange, errors }: GuacamoleSectionProps) {
  const { options, isLoading, isError } = useOptions();

  if (isLoading) return <p>Načítání možností…</p>;
  if (isError || !options) return <p>Nepodařilo se načíst možnosti</p>;

  return (
    <div className="form-section">
      <h3>Guacamole</h3>

      <Toggle
        checked={value.enabled}
        onChange={(e) => onChange({ enabled: e })}
        label="Povolit Guacamole"
      />

      {value.enabled && (
        <div className="form-subsection">
            <div className="form-row form-row-3">
                <div className="form-group">
                    <Select
                    label="Operační systém"
                    value={value.os}
                    options={options.operatingSystems}
                    onChange={(v) => onChange({ os: v })}
                    />
                    {errors?.os && <span className="field-error">{errors.os}</span>}
                </div>

                <div className="form-group">
                    <Select
                    label="Typ prostředí"
                    value={value.type}
                    options={options.environmentTypes}
                    onChange={(v) => onChange({ type: v })}
                    />
                    {errors?.type && <span className="field-error">{errors.type}</span>}
                </div>

                <div className="form-group">
                    <Select
                    label="Rozložení klávesnice"
                    value={value.keyboardLayout}
                    options={options.keyboardLayouts}
                    onChange={(v) => onChange({ keyboardLayout: v })}
                    />
                    {errors?.keyboardLayout && <span className="field-error">{errors.keyboardLayout}</span>}
                </div>
            </div>

            <div className="form-row">
                <div className="form-group">
                <label>Uživatelské jméno</label>
                <input
                    value={value.username}
                    onChange={(e) => onChange({ username: e.target.value })}
                />
                {errors?.username && <span className="field-error">{errors.username}</span>}
                </div>

                <div className="form-group">
                <label>Heslo</label>
                <input
                    type="password"
                    value={value.password}
                    onChange={(e) => onChange({ password: e.target.value })}
                />
                {errors?.password && <span className="field-error">{errors.password}</span>}
                </div>
            </div>

            <Toggle
            checked={value.sftp}
            onChange={(v) => onChange({ sftp: v })}
            label="SFTP"
            />
        </div>
      )}
    </div>
  );
}