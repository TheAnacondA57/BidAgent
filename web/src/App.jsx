import { FileSearch, Quote, ShieldCheck, Sparkles } from 'lucide-react';
import React from 'react';

import { askQuestionWithTrace } from './api.js';
import { Button } from './design-system/components/core/Button.jsx';
import { Spinner } from './design-system/components/core/Spinner.jsx';
import { Input } from './design-system/components/forms/Input.jsx';
import { Card } from './design-system/components/layout/Card.jsx';
import { StatCard } from './design-system/components/layout/StatCard.jsx';
import { PipelineTrace } from './components/PipelineTrace.jsx';

export function App() {
  const [question, setQuestion] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [traceData, setTraceData] = React.useState(null);
  const [error, setError] = React.useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!question.trim() || loading) return;

    setLoading(true);
    setError(null);
    setTraceData(null);
    try {
      const result = await askQuestionWithTrace(question.trim());
      setTraceData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ minHeight: '100vh' }}>
      <section className="ba-aurora" style={{ padding: '96px 24px 64px' }}>
        <div style={{ maxWidth: 'var(--container-max)', margin: '0 auto', textAlign: 'center' }}>
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            font: 'var(--fw-medium) var(--text-xs)/1 var(--font-mono)',
            letterSpacing: 'var(--ls-eyebrow)', textTransform: 'uppercase',
            color: 'var(--cool-300)',
          }}>
            <Sparkles size={14} /> BidAgent — RIP-Agent
          </span>

          <h1 className="ba-grad-text" style={{ margin: '20px 0 0', font: 'var(--type-h1)', letterSpacing: 'var(--ls-tight)' }}>
            Posez vos questions sur vos contrats DSP/RIP
          </h1>

          <p style={{ margin: '20px auto 0', maxWidth: 640, font: 'var(--type-body)', color: 'var(--text-secondary)' }}>
            Un agent documentaire qui répond uniquement à partir de vos contrats de concession,
            cite systématiquement ses sources, et refuse de répondre si le contexte ne le permet pas.
          </p>

          <div style={{ marginTop: 40, display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 16, textAlign: 'left' }}>
            <StatCard label="Citations" value="100%" delta="systématiques" trend="up" icon={<Quote size={16} />} />
            <StatCard label="Hors-contexte" value="Refus" delta="explicite" trend="up" icon={<ShieldCheck size={16} />} />
            <StatCard label="Retrieval" value="Hybride" delta="BM25 + dense" icon={<FileSearch size={16} />} />
          </div>
        </div>
      </section>

      <section style={{ padding: '0 24px 96px' }}>
        <div style={{ maxWidth: 720, margin: '0 auto' }}>

          {/* Query form */}
          <Card glow padding="var(--space-8)">
            <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 12, alignItems: 'flex-end' }}>
              <div style={{ flex: 1 }}>
                <Input
                  label="Votre question"
                  placeholder="Quelle est la durée du contrat de concession ?"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  disabled={loading}
                />
              </div>
              <Button type="submit" variant="accent" loading={loading} disabled={!question.trim()}>
                Interroger
              </Button>
            </form>

            {loading && (
              <div style={{ marginTop: 28, display: 'flex', alignItems: 'center', gap: 10, color: 'var(--text-secondary)' }}>
                <Spinner size={18} /> Analyse du pipeline en cours…
              </div>
            )}

            {error && (
              <p style={{ marginTop: 20, color: 'var(--danger-500)', font: 'var(--type-body)' }}>
                {error}
              </p>
            )}
          </Card>

          {/* Pipeline trace */}
          {traceData && <PipelineTrace data={traceData} />}

        </div>
      </section>
    </div>
  );
}
