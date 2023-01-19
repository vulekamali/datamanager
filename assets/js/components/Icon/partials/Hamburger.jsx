import createSizeModifier from './createSizeModifier.js';


export default function Hamburger({ size }) {
  return (
    <svg className={`Icon${createSizeModifier(size)}`} version="1.2" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <path d="M5.8 19.7h88.4c3.2 0 5.8-2.6 5.8-5.9 0-3.3-2.6-5.9-5.8-5.9H5.8A5.8 5.8 0 0 0 0 13.8c0 3.3 2.6 5.9 5.8 5.9zm88.4 24.4H5.8A5.8 5.8 0 0 0 0 50c0 3.3 2.6 5.9 5.8 5.9h88.4c3.2 0 5.8-2.6 5.8-5.9 0-3.3-2.6-5.9-5.8-5.9zm0 36.2H5.8A5.9 5.9 0 0 0 0 86.2c0 3.3 2.6 5.9 5.8 5.9h88.4c3.2 0 5.8-2.6 5.8-5.9 0-3.3-2.6-5.9-5.8-5.9zm0 0" />
    </svg>
  );
}
