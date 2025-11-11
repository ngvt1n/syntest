import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Button from '../components/ui/Button';
import Checkbox from '../components/ui/Checkbox';
import ScreeningStep from '../components/screening/ScreeningStep';
import ChoiceCard from '../components/screening/ChoiceCard';
import TypeRow from '../components/screening/TypeRow';
import useScreeningState from '../hooks/useScreeningState';
import '../styles/app.css';

export default function ScreeningFlow() {
  const { step: stepParam } = useParams();
  const step = parseInt(stepParam) || 0;
  const navigate = useNavigate();
  const {
    state,
    updateState,
    clearState,
    handleHealthChange, 
    handleSynTypesChange, 
  } = useScreeningState();


  // Step 0: Intro
  if (step === 0) {
    return (
      <ScreeningStep
        step={0}
        totalSteps={5}
        title="Take the questionnaire"
        showActions={false}
      >
        <p className="lead">
          In this first screening, we'll check basic eligibility and your experiences.
        </p>

        <label className="checkbox-group">
          <input
            id="consent"
            type="checkbox"
            checked={state.consent}
            onChange={(e) => updateState({consent: e.target.checked})}
            data-audit-label="Consent agreement"
          />
          <span>I consent to take part in this study.</span>
        </label>

        <p className="text-muted mb-3">
          By checking this box, you acknowledge that you have read and understood the
          study information sheet, agree to participate voluntarily, and consent to the
          collection and use of your data for research purposes. You may withdraw at any
          time without penalty.
        </p>

        <Button
          id="begin-screening"
          className="btn-block"
          disabled={!state.consent}
          onClick={() => state.consent && navigate('/screening/1')}
        >
          Begin screening
        </Button>
      </ScreeningStep>
    );
  }

  // Step 1: Health & Substances
  if (step === 1) {
    const hasExclusions = [
      state.health.drug,
      state.health.neuro,
      state.health.medical
    ].some(value => value);

    return (
      <ScreeningStep
        step={1}
        totalSteps={5}
        chip={{ label: 'Health & Substances', variant: 'primary' }}
        title="Confirm none apply to you:"
        onNext={() => hasExclusions ? navigate('/screening/exit/BC') : navigate('/screening/2')}
        nextLabel={hasExclusions ? "Exit study" : "Continue"}
      >
        <Checkbox
          children="Use of recreational drugs including marijuana, LSD, or psychedelics"
          checked={state.health.drug}
          onChange={(e) => {handleHealthChange('drug', e)}}
          data-audit-label="Substance exclusion — recreational drugs"
        />
        <Checkbox
          children="Neurological condition or treatment affecting perception"
          checked={state.health.neuro}
          onChange={(e) => {handleHealthChange('neuro', e)}}
          data-audit-label="Substance exclusion — neurological condition"
        />
        <Checkbox
          children="Medical treatment impacting perception (e.g., brain tumor) or hallucinogenic physiology"
          checked={state.health.medical}
          onChange={(e) => {handleHealthChange('edical', e)}}
          data-audit-label="Substance exclusion — medical treatment"
        />
        <p className="text-muted">If any are checked, you're not eligible.</p>
      </ScreeningStep>
    );
  }

  // Step 2: Definition
  if (step === 2) {
    const hasDefinitions = state.definition == "YES" || state.definition == "NO"

    return (
      <ScreeningStep
        step={2}
        totalSteps={5}
        chip={{ label: 'Definition', variant: 'info' }}
        title="What is synesthesia?"
        onNext={() => !hasDefinitions ? navigate('/screening/exit/A') : navigate('/screening/3')}
        nextLabel={!hasDefinitions ? "Exit study" : "Continue"}
      >
        <p>
          Synesthesia is a neurological condition where stimulation of <em>one</em> sense automatically
          triggers a perception in another sense. It's not a metaphor, a mood-based association,
          or a one-time experience—it's a consistent, involuntary sensory connection that occurs
          throughout a person's life.
        </p>

        <div className="grid-2">
          <div>
            <div className="label-uppercase">DO</div>
            <ul className="arrow-list">
              <li><span className="arrow"></span> Letters → Colors</li>
              <li><span className="arrow"></span> Music → Colors</li>
              <li><span className="arrow"></span> Words → Tastes</li>
            </ul>
          </div>
          <div>
            <div className="label-uppercase">DON'T</div>
            <ul className="plain-list">
              <li>Mnemonics</li>
              <li>Guesses</li>
              <li>Random choices</li>
            </ul>
          </div>
        </div>

        <div className="choice-grid">
          <ChoiceCard
            title="Yes"
            subtitle="I experience consistent sensory connections"
            selected={state.definition === 'YES'}
            onClick={() => updateState({definition: 'YES'})}
            data-audit-label="Definition choice — yes"
          />
          <ChoiceCard
            title="Maybe"
            subtitle="I'm not sure if my experiences qualify"
            selected={state.definition === 'MAYBE'}
            onClick={() => updateState({definition: 'MAYBE'})}
            data-audit-label="Definition choice — maybe"
          />
        </div>
        <ChoiceCard
          variant="negative"
          title="No — exit per criterion A"
          subtitle="I don't experience these sensory connections"
          selected={state.definition === 'NO'}
          onClick={() => { updateState({definition: 'NO'}); }}
          data-audit-label= "Definition choice - no"
        />
      </ScreeningStep>
    );
  }

  // Step 3: Pain & Emotion
  if (step === 3) {
    return (
      <ScreeningStep
        step={3}
        totalSteps={5}
        chip={{ label: 'Pain & Emotion', variant: 'info' }}
        title="Are your triggers pain or emotions?"
        onNext={() => state.pain === "YES" ? navigate('/screening/exit/D') : navigate('/screening/4')}
        nextLabel={state.pain === "YES" ? "Exit study" : "Continue"}
      >
        <p>
          For ethical and replicability reasons, we must exclude synesthetic experiences that are primarily
          triggered by pain or strong emotions. We're looking for consistent, automatic associations with
          neutral stimuli.
        </p>

        <div className="info-panel">
          <ul className="info-rows">
            <li>
              <span className="i bolt"></span>
              <span className="info-label">Pain</span>
              <span className="info-text">→ flashes of light or color</span>
            </li>
            <li>
              <span className="i heart"></span>
              <span className="info-label">Emotion</span>
              <span className="info-text">→ specific tastes or smells</span>
            </li>
            <li>
              <span className="i dot"></span>
              <span className="info-label">Valid example:</span>
              <span className="info-text">The neutral word "Tuesday" consistently tastes sweet</span>
            </li>
          </ul>
        </div>

        <div className="select-list">
          <label className="select-card">
            <input
              type="radio"
              name="pain_emotion"
              value="YES"
              checked={state.pain === 'YES'}
              onChange={(e) => updateState({pain: e.target.value})}
              data-audit-label="Pain/emotion trigger — yes"
            />
            <div className="select-body">
              <div className="select-title">Yes</div>
              <div className="select-subtitle">
                My experiences are primarily triggered by pain or strong emotions (exit per criterion D)
              </div>
            </div>
          </label>
          <label className="select-card">
            <input
              type="radio"
              name="pain_emotion"
              value="NO"
              checked={state.pain === 'NO'}
              onChange={(e) => updateState({pain: e.target.value})}
              data-audit-label="Pain/emotion trigger — no"
            />
            <div className="select-body">
              <div className="select-title">No</div>
              <div className="select-subtitle">My experiences occur with neutral stimuli</div>
            </div>
          </label>
        </div>
      </ScreeningStep>
    );
  }

  // Step 4: Type Selection
  if (step === 4) {
    const hasSynTypes = Object.values(state.synTypes).some(value => value);

    return (
      <ScreeningStep
        step={4}
        totalSteps={5}
        chip={{ label: 'Type Selection', variant: 'success' }}
        title="Select any types you experience"
        onNext={() => !hasSynTypes ? navigate('/screening/exit/NONE') : navigate('/screening/4')}
        nextLabel="Continue"
      >
        <ul className="type-rows">
          <TypeRow
            title="Letter • Color"
            description='Letters/numbers evoke specific colors (e.g., "A" is red).'
            name="grapheme"
            value={state.synTypes.letter_color}
            onChange={(e) =>  handleSynTypesChange('letter_color', e) }
          />
          <TypeRow
            title="Music/Sound • Color"
            description="Single notes or dyads evoke colors (70 tones testable)."
            name="music"
            value={state.synTypes.sound_color}
            onChange={(e) =>  handleSynTypesChange('sound_color', e) }
          />
          <TypeRow
            title="Lexical/Word • Taste"
            description="Words evoke tastes via the 5 basic tastes."
            name="lexical"
            value={state.synTypes.words_taste}
            onChange={(e) =>  handleSynTypesChange('words_taste', e) }
          />
          <TypeRow
            title="Sequence • Space"
            description="Days, months, or years have fixed spatial layouts."
            name="sequence"
            value={state.synTypes.sequence_space}
            onChange={(e) =>  handleSynTypesChange('sequence_space', e) }
          />
        </ul>

        <input
          id="other-experiences"
          className="other-input"
          type="text"
          placeholder="Other synesthetic experiences (optional)"
          value={state.otherExperiences}
          onChange={(e) => updateState({otherExperiences: e.target.value})}
          // TODO: this needs work
          data-mask="true"
          data-audit-label="Other synesthetic experiences free-text"
        />
        <p className="text-muted">
          Only types with available tasks proceed; pain/emotion triggers excluded.
        </p>
      </ScreeningStep>
    );
  }

  // Step 5: Routing Summary
  if (step === 5) {
    return (
      <ScreeningStep
        step={5}
        totalSteps={5}
        chip={{ label: 'Routing', variant: 'info' }}
        title="Your next step"
        nextLabel="Begin Assigned Task"
        onNext={() => navigate('/test/assigned')}
      >
        <div className="tag-group">
          <span className="tag">Grapheme – Color</span>
          <span className="tag">Lexical – Taste</span>
        </div>

        <div className="summary-grid">
          <div className="summary-card">
            <div className="summary-title">Trigger → Color</div>
            <div className="summary-sub">Color consistency + speeded congruency</div>
            <ul className="summary-list">
              <li>Grapheme-Color</li>
              <li>Music-Color</li>
            </ul>
          </div>

          <div className="summary-card">
            <div className="summary-title">Trigger → Gustatory</div>
            <div className="summary-sub">Two-trial taste consistency (R²)</div>
            <ul className="summary-list">
              <li>Lexical-Gustatory</li>
              <li>Sound-Taste</li>
            </ul>
          </div>

          <div className="summary-card">
            <div className="summary-title">Sequence → Space</div>
            <div className="summary-sub">Layout mapping + consistency</div>
            <ul className="summary-list">
              <li>Days</li>
              <li>Months</li>
              <li>Year</li>
            </ul>
          </div>
        </div>

        <div className="summary-note">
          <div className="note-title">What you'll do</div>
          <ul className="note-list">
            <li>We test only your selected types</li>
            <li>You can stop at any time</li>
          </ul>
        </div>
      </ScreeningStep>
    );
  }

  return null;
}
