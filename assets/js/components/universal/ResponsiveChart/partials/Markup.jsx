import { h } from 'preact';
import BarChart from './../../BarChart/index.jsx';
import LineChart from './../../LineChart/index.jsx';


export default function Markup(props) {
  const {
    width,
    type,
    items,
    guides,
    hover,
    purple,
  } = props;

  const { getNode } = props;


  if (type === 'bar') {
    return (
      <BarChart
        scale={1}
        {...{ getNode, items, width, guides, hover, purple }}
      />
    );
  }

  if (type === 'line') {
    return (
      <LineChart
        {...{ getNode, width, items, guides, hover }}
      />
    );
  }
}
