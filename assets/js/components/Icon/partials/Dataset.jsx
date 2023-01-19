import { h } from 'preact';
import createSizeModifier from './createSizeModifier.js';


export default function Download({ size }) {
  return (
    <svg className={`Icon${createSizeModifier(size)}`} version="1.2" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg" width="0" height="0" viewBox="0 0 100 100">
      <path d="M69.2 38.46H45.46l-6.25-5.68H28.55c-.82 0-1.48.66-1.48 1.48v36.3c0 .82.66 1.48 1.48 1.48h1.12l5.9-30.34h35.11v-1.76c0-.82-.67-1.48-1.48-1.48zm0 0" />
      <path d="M50 0C22.39 0 0 22.39 0 50s22.39 50 50 50 50-22.39 50-50S77.61 0 50 0zm25.75 70.91a6.659 6.659 0 0 1-6.45 6.3c-.03 0-.07.01-.1.01H28.55c-3.67 0-6.66-2.99-6.66-6.67v-36.3c0-3.68 2.99-6.67 6.67-6.67h12.66l6.25 5.68H69.2c3.67 0 6.66 2.99 6.66 6.66v1.76h5.97l-6.08 29.23zm0 0" />
    </svg>
  );
}
