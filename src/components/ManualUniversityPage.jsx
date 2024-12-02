import React, { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaArrowLeft } from 'react-icons/fa';
import BlobButton from './BlobButton';

// Only keep regions data as it's more specific to universities
const regionsByCountry = {
  "United States": [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming"
  ],
  "United Kingdom": [
    "England", "Scotland", "Wales", "Northern Ireland"
  ],
  "Canada": [
    "Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador",
    "Nova Scotia", "Ontario", "Prince Edward Island", "Quebec", "Saskatchewan"
  ],
};

const ManualUniversityPage = () => {
  const navigate = useNavigate();
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    schoolName: '',
    emailAddress: '',
    phoneNumber: '',
    country: '',
    region: '',
    websiteURL: ''
  });

  // Fetch countries on component mount
  useEffect(() => {
    const fetchCountries = async () => {
      try {
        const response = await fetch('https://restcountries.com/v3.1/all');
        const data = await response.json();
        
        // Sort countries by name
        const sortedCountries = data
          .map(country => country.name.common)
          .sort((a, b) => a.localeCompare(b));
        
        setCountries(sortedCountries);
      } catch (error) {
        console.error('Error fetching countries:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCountries();
  }, []);

  // Get available regions based on selected country
  const availableRegions = useMemo(() => {
    return regionsByCountry[formData.country] || [];
  }, [formData.country]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
      // Reset region if country changes
      ...(name === 'country' ? { region: '' } : {})
    }));
  };

  const handleBack = () => {
    navigate(-1);
  };

  const handleSave = async () => {
    try {
      const response = await fetch(`${import.meta.env.NODE_ENV === 'production' ? 'https://skill3.onrender.com/api/university' : 'http://localhost:8000/api/university'}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        console.log('University details saved successfully');
        navigate('/career-path');
      } else {
        console.error('Failed to save university details');
      }
    } catch (error) {
      console.error('Error:', error);
    }
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
      <div className="flex-grow px-6 py-8 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-semibold mb-8">Tell us about your University!</h1>
          
          <div className="flex flex-col md:flex-row justify-between gap-12">
            {/* Left side - illustration */}
            <div className="w-full md:w-1/2 flex items-center justify-center mb-6 md:mb-0">
              <img 
                src="/welcome.jpeg"
                alt="University illustration" 
                className="max-w-full h-auto"
              />
            </div>

            {/* Right side - form */}
            <div className="w-full md:w-1/2 space-y-6">
              <div className="relative mb-8">
                <input
                  type="text"
                  name="schoolName"
                  value={formData.schoolName}
                  onChange={handleInputChange}
                  className="w-full pt-6 pb-2 px-4 bg-[#1A1A1F] text-white rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500 peer"
                  placeholder=" "
                />
                <label className="absolute left-4 -top-4 text-gray-500 text-sm transition-all peer-placeholder-shown:top-3 peer-placeholder-shown:text-base peer-focus:-top-4 peer-focus:text-sm">
                  School Name
                </label>
              </div>

              <div className="relative mb-8">
                <input
                  type="email"
                  name="emailAddress"
                  value={formData.emailAddress}
                  onChange={handleInputChange}
                  className="w-full pt-6 pb-2 px-4 bg-[#1A1A1F] text-white rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500 peer"
                  placeholder=" "
                />
                <label className="absolute left-4 -top-4 text-gray-500 text-sm transition-all peer-placeholder-shown:top-3 peer-placeholder-shown:text-base peer-focus:-top-4 peer-focus:text-sm">
                  Email Address
                </label>
              </div>

              <div className="relative mb-8">
                <input
                  type="tel"
                  name="phoneNumber"
                  value={formData.phoneNumber}
                  onChange={handleInputChange}
                  className="w-full pt-6 pb-2 px-4 bg-[#1A1A1F] text-white rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500 peer"
                  placeholder=" "
                />
                <label className="absolute left-4 -top-4 text-gray-500 text-sm transition-all peer-placeholder-shown:top-3 peer-placeholder-shown:text-base peer-focus:-top-4 peer-focus:text-sm">
                  Phone Number
                </label>
              </div>

              <div className="relative mb-8">
                <select
                  name="country"
                  value={formData.country}
                  onChange={handleInputChange}
                  className="w-full pt-6 pb-2 px-4 bg-[#1A1A1F] text-white rounded-lg border border-gray-700 appearance-none cursor-pointer focus:outline-none focus:border-blue-500 peer"
                  disabled={loading}
                >
                  {loading ? (
                    <option value="">Loading countries...</option>
                  ) : (
                    <>
                      <option value="">Select a country</option>
                      {countries.map((country) => (
                        <option key={country} value={country}>{country}</option>
                      ))}
                    </>
                  )}
                </select>
                <label className="absolute left-4 -top-4 text-gray-500 text-sm transition-all peer-placeholder-shown:top-3 peer-placeholder-shown:text-base peer-focus:-top-4 peer-focus:text-sm">
                  Country
                </label>
              </div>

              <div className="relative mb-8">
                <input
                  type="text"
                  name="region"
                  value={formData.region}
                  onChange={handleInputChange}
                  className="w-full pt-6 pb-2 px-4 bg-[#1A1A1F] text-white rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500 peer"
                  placeholder=" "
                />
                <label className="absolute left-4 -top-4 text-gray-500 text-sm transition-all peer-placeholder-shown:top-3 peer-placeholder-shown:text-base peer-focus:-top-4 peer-focus:text-sm">
                  Region/State/Province/County
                </label>
              </div>

              <div className="relative mb-8">
                <input
                  type="url"
                  name="websiteURL"
                  value={formData.websiteURL}
                  onChange={handleInputChange}
                  className="w-full pt-6 pb-2 px-4 bg-[#1A1A1F] text-white rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500 peer"
                  placeholder=" "
                />
                <label className="absolute left-4 -top-4 text-gray-500 text-sm transition-all peer-placeholder-shown:top-3 peer-placeholder-shown:text-base peer-focus:-top-4 peer-focus:text-sm">
                  School's website URL (optional)
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom button */}
      <div className="border-t border-gray-700">
        <div className="max-w-full mx-auto px-6 py-4 flex justify-end">
          <BlobButton onClick={handleSave}>Save</BlobButton>
        </div>
      </div>
    </div>
  );
};

export default ManualUniversityPage;
