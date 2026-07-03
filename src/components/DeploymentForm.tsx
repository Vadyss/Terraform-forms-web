import { useState } from 'react';
import type { FormEvent } from 'react';
import type { DeploymentConfig } from '../types';

interface DeploymentFormProps {
  onJobCreated: (id: string) => void;
}

export function DeploymentForm({ onJobCreated }: DeploymentFormProps) {
  const [name, setName] = useState('');
  const [region, setRegion] = useState('');
  const [size, setSize] = useState('');
  const [image, setImage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if ([name, region, size, image].some(v => v.trim() === '')) {
      setError('Všechna pole jsou povinná')
      return
    }
    const config: DeploymentConfig = { name, region, size, image };
    setError(null)
    setIsSubmitting(true)
    try {
      const res = await fetch('/api/deployments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      if (!res.ok) {
        setError(res.status === 422 ? 'Neplatné hodnoty formuláře' : 'Nasazení se nepodařilo vytvořit')
        return
      }
      const { id } = await res.json();
      onJobCreated(id);
    } catch (e) {
      setError('Nasazení selhalo, zkuste to znovu')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <div className="form-header">
        <h2>Nový deployment</h2>
      </div >
      <div className="form-group">
        <label>Název</label>
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </div >
      <div className="form-group">
        <label>Region</label>
        <input value={region} onChange={(e) => setRegion(e.target.value)} required />
      </div>
      <div className="form-group">
        <label>Velikost</label>
        <input value={size} onChange={(e) => setSize(e.target.value)} required />
      </div>
      <div className="form-group">
        <label>Image</label>
        <input value={image} onChange={(e) => setImage(e.target.value)} required />
      </div>
      <button type="submit" disabled={isSubmitting}>Nasadit</button>
      {error && <p className="form-error">{error}</p>}
    </form>
  );
}
