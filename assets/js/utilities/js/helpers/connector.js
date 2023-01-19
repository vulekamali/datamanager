import React from 'react';
import ReactDOM from 'react-dom';
import ReactHtmlConnector from 'react-html-connector';


const { connect: jsConnect } = new ReactHtmlConnector(null, null, { library: 'none' });
const { connect: preactConnect } = new ReactHtmlConnector(React.createElement, ReactDOM.render);
export { jsConnect, preactConnect };
