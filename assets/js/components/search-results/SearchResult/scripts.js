import SearchResult from './services/SearchResult.js';
import { preactConnect } from '../../../utilities/js/helpers/connector.js';


const query = {
  year: 'string',
  root: null,
  search: 'url',
  view: 'url',
};


export default preactConnect(SearchResult, 'SearchResult', query);
