import { h } from 'preact';
import createSizeModifier from './createSizeModifier.js';


export default function Home({ size }) {
  return (
    <svg className={`Icon${createSizeModifier(size)}`} version="1.2" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
      <path d="M83 27V9.3c0-3.2-2.6-5.7-5.7-5.7-3.2 0-5.7 2.6-5.7 5.7v6L60.3 4.2c-5.6-5.6-15.3-5.6-20.8 0L1.7 42c-2.2 2.2-2.2 6 0 8 2.2 2.3 6 2.3 8 0l38-37.7c1-1.2 3.3-1.2 4.5 0L90 50c1 1.2 2.6 1.8 4 1.8 1.5 0 3-.6 4-1.7 2.2-2 2.2-5.8 0-8L83 27z" />
      <path d="M52 23c-1.2-1-3-1-4 0L14.6 56.5c-.5.5-.8 1.2-.8 2v24.3C14 88.4 18.4 93 24 93h16.5V67.5h18.6V93h16.5C81.4 93 86 88.4 86 82.7V58.4c0-.7-.3-1.5-.8-2L52 23zm0 0" />
    </svg>
  );
}
