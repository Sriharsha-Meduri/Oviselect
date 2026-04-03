import React from 'react';
import './copilot-dashboard.css';

const CopilotDashboard: React.FC = () => {
  return (
    <div className="copilot-dash">
      {/* Header */}
      <div className="cd-header">
        <div className="cd-wordmark">
          <div className="cd-wordmark-glyph"></div>
          <div>
            <div className="cd-wordmark-text">OviGuide</div>
            <div className="cd-wordmark-sub">COUNSELLING COPILOT</div>
          </div>
        </div>
        <div className="cd-header-right">
          <span className="cd-round-chip">ROUND 3 ACTIVE</span>
          <span className="cd-live-chip"><span className="cd-live-dot"></span> LIVE TRACKING</span>
        </div>
      </div>

      {/* Rank Hero */}
      <div className="cd-rank-hero">
        <div>
          <div className="cd-rank-number">24,150</div>
          <div className="cd-rank-sublabel">JEE MAIN CRL · GENERAL · JoSAA 2024</div>
        </div>
        <div className="cd-rank-attrs">
          <div><span className="cd-ra-label">Category</span><div className="cd-ra-val">General</div></div>
          <div><span className="cd-ra-label">Percentile</span><div className="cd-ra-val">~97.8</div></div>
          <div><span className="cd-ra-label">Home State</span><div className="cd-ra-val">Maharashtra</div></div>
          <div><span className="cd-ra-label">Preference</span><div className="cd-ra-val">Civil Engg.</div></div>
        </div>
      </div>

      {/* Allotment Banner */}
      <div className="cd-allotment">
        <span className="cd-ab-badge">Current allotment</span>
        <div className="cd-ab-body">
          <div className="cd-ab-college">NIT Warangal</div>
          <div className="cd-ab-branch">Civil Engineering · Other State · Gender Neutral</div>
          <div className="cd-ab-cutoff">R5 closing 2024 → 25,059 · you are ~909 ranks inside cutoff</div>
        </div>
        <button className="cd-ab-action">Freeze →</button>
      </div>

      {/* Metrics */}
      <div className="cd-metrics">
        <div className="cd-mcard">
          <div className="cd-mcard-label">Current allotment</div>
          <div className="cd-mcard-val green" style={{ fontSize: '17px', marginTop: '2px' }}>NITW Civil</div>
          <div className="cd-mcard-sub">~909 ranks inside cutoff</div>
        </div>
        <div className="cd-mcard">
          <div className="cd-mcard-label">Upgrade possible?</div>
          <div className="cd-mcard-val amber">Low</div>
          <div className="cd-mcard-sub">Better civil closes lower</div>
        </div>
        <div className="cd-mcard">
          <div className="cd-mcard-label">ECE / CS top NIT</div>
          <div className="cd-mcard-val red">✕</div>
          <div className="cd-mcard-sub">Closes well under 10k</div>
        </div>
        <div className="cd-mcard">
          <div className="cd-mcard-label">Decision score</div>
          <div className="cd-mcard-val green">74</div>
          <div className="cd-mcard-sub">Strong — lock it in</div>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="cd-two-col">
        {/* Copilot Panel */}
        <div className="cd-copilot">
          <div className="cd-cp-header">
            <div className="cd-cp-header-left">
              <div className="cd-cp-icon">
                <svg width="12" height="12" viewBox="0 0 10 10" fill="none">
                  <circle cx="5" cy="5" r="3.5" stroke="rgba(245,242,236,0.55)" strokeWidth="1"/>
                  <path d="M3.5 5l1 1L6.5 3.5" stroke="rgba(245,242,236,0.8)" strokeWidth="1.1" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <span className="cd-cp-title">COPILOT RECOMMENDATION</span>
            </div>
            <span className="cd-cp-round-tag">R3 / JoSAA 2024</span>
          </div>

          <div className="cd-round-track">
            <div className="cd-rt-step"><div className="cd-rt-dot cd-rt-done">✓</div><span className="cd-rt-label">R1</span></div>
            <div className="cd-rt-step"><div className="cd-rt-dot cd-rt-done">✓</div><span className="cd-rt-label">R2</span></div>
            <div className="cd-rt-step"><div className="cd-rt-dot cd-rt-active">3</div><span className="cd-rt-label active">R3</span></div>
            <div className="cd-rt-step"><div className="cd-rt-dot cd-rt-pending">4</div><span className="cd-rt-label">R4</span></div>
            <div className="cd-rt-step"><div className="cd-rt-dot cd-rt-pending">5</div><span className="cd-rt-label">R5</span></div>
          </div>

          <div className="cd-advice-list">
            <div className="cd-adv cd-adv-green">
              <span className="cd-adv-sym">→</span>
              <div className="cd-adv-body"><strong>Freeze recommended.</strong> NIT Warangal Civil (R5 OS closing: <strong>25,059</strong>) is an excellent outcome at your rank.</div>
            </div>
            <div className="cd-adv cd-adv-red">
              <span className="cd-adv-sym">✕</span>
              <div className="cd-adv-body"><strong>NIT Trichy Civil is out of range.</strong> R5 OS closing: <strong>18,965</strong> — 5,185 ranks beyond your CRL.</div>
            </div>
            <div className="cd-adv cd-adv-amber">
              <span className="cd-adv-sym">!</span>
              <div className="cd-adv-body"><strong>Do not Float looking for Civil upgrades.</strong> NITW Civil is already the best civil seat you can get.</div>
            </div>
            <div className="cd-adv cd-adv-blue">
              <span className="cd-adv-sym">i</span>
              <div className="cd-adv-body"><strong>NITW Civil placement:</strong> Median ₹10–16 LPA. NIRF rank 20 overall.</div>
            </div>
          </div>

          <div className="cd-cp-actions">
            <button className="cd-cta-btn">Freeze this seat →</button>
            <button className="cd-cta-btn ghost">NITW placements</button>
            <button className="cd-cta-btn ghost">CSAB special</button>
          </div>
        </div>

        {/* Right Column */}
        <div className="cd-right-col">
          <RankComparisonCard />
          <VerdictCard />
        </div>
      </div>
    </div>
  );
};

const RankComparisonCard: React.FC = () => (
  <div className="cd-bv-card">
    <div className="cd-section-label">Civil Engg. closing ranks · General OS R5 2024</div>

    <div className="cd-br-row">
      <span className="cd-br-name" style={{ color: 'var(--cd-accent)', fontWeight: 600 }}>NIT Trichy</span>
      <div className="cd-br-track"><div className="cd-br-fill" style={{ width: '9%', background: 'var(--cd-accent)' }} /></div>
      <span className="cd-br-score na">18,965 ✕</span>
    </div>
    <div className="cd-br-row">
      <span className="cd-br-name" style={{ color: 'var(--cd-accent)', fontWeight: 600 }}>NIT Surathkal</span>
      <div className="cd-br-track"><div className="cd-br-fill" style={{ width: '10%', background: 'var(--cd-accent)', opacity: 0.7 }} /></div>
      <span className="cd-br-score na">~19,200 ✕</span>
    </div>
    <div className="cd-br-row">
      <span className="cd-br-name" style={{ color: 'var(--cd-accent)', fontWeight: 600 }}>NIT Rourkela</span>
      <div className="cd-br-track"><div className="cd-br-fill" style={{ width: '14%', background: 'var(--cd-accent)', opacity: 0.5 }} /></div>
      <span className="cd-br-score na">24,286 ✕</span>
    </div>

    <div className="cd-divider" />

    <div className="cd-br-row">
      <span className="cd-br-name" style={{ color: 'var(--cd-green)', fontWeight: 600 }}>✓ NITW (yours)</span>
      <div className="cd-br-track"><div className="cd-br-fill" style={{ width: '78%', background: 'var(--cd-green)' }} /></div>
      <span className="cd-br-score" style={{ color: 'var(--cd-green)', fontWeight: 500 }}>25,059</span>
    </div>
    <div className="cd-br-row">
      <span className="cd-br-name">NIT Calicut</span>
      <div className="cd-br-track"><div className="cd-br-fill" style={{ width: '92%', background: '#2a6b4a', opacity: 0.4 }} /></div>
      <span className="cd-br-score">33,650</span>
    </div>

    <div className="cd-summary-text">
      NITW Civil is the <strong>best civil seat available</strong> at CRL 24,150. Trichy, Surathkal, and Rourkela are all closed.
    </div>
  </div>
);

const VerdictCard: React.FC = () => (
  <div className="cd-dark-card">
    <div className="cd-section-label">Verdict</div>
    <div className="cd-verdict-text">You have the best civil seat possible at your rank. Freeze it.</div>
    <div className="cd-verdict-sub">NITW Civil · NIRF #20 · Strong infra + placement record. No upgrade exists within reach.</div>
  </div>
);

export default CopilotDashboard;
