import PropTypes from 'prop-types';
import FormArea from './partials/FormArea.jsx';
import ResultsArea from './partials/ResultsArea.jsx';
import React from 'react';

export default function SearchMarkup(props) {
  const {
    count,
    currentKeywords,
    error,
    findSuggestions,
    focus,
    itemsArray,
    loading,
    searching,
    selectedYear,
    setFocus,
  } = props;

  if (loading) {
    return (
      <div className="Search-wrap">
        <div className="Search-form is-loading" />
      </div>
    );
  }

  const addFocus = () => setFocus(true);
  const removeFocus = () => setFocus(false);

  return (
    <div className="Search">

      <div className="Search-mobile" onClick={addFocus}>
        <svg className="Icon" width="0" height="0" version="1.2" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
          <title>Search</title>
          <path d="M97.2 85.4L75.5 63.8l-.4-.3C79.5 57 82 49.3 82 41c0-22.6-18.3-41-41-41S0 18.3 0 41c0 22.6 18.3 41 41 41 8.3 0 16-2.5 22.5-6.7l.3.4 21.6 21.6c3.3 3.3 8.5 3.3 11.8 0 3.2-3.4 3.2-8.6 0-12zM41 67.7c-14.8 0-26.8-12-26.8-26.8 0-15 12-27 26.8-27s26.8 12 26.8 27c0 14.7-12 26.7-26.8 26.7z" />
        </svg>
      </div>
      <div className={`Search-float${focus ? ' is-focused' : ''}`}>
        <div
          className={`Search-modalCover${focus ? ' is-focused' : ''}`}
          onClick={removeFocus}
        />
        <div className={`Search-wrap${focus ? ' is-focused' : ''}`}>
          <div className="Search-formWrap">
            <FormArea
              {...{
                currentKeywords,
                selectedYear,
                setFocus,
                focus,
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

SearchMarkup.propTypes = {
  count: PropTypes.string.isRequired,
  currentKeywords: PropTypes.string.isRequired,
  error: PropTypes.bool.isRequired,
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

  loading: PropTypes.bool.isRequired,
  searching: PropTypes.bool.isRequired,
  selectedYear: PropTypes.string.isRequired,
  setFocus: PropTypes.func.isRequired,
};

SearchMarkup.defaultProps = {
  itemsArray: [],
};
