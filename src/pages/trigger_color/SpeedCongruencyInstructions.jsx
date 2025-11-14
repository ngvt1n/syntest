// export default function SpeedCongruencyInstructions() {
//   return (
//     <div>
//       <h1>Speed Congruency Instructions</h1>
//       <p>Instructions coming soon...</p>
//     </div>
//   )
// }


// src/pages/trigger_color/SpeedCongruencyInstructions.jsx
import { useNavigate } from "react-router-dom";

export default function SpeedCongruencyInstructions() {
  const navigate = useNavigate();

  const handleStart = () => {
    // This should match the route you/your team define for the test page
    navigate("/speed-congruency/test");
  };

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#f9fafb" }}>
      <div
        style={{
          maxWidth: "900px",
          margin: "0 auto",
          padding: "4rem 2rem",
          textAlign: "center",
        }}
      >
        {/* Title */}
        <h1
          style={{
            fontSize: "2.5rem",
            fontWeight: "bold",
            marginBottom: "2rem",
            color: "#111827",
          }}
        >
          Speed Congruency Test
        </h1>

        {/* Intro description */}
        <p
          style={{
            fontSize: "1.125rem",
            marginBottom: "2rem",
            lineHeight: 1.7,
            color: "#4b5563",
          }}
        >
          In this test, we measure how quickly and consistently you match your
          automatic color associations to different triggers (such as words or
          numbers) that were identified in the previous Color Consistency Test.
        </p>

        {/* Step-by-step instructions */}
        <ul
          style={{
            textAlign: "left",
            maxWidth: "650px",
            margin: "0 auto 2.5rem",
            lineHeight: 1.9,
            fontSize: "1rem",
            color: "#374151",
          }}
        >
          <li style={{ marginBottom: "0.75rem" }}>
            You will see <strong>one of your personal triggers</strong> (for
            example, a word or number) in the center of the screen.
          </li>
          <li style={{ marginBottom: "0.75rem" }}>
            The trigger will appear by itself for a few seconds. Use this time
            to focus on the color you automatically experience for that trigger.
          </li>
          <li style={{ marginBottom: "0.75rem" }}>
            After that, the trigger disappears and several{" "}
            <strong>color options</strong> will appear.
          </li>
          <li style={{ marginBottom: "0.75rem" }}>
            As <strong>quickly</strong> as you can, click the color that best
            matches your internal association. We record{" "}
            <strong>both your accuracy and your reaction time</strong>.
          </li>
          <li>
            Try to respond based on your <strong>first instinct</strong>, not by
            thinking too hard or choosing a “nice” color.
          </li>
        </ul>

        {/* Tips */}
        <p
          style={{
            marginBottom: "3rem",
            color: "#6b7280",
            fontSize: "0.95rem",
          }}
        >
          ⏱️ Estimated time: about 3–5 minutes. For best results, use a
          laptop/desktop, sit somewhere quiet, and avoid distractions.
        </p>

        {/* Start button */}
        <button
          type="button"
          onClick={handleStart}
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
          Begin Speed Congruency Test
        </button>
      </div>
    </div>
  );
}
