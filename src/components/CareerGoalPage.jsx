import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import BlobButton from './BlobButton';
import { FaArrowLeft } from 'react-icons/fa';

const CareerGoalPage = () => {
  const navigate = useNavigate();
  const [selectedGoal, setSelectedGoal] = useState('');

  const handleContinue = () => {
    if (selectedGoal) {
      navigate('/industry');
    }
  };

  const handleSkip = () => {
    navigate('/industry');
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
            <div className="bg-blue-500 h-full rounded-full" style={{ width: '80%' }}></div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-grow px-6 py-8 overflow-y-auto pb-24">
        <div className="flex items-center gap-4 mb-8">
          <div className="text-4xl">💼</div>
          <h1 className="text-4xl font-bold text-left">What's your long term career goal?</h1>
        </div>

        <div className="w-full">
          <select
            value={selectedGoal}
            onChange={(e) => setSelectedGoal(e.target.value)}
            className="w-full py-3 px-4 bg-black border border-[#2A2A2F] rounded-lg hover:border-gray-600 transition-colors text-xl"
          >
            <option value="">I want to become a ...</option>
            <option value="Engineer">Engineer</option>
            <option value="Designer">Designer</option>
            <option value="Manager">Manager</option>
            <option value="Entrepreneur">Entrepreneur</option>
          </select>
        </div>
      </div>

      {/* Bottom buttons - fixed at bottom */}
      <div className="fixed bottom-0 left-0 right-0 border-t border-[#2A2A2F] bg-[#0A0A0F]">
        <div className="max-w-full mx-auto px-6 py-4 flex flex-col-reverse md:flex-row justify-between items-center gap-2 md:gap-6">
          <button onClick={handleSkip} className="text-gray-400 py-2 hover:text-gray-300 transition-colors text-lg">Skip for now</button>
          <BlobButton
            onClick={handleContinue}
            disabled={!selectedGoal}
          >
            Continue
          </BlobButton>
        </div>
      </div>
    </div>
  );
};

export default CareerGoalPage;