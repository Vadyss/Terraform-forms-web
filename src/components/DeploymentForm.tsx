import { useState } from 'react';
import type { FormEvent } from 'react';
import { NetworkConnectionSection } from './sections/NetworkConnectionSection';
import { VirtualMachineSection } from './sections/VirtualMachineSection';
import { NetworkSection } from './sections/NetworkSection';
import { GuacamoleSection } from './sections/GuacamoleSection';
import type { DeploymentConfig, ValidationErrors } from '../types';

interface DeploymentFormProps {
  onJobCreated: (id: string) => void;
}

function validateConfig(config: DeploymentConfig): ValidationErrors {
  const errors: ValidationErrors = {};

  const networkConnection: NonNullable<ValidationErrors['networkConnection']> = {};
  if (config.networkConnection.name.trim() === '') {
    networkConnection.name = 'Povinné pole';
  }
  if (Object.keys(networkConnection).length > 0) {
    errors.networkConnection = networkConnection;
  }

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

  const networks: NonNullable<ValidationErrors['networks']> = {};
  if (config.networks.lan && config.networks.lanIp.trim() === '') {
    networks.lanIp = 'Povinné pole';
  }
  if (config.networks.ipConfig === 'static' && config.networks.staticIp.trim() === '') {
    networks.staticIp = 'Povinné pole';
  }
  if (Object.keys(networks).length > 0) {
    errors.networks = networks;
  }

  if (config.guacamole.enabled) {
    const guacamole: NonNullable<ValidationErrors['guacamole']> = {};
    if (config.guacamole.os.trim() === '') {
      guacamole.os = 'Vyberte operační systém';
    }
    if (config.guacamole.type.trim() === '') {
      guacamole.type = 'Vyberte typ prostředí';
    }
    if (config.guacamole.keyboardLayout.trim() === '') {
      guacamole.keyboardLayout = 'Vyberte rozložení klávesnice';
    }
    if (config.guacamole.username.trim() === '') {
      guacamole.username = 'Povinné pole';
    }
    if (config.guacamole.password.trim() === '') {
      guacamole.password = 'Povinné pole';
    }
    if (Object.keys(guacamole).length > 0) {
      errors.guacamole = guacamole;
    }
  }

  return errors;
}

export function DeploymentForm({ onJobCreated }: DeploymentFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [config, setConfig] = useState<DeploymentConfig>({
    networkConnection: { name: '', subnet: '', portSecurity: false, internet: false },
    virtualMachine: { name: '', os: '', cpu: 2, ram: 4, disk: 40 },
    networks: { lan: false, lanIp: '', ipConfig: 'dhcp', staticIp: '' },
    guacamole: { enabled: false, os: '', type: '', keyboardLayout: '', username: '', password: '', sftp: false },
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

        <NetworkConnectionSection
          value={config.networkConnection}
          onChange={(updates) => updateSection('networkConnection', updates)}
          errors={errors.networkConnection}
        />
        <VirtualMachineSection
          value={config.virtualMachine}
          onChange={(updates) => updateSection('virtualMachine', updates)}
          errors={errors.virtualMachine}
        />
        <NetworkSection
          value={config.networks}
          onChange={(updates) => updateSection('networks', updates)}
          errors={errors.networks}
        />
        <GuacamoleSection
          value={config.guacamole}
          onChange={(updates) => updateSection('guacamole', updates)}
          errors={errors.guacamole}
        />


      <button type="submit" disabled={isSubmitting}>Nasadit</button>
      {error && <p className="form-error">{error}</p>}
    </form>
  );
}