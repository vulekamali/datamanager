import { jsConnect as connect } from '../../../../../utilities/js/helpers/connector.js';
import trimValues from '../../../../../utilities/js/helpers/trimValues.js';

const formatValue = ({ node, amount }) => {
  node.innerHTML = `R ${trimValues(amount)}`;
  return null;
};


export default connect(formatValue, 'ChangeIndicator', { node: null, amount: 'number' });
