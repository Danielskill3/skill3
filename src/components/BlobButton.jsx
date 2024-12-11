import React from 'react';
import '../styles/BlobButton.css';
import PropTypes from 'prop-types';

const BlobButton = ({ children, disabled, type = 'button', onClick, className = '' }) => {
  return (
    <>
      <div className="buttons">
        <div className="blob-btn-container">
          <button 
            className={`blob-btn ${className}`}
            disabled={disabled}
            type={type}
            onClick={onClick}
          >
            {children}
            <span className="blob-btn__inner">
              <span className="blob-btn__blobs">
                <span className="blob-btn__blob"></span>
                <span className="blob-btn__blob"></span>
                <span className="blob-btn__blob"></span>
                <span className="blob-btn__blob"></span>
              </span>
            </span>
          </button>
        </div>
      </div>

      <div className="svg-container">
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1">
          <defs>
            <filter id="goo">
              <feGaussianBlur in="SourceGraphic" result="blur" stdDeviation="10"></feGaussianBlur>
              <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 21 -7" result="goo"></feColorMatrix>
              <feBlend in2="goo" in="SourceGraphic" result="mix"></feBlend>
            </filter>
          </defs>
        </svg>
      </div>
    </>
  );
};
BlobButton.propTypes = {
  children: PropTypes.node,
  disabled: PropTypes.bool,
  type: PropTypes.string,
  onClick: PropTypes.func,
  className: PropTypes.string
};

export default BlobButton;
