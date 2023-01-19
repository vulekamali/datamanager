import createSizeModifier from './createSizeModifier.js';


export default function Play({ size }) {
  return (
    <svg className={`Icon${createSizeModifier(size)}`} version="1.2" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
      <path d="M85.9 48L16.9.4c-.7-.5-1.7-.6-2.5-.1-.8.4-1.3 1.2-1.3 2.1v95.2c0 .9.5 1.7 1.3 2.1.3.2.7.3 1.1.3a2 2 0 0 0 1.3-.4l69-47.6c.7-.4 1-1.2 1-2 .1-.8-.3-1.5-.9-2zm0 0" />
    </svg>
  );
}
