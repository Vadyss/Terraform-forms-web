import { useState } from 'react';
import type { FormEvent } from 'react';
import { VirtualMachineSection } from './sections/VirtualMachineSection';
import type { DeploymentConfig, ValidationErrors } from '../types';

interface DeploymentFormProps {
  onJobCreated: (id: string) => void;
}

function validateConfig(config: DeploymentConfig): ValidationErrors {
  const errors: ValidationErrors = {};

  const virtualMachine: NonNullable<ValidationErrors['virtualMachine']> = {};
  if (config.virtualMachine.name.trim() === '') {
    virtualMachine.name = 'Povinné pole';
  }
  if (config.virtualMachine.os.trim() === '') {
    virtualMachine.os = 'Vyberte operační systém';
  }
  if (Object.keys(virtualMachine).length > 0) {
    errors.virtualMachine = virtualMachine;
  }

  return errors;
}

export function DeploymentForm({ onJobCreated }: DeploymentFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [config, setConfig] = useState<DeploymentConfig>({
    virtualMachine: { name: '', os: '', cpu: 2, ram: 1024, disk: 10, sshkey: '' }
  });

  function updateSection<K extends keyof DeploymentConfig>(
    section: K,
    updates: Partial<DeploymentConfig[K]>
  ) {
    setConfig(prev => ({
      ...prev,
      [section]: { ...prev[section], ...updates },
    }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const validationErrors = validateConfig(config);
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) {
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      const res = await fetch('/api/deployments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      if (!res.ok) {
        setError(res.status === 422 ? 'Neplatné hodnoty formuláře' : 'Nasazení se nepodařilo vytvořit');
        return;
      }
      const { id } = await res.json();
      onJobCreated(id);
    } catch (e) {
      setError('Nasazení selhalo, zkuste to znovu');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card card-wide">
      <div className="form-header">
        <h2>Nový deployment</h2>
      </div>
        <VirtualMachineSection
          value={config.virtualMachine}
          onChange={(updates) => updateSection('virtualMachine', updates)}
          errors={errors.virtualMachine}
        />


      <button type="submit" disabled={isSubmitting}>Nasadit</button>
      {error && <p className="form-error">{error}</p>}
    </form>
  );
}