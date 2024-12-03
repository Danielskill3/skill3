import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import BlobButton from './BlobButton';
import { FaArrowLeft } from 'react-icons/fa';

const PersonalityPage = () => {
  const navigate = useNavigate();
  const [selectedPersonality, setSelectedPersonality] = useState(null);

  const personalityTypes = {
    Analysts: ['Architect', 'Logician', 'Commander', 'Debater'],
    Diplomats: ['Advocate', 'Mediator', 'Protagonist', 'Campaigner'],
    Sentinels: ['Logistician', 'Defender', 'Executive', 'Consul'],
    Explorers: ['Virtuoso', 'Adventurer', 'Entrepreneur', 'Entertainer'],
  };

  const handleSelect = (type) => {
    setSelectedPersonality(type);
  };

  const handleContinue = async () => {
    if (selectedPersonality) {
      try {
        const response = await fetch(`${import.meta.env.NODE_ENV === 'production' ? 'https://skill3.onrender.com/api/personality' : 'http://localhost:8000/api/personality'}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ personality: selectedPersonality }),
        });

        if (response.ok) {
          navigate('/work-model');
        } else {
          console.error('Failed to save personality type');
        }
      } catch (error) {
        console.error('Error:', error);
      }
    }
  };

  const handleSkip = () => {
    navigate('/work-model');
  };

  return (
    <div className="fixed inset-0 bg-[#0A0A0F] text-white flex flex-col">
      {/* Top section with progress bar */}
      <div className="px-6 py-4">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="text-white p-2">
            <FaArrowLeft />
          </button>
          <div className="w-full bg-[#1A1A1F] h-2 rounded-full">
            <div className="bg-blue-500 h-full rounded-full" style={{ width: '50%' }}></div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-grow px-6 py-8 overflow-y-auto pb-24">
        <div className="flex items-center gap-4 mb-8">
          <div className="w-8 h-8 bg-[#1A1A1F] rounded-lg flex items-center justify-center">
            🌟
          </div>
          <h1 className="text-2xl font-medium">What's your Personality?</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          {Object.entries(personalityTypes).map(([category, types]) => (
            <div key={category} className="space-y-4">
              <h2 className="text-xl font-semibold text-left">{category}</h2>
              <div className="grid grid-cols-2 gap-6">
                {types.map((type) => (
                  <button
                    key={type}
                    onClick={() => handleSelect(type)}
                    className={`py-3 px-4 bg-transparent border border-[#2A2A2F] rounded-lg hover:border-gray-600 transition-colors text-center text-lg ${
                      selectedPersonality === type ? 'bg-[#0066FF] text-white' : ''
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 text-sm">
          Don't know what your personality is?{' '}
          <a href="#" className="text-blue-500 hover:text-blue-400">Take a personality test</a>
        </div>
      </div>

      {/* Bottom buttons - fixed at bottom */}
      <div className="fixed bottom-0 left-0 right-0 border-t border-[#2A2A2F] bg-[#0A0A0F]">
        <div className="max-w-full mx-auto px-6 py-4 flex flex-col-reverse md:flex-row justify-between items-center gap-2 md:gap-6">
          <button onClick={handleSkip} className="text-gray-400 py-2 hover:text-gray-300 transition-colors text-lg">Skip for now</button>
          <BlobButton
            onClick={handleContinue}
            disabled={!selectedPersonality}
          >
            Continue
          </BlobButton>
        </div>
      </div>
    </div>
  );
};

export default PersonalityPage;
