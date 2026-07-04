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
          <stop offset="0" stopColor="#22D3EE" />
          <stop offset="1" stopColor="#4F8CFF" />
        </linearGradient>
      </defs>
      <rect width="40" height="40" rx="10" fill="#0B0D14" />
      <g className="agent-ring">
        <path
          d="M20 9 L29.5 14.5 L29.5 25.5 L20 31 L10.5 25.5 L10.5 14.5 Z"
          stroke="url(#ojas-mark-gradient)"
          strokeWidth="1.6"
          fill="none"
        />
        <circle cx="20" cy="9" r="2" fill="#22D3EE" />
      </g>
      <circle cx="20" cy="20" r="4.5" fill="url(#ojas-mark-gradient)" />
    </svg>
  );
}
