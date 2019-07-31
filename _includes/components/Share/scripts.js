import Share from './index.jsx';
import { preactConnect as connect } from '../../utilities/js/helpers/connector.js';


export default connect(Share, 'Share', { anchor: 'string', color: 'string' });
