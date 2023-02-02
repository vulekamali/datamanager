import React from 'react';
import createSizeModifier from './createSizeModifier.js';


export default function Facebook({ size }) {
  return (
    <svg className={`Icon${createSizeModifier(size)}`} version="1.2" baseProfile="tiny" width="0" height="0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
      <title>Twitter Link</title>
      <path d="M100 19a42 42 0 0 1-11.8 3.2c4.2-2.5 7.5-6.6 9-11.4a40 40 0 0 1-13.1 5 20.5 20.5 0 0 0-35 18.7c-17.1-.9-32.2-9-42.3-21.4a20.6 20.6 0 0 0 6.3 27.4c-3.4-.1-6.5-1-9.3-2.6v.3c0 9.9 7.1 18.2 16.4 20.1a19 19 0 0 1-9.3.3 20.5 20.5 0 0 0 19.2 14.2A41.2 41.2 0 0 1-.3 81.3a58.4 58.4 0 0 0 31.5 9.2 57.9 57.9 0 0 0 58.3-58.3l-.1-2.7c4.4-2.8 7.9-6.4 10.6-10.5zm0 0" />
    </svg>
  );
}
