import React from 'react';
import PropTypes from 'prop-types';
import Icon from './Icon.jsx';


export default function FormArea({ setFocus, currentKeywords, selectedYear }) {
  const searchUrl = `/${selectedYear}/search-result`;
  const addFocus = () => setFocus(true);

  return (
    <form className="Search-form" action={searchUrl} method="GET">
      <input type="hidden" name="search_type" value="full-search" />
      <input type="hidden" name="search_string" value={currentKeywords} />

      <input
        autoComplete="off"
        className="Search-keywords"
        name="search"
        onFocus={addFocus}
        placeholder="Search vulekamali"
        value={currentKeywords}
      />

      <div className="Search-action">
        <button className="Search-button" type="submit">
          <Icon size="s" />
        </button>
      </div>
    </form>
  );
}


FormArea.propTypes = {
  currentKeywords: PropTypes.string.isRequired,
  selectedYear: PropTypes.string.isRequired,
  setFocus: PropTypes.func.isRequired,
};
