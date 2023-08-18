import { ga } from 'react-ga';
import ReactDOM from 'react-dom';
import React from 'react';
import PropTypes from 'prop-types';
import queryString from 'query-string';
import Search from './index.jsx';
import removePunctuation from '../../../utilities/js/helpers/removePunctuation.js';


class SearchContainer extends React.Component {
  constructor(props) {
    super(props);

    // 'currentKeywords' indicates the current text the user typed in the search box
    // The second block contains factors that influence the UI state (searching means that UI is awaiting HTTP reponse for search suggestions)
    // The third block contains timeout specific variables (used when there is a delay/throttling in the UI)
    // The last block contains data that is retrieved from the HTTP request for search suggestions
    this.state = {
      currentKeywords: this.props.searchParam,

      focus: false,
      loading: false,
      searching: false,
      error: false,

      timeoutFocus: null,
      timeoutId: null,

      itemsArray: [],
      count: null,
    };

    this.setFocus = this.setFocus.bind(this);
  }

  /**
   * Debounces setting the focus state of the search input (and subsequently the dropdown) by 500 miliseconds. This means that the search only closes if the mouse has left it for a minimum of 500 miliseconds.
   *
   * @param {boolean} value - Whether you want to set the focus on the search input to `true` or `false`.
   */
  setFocus(value) {
    return this.setState({ focus: value });
  }

  render() {
    return (
      <Search
        currentKeywords={this.state.currentKeywords}

        focus={this.state.focus}
        loading={this.state.loading}
        searching={this.state.searching}
        error={this.state.error}

        itemsArray={this.state.itemsArray}
        count={this.state.count}

        setFocus={this.setFocus}

        selectedYear={this.props.selectedYear}
      />
    );
  }
}


SearchContainer.propTypes = {
  searchParam: PropTypes.string,
  selectedYear: PropTypes.string.isRequired,
  requestOverride: PropTypes.string,
};

SearchContainer.defaultProps = {
  searchParam: '',
  requestOverride: null,
};


function scripts() {
  // Find all instances of a specific UI component on a page by parent class name.
  const componentsList = document.getElementsByClassName('js-initSearch');

  // Destructure needed query strings from URL
  const { search: searchParam, no_js: noJs } = queryString.parse(location.search) || {};

  if (componentsList.length > 0 && !noJs) {
    for (let i = 0; i < componentsList.length; i++) {
      // Find DOM node that will house the Preact app and get associated data attributes that are passed via HTML
      const component = componentsList[i];
      const requestOverride = component.getAttribute('data-request-override');
      const selectedYear = component.getAttribute('data-year');

      if (!selectedYear) {
        console.error("year data attribute not found in page.");
      }

      // Initialise Search Preact App
      ReactDOM.render(
        <SearchContainer {...{ requestOverride, selectedYear, searchParam }} />,
        component,
      );
    }
  }
}


export default scripts();
