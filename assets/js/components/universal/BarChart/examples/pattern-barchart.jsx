import React from 'react';
import ReactDOM from 'react-dom';
import BarChart from './../index.jsx';


function pattern() {
  const basic = document.getElementById('pattern-barchart-basic');
  const download = document.getElementById('pattern-barchart-download');
  const multiple = document.getElementById('pattern-barchart-multiple');
  const no = document.getElementById('pattern-barchart-no');

  if (basic) {
    ReactDOM.render(
      <BarChart
        items={{ 'Test 1': [10], 'Test 2': [30], 'Test 3': [20] }}
        width={300}
        hover
        guides
      />,
      basic,
    );
  }

  if (multiple) {
    ReactDOM.render(
      <BarChart
        items={{ 'Test 1': [10, 50, 0], 'Test 2': [30, 10, 40], 'Test 3': [20, 0, 10] }}
        width={600}
        hover
        guides
      />,
      multiple,
    );
  }

  if (no) {
    ReactDOM.render(
      <BarChart
        items={{ 'Test 1': [10], 'Test 2': [30], 'Test 3': [20] }}
        width={700}
      />,
      no,
    );
  }

  if (download) {
    ReactDOM.render(
      <BarChart
        items={{ 'Test 1': [10], 'Test 2': [30], 'Test 3': [20] }}
        width={600}
        scale={1.5}
        download={{
          heading: 'Test Heading',
          subHeading: 'Sub Heading Test',
          type: 'Type Test',
        }}
      />,
      download,
    );
  }
}


export default pattern();
