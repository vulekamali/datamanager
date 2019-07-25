import { h, render } from 'preact';
import ReactHtmlConnector from 'react-html-connector';


const { connect: jsConnect } = new ReactHtmlConnector(null, null, { library: 'none' });
const { connect: preactConnect } = new ReactHtmlConnector(h, render, { library: 'preact' });
export { jsConnect, preactConnect };
