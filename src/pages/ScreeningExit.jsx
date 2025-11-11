import { useParams, useNavigate } from 'react-router-dom';
import Button from '../components/ui/Button';
import '../styles/app.css';

export default function ScreeningExit() {
  const exitReasons = {
    A: {
      "chip_label": "Exit: A",
      "heading": "Thanks for your time",
      "lead": "You indicated no synesthetic experience, so you are unable to continue in this study.",
      "thanks_line": "",
      "bullets": "",
      "note": "",
    },
    BC: {
      "chip_label": "Exit: B/C",
      "heading": "Not eligible (B/C)",
      "thanks_line": "Thanks for your time!",
      "lead": "Based on your health and substances responses, you are not eligible for this study.",
      "bullets": "",
      "note": "",
    },
    D: {
      "chip_label": "Exit: D",
      "heading": "Not eligible (D)",
      "thanks_line": "Thanks for your time!",
      "lead": "Experiences triggered by pain or emotions are excluded from this screening.",
      "bullets": "",
      "note": "",
    },
    NONE: {
      "chip_label": "Exit: None",
      "heading": "No eligible types selected",
      "thanks_line": "Thanks for your time!",
      "lead": "You didn’t select Yes or Maybe for any supported types, so there isn’t a follow-up task to run.",
      "bullets": "",
      "note": "",
    },
  };

  const { code } = useParams();
  const exitData = exitReasons[code] || exitReasons.A;
  const navigate = useNavigate();

  return (
    <div className="container container-centered container-md">
      <div className='card'>
        <span
          className='chip'
          label={exitData.chipLabel}
          variant="info"></span>
        <h2 className="h3">{exitData.heading}</h2>

        {exitData.thanksLine && (
          <p className="lead font-bold">{exitData.thanksLine}</p>
        )}

        {exitData.lead && (
          <p style={{ marginTop: '6px' }}>{exitData.lead}</p>
        )}

        {exitData.bullets && (
          <ul className="summary-list" style={{ margin: '10px 0 14px' }}>
            {exitData.bullets.map((bullet, idx) => (
              <li key={idx}>{bullet}</li>
            ))}
          </ul>
        )}

        {exitData.note && (
          <div className="note-panel">
            <div className="note-title">Details</div>
            <p style={{ margin: '6px 0 0' }}>{exitData.note}</p>
          </div>
        )}

        <div className="actions" style={{ marginTop: '16px' }}>
          <Button onClick={() => navigate('/screening/0')}>
            Return to start
          </Button>
          <Button variant="secondary" onClick={() => navigate('/')}>
            Close
          </Button>
        </div>

        <p className="footnote" style={{ marginTop: '12px' }}>
          Questions? <a className="footer-link" href="#">Contact support</a>
        </p>
      </div>
    </div>

  );
}
