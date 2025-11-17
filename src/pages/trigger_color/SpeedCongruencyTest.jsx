// src/pages/trigger_color/SpeedCongruencyTest.jsx

import React, { useEffect, useRef, useState } from 'react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import { speedCongruencyService } from '../../services/speedCongruency';

export default function SpeedCongruencyTest() {
  const [trialIndex, setTrialIndex] = useState(0);
  const [currentTrial, setCurrentTrial] = useState(null);
  const [totalTrials, setTotalTrials] = useState(1);

  const [phase, setPhase] = useState('stimulus'); // 'stimulus' | 'choices' | 'done'
  const [countdown, setCountdown] = useState(3);
  const [selectedOptionId, setSelectedOptionId] = useState(null);
  const [isLoadingTrial, setIsLoadingTrial] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const choiceStartRef = useRef(null);

  // ---- Load a trial from the backend whenever trialIndex changes ----
  useEffect(() => {
    async function loadTrial() {
      setIsLoadingTrial(true);
      setPhase('stimulus');
      setSelectedOptionId(null);

      try {
        const data = await speedCongruencyService.getNextTrial(trialIndex);

        // If backend says we're done
        if (data.done) {
          setPhase('done');
          setCurrentTrial(null);
          setTotalTrials(data.totalTrials || trialIndex);
          return;
        }

        setCurrentTrial(data);
        setTotalTrials(data.totalTrials || 1);
        setCountdown(3);
      } catch (e) {
        console.error('Error loading speed congruency trial:', e);
        setCurrentTrial(null);
      } finally {
        setIsLoadingTrial(false);
      }
    }

    loadTrial();
  }, [trialIndex]);

  // ---- Handle 3–2–1 countdown in "stimulus" phase ----
  useEffect(() => {
    if (phase !== 'stimulus' || !currentTrial) return;

    setCountdown(3);
    const timerId = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(timerId);
          setPhase('choices');
          choiceStartRef.current = performance.now();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timerId);
  }, [phase, currentTrial]);

  const handleOptionClick = optionId => {
    if (isSubmitting) return;
    setSelectedOptionId(optionId);
  };

  // const handleNextTrial = async () => {
  //   if (!currentTrial || !selectedOptionId) return;

  //   const reactionTimeMs = choiceStartRef.current
  //     ? performance.now() - choiceStartRef.current
  //     : null;

  //   const selectedOption = currentTrial.options.find(
  //     (opt) => opt.id === selectedOptionId
  //   );

  //   setIsSubmitting(true);
  //   try {
  //     await speedCongruencyService.submitTrial({
  //       trialIndex,
  //       trigger: currentTrial.trigger,
  //       testDataId: currentTrial.testDataId,
  //       stimulusId: currentTrial.stimulusId,
  //       cue_type: currentTrial.cue_type,
  //       reactionTimeMs,
  //       selectedOptionId,
  //       // Colors for server to record + check accuracy
  //       selectedColor: {
  //         r: selectedOption?.r ?? null,
  //         g: selectedOption?.g ?? null,
  //         b: selectedOption?.b ?? null,
  //         hex: selectedOption?.color ?? null,
  //       },
  //       // (Optional) send expectedColor too; server still re-derives from DB
  //       expectedColor: currentTrial.expectedColor || null,
  //     });
  //   } catch (e) {
  //     console.error('Error submitting speed congruency trial:', e);
  //   } finally {
  //     setIsSubmitting(false);
  //   }

  //   const nextIndex = trialIndex + 1;
  //   if (nextIndex < totalTrials) {
  //     setTrialIndex(nextIndex);
  //     setPhase('stimulus');
  //     setSelectedOptionId(null);
  //     choiceStartRef.current = null;
  //   } else {
  //     setPhase('done');
  //   }
  // };
  const handleNextTrial = async () => {
  if (!currentTrial || !selectedOptionId) return;

  const reactionTimeMs = choiceStartRef.current
    ? performance.now() - choiceStartRef.current
    : null;

  setIsSubmitting(true);
  try {
    await speedCongruencyService.submitTrial({
      trialIndex,
      trigger: currentTrial.trigger,
      selectedOptionId,
      reactionTimeMs,
      testDataId: currentTrial.testDataId,    
      stimulusId: currentTrial.stimulusId,   
    });
  } catch (e) {
    console.error('Error submitting speed congruency trial:', e);
  } finally {
    setIsSubmitting(false);
  }

  const nextIndex = trialIndex + 1;
  if (nextIndex < totalTrials) {
    setTrialIndex(nextIndex);
    setPhase('stimulus');
    setSelectedOptionId(null);
    choiceStartRef.current = null;
  } else {
    setPhase('done');
  }
};



  // ---- Layout styles ----
  const pageStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 'calc(100vh - 120px)',
  };

  const stimulusCardStyle = {
    maxWidth: '640px',
    width: '100%',
    padding: '32px',
    textAlign: 'center',
  };

  const triggerBoxStyle = {
    border: '2px solid #ccc',
    borderRadius: '8px',
    padding: '40px 24px',
    fontSize: '1.5rem',
    margin: '0 auto 32px',
    maxWidth: '320px',
  };

  const timerCircleStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '56px',
    height: '56px',
    borderRadius: '50%',
    backgroundColor: '#222',
    color: '#fff',
    fontSize: '1.25rem',
  };

  const choicesCardStyle = {
    maxWidth: '720px',
    width: '100%',
    padding: '32px',
    textAlign: 'center',
  };

  const optionsGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '32px',
    justifyItems: 'center',
    marginTop: '24px',
    marginBottom: '24px',
  };

  const optionBoxBaseStyle = {
    width: '140px',
    height: '140px',
    borderRadius: '12px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1rem',
    cursor: 'pointer',
    border: '3px solid transparent',
    color: '#000',
  };

  // ---- Render states ----
  if (isLoadingTrial && !currentTrial) {
    return (
      <div style={pageStyle}>
        <Card style={stimulusCardStyle} title="Speed Congruency Test">
          <p>Loading first trial…</p>
        </Card>
      </div>
    );
  }

  if (phase === 'done') {
    return (
      <div style={pageStyle}>
        <Card style={stimulusCardStyle} title="Speed Congruency Test">
          <p>Thank you for completing the test.</p>
        </Card>
      </div>
    );
  }

  if (!currentTrial) {
    return (
      <div style={pageStyle}>
        <Card style={stimulusCardStyle} title="Speed Congruency Test">
          <p>Unable to load test. Please make sure you have completed a color test first.</p>
        </Card>
      </div>
    );
  }

  // Phase: stimulus
  if (phase === 'stimulus') {
    return (
      <div style={pageStyle}>
        <Card style={stimulusCardStyle}>
          <div style={triggerBoxStyle}>{currentTrial.trigger}</div>
          <div style={timerCircleStyle}>{countdown}</div>
          <p style={{ marginTop: '16px', color: '#777' }}>
            Get ready to choose the matching colour…
          </p>
        </Card>
      </div>
    );
  }

  // Phase: choices
  return (
    <div style={pageStyle}>
      <Card style={choicesCardStyle}>
        <h2>Pick the correct association</h2>
        <p>
          Choose the colour that best matches your automatic association with
          the trigger.
        </p>

        <div style={optionsGridStyle}>
          {currentTrial.options.map(option => {
            const isSelected = option.id === selectedOptionId;
            const optionStyle = {
              ...optionBoxBaseStyle,
              backgroundColor: option.color,
              borderColor: isSelected ? '#000' : 'transparent',
              boxShadow: isSelected
                ? '0 0 0 2px rgba(0, 0, 0, 0.4)'
                : '0 0 0 0 rgba(0, 0, 0, 0)',
            };

            return (
              <div
                key={option.id}
                style={optionStyle}
                onClick={() => handleOptionClick(option.id)}
              >
                {option.label}
              </div>
            );
          })}
        </div>

        {selectedOptionId && (
          <Button onClick={handleNextTrial} disabled={isSubmitting}>
            {trialIndex + 1 === totalTrials ? 'Finish' : 'Next'}
          </Button>
        )}

        <p style={{ marginTop: '12px', fontSize: '0.9rem', color: '#777' }}>
          Trial {trialIndex + 1} of {totalTrials}
        </p>
      </Card>
    </div>
  );
}
