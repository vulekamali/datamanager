import { h } from 'preact';
import PropTypes from 'prop-types';
import List from './List.jsx';


// ...
export default function ResultsArea(props) {
  const {
    count,
    currentKeywords,
    error,
    findSuggestions,
    focus,
    itemsArray,
    searching,
    selectedYear,
  } = props;


  // ...
  const resultsClass = `Search-results${currentKeywords.length >= 2 && focus ? ' is-open' : ''}`;

  // ...
  return (
    <div className={resultsClass}>
      <List
        {...{
          count,
          currentKeywords,
          error,
          findSuggestions,
          itemsArray,
          searching,
          selectedYear,
        }}
      />
    </div>
  );
}


ResultsArea.propTypes = {
  count: PropTypes.string.isRequired,
  currentKeywords: PropTypes.string.isRequired,
  error: PropTypes.bool.isRequired,
  findSuggestions: PropTypes.func.isRequired,
  focus: PropTypes.bool.isRequired,

  itemsArray: PropTypes.arrayOf(
    PropTypes.shape({
      sphere: PropTypes.arrayOf(PropTypes.string),
      financial_year: PropTypes.arrayOf(PropTypes.string),
      extras: PropTypes.arrayOf(
        PropTypes.shape({
          key: PropTypes.string,
          value: PropTypes.string,
        }),
      ),
    }),
  ),

  searching: PropTypes.bool.isRequired,
  selectedYear: PropTypes.string.isRequired,
};


ResultsArea.defaultProps = {
  itemsArray: [],
};
