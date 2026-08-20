import type { DeploymentConfig, ValidationErrors } from "../../types";
import { Select } from "../Select";
import { useOptions } from "../../hooks/useOptions";

interface VirtualMachineSectionProps {
  value: DeploymentConfig['virtualMachine'];
  onChange: (updates: Partial<DeploymentConfig['virtualMachine']>) => void;
  errors?: ValidationErrors['virtualMachine'];
}

export function VirtualMachineSection({ value, onChange, errors }: VirtualMachineSectionProps) {
  const { options, isLoading, isError } = useOptions();

  if (isLoading) return <p>Načítání možností…</p>;
  if (isError || !options) return <p>Nepodařilo se načíst možnosti</p>;

  return (
    <div className="form-section">
      <h3>Virtuální stroje</h3>

      <div className="form-group">
        <label>Název</label>
        <input
          value={value.name}
          onChange={(e) => onChange({ name: e.target.value })}
        />
        {errors?.name && <span className="field-error">{errors.name}</span>}
      </div>

      <Select
        label="Operační systém"
        value={value.os}
        options={options.operatingSystems}
        onChange={(v) => onChange({ os: v })}
      />
      {errors?.os && <span className="field-error">{errors.os}</span>}

      <div className="form-row form-row-3">
        <Select
          label="CPU"
          value={value.cpu}
          options={options.cpuOptions}
          onChange={(v) => onChange({ cpu: Number(v) })}
        />

        <Select
          label="RAM"
          value={value.ram}
          options={options.ramOptions}
          onChange={(v) => onChange({ ram: Number(v) })}
        />

        <Select
          label="Disk"
          value={value.disk}
          options={options.diskOptions}
          onChange={(v) => onChange({ disk: Number(v) })}
        />
      </div>

      <div className="form-group">
        <label>SSH klíč</label>
        <input
          value={value.sshkey}
          onChange={(e) => onChange({ sshkey: e.target.value })}
        />
        {errors?.sshkey && <span className="field-error">{errors.sshkey}</span>}
      </div>
    </div>
  );
}