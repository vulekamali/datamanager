import React from 'react';
import createSizeModifier from './createSizeModifier.js';


export default function Download({ size }) {
  return (
    <svg className={`Icon${createSizeModifier(size)}`} version="1.2" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg" width="0" height="0" viewBox="0 0 100 100">
      <path d="M50.01 0A49.857 49.857 0 0 0 0 50.01C0 77.73 22.27 100 50.01 100 77.73 100 100 77.73 100 50.01 100 22.27 77.73 0 50.01 0zm22.03 58.41L51.59 78.87c-.45.46-1.13.68-1.58.68-.69 0-1.15-.22-1.6-.68L27.95 58.41c-.45-.46-.68-.91-.68-1.59s.22-1.13.68-1.59l3.19-3.18c.91-.91 2.28-.91 3.17 0l9.1 9.09c.68.69 2.04.23 2.04-.91v-37.5c0-1.36.91-2.27 2.27-2.27h4.54c1.37 0 2.28.91 2.28 2.27v37.73c0 .91 1.14 1.59 2.05.91l9.09-9.1c.91-.91 2.27-.91 3.17 0l3.18 3.18c.46.46.69.91.69 1.59.01.46-.22.91-.68 1.37zm0 0"/>
    </svg>
  );
}
