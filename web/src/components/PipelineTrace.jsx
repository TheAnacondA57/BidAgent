import { CheckCircle2, Database, Layers, Search, Sparkles } from 'lucide-react';
import React from 'react';

import { Badge } from '../design-system/components/core/Badge.jsx';
import { Card } from '../design-system/components/layout/Card.jsx';

// ─── Helpers ─────────────────────────────────────────────────────────────────

const fmt = (ms) => ms == null ? '—' : ms < 1 ? '<1' : ms < 10 ? ms.toFixed(1) : Math.round(ms).toString();

const STEP_COLORS = {
  warm:    { accent: 'var(--warm-500)',    glow: 'rgba(240,138,60,0.08)',  text: 'var(--warm-300)' },
  cool:    { accent: 'var(--cool-500)',    glow: 'rgba(61,123,255,0.08)',  text: 'var(--cool-300)' },
  purple:  { accent: '#C25CFF',            glow: 'rgba(194,92,255,0.08)',  text: '#D48AFF' },
  success: { accent: 'var(--success-500)', glow: 'rgba(54,194,139,0.08)', text: 'var(--success-500)' },
};

// ─── Sub-components ───────────────────────────────────────────────────────────

function StepNode({ color, icon, title, timingMs, delay = 0, children }) {
  const c = STEP_COLORS[color];
  return (
    <div style={{
      background: 'var(--surface-card)',
      border: '1px solid var(--line-soft)',
      borderLeft: `2px solid ${c.accent}`,
      borderRadius: 'var(--radius-lg)',
      overflow: 'hidden',
      boxShadow: 'var(--edge-highlight), var(--shadow-md)',
      opacity: 0,
      animation: `ba-fade-up var(--dur-slow) var(--ease-out) ${delay}ms both`,
    }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 10,
        padding: '11px 18px',
        borderBottom: '1px solid var(--line-faint)',
        background: c.glow,
      }}>
        <span style={{ color: c.accent, display: 'inline-flex', width: 16, height: 16, flexShrink: 0 }}>
          {icon}
        </span>
        <span style={{ font: 'var(--fw-medium) var(--text-sm)/1 var(--font-sans)', color: c.text, flex: 1 }}>
          {title}
        </span>
        {timingMs != null && (
          <span style={{
            font: 'var(--fw-medium) var(--text-xs)/1 var(--font-mono)',
            color: 'var(--text-muted)',
            background: 'var(--surface-3)',
            padding: '3px 10px', borderRadius: 'var(--radius-pill)',
          }}>
            {fmt(timingMs)} ms
          </span>
        )}
      </div>
      <div style={{ padding: '14px 18px' }}>{children}</div>
    </div>
  );
}

function Connector({ label, delay = 0 }) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'flex-start',
      paddingLeft: 24, gap: 0,
      opacity: 0, animation: `ba-fade-in var(--dur-base) var(--ease-out) ${delay}ms both`,
    }}>
      <div style={{ width: 1, height: 10, background: 'var(--line-faint)' }} />
      <span style={{
        font: 'var(--fw-regular) 0.7rem/1 var(--font-mono)',
        color: 'var(--text-faint)', padding: '2px 0',
      }}>
        {label}
      </span>
      <div style={{ width: 1, height: 10, background: 'var(--line-faint)' }} />
    </div>
  );
}

function MetricRow({ name, value, unit, barPct, barColor, divider = false }) {
  if (divider) {
    return <div style={{ height: 1, background: 'var(--line-faint)', margin: '6px 0' }} />;
  }
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, height: 26 }}>
      <span style={{
        font: 'var(--type-label)', color: 'var(--text-secondary)',
        width: 148, flexShrink: 0,
      }}>
        {name}
      </span>
      {barPct != null && (
        <div style={{ flex: 1, height: 3, background: 'var(--surface-3)', borderRadius: 2, overflow: 'hidden' }}>
          <div style={{
            height: '100%', borderRadius: 2,
            width: `${barPct}%`,
            background: barColor || 'var(--cool-500)',
            transition: 'width 0.5s var(--ease-out)',
          }} />
        </div>
      )}
      <span style={{
        font: 'var(--fw-medium) var(--text-sm)/1 var(--font-mono)',
        color: 'var(--text-primary)', flexShrink: 0,
        minWidth: 28, textAlign: 'right',
      }}>
        {value ?? '—'}
      </span>
      {unit && (
        <span style={{
          font: 'var(--type-mono)', color: 'var(--text-faint)',
          width: 62, flexShrink: 0,
        }}>
          {unit}
        </span>
      )}
    </div>
  );
}

function TimingBar({ retrievalSpan, generationSpan, totalMs }) {
  if (!totalMs || totalMs === 0) return null;
  const rows = [
    retrievalSpan && {
      label: retrievalSpan.name === 'tree_retrieval' ? 'Tree Retrieval' : 'Retrieval',
      ms: retrievalSpan.duration_ms,
      color: 'var(--cool-500)',
    },
    generationSpan && {
      label: 'Génération',
      ms: generationSpan.duration_ms,
      color: '#C25CFF',
    },
  ].filter(Boolean);

  return (
    <div style={{
      marginTop: 'var(--space-6)', paddingTop: 'var(--space-5)',
      borderTop: '1px solid var(--line-faint)',
      opacity: 0,
      animation: `ba-fade-up var(--dur-slow) var(--ease-out) 500ms both`,
    }}>
      <p style={{ font: 'var(--fw-medium) var(--text-xs)/1 var(--font-sans)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 'var(--ls-eyebrow)', marginBottom: 'var(--space-4)' }}>
        Répartition du temps — {fmt(totalMs)} ms total
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {rows.map(({ label, ms, color }) => {
          const pct = Math.min(100, (ms / totalMs) * 100);
          return (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ font: 'var(--type-label)', color: 'var(--text-secondary)', width: 120, flexShrink: 0, textAlign: 'right' }}>{label}</span>
              <div style={{ flex: 1, height: 6, background: 'var(--surface-3)', borderRadius: 3, overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${pct}%`, background: color, borderRadius: 3, transition: 'width 0.6s var(--ease-out)' }} />
              </div>
              <span style={{ font: 'var(--fw-medium) var(--text-xs)/1 var(--font-mono)', color: 'var(--text-muted)', width: 56, flexShrink: 0 }}>{fmt(ms)} ms</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

export function PipelineTrace({ data }) {
  const { answer, spans, total_ms } = data;

  const retrievalSpan = spans.find(s => s.name === 'retrieval' || s.name === 'tree_retrieval');
  const generationSpan = spans.find(s => s.name === 'generation');
  const isTree = retrievalSpan?.name === 'tree_retrieval';
  const question = retrievalSpan?.attributes?.['retrieval.question']
    ?? generationSpan?.attributes?.['generation.question']
    ?? '';

  const bm25Count  = retrievalSpan?.attributes?.['retrieval.bm25_count']  ?? 0;
  const denseCount = retrievalSpan?.attributes?.['retrieval.dense_count']  ?? 0;
  const fusedCount = retrievalSpan?.attributes?.['retrieval.fused_count']  ?? 0;
  const expandedCount = retrievalSpan?.attributes?.['retrieval.expanded_count'];
  const maxRetrieval = Math.max(bm25Count, denseCount, fusedCount, expandedCount ?? 0, 1);

  const ctxCount    = generationSpan?.attributes?.['generation.context_chunk_count'] ?? '—';
  const citCount    = generationSpan?.attributes?.['generation.citation_count'] ?? 0;
  const refused     = generationSpan?.attributes?.['generation.refused'] ?? answer.refused;

  const retrievalEnd = retrievalSpan
    ? retrievalSpan.start_ms + retrievalSpan.duration_ms
    : 0;
  const generationEnd = generationSpan
    ? generationSpan.start_ms + generationSpan.duration_ms
    : total_ms;

  return (
    <Card padding="var(--space-6)" style={{ marginTop: 'var(--space-6)' }}>
      <p style={{
        font: 'var(--fw-medium) var(--text-xs)/1 var(--font-sans)',
        color: 'var(--text-muted)', textTransform: 'uppercase',
        letterSpacing: 'var(--ls-eyebrow)', marginBottom: 'var(--space-5)',
      }}>
        Pipeline RAG — trace
      </p>

      <div style={{ display: 'flex', flexDirection: 'column' }}>

        {/* Query */}
        <StepNode color="warm" icon={<Search size={16} />} title="Query" delay={0}>
          <blockquote style={{
            margin: 0, border: 'none',
            font: 'var(--fw-regular) var(--text-base)/var(--lh-relaxed) var(--font-sans)',
            color: 'var(--text-primary)',
          }}>
            {question}
          </blockquote>
        </StepNode>

        {/* Retrieval */}
        {retrievalSpan && (
          <>
            <Connector label="t = 0 ms" delay={80} />
            <StepNode
              color="cool"
              icon={isTree ? <Layers size={16} /> : <Database size={16} />}
              title={isTree ? 'Tree Retrieval' : 'Retrieval'}
              timingMs={retrievalSpan.duration_ms}
              delay={160}
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <MetricRow name="BM25 Search"   value={bm25Count}  unit="docs"     barPct={(bm25Count  / maxRetrieval) * 100} barColor="var(--cool-500)" />
                <MetricRow name="Dense Search"  value={denseCount} unit="docs"     barPct={(denseCount / maxRetrieval) * 100} barColor="var(--cool-500)" />
                <MetricRow divider />
                <MetricRow name="RRF Fusion"    value={fusedCount} unit="chunks"   barPct={(fusedCount / maxRetrieval) * 100} barColor="var(--cool-300)" />
                {isTree && expandedCount != null && (
                  <MetricRow name="Expand to Parent" value={expandedCount} unit="sections" barPct={(expandedCount / maxRetrieval) * 100} barColor="var(--cool-300)" />
                )}
              </div>
            </StepNode>
          </>
        )}

        {/* Generation */}
        {generationSpan && (
          <>
            <Connector label={`t = ${fmt(retrievalEnd)} ms`} delay={240} />
            <StepNode
              color="purple"
              icon={<Sparkles size={16} />}
              title="Génération"
              timingMs={generationSpan.duration_ms}
              delay={320}
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <MetricRow name="Chunks en contexte"  value={ctxCount} unit="chunks" />
                <MetricRow name="Citations extraites" value={citCount} unit="" />
                <MetricRow divider />
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, height: 26 }}>
                  <span style={{ font: 'var(--type-label)', color: 'var(--text-secondary)', width: 148, flexShrink: 0 }}>
                    Réponse refusée
                  </span>
                  <Badge tone={refused ? 'danger' : 'success'} dot>
                    {refused ? 'Oui' : 'Non'}
                  </Badge>
                </div>
              </div>
            </StepNode>
          </>
        )}

        {/* Answer */}
        <Connector label={`t = ${fmt(generationEnd)} ms`} delay={400} />
        <StepNode
          color="success"
          icon={<CheckCircle2 size={16} />}
          title="Réponse"
          timingMs={total_ms}
          delay={480}
        >
          {answer.refused ? (
            <div>
              <Badge tone="warning" dot>Refus</Badge>
              <p style={{ marginTop: 10, font: 'var(--type-body)', color: 'var(--text-secondary)' }}>
                {answer.text}
              </p>
            </div>
          ) : (
            <div>
              <p style={{ margin: 0, font: 'var(--type-body)', color: 'var(--text-primary)', lineHeight: 'var(--lh-relaxed)', whiteSpace: 'pre-wrap' }}>
                {answer.text}
              </p>
              {answer.citations.length > 0 && (
                <div style={{ marginTop: 'var(--space-4)', display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {answer.citations.map(c => (
                    <Badge key={c.chunk_id} tone="info" dot>
                      {c.source_doc}{c.source_section ? ` — ${c.source_section}` : ''}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          )}
        </StepNode>

        {/* Timing bar */}
        <TimingBar retrievalSpan={retrievalSpan} generationSpan={generationSpan} totalMs={total_ms} />
      </div>
    </Card>
  );
}
