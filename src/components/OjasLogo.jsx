import React from 'react';

export default function OjasLogo({ size = 32, className = '' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      className={className}
    >
      <defs>
        <linearGradient id="ojas-mark-gradient" x1="8" y1="4" x2="32" y2="36" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#F5B841" />
          <stop offset="1" stopColor="#FF4438" />
        </linearGradient>
      </defs>
      <rect width="40" height="40" rx="10" fill="#17171C" />
      <path
        d="M20 6C20 6 12 15 12 22.5C12 27.7467 15.5817 32 20 32C24.4183 32 28 27.7467 28 22.5C28 19.6 26 17 24.5 15.2C24.7 17.5 23.6 19 22.2 19C20.6 19 20.8 16.8 21.3 14.8C21.9 12.4 21.2 9 20 6Z"
        fill="url(#ojas-mark-gradient)"
      />
    </svg>
  );
}
