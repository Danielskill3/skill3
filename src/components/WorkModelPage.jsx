import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import BlobButton from './BlobButton';
import { FaArrowLeft } from 'react-icons/fa';

const WorkModelPage = () => {
  const navigate = useNavigate();
  const [selectedModel, setSelectedModel] = useState(null);

  const workModels = ['In person', 'Remote', 'Hybrid'];

  const handleSelect = (model) => {
    setSelectedModel(model);
  };


  const handleContinue = async () => {
    if (selectedModel) {
      try {
        const response = await fetch('https://skill3.onrender.com/api/work-model', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ model: selectedModel }),
        });

        if (response.ok) {
          navigate('/career-goal');
        } else {
          console.error('Failed to save work model');
        }
      } catch (error) {
        console.error('Error:', error);
      }
    }
  };

  const handleSkip = () => {
    navigate('/next-step');
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
            <div className="bg-blue-500 h-full rounded-full" style={{ width: '70%' }}></div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-grow px-6 py-8 overflow-y-auto pb-24">
        <div className="flex flex-col items-start gap-4 mb-8">
          <div className="text-4xl">💻 What's your preferred work model?</div>
        </div>

        <div className="flex flex-col md:flex-row justify-between w-full gap-4">
          {workModels.map((model) => (
            <button
              key={model}
              onClick={() => handleSelect(model)}
              className={`flex-1 py-3 px-4 bg-transparent border border-[#2A2A2F] rounded-lg hover:border-gray-600 transition-colors text-center text-2xl ${
                selectedModel === model ? 'bg-[#0066FF] text-white' : ''
              }`}
            >
              {model}
            </button>
          ))}
        </div>
      </div>

      {/* Bottom buttons - fixed at bottom */}
      <div className="fixed bottom-0 left-0 right-0 border-t border-[#2A2A2F] bg-[#0A0A0F]">
        <div className="max-w-full mx-auto px-6 py-4 flex flex-col-reverse md:flex-row justify-between items-center gap-2 md:gap-6">
          <button onClick={handleSkip} className="text-gray-400 py-2 hover:text-gray-300 transition-colors text-lg">Skip for now</button>
          <BlobButton
            onClick={handleContinue}
            disabled={!selectedModel}
          >
            Continue
          </BlobButton>
        </div>
      </div>
    </div>
  );
};

export default WorkModelPage;
