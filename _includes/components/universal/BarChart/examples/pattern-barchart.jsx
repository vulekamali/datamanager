import { h, render } from 'preact';
import BarChart from './../index.jsx';


function pattern() {
  const basic = document.getElementById('pattern-barchart-basic');
  const download = document.getElementById('pattern-barchart-download');
  const multiple = document.getElementById('pattern-barchart-multiple');
  const no = document.getElementById('pattern-barchart-no');

  if (basic) {
    render(
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
    render(
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
    render(
      <BarChart
        items={{ 'Test 1': [10], 'Test 2': [30], 'Test 3': [20] }}
        width={700}
      />,
      no,
    );
  }

  if (download) {
    render(
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
