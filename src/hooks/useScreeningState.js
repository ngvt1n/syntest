import { useState, useEffect } from 'react';

const defaultScreeningState = () => {return {
  consent: false,
  health: {
    drug: false,
    neuro: false,
    medical: false,
  },
  definition: 'NO', //  'YES', 'MAYBE', 'NO'
  pain: false,
  synTypes: {
    letter_color: false,
    word_color: false,
    sound_color: false,
    number_color: false,
    words_taste: false,
    sound_taste: false,
    sequence_space: false,
  },
  otherExperiences: ''
}}

export default function useScreeningState() {
  const [state, setState] = useState(() => {
    const saved = sessionStorage.getItem('screening_state');
    return saved ? JSON.parse(saved) : defaultScreeningState();
  });

  useEffect(() => {
    sessionStorage.setItem('screening_state', JSON.stringify(state));
  }, [state]);

  const updateState = (updates) => {
    setState(prev => ({ ...prev, ...updates }));
  };

  const clearState = () => {
    sessionStorage.removeItem('screening_state');
    setState(defaultScreeningState());
  };

  const handleNestedChange = (key, nestedKey, value) => {
    setState((prev) => ({
      ...prev,
      [key]: {
        ...prev[key],
        [nestedKey]: value,
      },
    }));
  };

  const handleHealthChange = (field, e) => {
    handleNestedChange('health', field, e.target.checked);
  };

  const handleSynTypesChange = (type, e) => {
    handleNestedChange('synTypes', type, e.target.value);
  };


  return {
      state,
      updateState,
      clearState,
      handleHealthChange, 
      handleSynTypesChange, 
  };
}
