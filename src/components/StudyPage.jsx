import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaArrowLeft } from 'react-icons/fa';
import BlobButton from './BlobButton';

const StudyPage = () => {
  const navigate = useNavigate();
  const [selectedUniversity, setSelectedUniversity] = useState('');
  const [customUniversity, setCustomUniversity] = useState('');
  const universities = [
    'University of Copenhagen',
    'Aarhus University',
    'Technical University of Denmark',
    'Aalborg University',
    'Copenhagen Business School'
  ];

  const handleContinue = () => {
    navigate('/career-path');
  };

  const handleBack = () => {
    navigate(-1);
  };

  return (
    <div className="fixed inset-0 bg-[#0A0A0F] text-white flex flex-col">
      {/* Top section with progress bar */}
      <div className="px-6 py-4">
        <div className="flex items-center gap-4">
          <button onClick={handleBack} className="text-white p-2">
            <FaArrowLeft />
          </button>
          <div className="w-full bg-[#1A1A1F] h-3 rounded-full">
            <div className="bg-blue-500 h-full rounded-full" style={{ width: '30%' }}></div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-grow px-6 py-8">
        <div className="max-w-full mx-auto space-y-8">
          {/* Title with icon */}
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
              🎓
            </div>
            <h2 className="text-2xl font-bold">Where did you study?</h2>
          </div>

          {/* University selection */}
          <div className="relative mt-8">
            <select
              value={selectedUniversity}
              onChange={(e) => setSelectedUniversity(e.target.value)}
              className="w-full p-4 bg-[#0E0E12] text-white rounded-lg border border-[#1A1A1F] appearance-none cursor-pointer focus:outline-none focus:border-blue-500"
            >
              <option value="">Start typing to select your school</option>
              {universities.map((uni, index) => (
                <option key={index} value={uni} className="bg-[#0E0E12]">{uni}</option>
              ))}
            </select>
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2 pointer-events-none">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          {/* Manual entry link */}
          <div className="text-sm mt-2">
            <span className="text-gray-400">Can't find your school?</span>{' '}
            <button 
              onClick={() => navigate('/manual-university')} 
              className="text-blue-500 hover:text-blue-400"
            >
              Add your school manually
            </button>
          </div>
        </div>
      </div>

      {/* Bottom buttons - fixed at bottom */}
      <div className="border-t border-gray-800">
        <div className="max-w-md mx-auto px-6 py-4 flex justify-between items-center">
          <button className="text-gray-400 py-2">Skip for now</button>
          <BlobButton onClick={handleContinue}>Continue</BlobButton>
        </div>
      </div>
    </div>
  );
};

export default StudyPage;
