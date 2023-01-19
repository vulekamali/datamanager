import { h } from 'preact';
import createSizeModifier from './createSizeModifier.js';


export default function Pin({ size }) {
  return (
    <svg className={`Icon${createSizeModifier(size)}`} version="1.2" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
      <path d="M50 0a35 35 0 0 0-34.8 39.5c3 27.4 32.5 59 32.5 59 .5.6 1 .9 1.5 1.2l1 .3 1-.3c.5-.3 1-.6 1.5-1.2 0 0 29.1-31.6 32-59.1.1-1.4.3-2.8.3-4.3A35 35 0 0 0 50 0zm0 57.7c-12.4 0-22.6-10.2-22.6-22.6S37.6 12.5 50 12.5a22.6 22.6 0 0 1 0 45.2zm0 0" />
    </svg>
  );
}
