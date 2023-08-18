import React from 'react';
import createSizeModifier from './createSizeModifier.js';


export default function Facebook({ size }) {
  return (
    <svg className={`Icon${createSizeModifier(size)}`} version="1.2" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg" width="0" height="0" viewBox="0 0 100 100">
      <title>Facebook Link</title>
      <path d="M24.7 56.3h13v41.5c0 1.1.9 2 2 2h17a2 2 0 0 0 2-2V56.3h15.2a2 2 0 0 0 2-2V37.9c0-.5-.2-1.1-.6-1.4a2 2 0 0 0-1.4-.6h-15v-9.6c0-4.6 1.1-7 7.1-7h8.7a2 2 0 0 0 2-2V1.9A2 2 0 0 0 75.3 0H59C46 1.2 37.8 10.5 37.8 24.5v11.3h-13a2 2 0 0 0-2 2v16.4c-.1 1.2.8 2.1 1.9 2.1z" />
    </svg>
  );
}
