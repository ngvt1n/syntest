import { useNavigate } from 'react-router-dom';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Progress from '../ui/Progress';
import '../../styles/app.css';

export default function ScreeningStep({
  step,
  totalSteps,
  chip,
  title,
  children,
  onNext,
  onBack,
  nextLabel = 'Continue',
  backLabel = 'Back',
  showActions = true
}) {
  const navigate = useNavigate();

  const handleNext = () => {
    if (onNext) {
      onNext();
    } else {
      navigate(`/screening/${step + 1}`);
    }
  };

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      navigate(`/screening/${step - 1}`);
    }
  };

  return (
    <div className="container container-centered container-md">
      {step > 0 && (
        <Progress current={step} total={totalSteps} />
      )}

      <Card chip={chip} title={title}>
        {children}

        {showActions && (
          <div className="actions actions-between">
            {step > 0 && (
              <Button variant="secondary" onClick={handleBack}>
                {backLabel}
              </Button>
            )}
            <Button onClick={handleNext}>
              {nextLabel}
            </Button>
          </div>
        )}
      </Card>

      <p className="text-muted text-center mt-3">
        Questions? <a href="#">Contact support</a>
      </p>
    </div>
  );
}
