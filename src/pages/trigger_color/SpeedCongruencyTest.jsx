// export default function SpeedCongruencyTest() {
//   return (
//     <div>
//       <h1>Speed Congruency Test</h1>
//       <p>Test coming soon...</p>
//     </div>
//   )
// }

// src/pages/trigger_color/SpeedCongruencyTest.jsx
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { speedCongruencyService } from "../services/speedcongruency";

export default function SpeedCongruencyTest() {
  const [trial, setTrial] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showStimulus, setShowStimulus] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const stimulusTimeoutRef = useRef(null);
  const startTimeRef = useRef(null);

  const navigate = useNavigate();

  // Load first trial on mount
  useEffect(() => {
    loadNextTrial();

    return () => {
      if (stimulusTimeoutRef.current) {
        clearTimeout(stimulusTimeoutRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadNextTrial() {
    setIsLoading(true);
    setError(null);
    setFeedback(null);

    try {
      const data = await speedCongruencyService.getNextTrial();

      // Handle "no more trials" in several common formats
      if (!data || data.done || data.isComplete) {
        setIsComplete(true);
        setTrial(null);
        return;
      }

      const nextTrial = data.trial || data;

      setTrial(nextTrial);
      setShowStimulus(true);

      // reset and start new 3-second phase for the trigger
      if (stimulusTimeoutRef.current) {
        clearTimeout(stimulusTimeoutRef.current);
      }

      stimulusTimeoutRef.current = setTimeout(() => {
        setShowStimulus(false);
        startTimeRef.current = performance.now();
      }, 3000);
    } catch (err) {
      console.error(err);
      setError("Something went wrong loading the next trial. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleChoice(option) {
    // Prevent clicking when still showing trigger or while submitting
    if (showStimulus || isSubmitting || !trial) return;

    setIsSubmitting(true);
    setError(null);

    const endTime = performance.now();
    const reactionTimeMs = startTimeRef.current
      ? Math.round(endTime - startTimeRef.current)
      : null;

    const payload = {
      trialId: trial.id ?? trial.trial_id ?? null,
      triggerId: trial.triggerId ?? trial.trigger_id ?? null,
      selectedColorId: option.id ?? option.color_id ?? null,
      selectedColorHex:
        option.hex ?? option.hexCode ?? option.hex_code ?? null,
      reactionTimeMs,
    };

    try {
      const response = await speedCongruencyService.submitTrial(payload);

      if (response && typeof response.correct === "boolean") {
        setFeedback(response.correct ? "Correct!" : "Not consistent with your stored color.");
      }

      // brief feedback pause
      await new Promise((resolve) => setTimeout(resolve, 400));

      setIsSubmitting(false);
      await loadNextTrial();
    } catch (err) {
      console.error(err);
      setError("Something went wrong saving your answer. Please try again.");
      setIsSubmitting(false);
    }
  }

  function handleBackToInstructions() {
    navigate("/speed-congruency/instructions");
  }

  // ---------- UI helpers ----------

  const getTriggerText = () =>
    trial?.trigger ?? trial?.word ?? trial?.stimulus ?? "—";

  const getOptions = () =>
    trial?.colors || trial?.options || trial?.choices || [];

  const getTrialIndex = () =>
    trial?.index ?? trial?.trialNumber ?? trial?.trial_index ?? null;

  const getTrialTotal = () => trial?.totalTrials ?? trial?.total ?? null;

  // ---------- Render ----------

  if (isComplete) {
    return (
      <div style={{ minHeight: "100vh", backgroundColor: "#f9fafb" }}>
        <div
          style={{
            maxWidth: "800px",
            margin: "0 auto",
            padding: "4rem 2rem",
            textAlign: "center",
          }}
        >
          <h1
            style={{
              fontSize: "2.5rem",
              fontWeight: "bold",
              marginBottom: "1.5rem",
              color: "#16a34a",
            }}
          >
            Speed Congruency Test Complete
          </h1>
          <p
            style={{
              fontSize: "1.125rem",
              marginBottom: "2.5rem",
              color: "#4b5563",
            }}
          >
            Thank you for completing the Speed Congruency Test. Your responses
            and reaction times have been recorded.
          </p>
          <button
            type="button"
            onClick={handleBackToInstructions}
            style={{
              background: "#2563eb",
              color: "white",
              padding: "0.875rem 2.5rem",
              border: "none",
              fontSize: "1rem",
              fontWeight: 600,
              cursor: "pointer",
              boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
              borderRadius: "4px",
            }}
          >
            Back to Instructions
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#f9fafb" }}>
      <div
        style={{
          maxWidth: "1000px",
          margin: "0 auto",
          padding: "3rem 2rem",
        }}
      >
        {/* Header */}
        <header style={{ textAlign: "center", marginBottom: "2rem" }}>
          <h1
            style={{
              fontSize: "2.25rem",
              fontWeight: "bold",
              marginBottom: "0.75rem",
              color: "#111827",
            }}
          >
            Speed Congruency Test
          </h1>
          <p
            style={{
              fontSize: "0.95rem",
              color: "#6b7280",
              maxWidth: "650px",
              margin: "0 auto",
              lineHeight: 1.6,
            }}
          >
            Focus on the trigger while it is shown. When the color choices
            appear, click the color that best matches your automatic
            association as quickly as you can.
          </p>
        </header>

        {error && (
          <div
            style={{
              marginBottom: "1.5rem",
              padding: "0.75rem 1rem",
              backgroundColor: "#fee2e2",
              color: "#b91c1c",
              borderRadius: "4px",
              fontSize: "0.9rem",
            }}
          >
            {error}
          </div>
        )}

        {isLoading && !trial ? (
          <div
            style={{
              textAlign: "center",
              fontSize: "1rem",
              color: "#6b7280",
              marginTop: "2rem",
            }}
          >
            Loading next trial…
          </div>
        ) : (
          trial && (
            <div>
              {/* Trial status */}
              <div
                style={{
                  fontSize: "0.875rem",
                  color: "#6b7280",
                  marginBottom: "1.5rem",
                  display: "flex",
                  justifyContent: "center",
                  gap: "1.5rem",
                }}
              >
                {getTrialIndex() && (
                  <span>
                    Trial <strong>{getTrialIndex()}</strong>
                    {getTrialTotal() && (
                      <>
                        {" "}
                        / <strong>{getTrialTotal()}</strong>
                      </>
                    )}
                  </span>
                )}
              </div>

              {/* Main card */}
              <div
                style={{
                  backgroundColor: "white",
                  borderRadius: "8px",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
                  padding: "2.5rem 2rem",
                }}
              >
                {showStimulus ? (
                  // Phase 1: Trigger only
                  <div style={{ textAlign: "center" }}>
                    <p
                      style={{
                        fontSize: "0.95rem",
                        color: "#6b7280",
                        marginBottom: "1.25rem",
                      }}
                    >
                      Focus on this trigger and notice the color you
                      automatically associate with it:
                    </p>
                    <div
                      style={{
                        fontSize: "3rem",
                        fontWeight: "bold",
                        color: "#111827",
                        marginBottom: "0.75rem",
                        wordBreak: "break-word",
                      }}
                    >
                      {getTriggerText()}
                    </div>
                    <p
                      style={{
                        fontSize: "0.85rem",
                        color: "#9ca3af",
                      }}
                    >
                      Color choices will appear in a moment…
                    </p>
                  </div>
                ) : (
                  // Phase 2: Color choices
                  <div style={{ textAlign: "center" }}>
                    <p
                      style={{
                        fontSize: "0.95rem",
                        color: "#6b7280",
                        marginBottom: "1.25rem",
                      }}
                    >
                      Click the color that best matches your automatic
                      association for:
                    </p>
                    <div
                      style={{
                        fontSize: "2rem",
                        fontWeight: "bold",
                        color: "#111827",
                        marginBottom: "1.5rem",
                        wordBreak: "break-word",
                      }}
                    >
                      {getTriggerText()}
                    </div>

                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(auto-fit, minmax(80px, 1fr))",
                        gap: "1rem",
                        maxWidth: "500px",
                        margin: "0 auto 1rem",
                      }}
                    >
                      {getOptions().map((opt, idx) => {
                        const key =
                          opt.id ??
                          opt.color_id ??
                          opt.hex ??
                          opt.hexCode ??
                          opt.hex_code ??
                          idx;

                        const bgColor =
                          opt.hex ?? opt.hexCode ?? opt.hex_code ?? "#d1d5db";

                        const label = opt.label ?? opt.name ?? bgColor;

                        return (
                          <button
                            key={key}
                            type="button"
                            onClick={() => handleChoice(opt)}
                            disabled={isSubmitting}
                            style={{
                              width: "80px",
                              height: "80px",
                              borderRadius: "8px",
                              border: "2px solid #111827",
                              backgroundColor: bgColor,
                              cursor: isSubmitting ? "not-allowed" : "pointer",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              fontSize: "0.75rem",
                              color: "#111827",
                              fontWeight: 500,
                              boxShadow:
                                "0 1px 2px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.1)",
                            }}
                          >
                            <span
                              style={{
                                backgroundColor: "rgba(255,255,255,0.7)",
                                padding: "0.1rem 0.25rem",
                                borderRadius: "2px",
                              }}
                            >
                              {label}
                            </span>
                          </button>
                        );
                      })}
                    </div>

                    {feedback && (
                      <p
                        style={{
                          fontSize: "0.9rem",
                          color: "#4b5563",
                          marginTop: "0.75rem",
                        }}
                      >
                        {feedback}
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
          )
        )}
      </div>
    </div>
  );
}

