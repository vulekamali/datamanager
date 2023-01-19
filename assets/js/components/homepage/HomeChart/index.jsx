import ResponsiveChart from './../../universal/ResponsiveChart/index.jsx';
import ValueBlocks from './../ValueBlocks/index.jsx';

export default function HomeChart(props) {
  const {
    items,
    width,
    mobile,
    hasNull,
  } = props;

  const { parentAction } = props;

  const withValues = (
    <div className="Section-card">
      <ResponsiveChart
        name="programmes-chart"
        type="bar"
        {...{ items }}
      />
    </div>
  );


  return hasNull ? <ValueBlocks {...{ items }} /> : withValues;
}
