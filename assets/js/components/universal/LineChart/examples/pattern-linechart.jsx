import { h, render } from 'preact';
import LineChart from './../index.jsx';


function pattern() {
  const basic = document.getElementById('pattern-linechart-basic');
  const multiple = document.getElementById('pattern-linechart-multiple');
  const no = document.getElementById('pattern-linechart-no');

  if (basic) {
    render(
      <LineChart
        items={{ 'Test 1': [10], 'Test 2': [30], 'Test 3': [20] }}
        width={500}
        hover
        guides
      />,
      basic,
    );
  }

  if (multiple) {
    render(
      <LineChart
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
      <LineChart
        items={{ 'Test 1': [10], 'Test 2': [30], 'Test 3': [20] }}
        width={700}
      />,
      no,
    );
  }
}


export default pattern();
