import React, { useState, useEffect } from 'react';
import BlobButton from './BlobButton';

const ManualUniversityPage = () => {
  const [formData, setFormData] = useState({
    schoolName: '',
    email: '',
    phone: '',
    country: '',
    region: '',
    website: '',
  });
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCountries = async () => {
      try {
        const response = await fetch('https://restcountries.com/v3.1/all');
        const data = await response.json();
        const sortedCountries = data.map(country => country.name.common).sort();
        setCountries(sortedCountries);
      } catch (error) {
        console.error('Error fetching countries:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCountries();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch('/api/schools', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        console.log('University details saved successfully.');
        // Optionally, redirect or update the UI
      } else {
        console.error('Failed to save university details.');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="fixed inset-0 flex bg-[#0A0A0F]">
      {/* Left side illustration */}
      <div className="w-1/2 h-screen flex items-center justify-center">
        <img 
          src="/welcome.jpeg" 
          alt="University illustration" 
          className="h-full w-full object-contain"
        />
      </div>

      {/* Right side form */}
      <div className="w-1/2 h-screen overflow-y-auto px-16 py-8 text-white">
        <h1 className="text-2xl mb-16 text-center">Tell us about your University!</h1>
        
        <div className="flex flex-col justify-between h-[calc(100vh-12rem)]">
          <div className="space-y-12">
            <div className="relative">
              <input
                type="text"
                name="schoolName"
                value={formData.schoolName}
                onChange={handleChange}
                placeholder=" "
                className="w-full bg-transparent border border-[#2A2A2F] rounded p-3 focus:outline-none peer"
              />
              <label className="absolute text-gray-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-[#0A0A0F] px-2 peer-focus:px-2 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:-translate-y-4 peer-focus:scale-75 peer-focus:text-gray-400 left-1">
                School Name
              </label>
            </div>

            <div className="relative">
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder=" "
                className="w-full bg-transparent border border-[#2A2A2F] rounded p-3 focus:outline-none peer"
              />
              <label className="absolute text-gray-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-[#0A0A0F] px-2 peer-focus:px-2 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:-translate-y-4 peer-focus:scale-75 peer-focus:text-gray-400 left-1">
                Email Address
              </label>
            </div>

            <div className="relative">
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder=" "
                className="w-full bg-transparent border border-[#2A2A2F] rounded p-3 focus:outline-none peer"
              />
              <label className="absolute text-gray-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-[#0A0A0F] px-2 peer-focus:px-2 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:-translate-y-4 peer-focus:scale-75 peer-focus:text-gray-400 left-1">
                Phone number
              </label>
            </div>

            <div className="relative">
              <select
                name="country"
                value={formData.country}
                onChange={handleChange}
                className="w-full bg-black text-white border border-[#2A2A2F] rounded p-3 focus:outline-none peer appearance-none"
              >
                <option value="" disabled></option>
                {countries.map((country) => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
              <label className="absolute text-gray-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-[#0A0A0F] px-2 peer-focus:px-2 peer-focus:text-gray-400 left-1">
                Country
              </label>
            </div>

            <div className="relative">
              <input
                type="text"
                name="region"
                value={formData.region}
                onChange={handleChange}
                placeholder=" "
                className="w-full bg-black text-white border border-[#2A2A2F] rounded p-3 focus:outline-none peer"
              />
              <label className="absolute text-gray-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-[#0A0A0F] px-2 peer-focus:px-2 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:-translate-y-4 peer-focus:scale-75 peer-focus:text-gray-400 left-1">
                Region/State/Province
              </label>
            </div>

            <div className="relative">
              <input
                type="url"
                name="website"
                value={formData.website}
                onChange={handleChange}
                placeholder=" "
                className="w-full bg-transparent border border-[#2A2A2F] rounded p-3 focus:outline-none peer"
              />
              <label className="absolute text-gray-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-[#0A0A0F] px-2 peer-focus:px-2 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:-translate-y-4 peer-focus:scale-75 peer-focus:text-gray-400 left-1">
                School's website URL
                <span className="text-sm text-gray-400 ml-1">(optional)</span>
              </label>
            </div>
          </div>

          <BlobButton
            onClick={handleSubmit}
            className="w-full mt-8"
          >
            Save
          </BlobButton>
        </div>
      </div>
    </div>
  );
};

export default ManualUniversityPage;