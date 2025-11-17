// src/pages/trigger_color/SpeedCongruencyInstructions.jsx

import React from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';

export default function SpeedCongruencyInstructions() {
  const navigate = useNavigate();

  const handleBeginClick = () => {
    navigate('/tests/color/speed-congruency');
  };

  const pageStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 'calc(100vh - 120px)', // leave room for header/footer
  };

  const cardStyle = {
    maxWidth: '640px',
    width: '100%',
    padding: '32px',
  };

  const bodyTextStyle = {
    marginBottom: '12px',
    lineHeight: 1.5,
  };

  const footerStyle = {
    marginTop: '12px',
    textAlign: 'center',
    fontSize: '0.85rem',
    color: '#777',
  };

  return (
    <div style={pageStyle}>
      <Card style={cardStyle} title="Speed Congruency Test">
        <p style={bodyTextStyle}>
          In this test, you will see one of your personal triggers on the screen
          (for example, a word, letter, or number). As quickly and accurately
          as possible, choose the colour that you naturally associate with that
          trigger.
        </p>

        <p style={bodyTextStyle}>
          Your reaction time and accuracy will be recorded for research
          purposes. Please sit comfortably, try to minimise distractions, and
          respond with your first, instinctive colour choice.
        </p>

        <p style={bodyTextStyle}>
          When you are ready, click the button below to begin. You can stop the
          test at any time.
        </p>

        <Button
          onClick={handleBeginClick}
          style={{ width: '100%', marginTop: '16px' }}
        >
          Begin Test
        </Button>

        <p style={footerStyle}>You can stop at any time.</p>
      </Card>
    </div>
  );
}
