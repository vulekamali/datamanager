import React from 'react';
import createSizeModifier from './createSizeModifier.js';


export default function Download({ size }) {
  return (
    <svg className={`Icon${createSizeModifier(size)}`} version="1.2" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
      <path d="M68.8 50l28.1-28.1a10.7 10.7 0 0 0 0-15l-3.7-3.7a10.7 10.7 0 0 0-15.1-.1L50 31.2 21.9 3.1a10.8 10.8 0 0 0-15.1 0L3.1 6.8a10.7 10.7 0 0 0 0 15L31.2 50 3.1 78.1a10.7 10.7 0 0 0 0 15l3.7 3.7a10.7 10.7 0 0 0 15 0l28.2-28 28.1 28.1a10.7 10.7 0 0 0 15 0l3.7-3.7a10.7 10.7 0 0 0 0-15L68.8 50zm0 0" />
    </svg>
  );
}
